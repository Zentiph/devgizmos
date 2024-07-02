"""
regex.__regexes
===============
Module containing useful regexes.
"""

INT = r"[-+]?\d+"
INT_EXACT = r"^[-+]?\d+$"
FLOAT = r"[-+]?\d*\.?\d+([eE][-+]?\d+)?"
FLOAT_EXACT = r"^[-+]?\d*\.?\d+([eE][-+]?\d+)?$"
COMPLEX = r"\s*([-+]?\d*\.?\d+)\s*([-+])\s*(\d*\.?\d+)j\s*"
COMPLEX_EXACT = r"^\s*([-+]?\d*\.?\d+)\s*([-+])\s*(\d*\.?\d+)j\s*$"
COMPLEX_PARENS = r"\(\s*([-+]?\d*\.?\d+)\s*([-+])\s*(\d*\.?\d+)j\s*\)"
COMPLEX_PARENS_EXACT = r"^\(\s*([-+]?\d*\.?\d+)\s*([-+])\s*(\d*\.?\d+)j\s*\)$"
