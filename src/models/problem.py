import dataclasses
from typing import List, Optional

from models.coordinate_systems import CoordinateSystem

import sympy


@dataclasses.dataclass
class ProblemStrs:
    equation: str
    L_boundary_conditions: List[str]
    R_boundary_conditions: List[str]

    dimensions_count: int
    is_stationary: bool
    coordinate_system: CoordinateSystem

    initial_condition: Optional[str] = None

    def __post_init__(self):
        if len(self.L_boundary_conditions) != len(self.R_boundary_conditions):
            raise ValueError("Boundary conditions lists must be the same size")

        if self.is_stationary and self.initial_condition is None:
            raise ValueError(
                "For non stationary problem initial conditions must be set"
            )


class ProblemSympy:
    equation: sympy.Equality
    L_boundary_conditions: List[sympy.Equality]
    R_boundary_conditions: List[sympy.Equality]
    initial_condition: Optional[sympy.Equality]

    dimensions_count: int
    is_stationary: bool
    coordinate_system: CoordinateSystem

    def __init__(self, problem_strs: ProblemStrs):
        self.equation = sympy.parse_expr(problem_strs.equation)
        self.L_boundary_conditions = [
            sympy.parse_expr(bound_condition)
            for bound_condition in problem_strs.L_boundary_conditions
        ]
        self.R_boundary_conditions = [
            sympy.parse_expr(bound_condition)
            for bound_condition in problem_strs.R_boundary_conditions
        ]

        if problem_strs.initial_condition:
            self.initial_condition = sympy.parse_expr(problem_strs.initial_condition)

        self.dimensions_count = problem_strs.dimensions_count
        self.is_stationary = problem_strs.is_stationary
        self.coordinate_system = problem_strs.coordinate_system
