# pylint: disable=all

from typing import Any, Dict, Iterable, Optional, Sequence, Sized, Tuple, Type, Union

def check_type(
    value: Any,
    *types: Type,
    optional: bool = False,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_value(
    value: Any,
    *values: Any,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_in_range(
    value: Any,
    seq: Sequence,
    /,
    start: int = 0,
    end: int = -1,
    *,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_in_bounds(
    value: Union[int, float],
    lower: Optional[Union[int, float]],
    upper: Optional[Union[int, float]],
    *,
    inclusive: bool = True,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_regex(
    regex: str, *strings: str, raise_exc: bool = True, exc_msg: str = ""
) -> bool: ...
def check_keys_in_dict(
    dictionary: Dict[Any, Any],
    *keys: Any,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_contains(
    iterable: Iterable,
    *items: Any,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_subclass(
    superclass: Type,
    *subclasses: Type,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_callable(
    *objs: object,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_no_duplicates(
    *objs: object,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
