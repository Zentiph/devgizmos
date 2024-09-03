"""
errguards
---------
Package containing error guarding tools, such as type/value checkers.
"""

__all__ = [
    "contains",
    "contains_duplicates",
    "convertible_to",
    "dict_has_keys",
    "ensure_callable",
    "ensure_contains",
    "ensure_convertible_to",
    "ensure_dict_has_keys",
    "ensure_in_bounds",
    "ensure_in_range",
    "ensure_instance_of",
    "ensure_no_duplicates",
    "ensure_superclass_of",
    "ensure_value",
    "is_in_bounds",
    "is_in_range",
    "is_instance_of",
    "is_superclass_of",
    "is_value",
    "Timeout",
    "UnsupportedOSError",
]

from .__errguards import (
    contains,
    contains_duplicates,
    convertible_to,
    dict_has_keys,
    ensure_callable,
    ensure_contains,
    ensure_convertible_to,
    ensure_dict_has_keys,
    ensure_in_bounds,
    ensure_in_range,
    ensure_instance_of,
    ensure_no_duplicates,
    ensure_superclass_of,
    ensure_value,
    is_in_bounds,
    is_in_range,
    is_instance_of,
    is_superclass_of,
    is_value,
)
from .__timeout import Timeout, UnsupportedOSError
