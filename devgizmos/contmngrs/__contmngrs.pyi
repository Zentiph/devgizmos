# pylint: disable=all

import cProfile
import logging
from abc import abstractmethod
from typing import (
    Callable,
    ContextManager,
    Protocol,
    Literal,
    Optional,
    Type,
    Union,
    Any,
    Tuple,
)
from threading import Lock, Thread
from concurrent.futures import Future

Num = Union[int, float]

class _HasBoolAttr(Protocol):
    @abstractmethod
    def __bool__(self) -> bool:
        pass

ConvertibleToBool = _HasBoolAttr

LoggingLevel = int
BackoffFunc = Callable[[Num, int], Num]

def seed(
    a: Union[int, float, str, bytes, bytearray, None], version: Literal[1, 2] = 2
) -> ContextManager[None]: ...
def tempdir() -> ContextManager[str]: ...
def tempfile() -> ContextManager[str]: ...
def change_dir(path: str) -> ContextManager[None]: ...
def change_env(**env_vars: dict) -> ContextManager[None]: ...
def suppress(*exceptions: Type[BaseException]) -> ContextManager[None]: ...
def retry_on(
    exc: Type[BaseException],
    /,
    *,
    max_attempts: int = 3,
    delay: Union[int, float] = 1,
    backoff_strategy: Optional[BackoffFunc] = None,
): ...
def profile(output_file: Optional[str] = None) -> ContextManager[cProfile.Profile]: ...
def future_manager(future: Future) -> ContextManager[None]: ...
