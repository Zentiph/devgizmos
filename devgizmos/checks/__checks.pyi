# pylint: disable=all

from typing import Any, Dict, Iterable, Optional, Sequence, Sized, Tuple, Type, Union

def check_type(
    value: Any,
    /,
    types_or_tuple: Union[Type, Tuple[Type, ...]],
    optional: bool = False,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_value(
    value: Any,
    /,
    value_or_tuple: Union[Any, Tuple[Any, ...]],
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_in_range(
    value: Any,
    seq: Sequence,
    /,
    start: Optional[int] = None,
    end: Optional[int] = None,
    *,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_in_bounds(
    value: Union[int, float],
    lower: Optional[Union[int, float]],
    upper: Optional[Union[int, float]],
    /,
    inclusive: bool = True,
    *,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_truthy(value: Any, raise_exc: bool = True, exc_msg: str = "") -> bool: ...
def check_not_none(value: Any, raise_exc: bool = True, exc_msg: str = "") -> bool: ...
def check_length(
    value: Sized,
    /,
    min_length: int,
    max_length: int = -1,
    *,
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_regex(
    string: str, regex: str, raise_exc: bool = True, exc_msg: str = ""
) -> bool: ...
def check_key_in_dict(
    dictionary: Dict[Any, Any],
    key_or_tuple: Union[Any, Tuple[Any, ...]],
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_contains(
    iterable: Iterable,
    item_or_tuple: Union[Any, Tuple[Any, ...]],
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_subclass(
    superclass: Type,
    subclass_or_tuple: Union[Type, Tuple[Type, ...]],
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
def check_callable(
    obj_or_tuple: Union[object, Tuple[object, ...]],
    raise_exc: bool = True,
    exc_msg: str = "",
) -> bool: ...
