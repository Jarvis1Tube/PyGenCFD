import os

import jinja2

from models import codegen_problem, problem


def gen_template(problem_sympy: problem.ProblemSympy):
    problem_codegen = codegen_problem.ProblemCodeGen(problem_sympy)

    with open("src/templates/1dimension.jinja2", "r") as f:
        template = f.read()
    jinja_template = jinja2.Template(template)

    template = jinja_template.render(code_model=problem_codegen)

    with open("src/generated/fortran_solver.f95", "w") as fw:
        fw.write(template)
    os.system("fprettify src/generated/fortran_solver.f95")
