# pylint: disable=all

from typing import (
    overload,
    Any,
    Callable,
    Generic,
    Optional,
    ParamSpec,
    Type,
    TypeVar,
    Union,
)

T = TypeVar("T")  # generic type
P = ParamSpec("P")  # generic param
C = TypeVar("C")  # generic class instance type

Decorated = Callable[[Callable[P, T]], Callable[P, T]]

@overload
def rate_limit(interval: Union[int, float]) -> Decorated: ...
@overload
def rate_limit(calls: int, period: Union[int, float]) -> Decorated: ...
@overload
def cache(*, type_specific: bool = False) -> Decorated: ...
@overload
def cache(maxsize: int, *, type_specific: bool = False) -> Decorated: ...

class lazy_property(Generic[C, T]):
    def __init__(self, func: Callable[[C], T]) -> None: ...
    def __get__(self, instance: C, owner: Any) -> T: ...

def deprecated(
    reason: str,
    version: Optional[Union[int, float, str]] = None,
    date: Optional[str] = None,
) -> Decorated: ...
def decorate_all_methods(
    decorator: Callable[[Callable[P, T]], Callable[P, T]], *args: Any, **kwargs: Any
) -> Callable[[Type[T]], Type[T]]: ...
def immutable(cls: Type[T]) -> Callable[[Type[T]], Type[T]]: ...
def singleton(cls: Type[T]) -> Callable[[Type[T]], Type[T]]: ...
def type_checker(func: Callable[P, T]) -> Callable[P, T]: ...
