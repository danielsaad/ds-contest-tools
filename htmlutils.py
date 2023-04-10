import io
import os
from webbrowser import open_new

from checker import ProblemAnswer, Status
from logger import info_log
from metadata import Paths


def write_head(problem_name: str, f_out: io.TextIOWrapper) -> None:
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
    <link rel="stylesheet" href="../arquivos/assets/style/bootstrap.css">
</head>
    """
    print(head, file=f_out)


def write_nav_bar(f_out: io.TextIOWrapper) -> None:
    nav_bar: str = """
    <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-body-tertiary bg-dark" data-bs-theme="dark">
        <div class="container">
            <a class="navbar-brand h1 mb-0" href="./index.html">DS-CONTEST-TOOL</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                    aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNav">
                    <ul class="navbar-nav">
                        <li class="nav-item">
                            <a class="nav-link active" aria-current="page" href="./index.html">Report</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    """
    print(nav_bar, file=f_out)


def write_main(solutions_info_dict: dict, problem_metadata: dict, f_out: io.TextIOWrapper) -> None:
    main_init: str = """
     <main class="row col-md col-lg col-xl mx-auto mt-3 mb-3">
        <section>
            <div class="container-fluid">
                <div class="row">
                    <div class="col-md-10 col-lg-10 col-xl-10">
    """
    print(main_init, file=f_out)
    solutions: list = solutions_list(solutions_info_dict)
    problem_limits: dict = {'time': problem_metadata['problem']['time_limit'],
                            'memory': problem_metadata['problem']['memory_limit_mb']}

    write_test_case_table(solutions_info_dict, solutions,
                          problem_limits, f_out)
    write_auxiliary_table(solutions_info_dict, f_out)

    main_end: str = """
                </div>
            </div>
        </section>
    </main>
    """
    print(main_end, file=f_out)


def solutions_list(solutions_info_dict: dict) -> list:
    tmp_list: list = list()
    for solution, _ in solutions_info_dict.items():
        tmp_list.append(solution)

    return tmp_list


def write_test_case_table(solutions_info_dict: dict, solutions: list, problem_limits: dict, f_out: io.TextIOWrapper) -> None:
    thead: str = """
    <table class="table table-hover table-bordered border-secondary">
        <thead class="table-secondary sticky-top">
            <tr class="text-center">
                <th>#</th>
    """

    for solution in solutions:
        thead += f'<th>{solution}</th>\n\t'

    thead += """
    </tr>
    </thead>
    """
    print(thead, file=f_out)
    write_test_cases_tbody(solutions_info_dict,
                           solutions, problem_limits, f_out)


def write_test_cases_tbody(solutions_info_dict: dict, solutions: list, problem_limits: dict, f_out: io.TextIOWrapper) -> None:
    tbody: str = """
        <tbody class="table-group-divider">
    """
    n_test_cases: int = len(
        solutions_info_dict[solutions[0]]['test-case-info'])
    time_limit: float = problem_limits['time']
    mem_limit: float = problem_limits['memory']
    for i in range(n_test_cases):
        print(f'<tr class="text-center">', file=f_out)
        print(f'\t<td class="fw-bolder">{i + 1}</td>', file=f_out)
        for solution in solutions:
            test_case_info: list = solutions_info_dict[solution
                                                       ]['test-case-info'][i]
            test_color_class, test_status, tooltip_msg = test_case_status(
                test_case_info)
            memo_usage: float = test_case_info[2] / 1000000
            memo_usage: float = min(memo_usage, mem_limit)
            exec_time: float = min(test_case_info[1], time_limit)

            print(
                f'\t<td class="{test_color_class}"><a href="./assets/test-case-info.html?id={i + 1}&solution={solution}" {tooltip_msg}>{test_status} </a> <br>{exec_time:.2f} / {(memo_usage):.1f} </td>', file=f_out)
        print(f'</tr>', file=f_out)

    tbody = """
                            </tbody>
                        </table>
                    </div>
    """
    print(tbody, file=f_out)


def test_case_status(test_case_info: list) -> tuple:
    test_color_class: str = ''
    test_status: str = ''
    tooltip_msg: str = ''
    if test_case_info[0] == Status.AC:
        test_status = 'AC'
        test_color_class = "table-success"
    elif test_case_info[0] == Status.WA:
        test_status = 'WA'
        test_color_class = "table-danger"
    elif test_case_info[0] == Status.RE:
        test_status = 'RE'
        test_color_class = "table-info"
    elif test_case_info[0] == Status.HARD_TLE:
        test_status = 'TLE'
        test_color_class = "table-hard-warning"
    elif test_case_info[0] == Status.SOFT_TLE:
        test_status = 'TLE'
        test_color_class = "table-warning"
        tooltip_msg = 'data-bs-toggle="tooltip" data-bs-placement="top" data-bs-custom-class="custom-tooltip" data-bs-title="Solution passed in double of time!"'
    elif test_case_info[0] == Status.MLE:
        test_status = 'MLE'
        test_color_class = "table-primary"
    elif test_case_info[0] == Status.PE:
        test_status = 'PE'
        test_color_class = "table-light"
    return test_color_class, test_status, tooltip_msg


def write_auxiliary_table(solutions_info_dict, f_out) -> None:
    table_init = """
    <div class="col-md-2 col-lg-2 col-xl-2 position-fixed end-0">
        <table class="table table-hover table-bordered">
            <thead class="table-dark">
                <tr>
                    <th>Solutions</th>
                    <th>Result</th>
                </tr>
            </thead>
             <tbody>\
    """
    print(table_init, file=f_out)
    write_aux_trow(solutions_info_dict, f_out)
    table_end = """
            </tbody>
        </table>
    </div>\
    """
    print(table_end, file=f_out)


def write_aux_trow(solutions_info_dict: dict, f_out: io.TextIOWrapper) -> None:
    for solution, solution_info in solutions_info_dict.items():
        print('<tr>', file=f_out)
        row_color, solution_result_symbol = solution_status(
            solution_info['solution-result']['solution-result'])
        print(f'\t<td>{solution}</td>', file=f_out)
        print(
            f'\t<td class="{row_color}">{solution_result_symbol}</td>', file=f_out)
        print('</tr>', file=f_out)


def solution_status(result: ProblemAnswer) -> str:
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
    print(footer, file=f_out)


def print_to_html(problem_metadata: str, solutions_info_dict: dict) -> None:
    problem_folder: str = Paths().get_problem_dir()
    html_filename: str = 'index.html'
    html_filepath: str = os.path.join(problem_folder, html_filename)
    info_log(f'Creating {html_filename}')
    with open(html_filepath, 'w') as f_out:
        problem_name: str = problem_metadata['problem']['title']
        write_head(problem_name, f_out)
        write_nav_bar(f_out)
        write_main(solutions_info_dict, problem_metadata, f_out)
        write_footer(f_out)
