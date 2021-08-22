import os
import sys
from uuid import uuid4
import logging.config
from tempfile import TemporaryDirectory

import generators
import settings
from pipelines import PipelineManager
from utils.cmd import parser, validate


def main():
    logging.config.dictConfig(settings.LOGGING)
    manager = PipelineManager.from_settings(settings, parser)

    args = parser.parse_args()
    if not validate(args):
        return 1

    workspace = TemporaryDirectory()

    try:
        raw_subtitles = generators.generate_subtitles(args.source_path)

        srt_filename = uuid4().hex[:6] + '.srt'
        with open(srt_filename, 'wb') as f:
            srt_file = generators.generate_srt(raw_subtitles)
            f.write(srt_file.encode('utf-8'))

        slideshows = generators.generate_slideshows(raw_subtitles, save_to=workspace.name)

        args.srt_file = srt_filename
        args.force_style = 'MarginV=35'
        args.slideshows = slideshows

        code = manager.process(args.source_path, args.output, context=args)
    except Exception as e:
        workspace.cleanup()
        os.remove(srt_filename)
        raise e
    finally:
        os.remove(srt_filename)
        workspace.cleanup()

    return code


if __name__ == '__main__':
    sys.exit(main())
