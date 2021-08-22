import ffmpeg
from pipelines import Pipeline


class SocialMediaBlackBackgroundPipeline(Pipeline):

    def process(self, infile, outfile, context):
        audio = self.input(infile).audio

        stream = ffmpeg.input('color=black:1080x1920', f='lavfi')
        return self.output(stream, audio, outfile, shortest=None), context
