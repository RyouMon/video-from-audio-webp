from pipelines import Pipeline


class ContinuousTextPipeline(Pipeline):

    def process(self, infile, outfile, context):
        video = self.input(infile)
        audio = video.audio

        for text, font, size, color, x, y in context['texts']:
            video = video.drawtext(text=text, fontfile=font, fontcolor=color, fontsize=size, x=x, y=y)

        return self.output(video, audio, outfile), context


class SubtitlePipeline(Pipeline):

    def process(self, infile, outfile, context):
        video = self.input(infile)
        audio = video.audio

        video = video.filter('subtitles', context['srt_file'], force_style=context.get('force_style'))
        return self.output(video, audio, outfile), context
