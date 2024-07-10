# pylint: disable=all

import logging
from typing import ContextManager, Literal, Optional, Union

LoggingLevel = int

def seed(
    a: Union[int, float, str, bytes, bytearray, None], version: Literal[1, 2] = 2
) -> ContextManager[None]: ...
def timer(
    unit: Literal["ns", "us", "ms", "s"] = "ns",
    precision: int = 3,
    *,
    fmt: str = "",
    logger: Optional[logging.Logger] = None,
    level: LoggingLevel = logging.INFO,
) -> ContextManager[None]: ...
def tempdir() -> ContextManager[str]: ...
def tempfile() -> ContextManager[str]: ...
def change_dir(path: str) -> ContextManager[None]: ...
def set_env(**env_vars: dict) -> ContextManager[None]: ...
