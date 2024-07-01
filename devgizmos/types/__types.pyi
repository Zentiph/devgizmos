# pylint: disable=all

from typing import Any, Callable, Dict, TypeAlias, TypeVar, Union

Num: TypeAlias = Union[int, float]
NumOrComplex: TypeAlias = Union[int, float, complex]
Function: TypeAlias = Callable[..., Any]
JsonData: TypeAlias = Dict[Any, Any]

F = TypeVar("F", bound=Callable[..., Any])
Decorator: TypeAlias = Callable[[F], F]
