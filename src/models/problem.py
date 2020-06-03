import dataclasses
from typing import List, Optional

import models.coordinate_systems as cs

import sympy


@dataclasses.dataclass
class ProblemStrs:
    equation: str
    L_boundary_conditions: List[str]
    R_boundary_conditions: List[str]

    dimensions_count: int
    is_stationary: bool
    coordinate_system: cs.CoordinateSystem

    initial_condition: Optional[str] = None
    analytical_solution: Optional[str] = None

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
    analytical_solution: Optional[sympy.core.expr.Expr]

    dimensions_count: int
    is_stationary: bool
    coordinate_system: cs.CoordinateSystem

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

        if problem_strs.analytical_solution:
            self.analytical_solution = sympy.parse_expr(
                problem_strs.analytical_solution
            )

        self.dimensions_count = problem_strs.dimensions_count
        self.is_stationary = problem_strs.is_stationary
        self.coordinate_system = problem_strs.coordinate_system


StrsModelsFromLabs = {
    "1.1": ProblemStrs(
        equation="Eq(Derivative(u(x,t), t), Derivative(u(x,t), x, x))",
        L_boundary_conditions=["Eq(u(0,t), 0)"],
        R_boundary_conditions=["Eq(u(pi,t), 1)"],
        initial_condition="Eq(u(x,0), x/pi + 4*sin(3*x))",
        analytical_solution="Eq(u(x,0), x/pi + 4*e**(-9*t)*sin(3*x))",
        dimensions_count=1,
        is_stationary=False,
        coordinate_system=cs.CoordinateSystem.Xt,
    ),
    "5.8": ProblemStrs(
        equation="Eq(Derivative(u(x,y,t), t), Derivative(u(x,y,t), x, x)"
        " + Derivative(Derivative(u(x,y,t), y)*y*sin(x), y)"
        " + u(x, y, t) - y)",
        L_boundary_conditions=[
            "Eq(Derivative(u(0,y,t), x), u(0, y, t)**4 + t - y**4)",
            "Eq(Derivative(u(x,0,t), y), 1)",
        ],
        R_boundary_conditions=["Eq(u(pi,y,t),0)", "Eq(Derivative(u(x,1,t), y), 1)"],
        initial_condition="Eq(u(x,y, 0), y)",
        analytical_solution="t*sin(x) + y",
        dimensions_count=2,
        is_stationary=False,
        coordinate_system=cs.CoordinateSystem.XYt,
    ),
}
