# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring

import unittest

from logging import NOTSET, DEBUG, INFO, WARN, WARNING, ERROR, FATAL, CRITICAL

from .. import BasicLogger


class TestBasicLogger(unittest.TestCase):
    def test_correct_args(self):
        level_test_cases = [
            NOTSET,
            DEBUG,
            INFO,
            WARN,
            WARNING,
            ERROR,
            FATAL,
            CRITICAL,
            0,
            10,
            20,
            30,
            40,
            50,
        ]

        for level in level_test_cases:
            try:
                BasicLogger(level)
            except Exception as e:
                self.fail(
                    f"BasicLogger({level}) unexpectedly raised {type(e).__name__}"
                )

        fmt_test_cases = [
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "%(message)s",
        ]

        for fmt in fmt_test_cases:
            try:
                BasicLogger(fmt=fmt)
            except Exception as e:
                self.fail(f"BasicLogger({fmt=}) unexpectedly raised {type(e).__name__}")

    def test_incorrect_arg_types(self):
        level_test_cases = [
            10.0,
            "10",
            "DEBUG",
            [10],
        ]

        for level in level_test_cases:
            with self.subTest(level=level):
                with self.assertRaises(TypeError):
                    BasicLogger(level)

        fmt_test_cases = [10, 7.3, ["%(message)s"]]

        for fmt in fmt_test_cases:
            with self.subTest(fmt=fmt):
                with self.assertRaises(TypeError):
                    BasicLogger(fmt=fmt)

    def test_incorrect_arg_values(self):
        level_test_cases = [1, 12, -10]

        for level in level_test_cases:
            with self.subTest(level=level):
                with self.assertRaises(ValueError):
                    BasicLogger(level)

        with self.assertRaises(ValueError):
            BasicLogger(fmt="unformatted")

    def test_logs_correctly(self):
        logger = BasicLogger()

        with self.assertLogs(logger, DEBUG):
            logger.log(logger.level, "Logging commencing")


if __name__ == "__main__":
    unittest.main()
