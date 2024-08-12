# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, cell-var-from-loop, invalid-name

import unittest
from logging import DEBUG, Logger, StreamHandler

from ..classtools import (
    decorate_all_methods,
    ignore_method_decoration,
    immutable,
    lazyproperty,
    singleton,
)


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

    def test_methods_get_decorated(self):
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


class TestImmutable(unittest.TestCase):
    class TestClass:
        def __init__(self, a):
            self.a = a

    def test_decorated_class_cannot_be_edited(self):
        with self.subTest():
            with self.assertRaises(AttributeError):

                @immutable
                class Example(self.TestClass):
                    pass

                ex = Example(1)
                ex.a = 1

    def test_invalid_args(self):
        with self.subTest():
            with self.assertRaises(TypeError):

                @immutable
                def test_func():
                    pass


class TestLazyProperty(unittest.TestCase):
    class CircleFramework:
        logger = Logger("lazy_propertyTestingLogger")

        def __init__(self, radius):
            self.radius = radius

        def area(self):
            self.logger.log(DEBUG, "Computing area")
            return 3.14159 * self.radius**2

    def test_property_result_cached(self):
        with self.subTest():

            class Circle(self.CircleFramework):
                @lazyproperty
                def area(self):
                    return super().area()

            c = Circle(10)

            with self.assertLogs(c.logger, DEBUG):
                print(c.area)

            with self.assertRaises(AssertionError):
                with self.assertLogs(c.logger, DEBUG):
                    print(c.area)


class TestSingleton(unittest.TestCase):
    def test_only_one_instance(self):
        with self.subTest():

            @singleton
            class Single:
                def __init__(self, x):
                    self.x = x

            single1 = Single(1)
            single2 = Single(2)

            self.assertEqual(single1.x, 1)
            self.assertEqual(single2.x, 1)
            self.assertIs(single1, single2)


if __name__ == "__main__":
    unittest.main()
