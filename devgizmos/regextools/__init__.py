"""
regex
-----
Package containing useful regexes.

For regex matching utility, use
errguards.matches_regex() or errguards.ensure_matches_regex().
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
    "IPV4",
    "IPV6",
    "ensure_matches",
    "is_email",
    "is_ip",
    "is_ipv4",
    "is_ipv6",
    "matches",
]

from .__regexes import (
    COMPLEX,
    COMPLEX_EXACT,
    COMPLEX_PARENS,
    COMPLEX_PARENS_EXACT,
    EMAIL,
    FLOAT,
    FLOAT_EXACT,
    INT,
    INT_EXACT,
    IPV4,
    IPV6,
)
from .__rtools import ensure_matches, is_email, is_ip, is_ipv4, is_ipv6, matches
