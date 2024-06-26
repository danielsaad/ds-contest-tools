import json
import os
import shutil
import xml.etree.ElementTree as ET
from typing import Optional

from .config import IGNORED_DIRS
from .fileutils import get_statement_files, unzip_package
from .jsonutils import parse_json, write_to_json
from .logger import info_log, warning_log
from .metadata import Paths
from .polygon_connection import download_package_polygon, make_api_request
from .toolchain import init_problem
from .utils import verify_path,verify_file

DEFAULT_LANGUAGE = 'english'


def get_text(filename, language=DEFAULT_LANGUAGE):
    """Get statement texts from the Polygon package."""
    package_folder = Paths().get_output_dir()
    filename = os.path.join(
        package_folder, 'statement-sections', language, filename)
    if not os.path.isfile(filename):
        return ''
    with open(filename, 'r') as fh:
        text = fh.readlines()
    return text


def get_statement(language=DEFAULT_LANGUAGE):
    return get_text('legend.tex', language)


def get_input_description(language=DEFAULT_LANGUAGE):
    return get_text('input.tex', language)


def get_output_description(language=DEFAULT_LANGUAGE):
    return get_text('output.tex', language)


def get_notes(language=DEFAULT_LANGUAGE):
    return get_text('notes.tex', language)


def get_tutorial(language=DEFAULT_LANGUAGE):
    return get_text('tutorial.tex', language)


def get_title(language=DEFAULT_LANGUAGE):
    return get_text('name.tex', language)


def get_interaction(language=DEFAULT_LANGUAGE):
    return get_text('interaction.tex', language)


def get_input_list() -> list:
    """Get list of input files from the package."""
    package_folder = Paths().get_output_dir()
    input_folder = os.path.join(package_folder, 'tests')
    verify_path(input_folder)
    file_list = [os.path.join(input_folder, x) for x in os.listdir(
        input_folder) if not x.endswith('.a')]
    return file_list


def get_output_list() -> list:
    """Get list of output files from the package."""
    package_folder = Paths().get_output_dir()
    output_folder = os.path.join(package_folder, 'tests')
    verify_path(output_folder)
    file_list = [os.path.join(output_folder, x)
                 for x in os.listdir(output_folder) if x.endswith('.a')]
    return file_list


def get_interactive_list() -> list:
    """Get list of interactive I/O files of the statement from the package."""
    package_folder = Paths().get_output_dir()
    interactive_folder = os.path.join(package_folder, 'statements', 'english')
    verify_path(interactive_folder)
    file_list = [os.path.join(interactive_folder, x)
                 for x in os.listdir(interactive_folder) if x.startswith('example.')]
    return file_list


def copy_input_files() -> None:
    """Copy input files from the package to the problem folder."""
    info_log("Copying input files.")
    problem_folder = Paths().get_problem_dir()
    file_list = get_input_list()
    destination = os.path.join(problem_folder, 'input')
    for filepath in file_list:
        new_filename = os.path.basename(filepath).lstrip('0')
        shutil.copy(filepath, os.path.join(destination, new_filename))


def copy_output_files() -> None:
    """Copy output files from the package to the problem folder."""
    info_log("Copying output files.")
    problem_folder = Paths().get_problem_dir()
    file_list = get_output_list()
    destination = os.path.join(problem_folder, 'output')
    for filepath in file_list:
        new_filename = os.path.splitext(
            os.path.basename(filepath))[0].lstrip('0')
        new_filepath = os.path.join(destination, new_filename)
        shutil.copy(filepath, new_filepath)


def copy_interactive_files() -> None:
    """Copy interactive statement files from the package to the problem folder."""
    info_log("Copying interactive statement files.")
    problem_folder = Paths().get_problem_dir()
    file_list = get_interactive_list()
    destination_input = os.path.join(problem_folder, 'input')
    destination_output = os.path.join(problem_folder, 'output')
    for filepath in file_list:
        destination = destination_output if filepath.endswith(
            '.a') else destination_input
        new_filename = os.path.basename(filepath).lstrip(
            'example.').lstrip('0').rstrip('.a') + '.interactive'
        shutil.copy(filepath, os.path.join(destination, new_filename))


