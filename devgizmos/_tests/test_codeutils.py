# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, cell-var-from-loop, invalid-name

import unittest
from logging import DEBUG, Logger, StreamHandler
from time import perf_counter, sleep

from ..codeutils import (
    Seed,
    Timeout,
    UnsupportedOSError,
    cache,
    deprecated,
    enforce_type_hints,
    rate_limit,
)


class TestCache(unittest.TestCase):
    @unittest.skip("")
    @staticmethod
    def testing_func(*args, wait=0):
        print(args)
        if wait > 0:
            sleep(wait)

    def test_results_cached(self):
        maxsize_test_cases = (1, 128, 53, 20, 178)

        for maxsize in maxsize_test_cases:
            with self.subTest(maxsize=maxsize):
                try:

                    cache(maxsize)(self.testing_func)

                except Exception as e:
                    self.fail(
                        f"@cache({maxsize}) unexpectedly raised {type(e).__name__}"
                    )

        for b in (True, False):
            with self.subTest(b=b):
                try:

                    cache(type_specific=b)(self.testing_func)

                except Exception as e:
                    self.fail(
                        f"@cache(type_specific={b}) unexpectedly raised {type(e).__name__}"
                    )

    def test_incorrect_arg_types(self):
        maxsize_test_cases = (3.0, 4.2, "10", [4])

        for maxsize in maxsize_test_cases:
            with self.subTest(maxsize=maxsize):
                with self.assertRaises(TypeError):
                    cache(maxsize)(self.testing_func)

        type_specific_test_cases = ("True", 1, 0.0)

        for ts in type_specific_test_cases:
            with self.subTest(ts=ts):
                with self.assertRaises(TypeError):
                    cache(type_specific=ts)(self.testing_func)

    def test_incorrect_arg_values(self):
        maxsize_test_cases = (0, -10, -128)

        for maxsize in maxsize_test_cases:
            with self.subTest(maxsize=maxsize):
                with self.assertRaises(ValueError):
                    cache(maxsize)(self.testing_func)

    def test_cache_skips_computation(self):
        with self.subTest():
            t0 = perf_counter()

            @cache()
            def test(*args, wait=0):
                print(args)
                if wait > 0:
                    sleep(wait)

            test(2, 3, wait=1)
            test(2, 3, wait=1)

            tf = perf_counter()

            # make sure all tests take ~1 second due to 2nd call
            # returning cached value and skipping computation
            self.assertAlmostEqual(tf - t0, 1, places=2)

    def test_cache_pops_items(self):
        with self.subTest():
            t0 = perf_counter()

            @cache(1)
            def test(*args, wait=0):
                print(args)
                if wait > 0:
                    sleep(wait)

            test(2, 3, wait=1)
            test(3, 4, wait=1)
            test(2, 3, wait=1)

            tf = perf_counter()

            # make sure all tests take ~3 seconds due to the
            # 2nd call erasing the first call's cached return
            self.assertAlmostEqual(tf - t0, 3, places=2)


class TestDeprecated(unittest.TestCase):
    @unittest.skip("")
    @staticmethod
    def testing_func(*args, **kwargs):
        pass

    # TODO:
    # unfortunately this doesn't currently test that the message
    # is correctly formatted since using unittest.mock is not
    # working out. i'd like a msg format test to eventually be
    # added but as of now it'll be postponed.
    # if this is getting fixed, remove this comment when done.
    def test_deprecated_warning_pushed(self):
        def test_func():
            pass

        for reason in ("Hi", "This is bad", "Poo poo code", ""):
            with self.subTest(reason=reason):
                with self.assertWarns(DeprecationWarning):
                    deprecated(reason)(test_func)()

        for version in (1, 3.0, 1.2, "1.2.1", "alpha"):
            with self.subTest(version=version):
                with self.assertWarns(DeprecationWarning):
                    deprecated("", version)(test_func)()

        for date in ("", "Friday", "8/10/2024", "10-8-24"):
            with self.subTest(date=date):
                with self.assertWarns(DeprecationWarning):
                    deprecated("", date=date)(test_func)()

    def test_invalid_args(self):
        def test_func():
            pass

        for reason in (10, 5.5, ["Msg"], True):
            with self.subTest(reason=reason):
                with self.assertRaises(TypeError):
                    deprecated(reason)(test_func)

        with self.subTest(version=["version"]):
            with self.assertRaises(TypeError):
                deprecated("", ["version"])(test_func)

        for date in (10, 5.5, ["date"], True):
            with self.subTest(date=date):
                with self.assertRaises(TypeError):
                    deprecated("", date=date)(test_func)


class TestRateLimit(unittest.TestCase):
    def test_limits_calls(self):
        with self.subTest():
            # interval (single arg)
            @rate_limit(1)
            def test1():
                pass

            t0 = perf_counter()
            test1()
            test1()
            tf = perf_counter()

            self.assertAlmostEqual(tf - t0, 1, places=2)

            # calls / period (two args)
            @rate_limit(3, 3)
            def test2():
                pass

            t0 = perf_counter()
            test2()
            test2()
            tf = perf_counter()

            self.assertAlmostEqual(tf - t0, 1, places=2)

    def test_invalid_args(self):
        with self.subTest():
            for interval in ("1", [1]):
                with self.assertRaises(TypeError):

                    @rate_limit(interval)
                    def test1():
                        pass

            for calls in (4.3, "1", [1]):
                with self.assertRaises(TypeError):

                    @rate_limit(calls, 1)
                    def test2():
                        pass

            for period in ("1", [1]):
                with self.assertRaises(TypeError):

                    @rate_limit(1, period)
                    def test3():
                        pass


class TestTypeChecker(unittest.TestCase):
    def test_hints_enforced(self):
        with self.subTest():
            # test args
            @enforce_type_hints
            def typed_args(arg1: int, arg2: str, /):  # pylint: disable=unused-argument
                pass

            with self.assertRaises(TypeError):
                typed_args(1, 1)

            with self.assertRaises(TypeError):
                typed_args("1", "1")

            with self.assertRaises(TypeError):
                typed_args(1.0, "a")

            with self.assertRaises(AssertionError):
                with self.assertRaises(TypeError):
                    typed_args(3, "hi")

            # test kwargs
            @enforce_type_hints
            def typed_kwargs(
                *, kwarg1: float = 1.0, kwarg2: int = 3
            ):  # pylint: disable=unused-argument
                pass

            with self.assertRaises(TypeError):
                typed_kwargs(kwarg1=1, kwarg2=1)

            with self.assertRaises(TypeError):
                typed_kwargs(kwarg1=3.0, kwarg2=2.0)

            with self.assertRaises(TypeError):
                typed_kwargs(kwarg1="1", kwarg2=1.0)

            with self.assertRaises(AssertionError):
                with self.assertRaises(TypeError):
                    typed_kwargs(kwarg1=3.2, kwarg2=4)

            # test return
            @enforce_type_hints
            def typed_return(b) -> int:
                if b:
                    return 3
                return 3.0  # type: ignore

            with self.assertRaises(TypeError):
                typed_return(False)

            with self.assertRaises(AssertionError):
                with self.assertRaises(TypeError):
                    typed_return(True)


if __name__ == "__main__":
    unittest.main()
