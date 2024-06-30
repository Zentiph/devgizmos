"""
types.__types
=============
Module containing custom types.
"""

from typing import Any, Callable, Dict, Literal, TypeAlias, TypeVar, Union


class Char:
    """
    Char
    ====
    Represents a single character string.
    """

    def __init__(self, value: Any) -> None:
        """
        Char
        ====
        Represents a single character string.

        Parameters
        ----------
        :param value: The value to convert to a Char. The value must have a __str__ method.
        :type value: Any
        """
        if not hasattr(value, "__str__"):
            raise TypeError("Value to convert must have a __str__ method")

        val = str(value)

        if len(val) != 1:
            raise ValueError("Char must be a single character string")

        self._val: str = val

    def __str__(self) -> str:
        return self._val

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._val!r})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Char):
            return self._val == other._val
        return False

    def __hash__(self) -> int:
        return hash(self._val)

    def __add__(self, other: Any) -> str:
        if not hasattr(other, "__str__"):
            raise TypeError(
                "Cannot add a Char value to an object with no __str__ method"
            )

        return self._val + str(other)

    def __radd__(self, other: Any) -> str:
        if not hasattr(other, "__str__"):
            raise TypeError(
                "Cannot add a Char value to an object with no __str__ method"
            )

        return str(other) + self._val

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Char):
            raise TypeError(
                f"'<' not supported between instances of 'Char' and '{type(other).__name__}'"
            )

        return self._val < other._val

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, Char):
            raise TypeError(
                f"'<=' not supported between instances of 'Char' and '{type(other).__name__}'"
            )

        return self._val <= other._val

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, Char):
            raise TypeError(
                f"'>' not supported between instances of 'Char' and '{type(other).__name__}'"
            )

        return self._val > other._val

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, Char):
            raise TypeError(
                f"'>=' not supported between instances of 'Char' and '{type(other).__name__}'"
            )

        return self._val >= other._val

    def __int__(self) -> int:
        if not self._val.isdigit():
            raise ValueError("Cannot convert a non-digit Char value to an int")

        return int(self._val)

    def __len__(self) -> Literal[1]:
        return 1

    def upper(self) -> "Char":
        """
        upper
        =====
        Returns the capital version of the character.

        Return
        ------
        :return: The capital version of the character.
        :rtype: Char
        """

        return Char(self._val.upper())

    def lower(self) -> "Char":
        """
        lower
        =====
        Returns the lowercase version of the character.

        Return
        ------
        :return: The lowercase version of the character.
        :rtype: Char
        """

        return Char(self._val.lower())

    def isdigit(self) -> bool:
        """
        isdigit
        =======
        Returns whether the character is a digit.

        Return
        ------
        :return: Whether the character is a digit.
        :rtype: bool
        """

        return self._val.isdigit()

    def isalpha(self) -> bool:
        """
        isalpha
        =======
        Returns whether the character is in the alphabet.

        Return
        ------
        :return: Whether the character is in the alphabet.
        :rtype: bool
        """

        return self._val.isalpha()

    def isalnum(self) -> bool:
        """
        isalnum
        =======
        Returns whether the character is in the alphabet or a digit.

        Return
        ------
        :return: Whether the character is in the alphabet or a digit.
        :rtype: bool
        """

        return self._val.isalnum()


Number: TypeAlias = Union[int, float]
"""An int or float value."""
Function: TypeAlias = Callable[..., Any]
"""A callable with any arguments and any return type."""
JsonData: TypeAlias = Dict[Any, Any]
"""A dictionary of any keys and values."""

F = TypeVar("F", bound=Callable[..., Any])
Decorator = Callable[[F], F]
"""Standard decorator type."""
