"""
classtools
==========
Package containing utilities for working with classes.
"""

__all__ = [
    "decorate_all_methods",
    "ignore_method_decoration",
    "immutable",
    "lazyproperty",
    "singleton",
]

from .__clstools import (
    SingleMeta,
    decorate_all_methods,
    ignore_method_decoration,
    immutable,
    lazyproperty,
    singleton,
)
