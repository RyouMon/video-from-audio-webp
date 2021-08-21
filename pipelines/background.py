import ffmpeg
from pipelines import Pipeline


class SocialMediaBlackBackgroundPipeline(Pipeline):

    def process(self, infile, outfile, context):
        duration = context.get('duration', 0)
        duration = self.clean_duration(duration)

        stream = ffmpeg.input('color=black:1080x1920', f='lavfi')
        return self.output(stream, outfile, t=duration), context

    def clean_duration(self, value):

        if not value:
            self.logger.error('output duration set to 0!')
            raise ValueError('You must set duration(>0) on context!')

        if isinstance(value, (int, float)):
            return value

        try:
            return float(value)
        except ValueError:
            self.logger.error(f'output duration set to {value!r}!')
            raise ValueError('duration must a int or float!')
