import ffmpeg
from pipelines import Pipeline


class MaskingPipeline(Pipeline):

    def process(self, infile, outfile, context):
        video = self.input(infile)
        mask = ffmpeg.input('color=black:1080x600', f='lavfi')
        video = video.overlay(mask, shortest=1)
        video = video.overlay(mask, y='H-600', shortest=1)
        return self.output(video, context['a'], outfile), context
