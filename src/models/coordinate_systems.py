import enum
from typing import List

import sympy
from sympy.abc import t as time_axis


@enum.unique
class CoordinateSystem(enum.Enum):
    # X = "X"  # not works for a while
    Xt = "Xt"
    # XY = "XY"  # not works for a while
    XYt = "XYt"

    # RFi = "\u03A1\u03A6" # not works for a while
    # RFit = "\u03A1\u03A6t" #

    @classmethod
    def with_time(cls) -> List["CoordinateSystem"]:
        return [item for item in cls if "t" not in item.value]

    @classmethod
    def no_time(cls) -> List["CoordinateSystem"]:
        return [item for item in cls if "t" in item.value]

    @classmethod
    def filtered(
        cls, dimensions_count: int, is_stationary: bool
    ) -> List["CoordinateSystem"]:
        def check_time(val: CoordinateSystem):
            if is_stationary:
                return "t" not in val.value
            else:
                return "t" in val.value

        def check_dimensions(val: CoordinateSystem):
            return len(val.value.replace("t", "")) == dimensions_count

        return [item for item in cls if check_time(item) and check_dimensions(item)]

    @classmethod
    def from_str(cls, str_value: str) -> "CoordinateSystem":
        coordinate_systems: List[CoordinateSystem] = [
            item for item in cls if item.value == str_value
        ]
        if len(coordinate_systems) == 0:
            raise ValueError(f"{str_value} is not CoordinateSystem")
        return coordinate_systems[0]

    def axises(self) -> List[sympy.Symbol]:
        return sympy.symbols(list(self.value.lower()))

    def is_stationary(self) -> bool:
        return any([axis == time_axis for axis in self.axises()])

    def dimensions_count(self) -> int:
        return len([axis for axis in self.axises() if axis != time_axis])
