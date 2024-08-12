# pylint: disable=all

from typing import (
    overload,
    Callable,
    Optional,
    ParamSpec,
    TypeVar,
    Union,
)

T = TypeVar("T")  # generic type
P = ParamSpec("P")  # generic param

Decorated = Callable[[Callable[P, T]], Callable[P, T]]
Decorator = Decorated

@overload
def rate_limit(interval: Union[int, float]) -> Decorated: ...
@overload
def rate_limit(calls: int, period: Union[int, float]) -> Decorated: ...
@overload
def cache(*, type_specific: bool = False) -> Decorated: ...
@overload
def cache(maxsize: int, /, *, type_specific: bool = False) -> Decorated: ...
def deprecated(
    reason: str,
    version: Optional[Union[int, float, str]] = None,
    date: Optional[str] = None,
) -> Decorated: ...
def enforce_type_hints(func: Callable[P, T]) -> Callable[P, T]: ...
