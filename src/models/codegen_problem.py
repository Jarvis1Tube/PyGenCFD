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
        self._set_axis_and_point(cond_eq, coords)
        self._set_codegen_function_name()
        self._set_function_code(cond_eq, coords)

    def _set_axis_and_point(self, cond_eq: sympy.Equality, coords: cs.CoordinateSystem):
        coord_vars = coords.axises()
        self.axis, self.axis_point = None, None

        for i, arg in enumerate(cond_eq.lhs.args):
            if arg.is_constant():
                self.axis = coord_vars[i]
                # представление в Double в Fortran: 1d0
                self.axis_point = f"{arg.evalf()}d0"

        if self.axis is None:
            raise ValueError(
                "Bondary condition cannot be parsed"
                "Probably you did not specified U arguments or"
                "there is no constant in arguments"
            )

    def _set_codegen_function_name(self):
        if self.axis == sympy.Symbol("t"):
            self.func_name = "INITIAL_CONDITION"
        else:
            self.func_name = (
                f"{self.bound_side.name}_{str(self.axis).upper()}_CONDITION"
            )

    def _set_function_code(self, cond_eq: sympy.Equality, coords: cs.CoordinateSystem):
        [(file_name, func_code), (header_name, header_code)] = codegen(
            (self.func_name, cond_eq.rhs),  # .evalf() to double
            language="F95",
            header=False,
            argument_sequence=[var for var in coords.axises() if var != self.axis],
        )
        self.func_code = "! generated !\n" + func_code


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
        self._equation_processing(sympy_problem)
        self._set_analytical_solution(sympy_problem)

    def _set_analytical_solution(self, sympy_problem: problem.ProblemSympy):
        # fortran analytical_solution
        analytical_formula = (
            sympy_problem.analytical_solution
            if sympy_problem.analytical_solution
            else sympy.nan
        )

        [(file_name, func_code), (header_name, header_code)] = codegen(
            ("FAN", analytical_formula),  # .evalf() to double
            language="F95",
            header=False,
            argument_sequence=self.coordinate_system.axises(),
        )
        self.analytical_solution = "! generated !\n" + func_code

    def _equation_processing(self, sympy_problem: problem.ProblemSympy):
        equation = sympy_problem.equation
        self.Gam = {
            str(du.variables[0]): equation.rhs.coeff(
                du
            ).evalf()  # TODO: support as function
            for du in equation.rhs.find(sympy.Derivative)
        }

        if self.coordinate_system.is_stationary():
            try:
                self.Rho = [
                    equation.rhs.coeff(du).evalf()
                    for du in equation.lhs.find(sympy.Derivative)
                    if t in du.variables
                ][0]
            except IndexError:
                raise ValueError("No derivative by time in equation")
