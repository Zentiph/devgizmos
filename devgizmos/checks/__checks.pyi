# pylint: disable=all

from typing import Any, Dict, Iterable, Sequence, Sized, Type

def verify_types(
    value: Any, /, *types: Type, raise_exc: bool = True, exc_msg: str = ""
) -> bool: ...
def verify_values(
    value: Any, /, *values: Any, raise_exc: bool = True, exc_msg: str = ""
) -> bool: ...
def verify_in_range(
    value: Any,
    seq: Sequence,
    /,
    start: int = -1,
    end: int = -1,
    *,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def verify_truthy(*values: Any, raise_exc: bool = True, exc_msg: str = "") -> bool: ...
def verify_not_none(
    *values: Any, raise_exc: bool = True, exc_msg: str = ""
) -> bool: ...
def verify_length(
    value: Sized,
    /,
    min_length: int,
    max_length: int = -1,
    *,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def verify_regexes(
    string: str, *regexes: str, raise_exc: bool = True, exc_msg: str = ""
) -> bool: ...
def verify_keys_in_dict(
    dictionary: Dict[Any, Any],
    *keys: Any,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def verify_contains(
    iterable: Iterable, *items: Any, raise_exc: bool = True, exc_msg: str = ""
) -> bool: ...
def verify_subclasses(
    superclass: Type, *subclasses: Type, raise_exc: bool = True, exc_msg: str = ""
) -> bool: ...
def verify_callables(
    *objs: object, raise_exc: bool = True, exc_msg: str = ""
) -> bool: ...
