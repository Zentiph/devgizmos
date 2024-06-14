# pylint: disable=all

from typing import Any, Dict, Iterable, Sequence, Sized, Type, Union

def check_types(
    value: Any,
    /,
    *types: Type,
    optional: bool = False,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_values(
    value: Any, /, *values: Any, raise_exc: bool = True, exc_msg: str = ""
) -> bool: ...
def check_in_range(
    value: Any,
    seq: Sequence,
    /,
    start: int = -1,
    end: int = -1,
    *,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_in_bounds(
    value: Union[int, float],
    lower: Union[int, float, None],
    upper: Union[int, float, None],
    /,
    inclusive: bool = True,
    *,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_truthy(*values: Any, raise_exc: bool = True, exc_msg: str = "") -> bool: ...
def check_not_none(*values: Any, raise_exc: bool = True, exc_msg: str = "") -> bool: ...
def check_length(
    value: Sized,
    /,
    min_length: int,
    max_length: int = -1,
    *,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_regexes(
    string: str, *regexes: str, raise_exc: bool = True, exc_msg: str = ""
) -> bool: ...
def check_keys_in_dict(
    dictionary: Dict[Any, Any],
    *keys: Any,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_contains(
    iterable: Iterable, *items: Any, raise_exc: bool = True, exc_msg: str = ""
) -> bool: ...
def check_subclasses(
    superclass: Type, *subclasses: Type, raise_exc: bool = True, exc_msg: str = ""
) -> bool: ...
def check_callables(
    *objs: object, raise_exc: bool = True, exc_msg: str = ""
) -> bool: ...
