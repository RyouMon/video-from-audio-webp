import os
import ffmpeg
from pipelines import Pipeline


class SlideShowPipeline(Pipeline):

    def process(self, infile, outfile, context):
        slideshows = self.clean_slideshows(context)
        video = self.input(infile)
        audio = video.audio

        size = len(slideshows)
        for i, ((start, end), filename) in enumerate(slideshows):
            image = ffmpeg.input(filename)
            image = image.filter('scale', w=1080, h=-1)
            if i < (size - 1):
                video = video.overlay(image, y=600, enable=f'between(t,{start},{slideshows[i+1][0][0]})')
            else:
                video = video.overlay(image, y=600, enable=f'gt(t,{start})')

        return self.output(video, audio, outfile), context

    def clean_slideshows(self, context):
        slideshows = context.get('slideshows')

        if not slideshows:
            raise ValueError('You must set "slideshows" in context!')

        errors = []

        for timestamps, filename in slideshows:
            if not os.path.exists(filename):
                errors.append(f'file "{filename}" not exists!')

        if errors:
            raise ValueError(' '.join(errors))

        return slideshows
