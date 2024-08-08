"""
failurehandling
===============
Package containing the FailureManager class that can be
used along with _FailureHandler instances to handle exceptions.
"""

__all__ = [
    "FailureManager",
    "Fallback",
    "Suppress",
    "_FailureHandler",
    "CustomException",
    "Retry",
]

from .__failuremngr import (
    CustomException,
    FailureManager,
    Fallback,
    Suppress,
    _FailureHandler,
)
from .__retry import Retry
