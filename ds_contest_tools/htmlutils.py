import io
import os
from math import floor, inf

from .logger import info_log
from .metadata import Problem, ProblemAnswer, Solution, Status, Test

REPORT_NAME = "report.html"


def write_head(problem_name: str, f_out: io.TextIOWrapper) -> None:
    """
    Writes the head of the HTML file with a given problem name and an output file.

    Args:
        problem_name: The name of the problem.
        f_out: The output file.

    """
    head: str = f"""
    <!DOCTYPE html>
<html lang="pt-br">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{problem_name}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">
    <style>
        .table-hard-warning {{ 
          --bs-table-color: #000;
          --bs-table-bg: #ffe17d;
          --bs-table-border-color: #e6dbb9;
          --bs-table-striped-bg: #f2e7c3;
          --bs-table-striped-color: #000;
          --bs-table-active-bg: #e6dbb9;
          --bs-table-active-color: #000;
          --bs-table-hover-bg: #ece1be;
          --bs-table-hover-color: #000;
          color: var(--bs-table-color);
          border-color: var(--bs-table-border-color);
        }}
      </style>
</head>
    """
    f_out.write(head)


def write_nav_bar(f_out: io.TextIOWrapper, html_file_name: str) -> None:
    """
    Write HTML navigation bar to file

    Args:
        f_out : File object to write the HTML navigation bar to
        html_file_name : Name of the HTML file
    """
    nav_bar: str = f"""
    <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-body-tertiary bg-dark" data-bs-theme="dark">
        <div class="container">
            <a class="navbar-brand h1 mb-0" href="./{html_file_name}">DS-CONTEST-TOOL</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                    aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <a class="nav-link active" aria-current="page" href="./{html_file_name}">Report</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    """
    f_out.write(nav_bar)


def write_main(problem_obj: Problem, f_out: io.TextIOWrapper) -> None:
    """
    Write the main HTML section of the problem page, including the test case 
        and auxiliary tables.

    Args:
        problem_obj: The problem object to extract information from.
        f_out: The output file stream to write the generated HTML to.

    """
    main_init: str = """
     <main class="row col-md col-lg col-xl mx-auto mt-3 mb-3">
        <section>
            <div class="container-fluid">
                <div class="row">
                    <div class="col-md-10 col-lg-10 col-xl-10">
    """
    f_out.write(main_init)

    write_test_case_table(problem_obj, f_out)
    write_auxiliary_table(problem_obj, f_out)

    main_end: str = """
                </div>
            </div>
        </section>
    </main>
    """
    print(main_end, file=f_out)


def write_test_case_table(problem_obj: Problem, f_out: io.TextIOWrapper) -> None:
    """
    Writes the test case table into the HTML file.

    Args:
        problem_obj: The Problem object.
        f_out: The output file.

    """
    thead: str = """
    <table class="table table-hover table-bordered border-secondary">
        <thead class="table-secondary sticky-top">
            <tr class="text-center">
                <th>#</th>
    """
    solution: Solution
    for solution in problem_obj.get_list_solution():
        thead += f'<th>{solution.solution_name}</th>\n\t'

    thead += """
    </tr>
    </thead>
    """
    f_out.write(thead)
    write_test_cases_tbody(problem_obj, f_out)


def write_test_cases_tbody(problem_obj: Problem, f_out: io.TextIOWrapper) -> None:
    """
    Writes the table body of test cases for the problem.

    Args:
        problem_obj: The problem object.
        f_out: The output file object.

    """
    tbody: str = """
        <tbody class="table-group-divider">
    """
    f_out.write(tbody)
    memory_limit: float = problem_obj.memory_limit
    time_limit: float = problem_obj.time_limit
    test_cases_number: int = problem_obj.get_number_of_tests()
    href_path: str = os.path.join(os.path.dirname(
        __file__), 'files', 'assets', 'test-case-info.html')
    memory_usage: float = None
    execution_time: float = None
    solution: Solution
    for i in range(test_cases_number):
        f_out.write('<tr class="text-center">')
        f_out.write(f'\t<td class="fw-bolder">{i + 1}</td>')
        for solution in problem_obj.get_list_solution():
            test_case: Test = solution.tests[i]
            test_color_class, test_status, tooltip_msg = test_case_status(
                test_case)
            memory_usage = min(test_case.memory_usage, memory_limit) / 1000000
            execution_time = min(test_case.exec_time, time_limit)
            expected_result: str = set_expected_result(
                solution.expected_result)
            url_params = f'id={i + 1}&solution={solution.solution_name}&veredict={test_status}&expected-result={expected_result}&time={test_case.exec_time:.2f}&memory={(test_case.memory_usage / 1000):.2f}&checker-output={test_case.checker_output}'
            url_link_params = f'title={problem_obj.problem_name}&input={os.path.join(problem_obj.input_folder, str(i + 1))}&output={os.path.join(solution.output_path, str(i + 1))}&answer={os.path.join(problem_obj.problem_dir, "output", str(i + 1))}&report-link={os.path.join(problem_obj.problem_dir, REPORT_NAME)}'
            table_data_info = f'\t<td class="{test_color_class}"><a href="{href_path}?{url_params}&{url_link_params}" {tooltip_msg}>{test_status} </a> <br>{execution_time:.2f} s / {(memory_usage):.1f} MB </td>'
            f_out.write(table_data_info)
        f_out.write('</tr>')

    f_out.write('<tr class="text-center table-secondary">')
    f_out.write(f'\t<td class="fw-bolder ">Total</td>')
    for solution in problem_obj.get_list_solution():
        ac_count: int = solution.statistics.ac_count
        ac_percentage: int = ac_count / test_cases_number * 100
        memory_usage = min(
            solution.statistics.max_memory_usage, memory_limit) / 1000000
        execution_time = min(
            solution.statistics.max_exec_time, time_limit)
        table_data_info = f'\t<td> {floor(ac_percentage)} %<br>{execution_time:.2f} s / {(memory_usage):.1f} MB </td>'
        f_out.write(table_data_info)
    f_out.write('</tr>')

    tbody = """
                            </tbody>
                        </table>
                    </div>
    """
    f_out.write(tbody)


