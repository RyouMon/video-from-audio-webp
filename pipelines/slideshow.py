import ffmpeg
from pipelines import Pipeline


class SlideShowPipeline(Pipeline):

    def process(self, infile, outfile, context):
        subtitles = self.get_subtitles(context['infile'])
        images = self.get_images(subtitles)
        video = self.input(infile)

        for timestamps, filename in images:
            image = ffmpeg.input(f'sample_files/{filename}')
            image = image.filter('scale', w=1080, h=-1)
            video = video.overlay(image, y=600, enable=f'gt(t,{timestamps[0]})')

        return self.output(video, outfile), context

    def get_subtitles(self, filename):
        return [
            ((0.256, 1.024), '安徒生童话是。'),
            ((1.28, 3.328000000000001), '是丹麦作家安徒生创作的童话集。'),
            ((3.8400000000000016, 5.8880000000000035), '共有166篇故事组成。'),
            ((6.144000000000004, 7.424000000000005), '该作爱憎分明。'),
            ((7.680000000000005, 9.216000000000006), '热情歌颂劳动人民。'),
            ((9.472000000000007, 11.008000000000008), '赞美他们的善良和。'),
            ((11.264000000000008, 12.80000000000001), '纯洁的优秀品德。'),
            ((13.05600000000001, 15.872000000000012), '无情的揭露和批判王公贵族们的愚蠢。'),
            ((16.12800000000001, 16.64000000000001), '无能。'),
            ((16.89600000000001, 18.176000000000013), '贪婪和残暴。'),
            ((18.432000000000013, 20.224000000000014), '其中较为闻名的故事有。'),
            ((20.736000000000015, 21.248000000000015), '小人鱼。'),
            ((21.760000000000016, 22.272000000000016), '丑小鸭。'),
            ((22.784000000000017, 24.064000000000018), '卖火柴的小女孩。'),
            ((24.320000000000018, 25.08800000000002), '拇指姑娘等。')
        ]

    def get_images(self, subtitles):
        return [
            ((0.256, 1.024), '1.jpg'),
            ((1.28, 3.328000000000001), '2.jpg'),
            ((3.8400000000000016, 5.8880000000000035), '3.jpg'),
            ((6.144000000000004, 7.424000000000005), '4.jpg'),
            ((7.680000000000005, 9.216000000000006), '5.jpg'),
            ((9.472000000000007, 11.008000000000008), '6.jpg'),
            ((11.264000000000008, 12.80000000000001), '7.jpg'),
            ((13.05600000000001, 15.872000000000012), '8.jpg'),
            ((16.12800000000001, 16.64000000000001), '9.jpg'),
            ((16.89600000000001, 18.176000000000013),'10.jpg'),
            ((18.432000000000013, 20.224000000000014), '11.jpg'),
            ((20.736000000000015, 21.248000000000015), '12.jpg'),
            ((21.760000000000016, 22.272000000000016), '13.jpg'),
            ((22.784000000000017, 24.064000000000018), '14.jpg'),
            ((24.320000000000018, 25.08800000000002), '15.jpg')
        ]
