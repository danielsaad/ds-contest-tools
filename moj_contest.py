import argparse
import os
import pathlib
import shutil
import subprocess
from ds_contest_tools import moj, utils
from ds_contest_tools.jsonutils import parse_json

def convert_date_epoch(date:str)->str:
    cmd = ['date',f'--date="{date}"','+%s']
    print(' '.join(cmd))
    p = subprocess.run(' '.join(cmd),capture_output=True,shell=True)
    return p.stdout.decode().rstrip()

def compress(contest_folder) -> None:
    cmd = ['tar','-cvzf',f'{contest_folder}.tar.gz','-C', 
           pathlib.Path(contest_folder),'.']
    print(' '.join([str(x) for x in cmd]))   
    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('id',help='Contest UNIX ID')
    parser.add_argument('name',help='Contest Name')
    parser.add_argument('date_start',help='contest start in MM/DD/YY HH:MM:SS format')
    parser.add_argument('date_end',help='contest end in MM/DD/YY HH:MM:SS format')
    parser.add_argument('problem_dir', help='path to problem(s)', nargs='+')
    parser.add_argument('users_credentials_file', help='users credentials file')
    parser.add_argument('--lang',nargs='+',help='allowed languages',dest='allowed_languages',default=['C'])
    parser.add_argument('--pass', action='store_true',dest='allow_password_change',default=False)
    parser.add_argument('--type',choices=['super','prova','lista-privada','lista-publica'],dest='contest_type',default='lista-privada')
    parser.add_argument('contest_folder',help='location for the contest folder')
    args = parser.parse_args()

    contest_folder = args.contest_folder
    os.makedirs(contest_folder,exist_ok=True)
    statements_folder = os.path.join(contest_folder,'enunciados')
    os.makedirs(statements_folder,exist_ok=True)
    contest_file = os.path.join(args.contest_folder,'contest-description.txt')
    with open(contest_file,'w') as ouf:
        print(f'{args.id}',file=ouf)
        print(f'"{args.name}"',file=ouf)
        date_start_epoch = convert_date_epoch(args.date_start)
        date_end_epoch = convert_date_epoch(args.date_end)
        print(f'{date_start_epoch}',file=ouf)
        print(f'{date_end_epoch}',file=ouf)
        problems = args.problem_dir
        print(f'{len(problems)}',file=ouf)
        for i,p in enumerate(problems):
            label = chr(ord('A')+i)
            basename = pathlib.Path(p).name
            print(f'Processing {basename} {p}')
            json = parse_json(os.path.join(p,'problem.json'))
            print(f'cdmoj moj-problems/saad-{basename} "{json["problem"]["title"]}" {label} {basename}.pdf',file=ouf)
            pdf_basename = pathlib.Path(p).name+'.pdf'
            shutil.copyfile(os.path.join(p,pdf_basename),os.path.join(statements_folder,pdf_basename))
        with open(args.users_credentials_file,'r') as credentials:
            lines = [x.rstrip() for x in credentials.readlines()]
        print(f'{len(lines)}',file=ouf)
        for l in lines:
            print(l,file=ouf)
        print(f'CONTEST_TYPE={args.contest_type}',file=ouf)
        print(f'LANGUAGES="{" ".join(args.allowed_languages)}"',file=ouf)
    compress(contest_folder)

if __name__ == '__main__':
    main()