"""
types.__types
=============
Module containing custom types.
"""

from typing import Any, Callable, Dict, TypeVar, Union


Num = Union[int, float]
"""An int or float value."""
NumOrComplex = Union[int, float, complex]
"""An int, float, or complex value."""
Function = Callable[..., Any]
"""A callable with any arguments and any return type."""
JsonData = Dict[Any, Any]
"""A dictionary of any keys and values."""

F = TypeVar("F", bound=Callable[..., Any])
Decorator = Callable[[F], F]
"""Standard decorator type."""
