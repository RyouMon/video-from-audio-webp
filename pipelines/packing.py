import ffmpeg
from pipelines import Pipeline


class PackingAudioVideoPipeline(Pipeline):

    def process(self, infile, outfile, context):
        stream = self.input(infile)
        audio = ffmpeg.input(context['infile'])
        return self.output(stream, audio, outfile), context
