"""
codeutils.__misc
================
Misc utilities for the codeutils module.
"""

from collections import deque
from functools import wraps
from random import getstate, randint
from random import seed as random_seed
from random import setstate

from ..errguards import ensure_instance_of


class Seed:
    """Class used for executing random code with a set seed."""

    def __init__(self, seed):
        """
        Seed()
        ------
        Class for executing code involving randomness with a set seed.

        Parameters
        ~~~~~~~~~~
        :param seed: The seed to use.
        :type seed: int | float | str | bytes | bytearray | None

        Raises
        ~~~~~~
        :raises TypeError: If seed is not an int, float, str, bytes, bytearray, or None.

        Example Usage
        ~~~~~~~~~~~~~
        >>> from random import random
        >>>
        >>> # generate the seed
        >>> seed = Seed.generate()
        >>> # set the random state using the seed
        >>> seed.set_state()
        >>> # use the get method to calculate random results
        >>> # without changing the random state
        >>> seed.get(random)
        0.18126486333322134
        >>> seed.get(random)
        0.18126486333322134
        >>> # reset the random state
        >>> seed.reset_state()
        >>> random()
        0.19521491075191701
        >>>
        >>>
        >>> # use as a context manager
        >>> with Seed(18) as s:
        ...     random()
        ...
        0.18126486333322134
        >>> with s:
        ...     random()
        ...
        0.18126486333322134
        >>>
        >>>
        >>> # or a decorator
        >>> @s
        ... def print_rand():
        ...     print(random())
        ...
        >>> print_rand()
        0.18126486333322134
        >>> print_rand()
        0.18126486333322134
        >>>
        >>> # states can be nested,
        >>> # meaning they can be entered from inside other states
        >>> s = Seed.generate()
        >>> # set the outer state
        >>> s.set_state()
        >>> random()
        0.6387044505372729
        >>> s.generate_seed()
        >>> # set the inner state
        >>> s.set_state()
        >>> random()
        0.1692528073567121
        >>> # revert to the previous (outer) state
        >>> s.revert_state()
        >>> random()
        0.6387044505372729
        >>> # reset to the original state
        >>> s.reset_state()
        """

        # type checks
        ensure_instance_of(seed, int, float, str, bytes, bytearray, optional=True)

        self.__orig_state = getstate()
        self.__state_stack = deque()
        self.__seed = seed

    def __enter__(self):
        self.set_state()
        return self

    def __exit__(self, type_, value, traceback):
        self.revert_state()

    def __call__(self, func, /):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.set_state()
            try:
                return func(*args, **kwargs)
            finally:
                self.reset_state()

        return wrapper

    @classmethod
    def generate(cls):
        """
        Seed.generate()
        ---------------
        Generates a new seed object with a randomly generated seed.

        Return
        ~~~~~~
        :return: A new Seed object with a random seed.
        :rtype: Seed
        """

        seed = randint(0, 2**32 - 1)
        return cls(seed)

    def generate_seed(self):
        """
        Seed().generate_seed()
        ----------------------
        Generates a new seed and sets the Seed object's seed.
        """

        self.seed = randint(0, 2**32 - 1)

    @property
    def seed(self):
        """
        Seed().seed
        -----------
        Returns the seed given to the Seed object.

        Return
        ~~~~~~
        :return: The seed given to the Seed object.
        :rtype: int | float | str | bytes | bytearray | None
        """

        return self.__seed

    @seed.setter
    def seed(self, s, /):
        """
        Seed().seed()
        -------------
        Sets the seed to be used by the Seed object.
        This DOES NOT set the seed being used currently.
        To change the current seed to the Seed object's seed, call Seed.set_state().

        Parameters
        ~~~~~~~~~~
        :param s: The new seed.
        :type s: int | float | str | bytes | bytearray | None

        Raises
        ~~~~~~
        :raises TypeError: If s is not an int, float, str, bytes, bytearray, or None.
        """

        # type checks
        ensure_instance_of(s, int, float, str, bytes, bytearray, optional=True)

        self.__seed = s

    def get(self, func, *args, **kwargs):
        """
        Seed().get()
        ------------
        Gets the result from the random function and args/kwargs
        provided while maintaining the random state.

        Parameters
        ~~~~~~~~~~
        :param func: The random function to use.
        :type func: Callable[..., Any]
        :param args: The args to pass to the random function, if any.
        :type args: Any
        :param kwargs: The kwargs to pass to the random function, if any.
        :type kwargs: Any

        Raises
        ~~~~~~
        :raises TypeError: If func is not callable.
        """

        # type checks
        if not callable(func):
            raise TypeError("'func' must be callable")

        orig_state = getstate()
        result = func(*args, **kwargs)
        setstate(orig_state)
        return result

    def set_state(self):
        """
        Seed().set_state()
        ------------------
        Sets the random state to the Seed object's seed.
        """

        random_seed(self.__seed)
        self.__state_stack.append(getstate())

    def revert_state(self):
        """
        Seed().revert_state()
        ---------------------
        Reverts to the previous state.
        """

        if self.__state_stack:
            self.__state_stack.pop()
            if self.__state_stack:
                setstate(self.__state_stack[-1])

    def reset_state(self):
        """
        Seed().reset_state()
        --------------------
        Resets the random state to the original state.
        """

        setstate(self.__orig_state)

    def clone(self):
        """
        Seed().clone()
        --------------
        Clones the current Seed object and returns it.

        Return
        ~~~~~~
        :return: A new Seed object with matching data.
        :rtype:
        """

        clone = Seed(self.__seed)
        # pylint: disable=protected-access, unused-private-member
        clone.__state_stack = self.__state_stack.copy()
        return clone

    def __str__(self):
        return str(self.__seed)

    def __repr__(self):
        return f"Seed({self.__seed})"
