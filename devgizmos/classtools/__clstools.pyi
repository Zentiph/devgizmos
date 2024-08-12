# pylint: disable=all

from typing import Any, Callable, Dict, Generic, ParamSpec, Type, TypeVar, Union

T = TypeVar("T")  # generic type
P = ParamSpec("P")  # generic param
C = TypeVar("C")  # generic class instance type
Single = TypeVar("Single", bound="SingleMeta")

Decorated = Callable[[Callable[P, T]], Callable[P, T]]
Decorator = Decorated
DecoratedCls = Callable[[Type[T]], Type[T]]

class lazyproperty(Generic[C, T]):
    def __init__(self, func: Callable[[C], T]) -> None: ...
    def __get__(self, instance: C, owner: Any) -> T: ...

def decorate_all_methods(
    decorator: Union[Decorator, Callable[P, Decorated]],
    *args: Any,
    **kwargs: Any,
) -> DecoratedCls: ...
def ignore_method_decoration(method: Callable[P, T], /) -> Callable[P, T]: ...

class ImmutableInstance:
    def __init__(self, *args, **kwargs) -> None: ...
    def __setattr__(self, key, value) -> None: ...

def immutable(cls: Type[T]) -> ImmutableInstance: ...
def singleton(cls: Type[T]) -> DecoratedCls: ...

class SingleMeta(Generic[Single], type):
    __instances: Dict[Type[Single], Single] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Single: ...
