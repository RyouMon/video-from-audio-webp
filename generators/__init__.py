import autosubb
import need_an_image
import multiprocessing
from progressbar import ProgressBar, Percentage, Bar, ETA
from settings import *


def generate_subtitles(filename, concurrency=1):
    """
    generate subtitle from media file
    """
    return autosubb.generate_subtitles(
        source_path=filename, app_id=APP_ID, api_key=API_KEY, secret_key=SECRET_KEY, concurrency=concurrency,
        dev_pid='80001',
    )


def generate_srt(subtitles):
    return autosubb.formatters.srt_formatter(subtitles)


class SlideshowDownloader:

    def __init__(self, save_to, allow_pos=()):
        self.save_to = save_to
        self.allow_pos = allow_pos

    def __call__(self, subtitle):
        """
        :param subtitle: ((start, end), subtitle)
        :return: ((start, end), filename)
        """
        return subtitle[0], need_an_image.need_image_from(
            engine='bing',
            keyword=subtitle[1],
            exact=False,
            allow_pos=self.allow_pos,
            save_to=self.save_to
        )


def generate_slideshows(
        subtitles, save_to, concurrency=1,
        allow_pos=('n', 'nr', 'nz', 'PER', 'LOC', 'ORG', 'nw', 'nt', 's', 'ns')):
    """
    Passing a keyword list, download image for each keyword, return an image filename list.
    :param subtitles: A subtitle list: [((start, end), subtitle) ...]
    :param save_to: A path, image will download to this location
    :param concurrency: Number of files downloaded at the same time
    :param allow_pos: Part of speech used when extracting keywords
    :return: Filename list
    """
    pool = multiprocessing.Pool(concurrency)
    widgets = ["Downloading Images: ", Percentage(), ' ', Bar(), ' ', ETA()]
    downloader = SlideshowDownloader(save_to, allow_pos=allow_pos)

    slideshows = []
    pbar = ProgressBar(widgets=widgets, maxval=len(subtitles)).start()

    try:
        for i, slideshow in enumerate(pool.imap(downloader, subtitles)):
            slideshows.append(slideshow)
            pbar.update(i)
        pbar.finish()

    except KeyboardInterrupt:
        pbar.finish()
        pool.terminate()
        pool.join()
        print("Cancelling Slideshow Downloading")
        raise

    return slideshows
