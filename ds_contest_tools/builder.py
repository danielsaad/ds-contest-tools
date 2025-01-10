from collections import namedtuple
import pathlib
from jsonutils import parse_json
from utils import deep_merge_dicts
import os
from math import floor
from .pdfutils import build_pdf
from .toolchain import build_executables, run_programs
from parsers import common

Build_params = namedtuple(
    'Build_params', 'problem_dir all_solutions specific_solution cpu_count io pdf no_validator no_generator no_checker no_ouptut ngvoc')


class Builder:
    def __init__(self, params: Build_params):
        self.problem_dir = params.problem_dir
        self.problem_metadata = self.default_metadata()
        self.overwrite_metadata()
        self.process_params(params)

    def process_params(self, params: Build_params):
        # Adjust CPU count
        cpu_count: str = self.problem_metadata['build']['cpu_count']
        if cpu_count.isdigit():
            self.problem_metadata['build']['cpu_count'] = int(self)
        else:
            self.problem_metadata['build']['cpu_count'] = max(
                floor(os.cpu_count() * 0.7), 1)
        self.problem_metadata['build']['cpu-count'] == 'automatic'

        # Mutex group
        if params.pdf or params.io:
            self.problem_metadata['build']['generate_pdf_only'] = False
            self.problem_metadata['build']['run_all_solutions'] = False
            self.problem_metadata['build']['run_specific_solution'] = False
            self.problem_metadata['build']['generate_io_only'] = False
            self.problem_metadata['build']['run_generator'] = False
            self.problem_metadata['build']['run_validator'] = False
            self.problem_metadata['build']['produce_outputs'] = False
            self.problem_metadata['build']['run_checker'] = False

        # PDF only
        if params.pdf:
            self.problem_metadata['build']['generate_pdf_only'] = True
        # IO only
        elif params.io:
            self.problem_metadata['build']['generate_io_only'] = True
        elif params.specific_solution != '':
            self.problem_metadata['run_all_solutions'] = False
            self.problem_metadata['build']['run_specific_solution'] = params.specific_solution

    def default_metadata() -> dict:
        path = pathlib.Path('ds_contest_tools', 'files', 'problems.json')
        return parse_json(path)

    def overwrite_metadata(self) -> None:
        problem_metadata = parse_json(
            pathlib.Path(self.problem_dir, 'problem.json'))
        deep_merge_dicts(self.problem_metadata, problem_metadata)

    def build(self):
        problem_dir = self.problem_dir
        no_checker = not self.problem_metadata['build']['run_checker']
        no_validator = not self.problem_metadata['build']['run_validator']
        no_generator= not self.problem_metadata['build']['run_generator']
        no_output = not self.problem_metadata['build']['produce_outputs']
        all_solutions = self.problem_metadata['build']['run_all_solutions']
        specific_solution = self.problem_metadata['build']['run_specific_solution']
        pdf = self.problem_metadata['build']['generate_pdf_only']
        io = self.problem_metadata['build']['generate_io_only']
        cpu_count = self.problem_metadata['build']['cpu_count']
        ngvoc = no_checker and no_validator and no_generator and no_output
        common.setup_and_validate_paths(problem_dir)
        problem_name = common.get_basename(problem_dir)
        if pdf:
            common.info_log('Generating problem PDF')
            build_pdf()
            common.info_log('Problem PDF generated successfully')
        elif io:
            common.info_log("Generating input/output")
            build_executables(no_checker)
            if not ngvoc:
                run_programs(all_solutions=all_solutions, specific_solution=specific_solution,
                             cpu_number=cpu_count, no_validator=no_validator, no_generator=no_generator, no_output=no_output)
            common.info_log("Input/output generated successfully")
        else:
            common.info_log(f'Building problem {problem_name}')
            build_executables(no_checker)
            if not ngvoc:
                run_programs(all_solutions=all_solutions, specific_solution=specific_solution,
                             cpu_number=cpu_count, no_validator=no_validator, no_generator=no_generator, no_checker=no_checker, no_output=no_output)
            build_pdf()
            common.info_log(f'Problem {problem_name} built successfully')
