"""
codeutils
=========
Package containing general code utilities, such as controlling/error
handling utility like Timeout, FailureManager, etc.
"""

__all__ = [
    "FailureHandler",
    "FailureManager",
    "Fallback",
    "Retry",
    "Timeout",
    "UnsupportedOSError",
]

from .__failuremngr import FailureHandler, FailureManager, Fallback, Suppress
from .__retry import Retry, retry
from .__timeout import Timeout, UnsupportedOSError
