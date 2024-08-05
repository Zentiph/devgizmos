"""
devgizmos
=========
devgizmos is a Python package containing useful development
tools to be used within other Python scripts.

Documentation
-------------
devgizmos's documentation can be found [here](https://docs.python.org/).

Contributing
------------
Contributions are not currently welcome, but feel free to open
an issue or email if you notice any bugs or have suggestions.
"""

__version__ = "0.0.3"
__authors__ = ("Gavin Borne", "Leo Nguyen")
__email__ = "zentiphdev@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/Zentiph/devgizmos/tree/main"
__copyright__ = "Copyright 2024 Gavin Borne, Leo Nguyen"
__maintainers__ = ("Gavin Borne", "Leo Nguyen")

__all__ = [
    "errguards",
    "codeutils",
    "failurehandling",
    "info",
    "performance",
    "regex",
    "sysutils",
    "types",
    "BasicLogger",
]

from . import (
    codeutils,
    errguards,
    failurehandling,
    info,
    performance,
    regex,
    sysutils,
    types,
)
from .__basic_logger import BasicLogger
