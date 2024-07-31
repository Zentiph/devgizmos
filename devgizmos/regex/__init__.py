"""
regex
=====
Module containing useful regexes.
For regex matching utility, import 'matches_regex()'
or 'ensure_matches_regex()' from errguards.
"""

__all__ = [
    "COMPLEX",
    "COMPLEX_EXACT",
    "COMPLEX_PARENS",
    "COMPLEX_PARENS_EXACT",
    "FLOAT",
    "FLOAT_EXACT",
    "INT",
    "INT_EXACT",
    "EMAIL",
]

from .__regexes import (
    COMPLEX,
    COMPLEX_EXACT,
    COMPLEX_PARENS,
    COMPLEX_PARENS_EXACT,
    FLOAT,
    FLOAT_EXACT,
    INT,
    INT_EXACT,
    EMAIL,
)
