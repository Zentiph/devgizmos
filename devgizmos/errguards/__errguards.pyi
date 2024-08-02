# pylint: disable=all

from typing import Any, Dict, Iterable, Optional, Sequence, Sized, Tuple, Type, Union

def is_instance_of(
    value: Any,
    *types: Type,
    optional: bool = False,
) -> bool: ...
def ensure_instance_of(
    value: Any, *types: Type, optional: bool = False, msg: str = ""
) -> None: ...
def is_value(
    value: Any,
    *values: Any,
) -> bool: ...
def ensure_value(value: Any, *values: Any, msg: str = "") -> None: ...
def is_in_range(
    value: Any,
    seq: Sequence,
    /,
    start: int = 0,
    end: int = -1,
) -> bool: ...
def ensure_in_range(
    value: Any,
    seq: Sequence,
    /,
    start: int = 0,
    end: int = -1,
    *,
    msg: str = "",
) -> None: ...
def is_in_bounds(
    value: Union[int, float],
    lower: Optional[Union[int, float]],
    upper: Optional[Union[int, float]],
    *,
    inclusive: bool = True,
) -> bool: ...
def ensure_in_bounds(
    value: Union[int, float],
    lower: Optional[Union[int, float]],
    upper: Optional[Union[int, float]],
    *,
    inclusive: bool = True,
    msg: str = "",
) -> None: ...
def matches_regex(regex: str, *strings: str) -> bool: ...
def ensure_matches_regex(regex: str, *strings: str, msg: str = "") -> None: ...
def dict_has_keys(
    dictionary: Dict[Any, Any],
    *keys: Any,
) -> bool: ...
def ensure_dict_has_keys(
    dictionary: Dict[Any, Any], *keys: Any, msg: str = ""
) -> None: ...
def contains(
    iterable: Iterable,
    *items: Any,
) -> bool: ...
def ensure_contains(iterable: Iterable, *items: Any, msg: str = "") -> None: ...
def is_superclass_of(
    superclass: Type,
    *subclasses: Type,
) -> bool: ...
def ensure_superclass_of(
    superclass: Type,
    *subclasses: Type,
    msg: str = "",
) -> None: ...
def ensure_callable(*objs: object, msg: str = "") -> None: ...
def contains_duplicates(*objs: Iterable) -> bool: ...
def ensure_no_duplicates(*objs: Iterable, msg: str = "") -> None: ...
def convertible_to(value: Any, *objs: Type, **kwargs: Any) -> bool: ...
def ensure_convertible_to(
    value: Any, *objs: Type, msg: str = "", **kwargs: Any
) -> None: ...
