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
    def from_settings(cls, settings, parser):
        """Use settings module create PipelineManager instance"""
        pipelines = []

        pipeline_paths = settings.PIPELINES
        for cls_path in pipeline_paths:
            pipeline_cls = load_object(cls_path)
            if hasattr(pipeline_cls, 'add_arguments'):
                pipeline_cls.add_arguments(parser)
            pipelines.append(pipeline_cls(settings))

        return cls(*pipelines, settings=settings)

    def _prepare_processes(self, infile, outfile, context):
        """call process on each pipeline"""
        workspace = self.workspace.name

        if self._size == 1:
            out, _ = self.pipelines[0].process(infile, outfile, context)
            return [out]

        output_streams = []

        out, context = self.pipelines[0].process(infile, join(workspace, 'step1.mp4'), context)
        output_streams.append(out)

        for i, pipeline in enumerate(self.pipelines[1:-1]):
            out, context = pipeline.process(join(workspace, f'step{i+1}.mp4'), join(workspace, f'step{i+2}.mp4'), context)
            output_streams.append(out)

        out, _ = self.pipelines[-1].process(join(workspace, f'step{self._size-1}.mp4'), outfile, context)
        output_streams.append(out)

        return output_streams

    def _run_processes(self, *output_streams, quiet):
        """call run_async() on each output process"""
        code = 0

        for stream in output_streams:
            process = stream.run_async(quiet=quiet)

            if process.wait():
                code = process.returncode
                break

        return code

    def process(self, infile, outfile, context=None):

        if context is None:
            context = {}
        context['infile'] = infile

        output_streams = self._prepare_processes(infile, outfile, context)
        return self._run_processes(*output_streams, quiet=not self.debug)

    def __del__(self):
        self.workspace.cleanup()


class Pipeline:

    def __init__(self, settings):
        self.logger = logging.getLogger('maker.' + self.__class__.__qualname__)
        self.settings = settings
        self.overwrite_output = settings.OVERWRITE_OUTPUT

    def process(self, infile, outfile, context):
        raise NotImplementedError()

    def input(self, infile, **kwargs):
        return ffmpeg.input(infile, thread_queue_size=self.settings.THREAD_QUEUE_SIZE, **kwargs)

    def output(self, *streams_and_filename, **kwargs):
        output = ffmpeg.output(*streams_and_filename, **kwargs)

        if self.overwrite_output:
            output = output.overwrite_output()

        self.logger.info(
            'run command: "{}"'.format(' '.join(ffmpeg.compile(output)))
        )

        return output
