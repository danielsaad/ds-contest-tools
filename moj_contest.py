import argparse
import os
import pathlib
import shutil
import subprocess
from ds_contest_tools import moj, utils
from ds_contest_tools.jsonutils import parse_json
import uuid


def convert_date_epoch(date: str) -> str:
    cmd = ['date', f'--date="{date}"', '+%s']
    print(' '.join(cmd))
    p = subprocess.run(' '.join(cmd), capture_output=True, shell=True)
    return p.stdout.decode().rstrip()


def compress(contest_folder) -> None:
    print(f'Compressing {contest_folder} into {contest_folder}.tar.gz')
    cmd = ['tar', '-cvzf', f'{contest_folder}.tar.gz', '-C',
           pathlib.Path(contest_folder), '.']
    print(' '.join([str(x) for x in cmd]))
    subprocess.run(cmd)

def remove_old_pdfs(statements_folder) -> None:
    print(f'Removing old pdfs in {statements_folder}')
    for f in os.listdir(statements_folder):
        if f.endswith('.pdf'):
            os.remove(os.path.join(statements_folder, f))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('id', help='Contest UNIX ID')
    parser.add_argument('name', help='Contest Name')
    parser.add_argument(
        'date_start', help='contest start in MM/DD/YY HH:MM:SS format')
    parser.add_argument(
        'date_end', help='contest end in MM/DD/YY HH:MM:SS format')
    parser.add_argument('problem_dir', help='path to problem(s)', nargs='+')
    parser.add_argument('users_credentials_file',
                        help='users credentials file')
    parser.add_argument('--password', help='users_password',type=str,
                        dest='users_password', default=None)
    parser.add_argument('--lang', nargs='+', help='allowed languages',
                        dest='allowed_languages', default=['C'])
    parser.add_argument('--pass', action='store_true',
                        dest='allow_password_change', default=False)
    parser.add_argument('--type', choices=['super', 'prova', 'lista-privada',
                        'lista-publica'], dest='contest_type', default='lista-privada')
    parser.add_argument('--sonic', action='store_true', dest='sonic_flag')
    parser.add_argument('--statistics', action='store_true',
                        dest='statistics_flag')
    parser.add_argument('--showcode', action='store_true',
                        dest='showcode_flag')
    parser.add_argument(
        'contest_folder', help='location for the contest folder')
    args = parser.parse_args()

    contest_folder = args.contest_folder
    os.makedirs(contest_folder, exist_ok=True)
    statements_folder = os.path.join(contest_folder, 'enunciados')
    os.makedirs(statements_folder, exist_ok=True)
    remove_old_pdfs(statements_folder)
    contest_file = os.path.join(args.contest_folder, 'contest-description.txt')
    sonic_flag = args.sonic_flag
    showcode_flag = False if args.contest_type == 'prova' else args.showcode_flag
    statistics_flag = args.statistics_flag
    users_password = args.users_password
    with open(contest_file, 'w') as ouf:
        print(f'{args.id}', file=ouf)
        print(f'"{args.name}"', file=ouf)
        date_start_epoch = convert_date_epoch(args.date_start)
        date_end_epoch = convert_date_epoch(args.date_end)
        print(f'{date_start_epoch}', file=ouf)
        print(f'{date_end_epoch}', file=ouf)
        problems = args.problem_dir
        print(f'{len(problems)}', file=ouf)
        for i, p in enumerate(problems):
            label = chr(ord('A')+i)
            basename = pathlib.Path(p).name
            print(f'Processing {basename} {p}')
            json = parse_json(os.path.join(p, 'problem.json'))
            pdf_basename = pathlib.Path(p).name + '.pdf'
            output_pdf_basename = pathlib.Path(
                p).name + '-' + uuid.uuid4().hex + '.pdf'
            shutil.copyfile(os.path.join(p, pdf_basename),
                            os.path.join(statements_folder, output_pdf_basename))
            print(
                f'cdmoj saad-problems/saad-{basename} "{json["problem"]["title"]}" {label} {output_pdf_basename}', file=ouf)
            blank_index_file = os.path.join(statements_folder, 'index.html')
            with open(blank_index_file, 'w'):
                pass
        with open(args.users_credentials_file, 'r') as credentials:
            lines = [x.rstrip() for x in credentials.readlines()]

        if users_password:
            for i,l in enumerate(lines):
                if '.admin' in l or '.mon' in l:
                    continue
                fields = l.split(':')
                lines[i] = ':'.join([fields[0], users_password, fields[2], fields[3]])

        print(f'{len(lines)}', file=ouf)
        for l in lines:
            print(l, file=ouf)
        print(f'CONTEST_TYPE={args.contest_type}', file=ouf)
        print(f'LANGUAGES="{" ".join(args.allowed_languages)}"', file=ouf)
        if sonic_flag:
            print(f'SONIC=1', file=ouf)
        if showcode_flag:
            print(f'SHOWCODE=1', file=ouf)
        else:
            print(f'SHOWCODE=0', file=ouf)
        if statistics_flag:
            print(f'STATISTICS=1', file=ouf)
        else:
            print(f'STATISTIC=0', file=ouf)
    compress(contest_folder)


if __name__ == '__main__':
    main()
