import os
from unittest import TestCase
from make import generate_video


class VideoGenerateTest(TestCase):

    def test_video_generate(self):
        file_num = len(os.listdir())
        filename = generate_video('sample_files/sample.aac')

        self.assertEqual(len(os.listdir()), file_num + 1)
        self.assertTrue(filename.endswith('.mp4'))
