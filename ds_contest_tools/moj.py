import argparse
import os
import shutil
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
        self.fill_author()
        self.fill_tags()
        self.fill_conf()
        self.create_markdown()
        self.copy_tests()
        self.copy_checker()
        self.copy_solutions()

    def fill_conf(self):
        info_log('Creating conf file')
        conf_file = os.path.join(self.output_folder,'conf')
        with open(conf_file,'w') as ouf:
            print('PUBLIC=no',file=ouf)

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

    def create_markdown(self):
        ''' Creates the markdown file from the problem metadata and tex files'''
        image_files = [os.path.join(self.problem_folder, x) for x in os.listdir(
            self.problem_folder) if os.path.splitext(x)[1] in ['.png', '.jpeg', '.pdf', '.jpg'] and  os.path.splitext(x)[0] not in [f'{os.path.basename(self.problem_folder)}', f'{os.path.basename(self.problem_folder)}-tutorial']]
        for img in image_files:
            shutil.copy(img,self.output_folder)
            
        markdown_file = os.path.join(
            self.output_folder, 'docs', 'enunciado.md')
        title_str = self.problem_metadata['problem']['title']

        with open(markdown_file, 'w') as ouf:
            print(f'% {title_str}', file=ouf)
            statement_files = fileutils.get_statement_files(
                os.path.join(self.problem_folder, 'statement'))
            statement_str = fileutils.unserialize_file(statement_files[0])
            input_str = fileutils.unserialize_file(statement_files[1])
            output_str = fileutils.unserialize_file(statement_files[2])
            notes_str = fileutils.unserialize_file(statement_files[3])
            print(f'{statement_str}\n', file=ouf)
            print(f'## Entrada\n {input_str}\n', file=ouf)
            print(f'## Saída\n {output_str}\n', file=ouf)
            n_io_sample = self.problem_metadata['io_samples']
            if n_io_sample > 1:
                print('## Exemplos\n', file=ouf)
            elif n_io_sample == 1:
                print('## Exemplo\n', file=ouf)

            for i in range(n_io_sample):
                input_file = os.path.join(
                    self.problem_folder, 'input', f'{i+1}')
                output_file = os.path.join(
                    self.problem_folder, 'output', f'{i+1}')
                input_str = fileutils.unserialize_file(input_file)
                output_str = fileutils.unserialize_file(output_file)
                print('### Entrada\n', file=ouf)
                print(f"```\n{input_str}```\n", file=ouf)
                print('### Saída\n', file=ouf)
                print(f"```\n{output_str}```\n", file=ouf)

            if notes_str != '':
                print(f'## Notas\n {notes_str}\n', file=ouf)

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

    def copy_checker(self):
        info_log('Creating BOCA Checker')
        src_file = os.path.join(self.problem_folder, 'src', 'checker.cpp')
        executable_file = os.path.join(
            self.output_folder, 'scripts', 'compare.sh')
        subprocess.run(
            ['g++', src_file, '-DBOCA_SUPPORT', '-o', executable_file])

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
            self.output_folder, 'sols', 'good',os.path.basename(main_ac_file)))
        for aac in alternative_ac_files:
            shutil.copyfile(aac, os.path.join(
                self.output_folder, 'sols', 'good',os.path.basename(aac)))

        for tle in tle_files:
            shutil.copyfile(tle, os.path.join(
                self.output_folder, 'sols', 'slow',os.path.basename(tle)))

        for wa in wa_files:
            shutil.copyfile(wa, os.path.join(
                self.output_folder, 'sols', 'wrong',os.path.basename(wa)))

    def setup_moj_dirs(self) -> None:
        '''
        Creates MOJ problem directory structure
        '''
        info_log('Setting up directories')
        dirs = ['docs', 'sols', 'tests', 'generator', 'scripts', 'sols']
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
    parser.add_argument('problem_folder',help='Contest UNIX ID')
    parser.add_argument('output_folder',help='Contest Name')
    args = parser.parse_args()
    problem_folder = args.problem_folder
    output_folder = args.output_folder
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))
    check_problem_metadata(problem_metadata)
    mc = moj_converter(problem_folder, output_folder, problem_metadata)
    mc.convert_to_moj()


if __name__ == '__main__':
    main()
