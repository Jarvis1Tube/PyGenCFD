from models import coordinate_systems as cs
from models import problem

from sympy.utilities.codegen import codegen


def coords_to_vars(coordinate_system: cs.CoordinateSystem):
    return list(coordinate_system.value.lower())


def gen_template(problem_sympy: problem.ProblemSympy):
    arguments_order = coords_to_vars(problem_sympy.coordinate_system)

    with open("./fortran_template.f90", "r") as f:
        template = f.read()

    # fortran_analytical_solution
    [(f_name, f_code), (f_name, f_header)] = codegen(
        ("FAN", problem_sympy.analytical_solution),
        language="F95",
        header=False,
        argument_sequence=arguments_order,
    )
    f_code.replace("\n", "\n" + " " * 40)
    template = template.format(analytical_function=f_code)
    with open("./generated/fortran_solver.f90", "w") as fw:
        fw.write(template)
