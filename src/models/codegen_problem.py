import dataclasses
import enum
from typing import *

import sympy
from sympy.abc import t
from sympy.codegen.ast import Element
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


def calc_in_point(expr, coords, use_U=False):
    subs_vars = {}
    for axis, index in zip(coords.axises(), coords.indexes()):
        if axis == t:
            continue
        axis_name = f"{str(axis).upper()}" + ("U" if use_U else "")
        subs_vars.update({axis: sympy.IndexedBase(axis_name)[index]})

    T = sympy.IndexedBase("T")[coords.indexes()]
    U_pattern = sympy.WildFunction("U_pattern", nargs=len(coords.axises()))
    return expr.subs({t: "TIME", U_pattern: T, **subs_vars})


def _to_fcode(expr):
    return sympy.fcode(sympy.simplify(expr).evalf()).replace("\n", "").replace("@", "")


class BoundaryCondition:
    def __init__(
            self,
            cond_eq: sympy.Equality,
            coords: cs.CoordinateSystem,
            bound_side: BoundSide,
    ):
        self.bound_side = bound_side
        self._set_axis_and_point(cond_eq, coords)
        self._set_codegen_function_name()
        self._set_function_code(cond_eq, coords)
        if self.kind != ConditionKind.First.name:
            self._bound_cond_2_3_kind(cond_eq, coords)

    def _set_axis_and_point(self, cond_eq: sympy.Equality, coords: cs.CoordinateSystem):
        coord_vars = coords.axises()
        self.axis, self.axis_point = None, None

        U = sympy.Function("u")
        u_entrances = list(cond_eq.find(U))
        if len(u_entrances) != 1:
            raise ValueError(
                "Cannot contain different args in U for derivative and u function"
            )

        a1 = sympy.Wild("a1", properties=[lambda x: x.is_constant])
        a2 = sympy.Wild("a2", properties=[lambda x: x.is_constant])
        u_pow = sympy.Wild("u_pow", properties=[lambda x: x.is_constant])
        axis = sympy.Wild("axis", properties=[lambda x: x.is_symbol])
        U_pattern = sympy.WildFunction("U_pattern", nargs=len(coords.axises()))

        res = cond_eq.lhs.match(
            a1 * U_pattern ** u_pow + a2 * sympy.Derivative(U_pattern, axis)
        )
        if res is None:
            raise ValueError(f"Cannot parse {cond_eq}")
        self.a1 = res[a1]
        self.a2 = res[a2]
        u_with_args = res[U_pattern]

        if self.a1 != 0 and self.a2 == 0:
            self.kind = ConditionKind.First.name
        elif self.a1 == 0 and self.a2 != 0:
            self.kind = ConditionKind.Second.name
        elif self.a1 != 0 and self.a2 != 0:
            self.kind = ConditionKind.Third.name
        else:
            raise ValueError(
                f"Left side of boundary condition: {cond_eq} does"
                "not contain u function"
            )

        for i, arg in enumerate(u_with_args.args):
            if arg.is_constant():
                self.axis = coord_vars[i]
                # представление в Double в Fortran: 1d0
                self.axis_point = f"{arg.evalf()}d0"
                break

        if self.axis is None:
            raise ValueError(
                "Bondary condition cannot be parsed"
                "Probably you did not specified U arguments or"
                "there is no constant in arguments"
            )

    def _bound_cond_2_3_kind(
            self, cond_eq: sympy.Equality, coords: cs.CoordinateSystem
    ):
        T_indexes = []
        axis_inx, axis_h_inx = None, None
        for axis, index in zip(coords.axises(), coords.indexes()):
            if axis != self.axis:
                T_indexes.append(index)
            else:
                axis_inx = 1 if self.bound_side == BoundSide.L else f"L1"
                axis_h_inx = 2 if self.bound_side == BoundSide.L else f"L2"
                T_indexes.append(axis_h_inx)
        integral_coef = 1 if self.bound_side == BoundSide.R else -1

        X = sympy.IndexedBase("X")
        T = sympy.IndexedBase("T")[T_indexes]
        cond_coef = 1 / (self.a2 - self.a1 * (X[axis_h_inx] - X[axis_inx]))

        aps = -self.a1 * cond_coef * integral_coef
        con = calc_in_point(cond_eq.rhs, coords) * cond_coef * integral_coef
        if -self.a1 * integral_coef > 0:
            con += aps * T
            aps = sympy.simplify(0)

        self.CON = _to_fcode(con)
        self.APS = _to_fcode(aps)
        self.T = _to_fcode(T - (aps * T + con) * (X[axis_h_inx] - X[axis_inx]))

    def _set_codegen_function_name(self):
        if self.axis == sympy.Symbol("t"):
            self.func_name = "INITIAL_CONDITION"
        else:
            self.func_name = (
                f"{self.bound_side.name}_{str(self.axis).upper()}_CONDITION"
            )

    # First kind
    def _set_function_code(self, cond_eq: sympy.Equality, coords: cs.CoordinateSystem):
        self.expression = _to_fcode(calc_in_point(cond_eq.rhs, coords))


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
        coords = sympy_problem.coordinate_system

        rc, kx, Sp_, Sc_ = sympy.symbols("rc,kx,Sp,Sc", cls=sympy.Wild)
        U_pattern = sympy.WildFunction("U_pattern", nargs=len(coords.axises()))
        x_var = sympy.Symbol("x")

        res = equation.match(
            sympy.Eq(
                rc * sympy.Derivative(U_pattern, t),
                kx * sympy.Derivative(U_pattern, x_var, x_var) + Sp_ * U_pattern + Sc_,
            )
        )

        self.Gam = {"x": res[kx]}
        self.Rho = res[rc]

        xu_i = sympy.Symbol("I")
        XU = sympy.IndexedBase("XU")
        DT = sympy.Symbol("DT")
        T = sympy.IndexedBase("T")[xu_i]

        Sc = sympy.integrate(res[Sc_], (x_var, XU[xu_i], XU[xu_i + 1]))
        Sc = sympy.integrate(Sc, (t, "TIME", "TIME+DT")) / DT

        Sp = sympy.integrate(res[Sp_], (x_var, XU[xu_i], XU[xu_i + 1]))
        Sp = sympy.integrate(Sp, (t, "TIME", "TIME+DT")) / DT

        if res[Sp_].is_constant() and res[Sp_] > 0:
            Sc += Sp * T
            Sp = sympy.simplify(0)

        self.Sp = _to_fcode(sympy.simplify(calc_in_point(Sp, coords, use_U=True)))
        self.Sc = _to_fcode(sympy.simplify(calc_in_point(Sc, coords, use_U=True)))
