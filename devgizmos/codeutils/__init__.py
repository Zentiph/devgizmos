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
    "FailureHandler",
    "FailureManager",
    "Fallback",
    "Suppress",
    "Seed",
    "Retry",
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
from .__failuremngr import FailureHandler, FailureManager, Fallback, Suppress
from .__misc import Seed
from .__retry import Retry
from .__timeout import Timeout, UnsupportedOSError
