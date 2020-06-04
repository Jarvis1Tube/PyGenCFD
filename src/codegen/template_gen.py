import os
from typing import List

import jinja2
import sympy
from sympy.abc import t
from sympy.utilities.codegen import codegen

from models import coordinate_systems as cs
from models import problem


def coords_to_vars(coordinate_system: cs.CoordinateSystem) -> List[sympy.Symbol]:
    return sympy.symbols(list(coordinate_system.value.lower()))


# TODO: mode codegen logic to model
def gen_template(problem_sympy: problem.ProblemSympy):
    arguments_order = coords_to_vars(problem_sympy.coordinate_system)
    initial_cond_args = [
        var for var in coords_to_vars(problem_sympy.coordinate_system) if var != t
    ]

    with open("templates/1dimension.jinja2", "r") as f:
        template = f.read()
    jinja_template = jinja2.Template(template)

    # fortran analytical_solution
    [(f_name, f_code), (f_name, f_header)] = codegen(
        ("FAN", problem_sympy.analytical_solution),
        language="F95",
        header=False,
        argument_sequence=arguments_order,
    )
    analytical_solution_code = "! generated !\n" + f_code

    # fortran analytical_solution
    [(f_name, f_code), (f_name, f_header)] = codegen(
        ("INITIAL_CONDITION", problem_sympy.initial_condition.rhs),
        language="F95",
        header=False,
        argument_sequence=initial_cond_args,
    )
    initial_condition_code = "! generated !\n" + f_code

    code_model = problem.ProblemStrs(
        equation=str(problem_sympy.equation),
        initial_condition=initial_condition_code,
        analytical_solution=analytical_solution_code,
        L_boundary_conditions=[
            str(cond) for cond in problem_sympy.L_boundary_conditions
        ],
        R_boundary_conditions=[
            str(cond) for cond in problem_sympy.R_boundary_conditions
        ],
        coordinate_system=problem_sympy.coordinate_system,
        dimensions_count=problem_sympy.dimensions_count,
        is_stationary=problem_sympy.is_stationary,
    )

    template = jinja_template.render(code_model=code_model)
    with open("generated/fortran_solver.f95", "w") as fw:
        fw.write(template)
    os.system("fprettify generated/fortran_solver.f95")
