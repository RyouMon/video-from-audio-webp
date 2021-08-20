import ffmpeg
from pipelines import Pipeline


class BlackBackgroundPipeline(Pipeline):

    def process(self, infile, outfile, context):
        input_a = self.input(infile).audio
        context = {'a': input_a}
        input_v = ffmpeg.input('color=black:1080x1920', f='lavfi')
        return self.output(input_v, input_a, outfile, y=None, acodec='aac', r=25, shortest=None), context