def set_expected_result(expected_result: str) -> str:
    convert_expected_result: dict = {
        "main-ac": 'ACCEPTED',
        "alternative-ac": 'ACCEPTED',
        "wrong-answer": 'WRONG ANSWER',
        "time-limit": 'TIME LIMIT EXCEEDED',
        "runtime-error": 'RUNTIME ERROR',
        "memory-limit": 'MEMORY LIMIT EXCEEDED',
        "presentation-error": 'PRESENTATION ERROR',
        "time-limit-or-ac": 'TIME LIMIT OR ACCEPTED',
        "time-limit-or-memory-limit": 'TIME LIMIT OR MEMORY LIMIT  EXCEEDED'
    }
    return convert_expected_result[expected_result]


def test_case_status(test_case: Test) -> tuple:
    """
    Determine the status of a test case and return the relevant information.

    Args:
        test_case: An instance of the Test class.

    Returns:
        tuple: A tuple containing three values: the color class for the table 
            cell, the status abbreviation, and the tooltip message (if applicable).
    """
    test_color_class: str = ''
    test_status: str = ''
    tooltip_msg: str = ''
    if test_case.status == Status.AC:
        test_status = 'AC'
        test_color_class = "table-success"
    elif test_case.status == Status.WA:
        test_status = 'WA'
        test_color_class = "table-danger"
    elif test_case.status == Status.RE:
        test_status = 'RE'
        test_color_class = "table-info"
    elif test_case.status == Status.HARD_TLE:
        test_status = 'TLE'
        test_color_class = "table-hard-warning"
    elif test_case.status == Status.SOFT_TLE:
        test_status = 'TLE'
        test_color_class = "table-warning"
        tooltip_msg = 'data-bs-toggle="tooltip" data-bs-placement="top" data-bs-custom-class="custom-tooltip" data-bs-title="Solution passed in double of time!"'
    elif test_case.status == Status.MLE:
        test_status = 'MLE'
        test_color_class = "table-primary"
    elif test_case.status == Status.PE:
        test_status = 'PE'
        test_color_class = "table-light"
    return test_color_class, test_status, tooltip_msg


def write_auxiliary_table(problem_obj: Problem, f_out: io.TextIOWrapper) -> None:
    """
    Writes an auxiliary table containing a row for each solution for the problem.

    Args:
        problem_obj: The problem object to extract the solutions from.
        f_out: The output file object to write to.

    """
    table_init = """
    <div class="col-md-2 col-lg-2 col-xl-2 position-fixed end-0">
        <table class="table table-hover table-bordered">
            <thead class="table-dark">
                <tr class="text-center">
                    <th>Solutions</th>
                    <th>Expected Result</th>
                    <th>Result</th>
                </tr>
            </thead>
             <tbody>\
    """
    f_out.write(table_init)
    write_aux_trow(problem_obj, f_out)
    table_end = """
            </tbody>
        </table>
    </div>\
    """
    f_out.write(table_end)


