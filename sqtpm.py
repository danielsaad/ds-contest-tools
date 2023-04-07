import os
import shutil
import sys
from typing import Union

from jsonutils import parse_json
from logger import error_log, info_log
from metadata import Paths
from toolchain import generate_inputs, get_manual_tests
from utils import (check_problem_metadata, generate_timestamp, instance_paths,
                   verify_path)


def create_config(showcases: str, memory_limit: int, cputime: int) -> None:
    """Create default config file with problem informations."""
    output_folder = Paths().get_output_dir()
    info_log("Creating config file.")

    config_content = f"""description = statement.html
showcases = {showcases}
verifier = @checker
cputime = {cputime}
virtmem = {memory_limit * 1000}
"""

    config_content += """
# languages = {C C++ Python3 PDF}
# startup = aaaa/mm/dd hh:mm:ss
# deadline = aaaa/mm/dd hh:mm:ss
# penalty = n
# grading = {total, porportional}
# keep-open = n
# hide-grades = {on,off}
# tries = n
# files = n,m
# filenames = lista
# backup = {on,off}
# limits = nome{:[t,v,s]=inteiro}

gcc = /usr/bin/gcc
gcc-args = -Wall -O3 -static
g++ = /usr/bin/g++
g++-args = -Wall -O3 -static"""
    with open(os.path.join(output_folder, 'config'), 'w') as f:
        f.write(config_content)


def create_html_statement(problem_name: str, pdf_name: str) -> None:
    """Create statement HTML file to show the problem PDF."""
    output_folder = Paths().get_output_dir()
    info_log("Creating HTML statement file.")
    html_content = f"""<iframe src="{problem_name}/{pdf_name}.pdf" scrolling="auto" width="100%" height="1000" frameborder="0">
    Se o PDF não renderizou, utilize <a href="{problem_name}/{pdf_name}.pdf"> para o PDF!</a></p>
</iframe>"""
    with open(os.path.join(output_folder, 'statement.html'), 'w') as f:
        f.write(html_content)


def copy_pdf(pdf_name: str) -> None:
    """Copy PDF of the problem."""
    problem_folder = Paths().get_problem_dir()
    output_folder = Paths().get_output_dir()
    info_log("Copying problem PDF file.")
    pdf_name += '.pdf'
    verify_path(os.path.join(problem_folder, pdf_name))
    shutil.copy2(os.path.join(problem_folder, pdf_name),
                 os.path.join(output_folder, pdf_name))


def copy_source_files(main_solution: str) -> None:
    """Copy generators, scripts, checker and main solution
    to the output folder."""
    problem_folder = Paths().get_problem_dir()
    output_folder = Paths().get_output_dir()
    script_folder = os.path.join(problem_folder, 'src', 'script.sh')
    generator_list = set()

    # Copy script generators
    script = ''
    if os.path.exists(script_folder):
        with open(script_folder, 'r') as f:
            script = f.read()
    if script != '':
        with open(os.path.join(output_folder, 'src', 'script.sh'), 'w') as f:
            f.write(script)
        script_lines = script.split('\n')
        for line in script_lines:
            if line != '':
                generator_list.add(line.split()[0])

        for file in generator_list:
            file += '.cpp'
            generator = os.path.join(problem_folder, 'src', file)
            if not os.path.exists(generator):
                error_log(f"Generator {file} does not exist.")
                sys.exit(1)
            info_log(f"Copying {file} file.")
            destination = os.path.join(output_folder, 'src', file)
            shutil.copy(generator, destination)

    # Copy standard DS generator
    ds_generator = 'generator.cpp'
    ds_gen_path = os.path.join(problem_folder, 'src', ds_generator)
    if os.path.exists(ds_gen_path):
        info_log(f"Copying {ds_generator} file.")
        destination = os.path.join(output_folder, 'src', ds_generator)
        shutil.copy(ds_gen_path, destination)

    # Copy checker
    checker = 'checker.cpp'
    checker_path = os.path.join(problem_folder, 'src', checker)
    verify_path(checker_path)
    info_log(f"Copying {checker} file.")
    shutil.copy2(checker_path,
                 os.path.join(output_folder, 'src', checker))

    # Copy main solution
    solution_name = f'main_solution{os.path.splitext(main_solution)[1]}'
    solution_path = os.path.join(problem_folder, 'src', main_solution)
    verify_path(solution_path)
    info_log(f"Copying {main_solution} file.")
    shutil.copy2(solution_path,
                 os.path.join(output_folder, 'src', solution_name))

    # Copy testlib
    testlib_path = os.path.join(problem_folder, 'src', 'testlib.h')
    verify_path(testlib_path)
    info_log("Copying testlib.h file.")
    shutil.copy2(testlib_path,
                 os.path.join(output_folder, 'src', 'testlib.h'))


