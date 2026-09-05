import argparse
import os
import pathlib
import shutil
from pathlib import Path
import subprocess
import sys

from ds_contest_tools import fileutils
from .jsonutils import parse_json
from .logger import error_log, info_log
from .utils import check_problem_metadata, verify_path


class moj_converter:
    def __init__(self, problem_folder, output_folder):
        self.problem_folder = problem_folder
        self.output_folder = output_folder
        self.problem_metadata = parse_json(
            os.path.join(problem_folder, 'problem.json'))

    def convert_to_moj(self):
        check_problem_metadata(self.problem_metadata)
        self.setup_moj_dirs()
        self.fill_conf()
        self.fill_author()
        self.fill_tags()
        self.copy_tests()
        self.copy_images()
        self.copy_solutions()
        self.copy_originals()

    def copy_images(self):
        info_log('Copying images')

        images = [
            p for p in Path(self.problem_folder).iterdir()
            if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff"}
        ]

        for img in images:
            src_path = img
            dst_path = pathlib.Path(self.output_folder, 'docs', img.name)
            shutil.copy2(src_path, dst_path)
            info_log(f'Copied image {img.name} to {dst_path}')

    def copy_originals(self):
        src_path = pathlib.Path(self.problem_folder, 'src')
        dst_path = pathlib.Path(self.output_folder, 'original')
        info_log('Copying src files')
        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        statement_pdf = pathlib.Path(
            self.problem_folder, os.path.basename(self.problem_folder+'.pdf'))
        statement_tutorial = pathlib.Path(
            self.problem_folder, os.path.basename(self.problem_folder)+'-tutorial.pdf')
        info_log('Copying statement and tutorial PDFs')
        if os.path.isfile(statement_pdf):
            shutil.copy(statement_pdf, dst_path.as_posix())
        if os.path.isfile(statement_tutorial):
            shutil.copy(statement_tutorial, dst_path.as_posix())

    def fill_conf(self):
        conf_file = os.path.join(self.output_folder, 'conf')
        info_log(f'Creating conf file {conf_file}')
        with open(conf_file, 'w') as ouf:
            rss_limit = self.problem_metadata['problem']['memory_limit_mb']*1024
            print(f'MEMLIMITMB={rss_limit}', file=ouf)
            print(f'TLMOD[calibrafactor]=1.35', file=ouf)
            print(f'ULIMITS[-u]=10000', file=ouf)
            print(f'ALLOWPARALLELTEST=y', file=ouf)

    def fill_author(self):
        info_log('Creating author file')
        author_file = os.path.join(self.output_folder, 'author')
        with open(author_file, 'w') as ouf:
            author_str = f'{self.problem_metadata['author']['name']}'
            event_str = self.problem_metadata['problem']['event']
            output_str = author_str
            if event_str != '':
                output_str += f' ({event_str})'
            print(output_str, file=ouf)

    def fill_tags(self):
        '''Recovers the tags from json and fill the tags file'''
        info_log('Creating tags file')
        tag_file = os.path.join(self.output_folder, 'tags')
        with open(tag_file, 'w') as ouf:
            tags = self.problem_metadata['problem']['subject']['en_us']
            if 'pt_br' in self.problem_metadata['problem']['subject'].keys():
                tags += self.problem_metadata['problem']['subject']['pt_br']
            for t in tags:
                print(f'#{t}', file=ouf)

    def copy_tests(self):
        info_log('Copying input and output')
        input_folder = os.path.join(self.problem_folder, 'input')
        output_folder = os.path.join(self.problem_folder, 'output')
        moj_input_folder = os.path.join(self.output_folder, 'tests', 'input')
        moj_output_folder = os.path.join(self.output_folder, 'tests', 'output')
        fileutils.recursive_overwrite(input_folder, moj_input_folder)
        fileutils.recursive_overwrite(output_folder, moj_output_folder)
        fileutils.rename_io(moj_input_folder)
        fileutils.rename_io(moj_output_folder)
        info_log('Creating sample files')
        io_samples = self.problem_metadata['build']['io_samples']
        for i in range(io_samples):
            shutil.copyfile(os.path.join(
                input_folder, f'{i+1}'), os.path.join(moj_input_folder, f'sample{i+1}'))
            info_log(f'Created sample{i+1} in {moj_input_folder}')
            shutil.copyfile(os.path.join(
                output_folder, f'{i+1}'), os.path.join(moj_output_folder, f'sample{i+1}'))
            info_log(f'Created sample{i+1} in {moj_output_folder}')

    def copy_solutions(self):
        info_log('Copying Solutions')
        main_ac_file = os.path.join(
            self.problem_folder, 'src', self.problem_metadata['solutions']['main-ac'])
        alternative_ac_files = [os.path.join(self.problem_folder, 'src', x)
                                for x in self.problem_metadata['solutions']['alternative-ac']]
        tle_files = [os.path.join(self.problem_folder, 'src', x)
                     for x in self.problem_metadata['solutions']['time-limit']]
        wa_files = [os.path.join(self.problem_folder, 'src', x)
                    for x in self.problem_metadata['solutions']['wrong-answer']]
        shutil.copyfile(main_ac_file, os.path.join(
            self.output_folder, 'sols', 'good', os.path.basename(main_ac_file)))
        for aac in alternative_ac_files:
            shutil.copyfile(aac, os.path.join(
                self.output_folder, 'sols', 'good', os.path.basename(aac)))

        for tle in tle_files:
            shutil.copyfile(tle, os.path.join(
                self.output_folder, 'sols', 'slow', os.path.basename(tle)))

        for wa in wa_files:
            shutil.copyfile(wa, os.path.join(
                self.output_folder, 'sols', 'wrong', os.path.basename(wa)))

    def setup_moj_dirs(self) -> None:
        '''
        Creates MOJ problem directory structure
        '''
        info_log('Setting up directories')
        dirs = ['docs', 'sols', 'tests', 'generator',
                'scripts', 'sols', 'original']
        for d in dirs:
            os.makedirs(os.path.join(self.output_folder, d), exist_ok=True)
        os.makedirs(os.path.join(self.output_folder,
                    'tests', 'input'), exist_ok=True)
        os.makedirs(os.path.join(self.output_folder,
                    'tests', 'output'), exist_ok=True)
        os.makedirs(os.path.join(self.output_folder,
                    'sols', 'good'), exist_ok=True)
        os.makedirs(os.path.join(self.output_folder,
                    'sols', 'slow'), exist_ok=True)
        os.makedirs(os.path.join(self.output_folder,
                    'sols', 'wrong'), exist_ok=True)


def convert_to_moj(problem_folder, output_folder):
    mc = moj_converter(problem_folder, output_folder)
    mc.convert_to_moj()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('problem_folder', help='Input folder in DS format')
    parser.add_argument('output_folder', help='Output folder for MOJ problem')
    args = parser.parse_args()
    problem_folder = args.problem_folder
    output_folder = args.output_folder
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))
    check_problem_metadata(problem_metadata)
    mc = moj_converter(problem_folder, output_folder, problem_metadata)
    mc.convert_to_moj()


if __name__ == '__main__':
    main()
