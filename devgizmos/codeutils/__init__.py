"""
codeutils
=========
Package containing general code utilities, such as controlling/error
handling utility like Timeout, FailureManager, etc.
"""

__all__ = [
    "cache",
    "decorate_all_methods",
    "deprecated",
    "ignore_method_decoration",
    "immutable",
    "lazyproperty",
    "rate_limit",
    "singleton",
    "enforce_type_hints",
    "Seed",
    "Timeout",
    "UnsupportedOSError",
]

from .__decs import (
    cache,
    decorate_all_methods,
    deprecated,
    enforce_type_hints,
    ignore_method_decoration,
    immutable,
    lazyproperty,
    rate_limit,
    singleton,
)
from .__misc import Seed
from .__timeout import Timeout, UnsupportedOSError
