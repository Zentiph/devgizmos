"""
devgizmos
---------
devgizmos is a Python library containing development
tools such as performance testing, failure handling,
error guards, utilities, and more.

Documentation
~~~~~~~~~~~~~
devgizmos's documentation can be found [here](https://docs.python.org/).

Contributing
~~~~~~~~~~~~
Contributions are not currently welcome, but feel free to open
an issue or email if you notice any bugs or have suggestions.
"""

__version__ = "0.8.3"
__authors__ = ("Gavin Borne", "Leo Nguyen")
__email__ = "zentiphdev@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/Zentiph/devgizmos/tree/main"
__copyright__ = "Copyright 2024 Gavin Borne, Leo Nguyen"
__maintainers__ = ("Gavin Borne", "Leo Nguyen")

__all__ = [
    "errguards",
    "funcutils",
    "failurehandling",
    "info",
    "performance",
    "regextools",
    "sysutils",
    "types",
    "BasicLogger",
    "Seed",
]

from . import (
    errguards,
    failurehandling,
    funcutils,
    info,
    performance,
    regextools,
    sysutils,
    types,
)
from .__misc import BasicLogger, Seed
