# pylint: disable=all

import devgizmos as dgiz

dgiz.checks.verify_regex("example@example.com", r"^\S+@\S+\.\S+$")
dgiz.checks.verify_regex("example.com", r"^\S+@\S+\.\S+$")