def copy_generator(script: str) -> None:
    """Copy generators from package to problem folder.

    Args:
        script: String containing script content.
    """
    info_log("Copying generators.")
    package_folder = Paths().get_output_dir()
    problem_folder = Paths().get_problem_dir()
    generator_list = set()

    # Copy script generators
    with open(os.path.join(problem_folder, 'src', 'script.sh'), 'w') as f:
        f.write(script)

    if script == '':
        warning_log("No generator script found.")
        return

    script_lines = script.split('\n')
    for line in script_lines:
        if line != '':
            generator_list.add(line.split()[0])

    for file in generator_list:
        file += '.cpp'
        generator = os.path.join(*[package_folder, 'files', file])
        if not os.path.exists(generator):
            warning_log(f"Generator {os.path.relpath(generator)} not found.")
        else:
            destination = os.path.join(problem_folder, 'src', file)
            shutil.copy(generator, destination)


def copy_source_files(polygon_name: str, file_name: str) -> None:
    """Copy source files from package to problem folder."""
    package_folder = Paths().get_output_dir()
    problem_folder = Paths().get_problem_dir()
    file = os.path.join(package_folder, 'files', polygon_name)
    destination = os.path.join(problem_folder, 'src', file_name)

    # If problem has standard checker, verify new checker or skip it
    if not os.path.exists(file) and file_name == 'checker.cpp':
        file_dir = os.path.dirname(file)
        checker = [f for f in os.listdir(file_dir) if f.startswith('check')]
        if not checker:
            warning_log(
                f"Checker {os.path.basename(polygon_name)} not found. Skipping.")
            return
        file = os.path.join(file_dir, checker[0])

    if verify_file(file):
        shutil.copy2(file, destination)
    else:
        warning_log(f"{file} could not be copied to {destination}")

def copy_source_folder() -> None:
    """Copy source files from local package to problem folder."""
    info_log("Copying source folder")
    package_folder = Paths().get_output_dir()
    problem_folder = Paths().get_problem_dir()
    source_folder = os.path.join(package_folder, 'files')

    # Copy files from source folder
    source_files = [os.path.join(source_folder, x) for x in os.listdir(
        source_folder) if x.endswith(('.cpp', '.py', '.java'))]
    destination = os.path.join(problem_folder, 'src')
    for f in source_files:
        shutil.copy2(f, destination)


def copy_grader_files(data: list) -> None:
    """Copy grader files from package to problem folder.

    Args:
        data: List of tuples containing name of file and if it is used for grader.
    """
    for resource, for_grader in data:
        if not for_grader:
            continue
        resource = os.path.basename(resource)
        if resource.endswith('.cpp'):
            resource = 'grader.cpp'
        elif resource.endswith('.py'):
            resource = 'main.py'
        shutil.copy(os.path.join(Paths().get_output_dir(), 'files', resource), 
                    os.path.join(Paths().get_problem_dir(), 'src', resource))


def copy_solutions() -> None:
    """Copy solution files from package to problem folder."""
    info_log("Copying solutions.")
    package_folder = Paths().get_output_dir()
    problem_folder = Paths().get_problem_dir()
    solution_folder = os.path.join(package_folder, 'solutions')

    source_files = [os.path.join(solution_folder, f) for f in os.listdir(
        solution_folder) if not f.endswith(('.desc', '.exe', '.jar'))]
    destination = os.path.join(problem_folder, 'src')
    for f in source_files:
        shutil.copy2(f, destination)


def copy_checker(problem_id: str) -> None:
    """Copy checker file from Polygon."""
    info_log("Copying checker.")
    content = make_api_request('problem.checker', dict(), problem_id)
    content = json.loads(content)
    copy_source_files(content['result'], 'checker.cpp')


