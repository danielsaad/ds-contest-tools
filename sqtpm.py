from jsonutils import parse_json
from metadata import Paths
import os
import shutil
from utils import instance_paths


def create_config(showcases, stkmem, cputime) -> None:
    output_folder = Paths.instance().dirs['output_dir']

    config_content = f"""description = statement.html
showcases = {showcases}
verifier = @checker
three-parameters-verifier = on
stkmem = {stkmem}
cputime = {cputime}
"""

    config_content += """
# languages = {C CPP Python3}
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
# virtmem = n
# limits = nome{:[t,v,s]=inteiro}

gcc = /usr/bin/gcc
gcc-args = -Wall -O3
g++ = /usr/bin/g++
g++-args = -Wall -O3"""
    with open(os.path.join(output_folder, 'config'), 'w') as f:
        f.write(config_content)


def create_html_statement(pdf_name) -> None:
    """Create statement file for the problem PDF."""
    output_folder = Paths.instance().dirs['output_dir']
    html_content = f"""<object data="{pdf_name}.pdf" type="application/pdf" width="100%" height="500">
    <p>If the PDF was not rendered, use this <a href="{pdf_name}.pdf">to the PDF!</a></p>
</object>"""
    with open(os.path.join(output_folder, 'statement.html'), 'w') as f:
        f.write(html_content)


def copy_auxiliar_statement() -> None:
    problem_folder = Paths.instance().dirs['problem_dir']
    output_folder = Paths.instance().dirs['output_dir']
    statement_folder = os.path.join(problem_folder, 'statement')
    for file in os.listdir(statement_folder):
        if not file.endswith('.tex'):
            shutil.copy2(os.path.join(statement_folder, file),
                         os.path.join(output_folder, file))


def copy_pdf(pdf_name) -> None:
    problem_folder = Paths.instance().dirs['problem_dir']
    output_folder = Paths.instance().dirs['output_dir']
    pdf_name += '.pdf'
    shutil.copy2(os.path.join(problem_folder, pdf_name),
                 os.path.join(output_folder, pdf_name))


def copy_source_files(main_solution) -> None:
    """"""
    problem_folder = Paths.instance().dirs['problem_dir']
    output_folder = Paths.instance().dirs['output_dir']
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
                continue
            destination = os.path.join(output_folder, 'src', file)
            shutil.copy(generator, destination)

    # Copy standard DS generator
    ds_generator = 'generator.cpp'
    ds_gen_path = os.path.join(problem_folder, 'src', ds_generator)
    if os.path.exists(ds_gen_path) and ds_generator not in generator_list:
        destination = os.path.join(output_folder, 'src', ds_generator)
        shutil.copy(ds_gen_path, destination)

    # Copy checker
    shutil.copy2(os.path.join(problem_folder, 'src', 'checker.cpp'),
                 os.path.join(output_folder, 'src', 'checker.cpp'))

    # Copy main solution
    shutil.copy2(os.path.join(problem_folder, 'src', main_solution),
                 os.path.join(output_folder, 'src', f'main_solution{os.path.splitext(main_solution)[1]}'))

    # Copy testlib
    shutil.copy2(os.path.join(problem_folder, 'src', 'testlib.h'),
                 os.path.join(output_folder, 'src', 'testlib.h'))


def copy_generator_script() -> None:
    output_folder = Paths.instance().dirs['output_dir']
    shutil.copy2(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              'arquivos', 'sqtpm_io.sh'),
                 os.path.join(output_folder, 'runner.sh'))


def create_makefile():
    output_folder = Paths.instance().dirs['output_dir']
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
CXX_FLAGS := -Wall -O2
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


def convert_to_sqtpm(problem_dir, output_dir) -> None:
    instance_paths(problem_dir, output_dir)

    problem_folder = Paths.instance().dirs['problem_dir']
    output_folder = Paths.instance().dirs['output_dir']
    problem_metadata = parse_json(os.path.join(problem_folder, 'problem.json'))
    os.makedirs(os.path.join(output_folder, 'src'), exist_ok=True)

    pdf_name = os.path.basename(os.path.normpath(problem_folder))
    copy_pdf(pdf_name)
    create_html_statement(pdf_name)
    copy_auxiliar_statement()

    create_makefile()
    copy_source_files(problem_metadata['solutions']['main-ac'])
    copy_generator_script()
    create_config(' '.join([str(x) for x in list(
        range(1, problem_metadata['io_samples'] + 1))]),
        problem_metadata['problem']['memory_limit_mb'],
        problem_metadata['problem']['time_limit'])
