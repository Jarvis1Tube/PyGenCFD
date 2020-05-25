import dataclasses
import enum
from typing import List, Optional


@enum.unique
class CoordinateSystem(enum.Enum):
    X = "X"
    Xt = "Xt"
    XY = "XY"
    XYt = "XYt"
    RFi = "\u03A1\u03A6"
    RFit = "\u03A1\u03A6t"

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


@dataclasses.dataclass
class ProblemModel:
    equation: str
    L_boundary_conditions: List[str]
    R_boundary_conditions: List[str]
    initial_condition: Optional[str]

    dimensions_count: int
    is_stationary: bool
    coordinate_system: CoordinateSystem

    def __post__init__(self):
        if len(self.L_boundary_conditions) != len(self.R_boundary_conditions):
            return ValueError("Boundary conditions lists must be the same size")
