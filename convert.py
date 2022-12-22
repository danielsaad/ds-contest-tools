import argparse
import os
import sys
from utils import instance_paths
from jsonutils import parse_json
from json import dumps
from logger import info_log
from getpass import getpass
from polygon_submitter import send_to_polygon
from fileutils import write_secrets


def create_parser() -> argparse.ArgumentParser:
    """Initialize the argparser of the tool."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '-o', '--output', help='Directory where the problem will be saved. Default is "./".')
    parser.add_argument('-c', '--change-keys',
                        help='Change Polygon API keys.', action='store_true')
    parser.add_argument('reader', choices=['BOCA', 'DS', 'Polygon'],
                        help='Input problem format')
    parser.add_argument('writer', choices=['BOCA', 'DS', 'Polygon', 'SQTPM'],
                        help='Input problem format')
    parser.add_argument('problem_dir', help='Path to the problem.')
    return parser


def change_polygon_keys(secrets_path: str) -> None:
    """"""
    print('Define the keys used by Polygon API.' +
          'They will be stored locally in the tool directory.')

    write_secrets()
    keys = parse_json(secrets_path)
    keys["apikey"] = getpass('apiKey: ')
    keys["secret"] = getpass('secret: ')
    with open(secrets_path, 'w') as f:
        f.write(dumps(keys))
    info_log("Keys defined.")


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    if not os.path.exists(args.problem_dir):
        print("Problem path does not exist.")
        sys.exit(0)

    if (args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)

    tool_path = os.path.dirname(os.path.abspath(__file__))
    secrets_path = os.path.join(tool_path, 'secrets.json')
    output_dir = "" if args.output_dir == None else args.output_dir
    instance_paths(args.problem_dir, output_dir)

    if args.reader == 'Polygon' or args.writer == 'Polygon':
        if args.change_keys or not os.path.exists(secrets_path):
            change_polygon_keys(secrets_path)

    if (args.reader == 'Polygon'):
        if (args.writer == 'DS'):
            # TODO
            pass
        else:
            print("Not implemented yet.")
            pass
    elif (args.reader == 'DS'):
        if (args.writer == 'Polygon'):
            send_to_polygon()
            print('Problem sent successfully.')
        else:
            # TODO
            print("Not implemented yet.")
            pass
    elif (args.reader == 'BOCA'):
        # TODO
        print("Not implemented yet.")
        pass
