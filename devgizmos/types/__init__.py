"""
types
=====
Package containing custom types such as Number, Char, etc along with type hint types.

Built-in Utilizations
---------------------
This module utilizes the following functionality from built-in modules/packages:
math
- ceil
- floor
- trunc
re
- match
"""

__all__ = ["Char", "Number"]

from .__char import Char
from .__number import Number
