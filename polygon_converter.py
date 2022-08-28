# Converts a Linux Package from Polygon to ds-contest-tool format

import os
import shutil
import argparse

DEFAULT_LANGUAGE = 'english'


def get_text(package_folder, filename, language=DEFAULT_LANGUAGE):
    filename = os.path.join(
        *[package_folder, 'statement-sections', language, filename])
    if not os.path.isfile(filename):
        return ''
    with open(filename, 'r') as fh:
        text = fh.readlines()
    return text


def get_statement(package_folder, language=DEFAULT_LANGUAGE):
    return get_text(package_folder, 'legend.tex', language)


def get_input_description(package_folder, language=DEFAULT_LANGUAGE):
    return get_text(package_folder, 'input.tex', language)


def get_output_description(package_folder, language=DEFAULT_LANGUAGE):
    return get_text(package_folder, 'output.tex', language)


def get_notes(package_folder, language=DEFAULT_LANGUAGE):
    return get_text(package_folder, 'notes.tex', language)


def get_tutorial(package_folder, language=DEFAULT_LANGUAGE):
    return get_text(package_folder, 'tutorial.tex', language)


def get_title(package_folder, language=DEFAULT_LANGUAGE):
    return get_text(package_folder, 'name.tex', language)


def get_input_list(package_folder):
    input_folder = os.path.join(package_folder, 'tests')
    file_list = [os.path.join(input_folder, x) for x in os.listdir(
        input_folder) if not x.endswith('.a')]
    return file_list


def get_output_list(package_folder):
    output_folder = os.path.join(package_folder, 'tests')
    file_list = [os.path.join(output_folder, x)
                 for x in os.listdir(output_folder) if x.endswith('.a')]
    return file_list


def copy_input_files(package_folder, problem_folder):
    file_list = get_input_list(package_folder)
    destination = os.path.join(problem_folder, 'input')
    for filepath in file_list:
        new_filename = os.path.basename(filepath).lstrip('0')
        shutil.copy(filepath, os.path.join(destination,new_filename))


def copy_output_files(package_folder, problem_folder):
    file_list = get_output_list(package_folder)
    destination = os.path.join(problem_folder, 'output')
    for filepath in file_list:
        new_filename = os.path.splitext(os.path.basename(filepath))[0].lstrip('0')
        new_filepath = os.path.join(destination, new_filename)
        shutil.copy(filepath, new_filepath)


def copy_validator(package_folder, problem_folder):
    checker = os.path.join(*[package_folder, 'files', 'validator.cpp'])
    destination = os.path.join(*[problem_folder, 'src', 'validator.cpp'])
    shutil.copy(checker, destination)

# TODO: implement


def copy_generator(package_folder, problem_folder):
    pass


def copy_checker(package_folder, problem_folder):
    checker = os.path.join(*[package_folder, 'files', 'checker.cpp'])
    destination = os.path.join(*[problem_folder, 'src', 'checker.cpp'])
    shutil.copy(checker, destination)


def copy_testlib(package_folder, problem_folder):
    testlib = os.path.join(*[package_folder, 'files', 'testlib.h'])
    destination = os.path.join(*[problem_folder, 'include', 'testlib.h'])
    shutil.copy(testlib, destination)


def copy_solutions(package_folder, problem_folder):
    solution_folder = os.path.join(package_folder, 'solutions')
    source_files = [os.path.join(solution_folder, x) for x in os.listdir(
        solution_folder) if not x.endswith('.desc')]
    destination = os.path.join(problem_folder, 'src')
    for f in source_files:
        shutil.copy(f, destination)


def check(package_folder, problem_folder):
    if not os.path.isdir(package_folder):
        print(package_folder, 'not a valid Polygon package folder')
        exit(1)
    os.makedirs(problem_folder,exist_ok=True)
    if not os.path.isdir(problem_folder):
        print(package_folder, 'not a valid problem folder')
        exit(1)
    check_package(package_folder)
    check_problem(problem_folder)


# TODO: implement
def check_package(package_folder):
    pass


# TODO: implement
def check_problem(problem_folder):
    os.makedirs(os.path.join(problem_folder,'input'),exist_ok=True)
    os.makedirs(os.path.join(problem_folder,'output'),exist_ok=True)
    os.makedirs(os.path.join(problem_folder,'src'),exist_ok=True)
    os.makedirs(os.path.join(problem_folder,'include'),exist_ok=True)
    pass


def write_statement(package_data, problem_folder):
    statement_file = os.path.join(problem_folder, 'statement.md')
    with open(statement_file, 'w') as statement_fh:
        print('# Descrição \n', file=statement_fh)
        print(''.join(package_data['statement']), file=statement_fh)
        print('# Entrada \n', file=statement_fh)
        print(''.join(package_data['input_description']), file=statement_fh)
        print('# Saída \n', file=statement_fh)
        print(''.join(package_data['output_description']), file=statement_fh)
        print('# Notas \n', file=statement_fh)
        print(''.join(package_data['notes']), file=statement_fh)
        print('# Tutorial \n', file=statement_fh)
        print(''.join(package_data['tutorial']), file=statement_fh)


def get_package_data(package_folder):
    problem_data = {}
    problem_data['title'] = get_title(package_folder)
    problem_data['statement'] = get_statement(package_folder)
    problem_data['input_description'] = get_input_description(package_folder)
    problem_data['output_description'] = get_output_description(package_folder)
    problem_data['notes'] = get_notes(package_folder)
    problem_data['tutorial'] = get_tutorial(package_folder)
    return problem_data


def convert(package_folder, problem_folder):
    check(package_folder, problem_folder)
    package_data = get_package_data(package_folder)
    write_statement(package_data, problem_folder)
    copy_checker(package_folder, problem_folder)
    copy_input_files(package_folder, problem_folder)
    copy_output_files(package_folder, problem_folder)
    copy_testlib(package_folder, problem_folder)
    copy_solutions(package_folder, problem_folder)
    copy_checker(package_folder, problem_folder)
    copy_validator(package_folder, problem_folder)
    copy_generator(package_folder, problem_folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('package_folder')
    parser.add_argument('problem_folder')
    args = parser.parse_args()
    convert(args.package_folder, args.problem_folder)
