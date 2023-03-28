import io
import os
from webbrowser import open_new
from logger import info_log
from metadata import Paths
from checker import Status, ProblemAnswer


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
                            <a class="nav-link active" aria-current="page" href="./index.html">Relatório</a>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    """
    print(nav_bar, file=f_out)


def write_main(solutions_info_dict: dict, f_out: io.TextIOWrapper) -> None:
    main_init: str = """
     <main class="row col-md col-lg col-xl mx-auto mt-3 mb-3">
        <section>
            <div class="container-fluid">
                <div class="row">
                    <div class="col-md-10 col-lg-10 col-xl-10">
    """
    print(main_init, file=f_out)
    solutions: list = solutions_list(solutions_info_dict)
    write_test_case_table(solutions_info_dict, solutions, f_out)
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


def write_test_case_table(solutions_info_dict: dict, solutions: list, f_out: io.TextIOWrapper) -> None:
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
    write_test_cases_tbody(solutions_info_dict, solutions, f_out)


def write_test_cases_tbody(solutions_info_dict: dict, solutions: list, f_out: io.TextIOWrapper) -> None:
    tbody: str = """
        <tbody class="table-group-divider">
    """
    n_test_cases: int = len(
        solutions_info_dict[solutions[0]]['test-case-info'])
    for i in range(n_test_cases):
        print(f'<tr class="text-center">', file=f_out)
        print(f'\t<td class="fw-bolder">{i + 1}</td>', file=f_out)
        for solution in solutions:
            test_case_info: list = solutions_info_dict[solution
                                                       ]['test-case-info'][i]
            test_color_class, test_status = test_case_status(test_case_info)
            memo_info: int = test_case_info[2]
            exec_time: float = test_case_info[1]
            print(
                f'\t<td class="{test_color_class}"><a href="./assets/test-case-info.html?id={i + 1}&solution={solution}">{test_status} </a> <br>{exec_time:.2f} / {(memo_info // 1000000):.1f} </td>', file=f_out)
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
    if test_case_info[0] == Status.AC:
        test_status = 'AC'
        test_color_class = "table-success"
    elif test_case_info[0] == Status.WA:
        test_status = 'WA'
        test_color_class = "table-danger"
    elif test_case_info[0] == Status.RE:
        test_status = 'RE'
        test_color_class = "table-info"
    elif test_case_info[0] == Status.HARD_TLE or test_case_info[0] == Status.SOFT_TLE:
        test_status = 'TLE'
        test_color_class = "table-warning"
    elif test_case_info[0] == Status.MLE:
        test_status = 'MLE'
        test_color_class = "table-primary"
    elif test_case_info[0] == Status.PE:
        test_status = 'PE'
        test_color_class = "table-light"
    return test_color_class, test_status


def write_auxiliary_table(solutions_info_dict, f_out) -> None:
    table_init = """
    <div class="col-md-2 col-lg-2 col-xl-2 position-fixed end-0">
        <table class="table table-hover table-bordered">
            <thead class="table-dark">
                <tr>
                    <th>Soluções</th>
                    <th>Resultado</th>
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
     <footer class="bg-dark text-white pt-4 pb-4 position-absolute bottom-0">
        <div class="container text-center text-md-left">
            <div class="row text-center text-md-left">
                <div class="col-md-3 col-lg-3 col-xl-3 mx-auto mt-3">
                    <h5 class="text-uppercase mb-4 font-weight-bold text-warning">DS CONTEST TOOL</h5>
                    <p>
                        Essa ferramenta de preparação de competições de progamação competitiva objetiva facilitar e
						simplificar a formatação de problemas para a criação de <span class="fst-italic">contests</span>.
                    </p>
                </div>
                <div class="col-md-3 col-lg-2 col-xl-2 mx-auto mt-3">
                    <h5 class="text-uppercase mb-4 font-weight-bold text-warning">Useful links</h5>
                    <p>
                        <a href="https://github.com/danielsaad/ds-contest-tools" class="text-white" style="text-decoration: none;" target="_blank">GitHub</a>
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
						<a href="https://goo.gl/maps/BKp6Yg7mjcz4ZWhL9" class="text-white"
							style="text-decoration: none;" target="_blank">
							<i class="fas fa-home mr-3">
								Instituto Federal de Brasília - Campus Taguatinga <br>
								QNM 40, Área Especial 01, às margens da BR 070. Taguatinga/DF.
							</i>
						</a>
					</p>
                </div>        
            </div>
        </div>
    </footer>

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
        write_main(solutions_info_dict, f_out)
        write_footer(f_out)
