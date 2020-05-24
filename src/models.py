import dataclasses
import enum
from typing import List, Optional


@enum.unique
class CoordinateSystem(enum.Enum):
    X = "X"
    Xt = "Xt"
    XY = "XY"
    XYt = "XYt"

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
