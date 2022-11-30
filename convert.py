import argparse
import os
import sys
from utils import instance_paths
from jsonutils import parse_json
from json import dumps
from logger import info_log
from getpass import getpass
from polygon_submitter import send_to_polygon


def create_parser() -> argparse.ArgumentParser:
    """Initialize the argparser of the tool."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '-o', '--output_dir', help='Path to where the problem will be saved. Default is the same as problem_dir.')
    parser.add_argument('-c', '--change-keys', help='Change Polygon API keys.', action='store_true')
    parser.add_argument('reader', choices=['BOCA', 'DS', 'Polygon'],
                        help='Input problem format')
    parser.add_argument('writer', choices=['BOCA', 'DS', 'Polygon', 'SQTPM'],
                        help='Input problem format')
    parser.add_argument('problem_dir', help='Path to the problem.')
    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    tool_path = os.path.dirname(os.path.abspath(__file__))
    if (args.change_keys):
        print('The keys will be stored locally in the tool directory.')
        keys = dict()
        keys["polygon-apikey"] = getpass('Key: ')
        keys["polygon-secret"] = getpass('Secret: ')
        json_object = dumps(keys, indent=4)
        with open(os.path.join(tool_path, 'secrets.json'), 'w') as f:
            f.write(json_object)
        info_log("Keys defined.")

    output_dir = "" if args.output_dir == None else args.output_dir
    instance_paths(args.problem_dir, output_dir)
    if not os.path.exists(args.problem_dir):
        print("Problem path does not exist.")
        sys.exit(0)
    if (args.output_dir):
        os.makedirs(args.output_dir, exist_ok=True)

    if args.reader == 'Polygon' or args.writer == 'Polygon':
        if not os.path.exists(os.path.join(tool_path, 'secrets.json')):
            print("Polygon API keys not defined. Use flag '-c' or '--change-keys' to define.")
            sys.exit(0)
        keys = parse_json(os.path.join(tool_path, 'secrets.json'))
        if (keys['polygon-apikey'] == ''):
            print("Polygon Key not defined. Use flag '-c' or '--change-keys' to define.")
            sys.exit(0)
        if (keys['polygon-secret'] == ''):
            print("Polygon Secret not defined. Use flag '-c' or '--change-keys' to define.")
            sys.exit(0)

    if (args.reader == 'Polygon'):
        # TODO -> Procurar pacote no Polygon e baixá-lo na
        # pasta do problema. Após isso, converter para a pasta
        # de saída.
        print("Not implemented yet.")
        pass
    elif (args.reader == 'DS'):
        if (args.writer == 'Polygon'):
            send_to_polygon()
        else:
        # TODO -> Converter o pacote de DS para o Polygon
        # E enviar as informações para API
            print("Not implemented yet.")
            pass
    elif (args.reader == 'BOCA'):
        # Utilizar ferramenta 
        # um pacote do BOCA em um outro formato.
        print("Not implemented yet.")
        pass
