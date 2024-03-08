import argparse
import io
import json
import os
import shutil


def create_parser() -> argparse.ArgumentParser:
    """Create parser of the tool.

    Returns:
        argparse.ArgumentParser: The parser of the tool.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="Convert legacy problems to newer version.")
    parser.add_argument('problem_dir', help='path to the problem')
    return parser


def parse_json(json_file: str) -> dict:
    """Converts a JSON file to a Python dictionary.

    Args:
        json_file: The path to the JSON file.

    Returns:
        dict: The contents of the JSON file as a dictionary.
    """
    if not os.path.isfile(json_file):
        print(f'{os.path.basename(json_file)} does not exist.')
        exit(1)

    with open(json_file) as f:
        json_data = json.load(f)

    return json_data


def write_file(statement_file: str, statement: io.TextIOWrapper) -> str:
    """Write a new file with a header from statement.

    Args:
        statement_file (str): Path to the new file.
        statement (io.TextIOWrapper): Stream to the statement.md

    Returns:
        str: The next header of the statement file.
    """
    text = ''
    with open(statement_file, 'w') as f:
        while (True):
            line = statement.readline()
            if not line or line.startswith('# '):
                f.write(text.lstrip().rstrip())
                return line
            text += line


def convert_statement(problem_dir: str) -> None:
    """Create statement directory and its files."""
    statement_dir = os.path.join(problem_dir, 'statement')
    statement_path = os.path.join(problem_dir, 'statement.md')
    if not os.path.exists(statement_path):
        return

    print('Converting statement.md to TeX files.')
    os.makedirs(statement_dir, exist_ok=True)
    with open(statement_path, 'r') as statement:
        statement.readline()

        files = {
            'description': 'description',
            'input': 'input',
            'output': 'output',
            'notes': 'notes',
            'tutorial': 'tutorial'
        }

        for _, prefix in files.items():
            file_path = os.path.join(statement_dir, f'{prefix}.tex')
            line = write_file(file_path, statement)
            if line.startswith('# Interação'):
                write_file(os.path.join(statement_dir,
                                        'interactor.tex'), statement)


def move_makefile(problem_dir: str, grader: bool) -> None:
    """Change CMake to Makefile and move files"""
    tool_folder = os.path.dirname(os.path.abspath(__file__))

    print('Creating Makefile')
    cmake_path = os.path.join(problem_dir, 'CMakeLists.txt')
    if os.path.exists(cmake_path):
        os.remove(cmake_path)

    files_path = os.path.join(tool_folder, 'ds_contest_tools', 'files')

    move_files = ['maratona.cls']
    for file in move_files:
        shutil.copy2(os.path.join(files_path, file), problem_dir)

    # Move Makefile
    if grader:
        shutil.copy2(os.path.join(files_path, 'GraderMakefile'),
                     os.path.join(problem_dir, 'Makefile'))
    else:
        shutil.copy2(os.path.join(files_path, 'Makefile'), problem_dir)


def update_testlib(problem_dir: str) -> None:
    """Move updated testlib to src folder and remove the old one."""
    tool_folder = os.path.dirname(os.path.abspath(__file__))
    testlib_folder = os.path.join(problem_dir, 'include')

    if os.path.exists(testlib_folder):
        shutil.rmtree(testlib_folder)

    print('Updating testlib')
    shutil.copy2(os.path.join(tool_folder, 'ds_contest_tools', 'files', 'src', 'testlib.h'),
                 os.path.join(problem_dir, 'src', 'testlib.h'))


def convert_problem_json(problem_dir: str) -> bool:
    """Convert problem.json to new version."""
    tool_folder = os.path.dirname(os.path.abspath(__file__))

    metadata_path = os.path.join(problem_dir, 'problem.json')
    if not os.path.exists(metadata_path):
        return

    print('Converting problem.json')
    old_problem_metadata = parse_json(metadata_path)
    shutil.copy2(os.path.join(tool_folder, 'ds_contest_tools', 'files',
                 'problem.json'), metadata_path)
    new_problem_metadata = parse_json(metadata_path)

    for key, value in old_problem_metadata.items():
        if key == 'io_samples':
            new_problem_metadata[key] = value
            continue

        for subkey, subvalue in value.items():
            if subvalue == ['']:
                new_problem_metadata[key][subkey] = []
            else:
                new_problem_metadata[key][subkey] = subvalue

    if 'id' in new_problem_metadata['problem']:
        del new_problem_metadata['problem']['id']
    if 'label' in new_problem_metadata['problem']:
        del new_problem_metadata['problem']['label']

    with open(metadata_path, 'w') as f:
        f.write(json.dumps(new_problem_metadata, ensure_ascii=False))

    return new_problem_metadata['problem']['grader']


def convert_problem(problem_dir: str) -> None:
    """Convert legacy problem to newer version."""
    update_testlib(problem_dir)
    convert_statement(problem_dir)
    grader = convert_problem_json(problem_dir)
    move_makefile(problem_dir, grader)


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    if not os.path.exists(args.problem_dir):
        print(f'Problem directory {args.problem_dir} does not exist.')
        exit(1)

    convert_problem(problem_dir=args.problem_dir)

    print('Problem converted successfully. Update the solutions in problem.json file and rebuild the problem.')
