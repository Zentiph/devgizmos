"""
funcutils
=========
Package containing utility for working with functions.
"""

__all__ = [
    "cache",
    "deprecated",
    "rate_limit",
    "enforce_type_hints",
]

from .__fnutils import (
    cache,
    deprecated,
    enforce_type_hints,
    rate_limit,
)
