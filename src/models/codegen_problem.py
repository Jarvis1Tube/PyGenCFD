import enum
from typing import List, Optional

import sympy
from sympy.abc import t
from sympy.utilities.codegen import codegen

from models import coordinate_systems as cs
from models import problem


class BoundSide(enum.Enum):
    L = "L"
    R = "R"


class ConditionKind(enum.Enum):
    First = "First"
    Second = "Second"
    Third = "Third"


class BoundaryCondition:
    def __init__(
        self,
        cond_eq: sympy.Equality,
        coords: cs.CoordinateSystem,
        bound_side: BoundSide,
    ):
        self.bound_side = bound_side
        self.kind = ConditionKind.First.name

        coord_vars = coords.to_vars()
        self.axis, self.axis_point = None, None
        for i, arg in enumerate(cond_eq.lhs.args):
            if arg.is_constant():
                self.axis = coord_vars[i]
                self.axis_point = f"{arg.evalf()}d0"

        if self.axis is None:
            raise ValueError(
                "Bondary condition cannot be parsed"
                "Probably you did not specified U arguments or"
                "there is no constant in arguments"
            )

        if self.axis == sympy.Symbol("t"):
            self.func_name = "INITIAL_CONDITION"
        else:
            self.func_name = (
                f"{self.bound_side.name}_{str(self.axis).upper()}_CONDITION"
            )

        [(f_name, f_code), (f_name, f_header)] = codegen(
            (self.func_name, cond_eq.rhs),  # .evalf() to double
            language="F95",
            header=False,
            argument_sequence=[var for var in coord_vars if var != self.axis],
        )
        self.func_code = "! generated !\n" + f_code


class ProblemCodeGen:
    # equation: str
    L_boundary_conditions: List[BoundaryCondition]
    R_boundary_conditions: List[BoundaryCondition]

    # dimensions_count: int
    # is_stationary: bool
    coordinate_system: cs.CoordinateSystem

    initial_condition: Optional[BoundaryCondition] = None
    analytical_solution: Optional[str] = None

    def __init__(self, sympy_problem: problem.ProblemSympy):
        self._equation_processing(sympy_problem)
        self.coordinate_system = sympy_problem.coordinate_system
        if sympy_problem.initial_condition is not None:
            self.initial_condition = BoundaryCondition(
                sympy_problem.initial_condition, self.coordinate_system, BoundSide.L
            )
        self.L_boundary_conditions = [
            BoundaryCondition(bound_cond_sympy, self.coordinate_system, BoundSide.L)
            for bound_cond_sympy in sympy_problem.L_boundary_conditions
        ]
        self.R_boundary_conditions = [
            BoundaryCondition(bound_cond_sympy, self.coordinate_system, BoundSide.R)
            for bound_cond_sympy in sympy_problem.R_boundary_conditions
        ]

        # fortran analytical_solution
        [(f_name, f_code), (f_name, f_header)] = codegen(
            ("FAN", sympy_problem.analytical_solution),  # .evalf() to double
            language="F95",
            header=False,
            argument_sequence=self.coordinate_system.to_vars(),
        )
        self.analytical_solution = "! generated !\n" + f_code

    def _equation_processing(self, sympy_problem: problem.ProblemSympy):
        equation = sympy_problem.equation
        self.Gam = {
            str(du.variables[0]): equation.rhs.coeff(du).evalf()
            for du in equation.rhs.find(sympy.Derivative)
        }
        if not sympy_problem.is_stationary:
            try:
                self.Rho = [
                    equation.rhs.coeff(du).evalf()
                    for du in equation.lhs.find(sympy.Derivative)
                    if t in du.variables
                ][0]
            except IndexError:
                raise ValueError("No derivative by time in equation")
