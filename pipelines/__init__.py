import ffmpeg
from utils import load_object


class PipelineManager:

    def __init__(self, *pipelines):
        self.pipelines = pipelines
        self._size = len(pipelines)

    @classmethod
    def from_settings(cls, settings):
        """Use settings module create PipelineManager instance"""
        pipelines = []

        pipeline_paths = settings.PIPELINES
        for cls_path in pipeline_paths:
            pipeline_cls = load_object(cls_path)
            pipelines.append(pipeline_cls(settings))

        return cls(*pipelines)

    def _prepare_processes(self, infile, outfile, context):
        """call process on each pipeline"""
        if self._size == 1:
            out, _ = self.pipelines[0].process(infile, outfile, context)
            return [out]

        processes = []

        out, context = self.pipelines[0].process(infile, 'pipe:', context)
        processes.append(out)

        for pipeline in self.pipelines[1:-1]:
            out, context = pipeline.process('pipe:', 'pipe:', context)
            processes.append(out)

        out, _ = self.pipelines[-1].process('pipe:', outfile, context)
        processes.append(out)

        return processes

    def _run_processes(self, *processes):
        """call run_async() on each output process"""
        if self._size == 1:
            return [processes[0].run_async()]

        subprocesses = [processes[0].run_async(pipe_stdout=True)]

        for process in processes[1:-1]:
            subprocesses.append(process.run_async(pipe_stdin=True, pipe_stdout=True))

        subprocesses.append(processes[-1].run_async(pipe_stdin=True))

        return subprocesses

    def _connect_processes(self, *subprocesses):
        """communicate between processes"""
        out, err = subprocesses[0].communicate()
        if self._size == 1:
            return out, err

        for process in subprocesses[1:-1]:
            out, err = process.communicate(input=out)

        return subprocesses[-1].communicate(input=out)

    def _wait_processes(self, *subprocesses):
        """wait subprocesses terminate"""
        code = subprocesses[0].wait()

        if self._size == 1:
            return code

        for subprocess in subprocesses[1:]:
            subprocess.stdin.close()
            subprocess.wait()

    def process(self, infile, outfile, context=None):
        output_processes = self._prepare_processes(infile, outfile, context)
        subprocesses = self._run_processes(*output_processes)
        out, err = self._connect_processes(*subprocesses)
        code = self._wait_processes(*subprocesses)
        return code, out, err


class Pipeline:

    def __init__(self, settings):
        self.settings = settings

    def process(self, infile, outfile, context=None):
        raise NotImplementedError()

    def input(self, infile, **kwargs):
        if infile == 'pipe:':
            kwargs.update({'format': 'rawvideo', 'pix_fmt': 'rgb24', 's': '1080x1920'})
        return ffmpeg.input(infile, thread_queue_size=100, **kwargs)

    def output(self, *streams_and_filename, **kwargs):
        streams_and_filename = list(streams_and_filename)
        if 'filename' not in kwargs:
            if not isinstance(streams_and_filename[-1], str):
                raise ValueError('A filename must be provided')
            kwargs['filename'] = streams_and_filename.pop(-1)

        if kwargs['filename'] == 'pipe:':
            kwargs.update({'format': 'rawvideo', 'pix_fmt': 'rgb24'})
        output = ffmpeg.output(*streams_and_filename, **kwargs)
        cmd = ffmpeg.compile(output)
        print(cmd)
        return output
