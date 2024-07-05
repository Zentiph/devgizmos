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
Contributions are not currently welcome, but feel free to open an issue if you notice any bugs/have suggestions.

Built-in Utilizations
---------------------
This package utilizes the following functionality from built-in modules/packages:
TODO:
"""

__version__ = "0.0.3"
__authors__ = ("Gavin Borne", "Leo Nguyen")
__email__ = "zentiphdev@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/Zentiph/devgizmos/tree/main"
__copyright__ = "Copyright 2024 Gavin Borne, Leo Nguyen"
__maintainers__ = ("Gavin Borne", "Leo Nguyen")

__all__ = ["checks", "decorators", "types", "BasicLogger"]

from . import checks, decorators, types
from .__basic_logger import BasicLogger