def copy_generator_script() -> None:
    """Copy script to generate test cases for SQTPM."""
    output_folder = Paths().get_output_dir()
    info_log("Copying genio.sh script file.")
    shutil.copy2(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'files', 'sqtpm.sh'),
                 os.path.join(output_folder, 'genio.sh'))


def copy_manual_tests() -> None:
    """Move manual tests to SQTPM folder."""
    output_folder = Paths().get_output_dir()
    tmp_folder = os.path.join(
        '/', 'tmp', f'ds-contest-tool-{generate_timestamp()}', 'input')

    generate_inputs(move=False, output_folder=tmp_folder)
    manual_tests = get_manual_tests(tmp_folder)
    for test in manual_tests:
        shutil.copy2(test, os.path.join(
            output_folder, os.path.basename(test) + '.in'))


def create_makefile() -> None:
    """Create Makefile to compile source files for SQTPM."""
    output_folder = Paths().get_output_dir()
    info_log("Creating Makefile.")
    makefile_content = """SRC = $(wildcard *.cpp)
BIN = $(patsubst %.cpp, %, $(SRC))
DBG = $(patsubst %.cpp, %, $(SRC))

SRC_C = $(wildcard *.c)
BIN_C = $(patsubst %.c, %, $(SRC_C))
DBG_C = $(patsubst %.c, %, $(SRC_C))

SRC_JAVA = $(wildcard *.java)
BIN_JAVA = $(patsubst %.java, %.class, $(SRC_JAVA))
DBG_JAVA = $(patsubst %.java, %.class, $(SRC_JAVA))

BINARIES = $(basename $(SRC) $(SRC_C) $(SRC_JAVA))

C := gcc
CPP := g++
CXX_FLAGS := -Wall -O3 -static
JV = javac

.PHONY: all release clean

all: release

release: $(BIN) $(BIN_C) $(BIN_JAVA)

$(BIN): % : %.cpp
	$(CPP) $(CXX_FLAGS) $^ -o $@

$(BIN_C): % : %.c
	$(C) $(CXX_FLAGS) $^ -o $@

$(BIN_JAVA): %.class : %.java
	$(JV) $(JV_DIR) $^

clean:
	@echo Cleaning executables
	rm -f $(BINARIES)

"""
    with open(os.path.join(output_folder, 'src', 'Makefile'), 'w') as f:
        f.write(makefile_content)


def convert_to_sqtpm(problem_dir: str, output_dir: Union[str, None]) -> None:
    """Convert DS problem to SQTPM."""
    if not output_dir:
        output_dir = os.path.join(problem_dir, 'sqtpm')
    instance_paths(problem_dir, output_dir)
    info_log("Starting DS -> SQTPM conversion.")
    problem_folder = Paths().get_problem_dir()
    output_folder = Paths().get_output_dir()
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))
    check_problem_metadata(problem_metadata)
    pdf_name = os.path.basename(os.path.normpath(problem_folder))
    os.makedirs(os.path.join(output_folder, 'src'), exist_ok=True)

    copy_pdf(pdf_name)
    copy_generator_script()
    copy_source_files(problem_metadata['solutions']['main-ac'])
    copy_manual_tests()

    create_makefile()
    create_html_statement(os.path.basename(
        os.path.normpath(output_folder)), pdf_name)
    create_config(' '.join([str(x).zfill(3) for x in list(
        range(1, problem_metadata['io_samples'] + 1))]),
        problem_metadata['problem']['memory_limit_mb'],
        problem_metadata['problem']['time_limit'])
