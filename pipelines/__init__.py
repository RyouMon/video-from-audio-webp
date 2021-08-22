import logging
import ffmpeg
from os.path import join
from tempfile import TemporaryDirectory
from utils.misc import load_object


class PipelineManager:

    def __init__(self, *pipelines, settings):
        self.pipelines = pipelines
        self.settings = settings
        self.debug = settings.DEBUG
        self._size = len(pipelines)
        self.workspace = TemporaryDirectory()

    @classmethod
    def from_settings(cls, settings):
        """Use settings module create PipelineManager instance"""
        pipelines = []

        pipeline_paths = settings.PIPELINES
        for cls_path in pipeline_paths:
            pipeline_cls = load_object(cls_path)
            pipelines.append(pipeline_cls(settings))

        return cls(*pipelines, settings=settings)

    def _prepare_processes(self, infile, outfile, context):
        """call process on each pipeline"""
        workspace = self.workspace.name

        if self._size == 1:
            out, _ = self.pipelines[0].process(infile, outfile, context)
            return [out]

        processes = []

        out, context = self.pipelines[0].process(infile, join(workspace, 'step1.mp4'), context)
        processes.append(out)

        for i, pipeline in enumerate(self.pipelines[1:-1]):
            out, context = pipeline.process(join(workspace, f'step{i+1}.mp4'), join(workspace, f'step{i+2}.mp4'), context)
            processes.append(out)

        out, _ = self.pipelines[-1].process(join(workspace, f'step{self._size-1}.mp4'), outfile, context)
        processes.append(out)

        return processes

    def _run_processes(self, *processes, quiet):
        """call run_async() on each output process"""
        if self._size == 1:
            return [processes[0].run_async(quiet=quiet)]

        subprocesses = [processes[0].run_async(pipe_stdout=True, quiet=quiet)]

        for process in processes[1:-1]:
            subprocesses.append(process.run_async(pipe_stdin=True, pipe_stdout=True, quiet=quiet))

        subprocesses.append(processes[-1].run_async(pipe_stdin=True, quiet=quiet))

        return subprocesses

    def process(self, infile, outfile, context=None):

        if context is None:
            context = {}
        context['infile'] = infile

        output_processes = self._prepare_processes(infile, outfile, context)
        subprocesses = self._run_processes(*output_processes, quiet=not self.debug)
        out, err = self._connect_processes(*subprocesses)
        code = self._wait_processes(*subprocesses)
        return code, out, err

    def __del__(self):
        self.workspace.cleanup()


class Pipeline:

    def __init__(self, settings):
        self.logger = logging.getLogger('maker.' + self.__class__.__qualname__)
        self.settings = settings
        self.overwrite_output = settings.OVERWRITE_OUTPUT
        self.fps = settings.FPS

    def process(self, infile, outfile, context):
        raise NotImplementedError()

    def input(self, infile, **kwargs):
        if infile == 'pipe:':
            kwargs.update({
                'format': 'rawvideo',
                'pix_fmt': 'rgb24',
                'video_size': (1080, 1920),
                'framerate': self.fps
            })

        return ffmpeg.input(infile, thread_queue_size=self.settings.THREAD_QUEUE_SIZE, **kwargs)

    def output(self, *streams_and_filename, **kwargs):
        streams_and_filename = list(streams_and_filename)
        if 'filename' not in kwargs:
            if not isinstance(streams_and_filename[-1], str):
                raise ValueError('A filename must be provided')
            kwargs['filename'] = streams_and_filename.pop(-1)

        if kwargs['filename'] == 'pipe:':
            kwargs.update({
                'format': 'rawvideo',
                'pix_fmt': 'rgb24',
                'r': self.fps,
            })
        output = ffmpeg.output(*streams_and_filename, **kwargs)

        if self.overwrite_output:
            output = output.overwrite_output()

        self.logger.info(
            'run command: "{}"'.format(' '.join(ffmpeg.compile(output)))
        )

        return output
