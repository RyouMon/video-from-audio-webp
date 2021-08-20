import ffmpeg
from pipelines import Pipeline


class BlackBackgroundPipeline(Pipeline):

    def process(self, infile, outfile, context):
        input_a = self.input(infile).audio
        context = {'a': input_a}
        input_v = ffmpeg.input('fixtures/black1080x1920.jpg', loop=1)
        return self.output(input_v, input_a, outfile, y=None, acodec='aac', r=25, shortest=None), context