def copy_validator(problem_id: str) -> None:
    """Copy validator file from Polygon."""
    info_log("Copying validator.")
    content = make_api_request('problem.validator', dict(), problem_id)
    content = json.loads(content)
    copy_source_files(content['result'], 'validator.cpp')


def copy_interactor(problem_id: str) -> None:
    """Copy interactor file from Polygon."""
    info_log("Copying interactor.")
    content = make_api_request('problem.interactor', dict(), problem_id)
    content = json.loads(content)
    copy_source_files(content['result'], 'interactor.cpp')


def get_local_interactive() -> bool:
    """Ask the user whether the problem is interactive"""
    while True:
        user_input = input(
            "Is the problem interactive? (Y/n) ").strip().lower()
        if user_input.lower().startswith('y'):
            return True
        elif user_input.lower().startswith('n'):
            return False
        else:
            print("Invalid input. Please enter Y or N.")


def get_remote_interactive(problem_id: str) -> bool:
    """Make request to verify if the problem is interactive."""
    content = make_api_request('problem.info', dict(), problem_id)
    content = json.loads(content)
    return content['result']['interactive']


def start_problem(interactive: bool, grader: bool) -> None:
    """Initialize problem folder before the conversion.

    Args:
        interactive: Whether the problem is interactive.
    """
    info_log("Initializing problem folder.")
    init_problem(interactive, grader, verify_folder=False, ignore_patterns=IGNORED_DIRS + ['src'])

    # Create necessary directories
    problem_folder = Paths().get_problem_dir()
    os.makedirs(os.path.join(problem_folder, 'src'), exist_ok=True)
    os.makedirs(os.path.join(problem_folder, 'input'), exist_ok=True)
    os.makedirs(os.path.join(problem_folder, 'output'), exist_ok=True)

    # Copy testlib
    tool_path = os.path.dirname(os.path.abspath(__file__))
    testlib = os.path.join(tool_path, 'files', 'src')
    shutil.copy2(os.path.join(testlib, 'testlib.h'),
                os.path.join(problem_folder, 'src', 'testlib.h'))

    # Remove unused grader files
    if grader:
        grader_files = ['grader.cpp', 'grader.h']
        for f in grader_files:
            file_path = os.path.join(problem_folder, 'src', f)
            if os.path.exists(file_path):
                os.remove(file_path)


def copy_statement_files(package_data: dict, interactive: bool, language=DEFAULT_LANGUAGE) -> None:
    """Write statement files in the problem folder."""
    info_log("Copying statement files.")
    problem_folder = Paths().get_problem_dir()
    statement_dir = os.path.join(problem_folder, 'statement')

    statement_files = get_statement_files(statement_dir, interactive)
    with open(statement_files[0], 'w') as f:
        f.writelines(package_data['statement'])
    with open(statement_files[1], 'w') as f:
        f.writelines(package_data['input_description'])
    with open(statement_files[2], 'w') as f:
        f.writelines(package_data['output_description'])
    with open(statement_files[3], 'w') as f:
        f.writelines(package_data['notes'])
    with open(statement_files[4], 'w') as f:
        f.writelines(package_data['tutorial'])
    if interactive:
        with open(statement_files[5], 'w') as f:
            f.writelines(package_data['interaction'])

    package_folder = os.path.join(
        Paths().get_output_dir(), 'statement-sections', language)
    ignored_extensions = {'.tex', '.log'}
    ignored_prefixes = {'example'}
    for f in os.listdir(package_folder):
        if not any(f.endswith(ext) for ext in ignored_extensions) and not any(f.startswith(prefix) for prefix in ignored_prefixes):
            file_path = os.path.join(package_folder, f)
            shutil.copy(file_path, os.path.join(problem_folder, f))


