import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('source_path', help="Path to the video or audio file")
parser.add_argument('-o', '--output',
                    help="Output path for subtitles (by default, subtitles are saved in \
                        the same directory and name as the source path)")


def validate(args):

    if not os.path.exists(args.source_path):
        print(f'source_path Error: File "{args.source_path}" not exists!')
        return False

    if not os.path.isfile(args.source_path):
        print(f'source_path Error: "{args.source_path}" is not a file!')
        return False

    if not args.titles or len(args.titles) != 2:
        print(f'titles Error: you must provide two title!')
        return False

    if args.output is None:
        args.output = '-'.join(args.titles) + '.mp4'

    return True
