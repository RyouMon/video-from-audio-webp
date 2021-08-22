from pipelines import Pipeline


class DoubleTitlePipeline(Pipeline):

    def process(self, infile, outfile, context):
        video = self.input(infile)
        audio = video.audio

        for text, x, y in zip(context.titles, context.titles_x_positions, context.titles_y_positions):
            video = video.drawtext(
                text=text,
                fontfile=self.settings.DEFAULT_FONT_FILE,
                fontcolor=context.title_color,
                fontsize=context.title_size,
                x=x,
                y=y,
            )

        return self.output(video, audio, outfile), context

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument('-T', '--titles', help="Video titles", nargs=2)
        parser.add_argument('--titles-x-positions', help="Title X Positions", nargs=2, default=['w/2-tw/2', 'w/2-tw/2'])
        parser.add_argument('--titles-y-positions', help="Title Y Positions", nargs=2, default=[100, 360])
        parser.add_argument('--title-size', default=100)
        parser.add_argument('--title-color', default='white')


class SubtitlePipeline(Pipeline):

    def process(self, infile, outfile, context):
        video = self.input(infile)
        audio = video.audio

        video = video.filter('subtitles', context.srt_file, force_style=context.force_style)
        return self.output(video, audio, outfile), context