def get_package_data(interactive: bool) -> dict:
    """Get statement information from package."""
    problem_data = {}
    problem_data['title'] = get_title()
    problem_data['statement'] = get_statement()
    problem_data['input_description'] = get_input_description()
    problem_data['output_description'] = get_output_description()
    problem_data['notes'] = get_notes()
    problem_data['tutorial'] = get_tutorial()
    if interactive:
        problem_data['interaction'] = get_interaction()
    return problem_data


def get_solution_tags() -> dict:
    """Get dictionary with every solution tag."""
    tags = {
        'main': 'main-ac',
        'failed': 'runtime-error',
        'rejected': 'runtime-error',
        'accepted': 'alternative-ac',
        'wrong-answer': 'wrong-answer',
        'memory-limit-exceeded': 'memory-limit',
        'presentation-error': 'presentation-error',
        'time-limit-exceeded': 'time-limit',
        'time-limit-exceeded-or-accepted': 'time-limit-or-ac',
        'time-limit-exceeded-or-memory-limit-exceeded': 'time-limit-or-memory-limit'
    }
    return tags


def get_scripts_xml(root: ET.Element) -> str:
    """Extract generator scripts from the XML file.

    Args:
        root: The root element of the test XML file.

    Returns:
        A string containing the generator scripts used to create inputs.
    """
    generator_scripts: str = ''
    for test in root.findall('./judging/testset/tests/test'):
        script = test.get('cmd')
        if script:
            generator_scripts += script + '\n'
    return generator_scripts


def get_solutions_xml(root: ET.Element) -> dict:
    """Parse solution files from XML.

    Args:
        root: The root Element object of the XML tree.

    Returns:
        A dictionary with parsed solution files. The keys are string codes for the solution type
        ('main-ac', 'main-wa', 'checker', 'validator', 'interactor', and 'solution'). The values are
        either a single string (for the 'main-ac' key) or a list of strings (for the other keys).
    """
    solutions: dict = {}
    tags = get_solution_tags()
    for data in root.findall('./assets/solutions/solution'):
        solution_tag = data.get('tag')
        if solution_tag is None:
            continue

        for filename in data.findall('source'):
            # Add solution to list inside the dictionary
            name = filename.get('path')
            if name:
                solutions.setdefault(tags[solution_tag], []).append(
                    os.path.basename(name))
    # Convert main solution to a string
    solutions['main-ac'] = ''.join(solutions['main-ac'])

    return solutions


def get_resources_xml(root: ET.Element) -> list:
    """Parse resource files from problem XML.

    Args:
        root: The root Element object of the XML tree.

    Returns:
        A list of tuples containing the resource file names and if they are used for grader.
    """
    resources: list = []
    for data in root.findall('./files/resources/'):
        name = data.get('path')
        for_type = data.get('for-types')
        if name:
            resources.append((name, True if for_type else False))
    return resources


def get_data_xml() -> dict:
    """Parses the problem.xml file in the package folder to retrieve
    generator scripts and solutions for the problem.

    Returns:
        A dictionary containing two keys: "script" and "solutions".
        The "script" key maps to a string containing the generator scripts,
        and the "solutions" key maps to a dictionary containing the solutions.
    """
    package_folder: str = Paths().get_output_dir()
    tree_path = os.path.join(package_folder, 'problem.xml')
    verify_path(tree_path)

    tree: ET.ElementTree = ET.parse(tree_path)
    root: ET.Element = tree.getroot()

    xml_data: dict = {
        'script': get_scripts_xml(root),
        'solutions': get_solutions_xml(root),
        'resources': get_resources_xml(root)
    }
    return xml_data


def get_tags() -> dict:
    """Get tags of the problem.

    Returns:
        A dictionary containing the flags used.
    """
    package_folder: str = Paths().get_output_dir()
    tags: dict = {'en_us': list()}
    tags_paths = os.path.join(package_folder, 'tags')
    if not os.path.exists(tags_paths):
        return tags
    with open(tags_paths, 'r') as f:
        for line in f.readlines():
            tags['en_us'].append(line.rstrip())
    return tags


