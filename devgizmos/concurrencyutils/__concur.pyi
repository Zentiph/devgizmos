# pylint: disable=all

from threading import Lock, Thread, Barrier
from typing import (
    TypeVar,
    Callable,
    Any,
    Union,
    Tuple,
    Type,
    ContextManager,
    Iterable,
    List,
)

F = TypeVar("F", bound=Callable[..., Any])

Decorator = Callable[[F], F]

DecoratedFunc = Decorator
DecoratedCls = Callable[[Type], Type]

def thread_manager(
    target: Callable[..., Any], *args: Tuple[Any, ...], **kwargs: Any
) -> ContextManager[Thread]: ...
def lock_handler(lock: Lock) -> ContextManager[None]: ...
def barrier_sync(barrier: Barrier) -> ContextManager[None]: ...

class PeriodicTask:
    def __init__(
        self,
        interval: Union[int, float],
        func: F,
        *args: Tuple[Any, ...],
        **kwargs: Any,
    ) -> None: ...
    def _target(self) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...

def periodic_running_task(interval: Union[int, float]) -> DecoratedFunc: ...
def batch_processer(
    data: Iterable[Any], workers: int, process_function: F
) -> List[Any]: ...

class QueueProcessor:
    def __init__(self, num_workers: int, process_item: F) -> None: ...
    def _consumer(self) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def add_task(self, item: Any) -> None: ...
