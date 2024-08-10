# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, cell-var-from-loop, invalid-name

import unittest
import unittest.mock as mock
from io import StringIO
from logging import DEBUG, Logger, StreamHandler
from time import perf_counter, sleep

from ..codeutils import (
    Seed,
    Timeout,
    UnsupportedOSError,
    cache,
    decorate_all_methods,
    deprecated,
    ignore_method_decoration,
    immutable,
    lazy_property,
    rate_limit,
    singleton,
    type_checker,
)


class TestCache(unittest.TestCase):
    @unittest.skip("")
    @staticmethod
    def testing_func(*args, wait=0):
        print(args)
        if wait > 0:
            sleep(wait)

    def test_correct_args(self):
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


# also for testing ignore_method_decoration
# since both are used together
class TestDecorateAllMethods(unittest.TestCase):
    # logger for testing purposes
    logger = Logger("DecorateAllMethodsLogger")
    logger.addHandler(StreamHandler())

    # decorator examples to use for ensuring type checking is happening
    def decorator_ex1(self):
        def decorator(func):
            def wrapper(*args, **kwargs):
                self.logger.debug("%s\n%s", args, kwargs)
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def decorator_ex2(self, func):
        def wrapper(*args, **kwargs):
            self.logger.debug("%s\n%s", args, kwargs)
            return func(*args, **kwargs)

        return wrapper

    # basic func for testing
    @staticmethod
    def example_func(*args, **kwargs):  # pylint: disable=unused-argument
        return

    # basic class for testing
    class Tester:
        def __init__(self, a):
            self.a = a

        def get_a(self):
            return self.a

        def set_a(self, a):
            self.a = a

    def test_correct_args(self):
        for decorator in (self.decorator_ex1, self.decorator_ex2):
            with self.subTest(decorator=decorator):

                @decorate_all_methods(decorator)
                class Example(self.Tester):
                    pass

                ex = Example(1)

                # ensure the loggers activate since all of the methods are
                # decorated with funcs that use a logger
                with self.assertLogs(self.logger, DEBUG):
                    ex.get_a()
                with self.assertLogs(self.logger, DEBUG):
                    ex.set_a(3)

    # this only tests if the decorator passed is callable, not if
    # the other args are the correct args for the decorator.
    # those tests should be done inside that
    # decorator's test class, not here.
    def test_incorrect_arg_types(self):
        test_cases = (10, "decorator", int())

        for decorator in test_cases:
            with self.subTest(decorator=decorator):
                with self.assertRaises(TypeError):

                    @decorate_all_methods(decorator)
                    class Example(self.Tester):  # pylint: disable=unused-variable
                        pass

    def test_incorrect_arg_values(self):
        class Callable:
            def __init__(self):
                pass

            def __call__(self):
                pass

        for callable_ in (Callable, self.example_func):
            with self.subTest(callable=callable_):
                with self.assertRaises(TypeError):

                    @decorate_all_methods(callable_)
                    class Example(self.Tester):  # pylint: disable=unused-variable
                        def new_method(self):
                            return self.a

                    Example(1).new_method()

    def test_magic_methods_not_decorated(self):
        for decorator in (self.decorator_ex1, self.decorator_ex2):
            with self.subTest(decorator=decorator):

                @decorate_all_methods(decorator)
                # pylint: disable=unused-argument
                class Example(self.Tester):
                    def __magic__(self, *args, **kwargs):
                        return

                    def __front_dunder(
                        self, *args, **kwargs
                    ):  # pylint: disable=unused-private-member
                        return

                    @ignore_method_decoration
                    def call_front_dunder(self, *args, **kwargs):
                        return self.__front_dunder(*args, **kwargs)

                    def back_dunder__(self, *args, **kwargs):
                        return

                ex = Example(1)

                # negate assertLogs by checking for an AssertionError
                # (making sure it DOESN'T log)
                with self.assertRaises(AssertionError):
                    with self.assertLogs(self.logger, DEBUG):
                        ex.__magic__(2, 3)

                with self.assertLogs(self.logger, DEBUG):
                    ex.call_front_dunder(2, 3)

                with self.assertLogs(self.logger, DEBUG):
                    ex.back_dunder__(2, 3)

    def test_ignore_method_decoration_works(self):
        for decorator in (self.decorator_ex1, self.decorator_ex2):
            with self.subTest(decorator=decorator):

                @decorate_all_methods(decorator)
                class Example(self.Tester):
                    @ignore_method_decoration
                    def new_method(self):
                        pass

                ex = Example(1)

                with self.assertLogs(self.logger, DEBUG):
                    ex.get_a()

                with self.assertRaises(AssertionError):
                    with self.assertLogs(self.logger, DEBUG):
                        ex.new_method()

    def test_ignore_method_decoration_incorrect_args(self):
        for func in (10, "decorator", int()):
            with self.subTest(func=func):
                with self.assertRaises(TypeError):
                    ignore_method_decoration(func)


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
    def test_correct_args(self):
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

    def test_incorrect_args(self):
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


if __name__ == "__main__":
    unittest.main()