def update_problem_metadata(title: str, solutions: dict, interactive: bool, problem_id: str, local: bool, grader: bool) -> None:
    """Update problem information in problem.json file.

    Args:
        title: Name of the problem.
        solutions: Dictionary containing the solutions.
        interactive: Whether the problem is interactive.
        problem_id: Problem ID.
        local: Whether the conversion is being done locally or remotely.
    """
    info_log("Updating problem metadata.")
    package_folder = Paths().get_output_dir()
    problem_folder = Paths().get_problem_dir()

    # Get paths
    json_path = os.path.join(problem_folder, 'problem.json')
    package_json_path = os.path.join(
        package_folder, 'statements', 'english', 'problem-properties.json')

    # Get problem metadata
    tags = get_tags()
    problem_metadata = parse_json(json_path)
    package_json = parse_json(package_json_path)

    # Update problem metadata
    problem_metadata['author']['name'] = package_json['authorName']
    problem_metadata['problem']['subject'] = tags
    problem_metadata['problem']['interactive'] = interactive
    problem_metadata['problem']['grader'] = grader
    problem_metadata['io_samples'] = len(package_json['sampleTests'])
    problem_metadata['problem']['title'] = title.rstrip()
    problem_metadata['problem']['input_file'] = package_json['inputFile']
    problem_metadata['problem']['output_file'] = package_json['outputFile']
    problem_metadata['problem']['time_limit'] = int(
        package_json['timeLimit'] / 1000)
    problem_metadata['problem']['memory_limit_mb'] = int(
        (package_json['memoryLimit'] / 1024) / 1024)
    if not local:
        problem_metadata['polygon_config']['id'] = problem_id
    for key in solutions:
        problem_metadata['solutions'][key] = solutions[key]

    # Write updated problem metadata to file
    write_to_json(json_path, problem_metadata)


def convert_problem(local: bool, problem_id: Optional[str] = '') -> None:
    """Converts a problem from Polygon to DS format.

    Args:
        local: Whether the conversion is being done locally or remotely.
        problem_id: The ID of the problem on Polygon. Only used if local is False.
    """
    xml_data = get_data_xml()
    # Polygon packages do not contain the interactive parameter
    interactive = get_local_interactive() if local else get_remote_interactive(problem_id)
    grader = any(value for _, value in xml_data['resources'])
    package_data = get_package_data(interactive)

    # Copy data from package to problem folder
    start_problem(interactive, grader)
    copy_input_files()
    copy_output_files()
    copy_solutions()

    # In local problems, there is no way to know the
    # source files names, so the user has to change it
    # manually.
    if local:
        copy_source_folder()
    else:
        copy_checker(problem_id)
        copy_validator(problem_id)
        if interactive:
            copy_interactor(problem_id)
            copy_interactive_files()

    # Copy resources files from grader
    if grader:
        copy_grader_files(xml_data['resources'])

    copy_generator(xml_data['script'])
    copy_statement_files(package_data, interactive)
    update_problem_metadata(''.join(package_data['title']),
                            xml_data['solutions'], interactive, problem_id, local, grader)
    # Clean up temporary package folder
    if not local:
        shutil.rmtree(Paths().get_output_dir())
    else:
        warning_log("Change the names of the source files to DS standard:")
        warning_log("checker: checker.cpp")
        warning_log("validator: validator.cpp")
        warning_log("interactor: interactor.cpp")


def get_polygon_problem(problem_id: str, local: Optional[bool] = False):
    """Verifies the source and converts a problem package.

    Args:
        local: A boolean indicating if the package is local (default False).
        problem_id: The ID of the problem to download (default None).
    """
    package_folder = Paths().get_output_dir()
    if not local:
        download_package_polygon(problem_id)
    # Verificar se o caminho é uma pasta zippada
    elif not os.path.isdir(package_folder):
        unzip_package(package_folder)
        Paths().set_output_dir(package_folder[:-4])

    convert_problem(local, problem_id)
