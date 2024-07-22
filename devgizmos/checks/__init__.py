"""
checks
======
Module containing checker functions such as type checkers,
value checkers, range checkers, and more.

Built-in Utilizations
---------------------
This module utilizes the following functionality from built-in modules/packages:
re
- match
"""

from .__checks import (
    check_callable,
    check_contains,
    check_in_bounds,
    check_in_range,
    check_key_in_dict,
    check_length,
    check_no_duplicates,
    check_not_none,
    check_regex,
    check_subclass,
    check_truthy,
    check_type,
    check_value,
)
