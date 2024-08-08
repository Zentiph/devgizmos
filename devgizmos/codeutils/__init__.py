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
    "immutable",
    "lazy_property",
    "rate_limit",
    "singleton",
    "type_checker",
    "Seed",
    "Timeout",
    "UnsupportedOSError",
]

from .__decs import (
    cache,
    decorate_all_methods,
    deprecated,
    immutable,
    lazy_property,
    rate_limit,
    singleton,
    type_checker,
)
from .__misc import Seed
from .__timeout import Timeout, UnsupportedOSError
