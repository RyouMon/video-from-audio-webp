import autosubb
import need_an_image
from progressbar import ProgressBar, Percentage, Bar, ETA
from settings import *


def generate_subtitles(filename):
    """
    generate subtitle from media file
    """
    return autosubb.generate_subtitles(
        source_path=filename, app_id=APP_ID, api_key=API_KEY, secret_key=SECRET_KEY, concurrency=1,
        dev_pid='80001',
    )


def generate_srt(subtitles):
    return autosubb.formatters.srt_formatter(subtitles)


def generate_slideshows(keywords, save_to):
    widgets = ["Downloading Images: ", Percentage(), ' ', Bar(), ' ', ETA()]

    def get_image(keyword):
        image = need_an_image.need_image_from('bing', keyword[1], exact=False, allow_pos=(
            'n', 'nr', 'nz', 'PER', 'LOC', 'ORG', 'nw', 'nt', 's', 'ns',
        ), save_to=save_to)
        return keyword[0], image

    slideshows = []

    pbar = ProgressBar(widgets=widgets, maxval=len(keywords)).start()
    for i, keyword in enumerate(keywords):
        slideshows.append(get_image(keyword))
        pbar.update(i)
    pbar.finish()

    return slideshows
