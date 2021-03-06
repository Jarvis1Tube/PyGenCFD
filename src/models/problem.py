import dataclasses
from typing import List, Optional

import sympy

import models.coordinate_systems as cs


@dataclasses.dataclass
class GridParams:
    x_step: float
    t_step: float


@dataclasses.dataclass
class ProblemStrs:
    equation: str
    L_boundary_conditions: List[str]
    R_boundary_conditions: List[str]

    coordinate_system: cs.CoordinateSystem

    initial_condition: Optional[str] = None
    analytical_solution: Optional[str] = None

    def __post_init__(self):
        if len(self.L_boundary_conditions) != len(self.R_boundary_conditions):
            raise ValueError("Boundary conditions lists must be the same size")

        if (
            not self.coordinate_system.is_stationary
            and self.coordinate_system.initial_condition is None
        ):
            raise ValueError(
                "For non stationary problem initial conditions must be set"
            )


class ProblemSympy:
    equation: sympy.Equality
    L_boundary_conditions: List[sympy.Equality]
    R_boundary_conditions: List[sympy.Equality]
    initial_condition: Optional[sympy.Equality]
    analytical_solution: Optional[sympy.core.expr.Expr]

    coordinate_system: cs.CoordinateSystem
    grid_params: GridParams

    def __init__(self, problem_strs: ProblemStrs, grid_params: GridParams):
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

        self.coordinate_system = problem_strs.coordinate_system
        self.grid_params = grid_params


StrsModelsFromLabs = {
    "1.1": ProblemStrs(
        equation="Eq(Derivative(u(x,t), t), Derivative(u(x,t), x, x))",
        L_boundary_conditions=["Eq(u(0,t), 0)"],
        R_boundary_conditions=["Eq(u(pi,t), 1)"],
        initial_condition="Eq(u(x,0), x/pi + 4*sin(3*x))",
        analytical_solution="x/pi + 4*E**(-9*t)*sin(3*x)",
        coordinate_system=cs.CoordinateSystem.Xt,
    ),
    "2.1": ProblemStrs(
        equation="Eq(Derivative(u(x,t), t), Derivative(u(x,t), x, x) - u(x,t) + 1)",
        L_boundary_conditions=["Eq(Derivative(u(0,t), x) - u(0,t), -1)"],
        R_boundary_conditions=["Eq(Derivative(u(1,t),x), E**(-t))"],
        initial_condition="Eq(u(x,0), x + 2)",
        analytical_solution="E**(-t)*(x+1) + 1",
        coordinate_system=cs.CoordinateSystem.Xt,
    ),
    "2.3": ProblemStrs(
        equation="Eq(Derivative(u(x,t), t), Derivative(u(x,t), x, x) - 2*u(x,t) -2*x - 2)",
        L_boundary_conditions=["Eq(Derivative(u(0,t), x) - u(0,t), 0)"],
        R_boundary_conditions=["Eq(Derivative(u(1,t),x), E**(1-t) - 1)"],
        initial_condition="Eq(u(x,0), E**x -x - 1)",
        analytical_solution="E**(x-t) - x - 1",
        coordinate_system=cs.CoordinateSystem.Xt,
    ),
    "2.6": ProblemStrs(
        equation="Eq(Derivative(u(x,t), t), Derivative(u(x,t), x, x) + u(x,t) + cos(t)*sin(x))",
        L_boundary_conditions=["Eq(u(0,t), 0)"],
        R_boundary_conditions=["Eq(Derivative(u(pi,t),x) + u(pi,t), -sin(t))"],
        initial_condition="Eq(u(x,0), 0)",
        analytical_solution="sin(t)*sin(x)",
        coordinate_system=cs.CoordinateSystem.Xt,
    ),
    "5.8": ProblemStrs(
        equation="Eq(Derivative(u(x,y,t), t), Derivative(u(x,y,t), x, x)"
        " + Derivative(Derivative(u(x,y,t), y)*y*sin(x), y)"
        " + u(x, y, t) - y)",
        L_boundary_conditions=[
            "Eq(Derivative(u(0,y,t), x) - u(0, y, t)**4, t - y**4)",
            "Eq(Derivative(u(x,0,t), y), 1)",
        ],
        R_boundary_conditions=["Eq(u(pi,y,t),0)", "Eq(Derivative(u(x,1,t), y), 1)"],
        initial_condition="Eq(u(x,y, 0), y)",
        analytical_solution="t*sin(x) + y",
        coordinate_system=cs.CoordinateSystem.XYt,
    ),
}
