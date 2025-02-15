from enum import auto
from typing import List

import param
from param import Number
from strenum import StrEnum
import holoviews as hv
from bencher.utils import hash_sha1

# from bencher.variables.parametrised_sweep import ParametrizedSweep


class OptDir(StrEnum):
    minimize = auto()
    maximize = auto()
    none = auto()  # If none this var will not appear in pareto plots


class ResultVar(Number):
    """A class to represent result variables and the desired optimisation direction"""

    __slots__ = ["units", "direction"]

    def __init__(self, units="ul", direction: OptDir = OptDir.minimize, **params):
        Number.__init__(self, **params)
        assert isinstance(units, str)
        self.units = units
        self.default = 0  # json is terrible and does not support nan values
        self.direction = direction

    def as_dim(self) -> hv.Dimension:
        return hv.Dimension((self.name, self.name), unit=self.units)

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_sha1((self.units, self.direction))


class ResultVec(param.List):
    """A class to represent fixed size vector result variable"""

    __slots__ = ["units", "direction", "size"]

    def __init__(self, size, units="ul", direction: OptDir = OptDir.minimize, **params):
        param.List.__init__(self, **params)
        self.units = units
        self.default = 0  # json is terrible and does not support nan values
        self.direction = direction
        self.size = size

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_sha1((self.units, self.direction))

    def index_name(self, idx: int) -> str:
        """given the index of the vector, return the column name that

        Args:
            idx (int): index of the result vector

        Returns:
            str: column name of the vector for the xarray dataset
        """

        mapping = ["x", "y", "z"]
        if idx < 3:
            index = mapping[idx]
        else:
            index = idx
        return f"{self.name}_{index}"

    def index_names(self) -> List[str]:
        """Returns a list of all the xarray column names for the result vector

        Returns:
            list[str]: column names
        """
        return [self.index_name(i) for i in range(self.size)]


class ResultHmap(param.Parameter):
    """A class to represent a holomap return type"""

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_sha1(self)


def curve(x_vals: List[float], y_vals: List[float], x_name: str, y_name: str, **kwargs) -> hv.Curve:
    return hv.Curve(zip(x_vals, y_vals), kdims=[x_name], vdims=[y_name], label=y_name, **kwargs)


class PathResult(param.Filename):
    __slots__ = ["units"]

    def __init__(self, default=None, units="path", **params):
        super().__init__(default=default, check_exists=False, **params)
        self.units = units

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_sha1(self)


class ResultVideo(PathResult):
    def __init__(self, default=None, units="video", **params):
        super().__init__(default=default, units=units, **params)


class ResultImage(PathResult):
    def __init__(self, default=None, units="image", **params):
        super().__init__(default=default, units=units, **params)


class ResultString(param.String):
    __slots__ = ["units"]

    def __init__(self, default=None, units="str", **params):
        super().__init__(default=default, **params)
        self.units = units

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_sha1(self)


class ResultContainer(param.Parameter):
    __slots__ = ["units"]

    def __init__(self, default=None, units="container", **params):
        super().__init__(default=default, **params)
        self.units = units

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_sha1(self)


class ResultReference(param.Parameter):
    __slots__ = ["units", "obj"]

    def __init__(self, obj=None, default=None, units="container", **params):
        super().__init__(default=default, **params)
        self.units = units
        self.obj = obj

    def hash_persistent(self) -> str:
        """A hash function that avoids the PYTHONHASHSEED 'feature' which returns a different hash value each time the program is run"""
        return hash_sha1(self)


PANEL_TYPES = (ResultImage, ResultContainer, ResultString, ResultReference)