def write_aux_trow(problem_obj: Problem, f_out: io.TextIOWrapper) -> None:
    """
    Write a table row for each solution in the problem object and write it 
    to the output file.

    Args:
        problem_obj: The problem object containing the solutions to be written 
            to the table row.
        f_out: The output file to which the table rows are written.

    """
    solution: Solution
    for solution in problem_obj.get_list_solution():
        f_out.write('<tr class="text-center">')
        row_color, solution_result_symbol = solution_status(
            solution.solution_status)
        f_out.write(f'\t<td>{solution.solution_name}</td>')
        f_out.write(
            f'\t<td>{set_expected_result(solution.expected_result)}</td>')
        f_out.write(f'\t<td class="{row_color}">{solution_result_symbol}</td>')
        f_out.write('</tr>')


def solution_status(result: ProblemAnswer) -> str:
    """
    Return the HTML row color and solution result symbol based on the result.

    Args:
        result: The result of the problem solution.

    Returns:
        Tuple[str, str]: A tuple containing the HTML row color and solution 
            result symbol.
    """
    solution_result_symbol: str = ''
    row_color: str = ''
    if result == ProblemAnswer.CORRECT:
        solution_result_symbol = '&#9989;'
        row_color = 'table-success'
    else:
        solution_result_symbol = '&#10060;'
        row_color = 'table-danger'

    return row_color, solution_result_symbol


