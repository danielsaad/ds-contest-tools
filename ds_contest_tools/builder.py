from ds_contest_tools.parsers.dto.build_options import BuildOptions
from ds_contest_tools.pdfutils import build_pdf
from ds_contest_tools.toolchain import build_executables, run_programs
from ds_contest_tools.parsers.common import info_log, get_basename


def execute_build(options: BuildOptions) -> None:
    problem_name = get_basename(options.problem_dir)

    if options.pdf:
        info_log('Generating problem PDF')
        build_pdf()
        info_log('Problem PDF generated successfully')
    elif options.io:
        info_log("Generating input/output")
        build_executables(options.no_checker)
        if not options.ngvoc:
            run_programs(all_solutions=options.all_solutions, specific_solution=options.specific_solution,
                     cpu_number=options.cpu_count, no_validator=options.no_validator, no_generator=options.no_generator, no_output=options.no_output)
        info_log("Input/output generated successfully")
    else:
        info_log(f'Building problem {problem_name}')
        build_executables(options.no_checker)
        if not options.ngvoc:
            run_programs(all_solutions=options.all_solutions, specific_solution=options.specific_solution,
                        cpu_number=options.cpu_count, no_validator=options.no_validator, no_generator=options.no_generator, no_checker=options.no_checker, no_output=options.no_output)
        build_pdf()
        info_log(f'Problem {problem_name} built successfully')