def write_footer(f_out: io.TextIOWrapper) -> None:
    """
    Writes the footer HTML code to a given text file object.

    Args:
        f_out: A text file object to write the footer HTML code.

    """
    footer = """
     	<footer class="col-md-12 col-lg-12 col-xl-12 bg-dark text-white pt-4 pb-4 bottom-0">
        <div class="container text-center text-md-left">
            <div class="row text-center text-md-left">
                <div class="col-md-3 col-lg-3 col-xl-3 mx-auto mt-3">
                    <h5 class="text-uppercase mb-4 font-weight-bold text-warning">DS CONTEST TOOL
                    </h5>
                    <p>
                        This tool for preparing competitive programming competitions aims 
                        to facilitate and simplify the formatting of problems for creating 
                        <i>contests</i>.
                    </p>
                </div>
                <div class="col-md-3 col-lg-2 col-xl-2 mx-auto mt-3">
                    <h5 class="text-uppercase mb-4 font-weight-bold text-warning">Useful links</h5>
                    <p>
                        <a href="https://github.com/danielsaad/ds-contest-tools" class="text-white"
                            style="text-decoration: none;" target="_blank">GitHub</a>
                    </p>
                    <p>
                        <a href="https://danielsaad.com/" class="text-white"
                            style="text-decoration: none;" target="_blank">Daniel Saad</a>
                    </p>
                    <p>
                        <a href="https://www.ifb.edu.br/taguatinga/pagina-inicial" class="text-white"
                            style="text-decoration: none;" target="_blank">Instituto Federal de Brasília - Campus
                            Taguatinga</a>
                    </p>
                </div>
                <div class="col-md-4 col-lg-3 col-xl-3 mx-auto mt-3">
                    <h5 class="text-uppercase mb-4 font-weight-bold text-warning">Contact</h5>
					<p>
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
							class="bi bi-envelope-at" viewBox="0 0 16 16">
							<path
								d="M2 2a2 2 0 0 0-2 2v8.01A2 2 0 0 0 2 14h5.5a.5.5 0 0 0 0-1H2a1 1 0 0 1-.966-.741l5.64-3.471L8 9.583l7-4.2V8.5a.5.5 0 0 0 1 0V4a2 2 0 0 0-2-2H2Zm3.708 6.208L1 11.105V5.383l4.708 2.825ZM1 4.217V4a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v.217l-7 4.2-7-4.2Z" />
							<path
								d="M14.247 14.269c1.01 0 1.587-.857 1.587-2.025v-.21C15.834 10.43 14.64 9 12.52 9h-.035C10.42 9 9 10.36 9 12.432v.214C9 14.82 10.438 16 12.358 16h.044c.594 0 1.018-.074 1.237-.175v-.73c-.245.11-.673.18-1.18.18h-.044c-1.334 0-2.571-.788-2.571-2.655v-.157c0-1.657 1.058-2.724 2.64-2.724h.04c1.535 0 2.484 1.05 2.484 2.326v.118c0 .975-.324 1.39-.639 1.39-.232 0-.41-.148-.41-.42v-2.19h-.906v.569h-.03c-.084-.298-.368-.63-.954-.63-.778 0-1.259.555-1.259 1.4v.528c0 .892.49 1.434 1.26 1.434.471 0 .896-.227 1.014-.643h.043c.118.42.617.648 1.12.648Zm-2.453-1.588v-.227c0-.546.227-.791.573-.791.297 0 .572.192.572.708v.367c0 .573-.253.744-.564.744-.354 0-.581-.215-.581-.8Z" />
						</svg> daniel.nunes@ifb.edu.br
					</p>
					<p>
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
							class="bi bi-envelope-at" viewBox="0 0 16 16">
							<path
								d="M2 2a2 2 0 0 0-2 2v8.01A2 2 0 0 0 2 14h5.5a.5.5 0 0 0 0-1H2a1 1 0 0 1-.966-.741l5.64-3.471L8 9.583l7-4.2V8.5a.5.5 0 0 0 1 0V4a2 2 0 0 0-2-2H2Zm3.708 6.208L1 11.105V5.383l4.708 2.825ZM1 4.217V4a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v.217l-7 4.2-7-4.2Z" />
							<path
								d="M14.247 14.269c1.01 0 1.587-.857 1.587-2.025v-.21C15.834 10.43 14.64 9 12.52 9h-.035C10.42 9 9 10.36 9 12.432v.214C9 14.82 10.438 16 12.358 16h.044c.594 0 1.018-.074 1.237-.175v-.73c-.245.11-.673.18-1.18.18h-.044c-1.334 0-2.571-.788-2.571-2.655v-.157c0-1.657 1.058-2.724 2.64-2.724h.04c1.535 0 2.484 1.05 2.484 2.326v.118c0 .975-.324 1.39-.639 1.39-.232 0-.41-.148-.41-.42v-2.19h-.906v.569h-.03c-.084-.298-.368-.63-.954-.63-.778 0-1.259.555-1.259 1.4v.528c0 .892.49 1.434 1.26 1.434.471 0 .896-.227 1.014-.643h.043c.118.42.617.648 1.12.648Zm-2.453-1.588v-.227c0-.546.227-.791.573-.791.297 0 .572.192.572.708v.367c0 .573-.253.744-.564.744-.354 0-.581-.215-.581-.8Z" />
						</svg> matheus.silva18@estudante.ifb.edu.br
					</p>
					<p>
						<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
							class="bi bi-envelope-at" viewBox="0 0 16 16">
							<path
								d="M2 2a2 2 0 0 0-2 2v8.01A2 2 0 0 0 2 14h5.5a.5.5 0 0 0 0-1H2a1 1 0 0 1-.966-.741l5.64-3.471L8 9.583l7-4.2V8.5a.5.5 0 0 0 1 0V4a2 2 0 0 0-2-2H2Zm3.708 6.208L1 11.105V5.383l4.708 2.825ZM1 4.217V4a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v.217l-7 4.2-7-4.2Z" />
							<path
								d="M14.247 14.269c1.01 0 1.587-.857 1.587-2.025v-.21C15.834 10.43 14.64 9 12.52 9h-.035C10.42 9 9 10.36 9 12.432v.214C9 14.82 10.438 16 12.358 16h.044c.594 0 1.018-.074 1.237-.175v-.73c-.245.11-.673.18-1.18.18h-.044c-1.334 0-2.571-.788-2.571-2.655v-.157c0-1.657 1.058-2.724 2.64-2.724h.04c1.535 0 2.484 1.05 2.484 2.326v.118c0 .975-.324 1.39-.639 1.39-.232 0-.41-.148-.41-.42v-2.19h-.906v.569h-.03c-.084-.298-.368-.63-.954-.63-.778 0-1.259.555-1.259 1.4v.528c0 .892.49 1.434 1.26 1.434.471 0 .896-.227 1.014-.643h.043c.118.42.617.648 1.12.648Zm-2.453-1.588v-.227c0-.546.227-.791.573-.791.297 0 .572.192.572.708v.367c0 .573-.253.744-.564.744-.354 0-.581-.215-.581-.8Z" />
						</svg> leonam.knupp@estudante.ifb.edu.br
					</p>
                </div>
            </div>
        </div>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.7/dist/umd/popper.min.js" integrity="sha384-zYPOMqeu1DAVkHiLqWBUTcbYfZ8osu1Nd6Z89ify25QV9guujx43ITvfi12/QExE" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.min.js" integrity="sha384-Y4oOpwW3duJdCWv5ly8SCFYWqFDsfob/3GkgExXKV4idmbt98QcxXYs9UoXAB7BZ" crossorigin="anonymous"></script>
	<script>
		const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
		const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
	</script>
</body>
</html>
    """
    f_out.write(footer)


def print_to_html(problem_obj: Problem) -> None:
    """
    Create an HTML report for a given problem.

    Args:
        problem_obj (Problem): An instance of the Problem class.

    """
    problem_folder: str = problem_obj.problem_dir
    html_filename: str = REPORT_NAME
    html_filepath: str = os.path.join(problem_folder, html_filename)
    info_log(f'Creating {html_filename}')
    with open(html_filepath, 'w') as f_out:
        problem_name: str = problem_obj.problem_name
        write_head(problem_name, f_out)
        write_nav_bar(f_out, html_filename)
        write_main(problem_obj, f_out)
        write_footer(f_out)
