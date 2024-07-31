"""
checks.__checks
===============

Module used for checking certain cases.
Mainly used for type and value checking function parameters.
"""

from collections.abc import Iterable, Sequence
from re import match as re_match


def _msg_chk(msg):
    """
    _msg_chk()
    ----------
    Checks that the msg is a str.

    Parameters
    ~~~~~~~~~~
    :param msg: The message to check.
    :type msg: str

    Raises
    ~~~~~~
    :raises TypeError: If msg is not a str.
    """

    if not isinstance(msg, str):
        raise TypeError(f"'msg' must be a 'str', not '{type(msg).__name__}'")


def is_instance_of(value, *types, optional=False):
    """
    is_instance_of()
    ----------------
    Determines if the given value is an instance of one of the expected type(s).

    Parameters
    ~~~~~~~~~~
    :param value: The value to check.
    :type value: Any
    :param types: The expected types.
    :type types: Type
    :param optional: Whether the types are optional, meaning the value can be None, defaults to False.
    :type optional: bool

    Raises
    ~~~~~~
    :raises TypeError: If any of the types are not a type.

    Return
    ------
    :return: True if the value is a member of the expected type(s), otherwise False.
    :rtype: bool

    Example Usage
    ~~~~~~~~~~~~~
    >>> is_instance_of(10, int)
    True
    >>> is_instance_of(True, (float, str))
    False
    >>> is_instance_of(None, (float, str), optional=True)
    True
    """

    # type checks
    if not all(isinstance(t, type) for t in types):
        raise TypeError("all types given must be a type")

    if isinstance(value, types):
        return True
    if optional and value is None:
        return True
    return False


def ensure_instance_of(value, *types, optional=False, msg=""):
    """
    ensure_instance_of()
    --------------------
    Ensures the given value is an instance of one of the expected type(s).

    Parameters
    ~~~~~~~~~~
    :param value: The value to check.
    :type value: Any
    :param types: The expected types.
    :type types: Type
    :param optional: Whether the types are optional, meaning the value can be None, defaults to False.
    :type optional: bool
    :param msg: The exception message, leave empty to use the default, defaults to "".
    Ex: msg="{value} is not one of the expected types: {types}"
    :type msg: str

    Raises
    ~~~~~~
    :raises TypeError: If any of the types are not a type.
    :raises TypeError: If msg is not a str.
    :raises TypeError: If value is not an instance of one of the types.

    Example Usage
    ~~~~~~~~~~~~~
    >>> ensure_instance_of(10, int)
    >>> ensure_instance_of(None, float, str, optional=True)
    >>> ensure_instance_of(True, float, str)
    TypeError: True is not one of the expected types: float, str
    """

    if not is_instance_of(value, *types, optional=optional):
        _msg_chk(msg)

        type_names = ", ".join([type_.__name__ for type_ in types])

        if msg:
            msg = msg.format(value=repr(value), types=type_names)
        else:
            msg = f"{repr(value)} is not one of the expected types: {type_names}"

        raise TypeError(msg)


def is_value(value, *values):
    """
    is_value()
    ----------
    Determines if the given value is one of the expected values.

    Parameters
    ~~~~~~~~~~
    :param value: The value to check.
    :type value: Any
    :param values: The expected values.
    :type values: Any

    Return
    ------
    :return: True if the value(s) is/are equal to one of the expected values, otherwise False.
    :rtype: bool

    Example Usage
    ~~~~~~~~~~~~~
    >>> APPROVED_VALUES = (0, 1, 2, 3)
    >>> check_value(2, *APPROVED_VALUES)
    True
    >>> check_value(7, *APPROVED_VALUES)
    False
    """

    for v in values:
        if v == value:
            return True
    return False


def ensure_value(value, *values, msg=""):
    """
    ensure_value()
    --------------
    Ensures the given value is one of the expected values.

    Parameters
    ~~~~~~~~~~
    :param value: The value to check.
    :type value: Any
    :param values: The expected values.
    :type values: Any
    :param msg: The exception message, leave empty to use the default, defaults to "".
    Ex: msg="{value} is not one of the expected values: {values}"
    :type msg: str

    Raises
    ~~~~~~
    :raises TypeError: If msg is not a str.
    :raises ValueError: If the value is not one of the expected value(s).

    Example Usage
    ~~~~~~~~~~~~~
    >>> APPROVED_VALUES = (0, 1, 2, 3)
    >>> check_value(2, *APPROVED_VALUES)
    >>> check_value(7, *APPROVED_VALUES)
    ValueError: 7 is not one of the expected values: 0, 1, 2, 3
    """

    if not is_value(value, *values):
        _msg_chk(msg)

        value_names = ", ".join([repr(v) for v in values])

        if msg:
            msg = msg.format(value=repr(value), values=value_names)
        else:
            msg = f"{repr(value)} is not one of the expected values: {value_names}"

        raise ValueError(msg)


def is_in_range(value, seq, /, start=0, end=-1):
    """
    is_in_range()
    -------------
    Determines if the given value is in the specified range in the sequence provided.

    Parameters
    ~~~~~~~~~~
    :param value: The value to check.
    :type value: Any
    :param seq: The sequence to check within.
    :type seq: Sequence
    :param start: The start index of the range to check (inclusive), defaults to 0.
    :type start: int, optional
    :param end: The end index of the range to check (inclusive), defaults to -1 (checks the whole sequence).
    :type end: int, optional

    Raises
    ~~~~~~
    :raises TypeError: If seq is not a Sequence.
    :raises TypeError: If start is not an int.
    :raises TypeError: If end is not an int.

    Return
    ------
    :return: True if the value is in the inclusive range in the sequence, otherwise False.
    :rtype: bool

    Example Usage
    ~~~~~~~~~~~~~
    >>> is_in_range(3, range(0, 4))
    True
    >>> is_in_range(10, range(0, 4))
    False
    """

    # type checks
    if not isinstance(seq, Sequence):
        raise TypeError(f"'seq' must be a 'Sequence', not '{type(seq).__name__}'")
    if not isinstance(start, int):
        raise TypeError(f"'start' must be an 'int', not '{type(start).__name__}'")
    if not isinstance(end, int):
        raise TypeError(f"'end' must be an 'int', not '{type(end).__name__}'")

    if end == -1:
        end = len(seq)

    if value in seq[start:end]:
        return True
    return False


def ensure_in_range(value, seq, /, start=0, end=-1, *, msg=""):
    """
    ensure_in_range()
    ------------------
    Ensures the given value is in the specified range in the sequence provided.

    Parameters
    ~~~~~~~~~~
    :param value: The value to check.
    :type value: Any
    :param seq: The sequence to check within.
    :type seq: Sequence
    :param start: The start index of the range to check (inclusive), defaults to 0.
    :type start: int, optional
    :param end: The end index of the range to check (inclusive), defaults to -1 (checks the whole sequence).
    :type end: int, optional
    :param msg: The exception message, leave empty to use the default, defaults to "".
    Ex: msg="{value} is not in the range {lower}-{upper} in the sequence {seq}"
    :type msg: str

    Raises
    ~~~~~~
    :raises TypeError: If seq is not a Sequence.
    :raises TypeError: If start is not an int.
    :raises TypeError: If end is not an int.
    :raises TypeError: If msg is not a str.
    :raises ValueError: If the value is not within the range in the sequence.

    Example Usage
    ~~~~~~~~~~~~~
    >>> ensure_in_range(3, range(0, 4))
    >>> ensure_in_range(10, range(0, 4))
    ValueError: expected 10 to be within the range: (0, 4) in range(0, 4)
    """

    if not is_in_range(value, seq, start, end):
        _msg_chk(msg)

        if msg:
            msg = msg.format(value=repr(value), seq=repr(seq), start=start, end=end)
        else:
            msg = (
                f"expected {repr(value)} to be within the range: "
                + f"({start}, {end}) in {repr(seq)}"
            )

        raise ValueError(msg)


# what can ya do
# pylint: disable=too-many-return-statements
def is_in_bounds(value, lower, upper, /, *, inclusive=True):
    """
    is_in_bounds()
    --------------
    Determines if the given value is within the lower and upper bounds.

    Parameters
    ~~~~~~~~~~
    :param value: The value to check.
    :type value: int | float
    :param lower: The lower bound. If None, no lower bound will be set.
    :type lower: int | float | None
    :param upper: The upper bound. If None, no upper bound will be set.
    :type upper: int | float | None
    :param inclusive: Whether the bounds are inclusive or exclusive, defaults to True.
    :type inclusive: bool, optional

    Raises
    ~~~~~~
    :raises TypeError: If value is not an int or float.
    :raises TypeError: If lower is not an int, float, or None.
    :raises TypeError: If upper is not an int, float, or None.
    :raises TypeError: If inclusive is not a bool.

    Return
    ------
    :return: True if the value is within the bounds, otherwise False.
    :rtype: bool

    Example Usage
    ~~~~~~~~~~~~~
    >>> is_in_bounds(3, 1, 4)
    True
    >>> is_in_bounds(12, 1, 4)
    False
    """

    # type checks
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"'value' must be an 'int' or 'float', not '{type(value).__name__}'"
        )
    if not isinstance(lower, (int, float)) and lower is not None:
        raise TypeError(
            f"'lower' must be an 'int', 'float', or 'None', not '{type(lower).__name__}'"
        )
    if not isinstance(upper, (int, float)) and upper is not None:
        raise TypeError(
            f"'upper' must be an 'int', 'float', or 'None', not '{type(upper).__name__}'"
        )
    if not isinstance(inclusive, bool):
        raise TypeError(
            f"'inclusive' must be a 'bool', not '{type(inclusive).__name__}'"
        )

    if lower is not None and upper is not None:
        if inclusive:
            if lower <= value <= upper:
                return True
            return False

        if lower < value < upper:
            return True
        return False

    if lower is not None:
        if inclusive:
            if value >= lower:
                return True
            return False

        if value > lower:
            return True
        return False

    if upper is not None:
        if inclusive:
            if value <= upper:
                return True
            return False

        if value < upper:
            return True
        return False

    # if both bounds are None, return True
    # since there is no upper or lower bound
    return True


def ensure_in_bounds(value, lower, upper, /, *, inclusive=True, msg=""):
    """
    ensure_in_bounds()
    ------------------
    Ensures the given value is within the lower and upper bounds.

    Parameters
    ~~~~~~~~~~
    :param value: The value to check.
    :type value: int | float
    :param lower: The lower bound. If None, no lower bound will be set.
    :type lower: int | float | None
    :param upper: The upper bound. If None, no upper bound will be set.
    :type upper: int | float | None
    :param inclusive: Whether the bounds are inclusive or exclusive, defaults to True.
    :type inclusive: bool, optional
    :param msg: The exception message, leave empty to use the default, defaults to "".
    Ex: msg="{value} is not in the bounds ({lower}, {upper})."
    :type msg: str, optional

    Raises
    ~~~~~~
    :raises TypeError: If value is not an int or float.
    :raises TypeError: If lower is not an int, float, or None.
    :raises TypeError: If upper is not an int, float, or None.
    :raises TypeError: If inclusive is not a bool.
    :raises ValueError: If the value is not within the bounds.

    Example Usage
    ~~~~~~~~~~~~~
    >>> ensure_in_bounds(3, 1, 4)
    >>> ensure_in_bounds(12, 1, 4)
    ValueError: 12 must be >= 1 and <= 4
    """

    if not is_in_bounds(value, lower, upper, inclusive=inclusive):
        _msg_chk(msg)

        if msg:
            msg = msg.format(value=value, lower=lower, upper=upper)
        else:
            msg = f"{value} must be in the bounds ({lower}, {upper})"

        raise ValueError(msg)


def matches_regex(regex, *strings):
    """
    matches_regex()
    ---------------
    Determines if the given string matches the regex provided.

    Parameters
    ~~~~~~~~~~
    :param regex: The regex to compare the strings to.
    :type regex: str
    :param strings: The strings to check.
    :type strings: str

    Raises
    ~~~~~~
    :raises TypeError: If regex is not a str.
    :raises TypeError: If a string in strings is not a str.

    Return
    ------
    :return: True if the string matches the regex, otherwise False.
    :rtype: bool

    Example Usage
    ~~~~~~~~~~~~~
    >>> matches_regex(r'^\\S+@\\S+\\.\\S+$', "name@example.com")
    True
    >>> matches_regex(r'^\\S+@\\S+\\.\\S+$', "hello")
    False
    """

    # type checks
    if not isinstance(regex, str):
        raise TypeError(f"'regex' must be a 'str', not '{type(regex).__name__}'")
    if not all(isinstance(s, str) for s in strings):
        raise TypeError("all strings given must be type 'str'")

    if all(re_match(regex, s) for s in strings):
        return True
    return False


def ensure_matches_regex(regex, *strings, msg=""):
    """
    ensure_matches_regex()
    ----------------------
    Ensures the given strings match the regex provided.

    Parameters
    ~~~~~~~~~~
    :param regex: The regex to compare the strings to.
    :type regex: str
    :param strings: The strings to check.
    :type strings: str
    :param msg: The exception message, leave empty to use the default, defaults to ""
    Ex: msg="{strings} do not match the regex: {regex}."
    :type msg: str, optional

    Raises
    ~~~~~~
    :raises TypeError: If regex is not a str.
    :raises TypeError: If a string in strings is not a str.
    :raises ValueError: If the strings do not match the regex.

    Example Usage
    ~~~~~~~~~~~~~
    >>> ensure_matches_regex(r'^\\S+@\\S+\\.\\S+$', "name@example.com")
    >>> ensure_matches_regex(r'^\\S+@\\S+\\.\\S+$', "hello")
    ValueError: expected strings 'hello' to match the regex: '^\\S+@\\S+\\.\\S+$'
    """

    if not matches_regex(regex, *strings):
        _msg_chk(msg)

        string_names = ", ".join(repr(s) for s in strings)

        if msg:
            msg = msg.format(strings=string_names, regex=repr(regex))
        else:
            msg = f"expected strings {string_names} to match the regex: {repr(regex)}"

        raise ValueError(msg)


def dict_has_keys(dictionary, *keys):
    """
    dict_has_keys()
    ---------------
    Determines if the given dictionary contains the keys provided.

    Parameters
    ~~~~~~~~~~
    :param dictionary: The dictionary to check.
    :type dictionary: Dict[Any, Any]
    :param keys: The keys to search for.
    :type keys: Any

    Raises
    ~~~~~~
    :raises TypeError: If dictionary is not a dict.

    Return
    ------
    :return: True if the dictionary contains each of the keys, otherwise False.
    :rtype: bool

    Example Usage
    ~~~~~~~~~~~~~
    >>> ages = {"Bob": 24, "Martha": 22}
    >>> dict_has_keys(ages, "Bob", "Martha")
    True
    >>> dict_has_keys(ages, "Kevin")
    False
    """

    # type checks
    if not isinstance(dictionary, dict):
        raise TypeError(
            f"'dictionary' must be a 'dict', not '{type(dictionary).__name__}'"
        )

    if all(k in dictionary.keys() for k in keys):
        return True
    return False


def ensure_dict_has_keys(dictionary, *keys, msg=""):
    """
    ensure_dict_has_keys()
    ----------------------
    Ensures the given dictionary contains the keys provided.

    Parameters
    ~~~~~~~~~~
    :param dictionary: The dictionary to check.
    :type dictionary: Dict[Any, Any]
    :param keys: The keys to search for.
    :type keys: Any
    :param msg: The exception message, leave empty to use the default, defaults to ""
    Ex: msg="{dict} does not contain the keys: {keys}."
    :type msg: str, optional

    Raises
    ~~~~~~
    :raises TypeError: If dictionary is not a dict.
    :raises KeyError: If any of the keys are not in the dictionary.

    Example Usage
    ~~~~~~~~~~~~~
    >>> ages = {"Bob": 24, "Martha": 22}
    >>> ensure_dict_has_keys(ages, "Bob", "Martha")
    >>> ensure_dict_has_keys(ages, "Kevin")
    KeyError: "expected {'Bob': 24, 'Martha': 22} to contain the keys: 'Kevin'"
    """

    if not dict_has_keys(dictionary, *keys):
        _msg_chk(msg)

        key_names = ", ".join([repr(k) for k in keys])

        if msg:
            msg = msg.format(dict=repr(dictionary), keys=key_names)
        else:
            msg = f"expected {repr(dictionary)} to contain the keys: {key_names}"

        raise KeyError(msg)


def contains(iterable, *items):
    """
    contains()
    ----------
    Determines if the given iterable contains the items provided.

    Parameters
    ~~~~~~~~~~
    :param iterable: The iterable to check.
    :type iterable: Iterable
    :param items: The items to search for.
    :type items: Any

    Raises
    ~~~~~~
    :raises TypeError: If iterable is not an Iterable.

    Return
    ------
    :return: True if the iterable contains the items, otherwise False.
    :rtype: bool

    Example Usage
    ~~~~~~~~~~~~~
    >>> contains((0, 1, 2, 3), 3)
    True
    >>> contains(('a', 'b', 'c', 'd'), 'e')
    False
    """

    if not isinstance(iterable, Iterable):
        raise TypeError(
            f"'iterable' must be an 'Iterable', not '{type(iterable).__name__}'"
        )

    if all(i in iterable for i in items):
        return True
    return False


def ensure_contains(iterable, *items, msg=""):
    """
    ensure_contains()
    -----------------
    Ensures the given iterable contains the items provided.

    Parameters
    ~~~~~~~~~~
    :param iterable: The iterable to check.
    :type iterable: Iterable
    :param items: The items to search for.
    :type items: Any
    :param msg: The exception message, leave empty to use the default, defaults to ""
    Ex: msg="{iter} does not contain the items: {items}."
    :type msg: str, optional

    Raises
    ~~~~~~
    :raises TypeError: If iterable is not an Iterable.
    :raises: ValueError: If the iterable does not contain the items.

    Example Usage
    ~~~~~~~~~~~~~
    >>> ensure_contains((0, 1, 2, 3), 3)
    >>> ensure_contains(('a', 'b', 'c', 'd'), 'e')
    ValueError: expected ('a', 'b', 'c', 'd') to contain the items: 'e'
    """

    if not contains(iterable, *items):
        _msg_chk(msg)

        item_names = ", ".join([repr(i) for i in items])

        if msg:
            msg = msg.format(iter=repr(iterable), items=item_names)
        else:
            msg = f"expected {repr(iterable)} to contain the items: {item_names}"

        raise ValueError(msg)


def is_superclass_of(superclass, *subclasses):
    """
    is_superclass_of()
    ------------------
    Verifies the given subclasses are subclasses of the superclass.

    Parameters
    ~~~~~~~~~~
    :param superclass: The superclass.
    :type superclass: Type
    :param subclasses: The subclasses to check.
    :type subclasses: Type

    Raises
    ~~~~~~
    :raises TypeError: If superclass is not a type.
    :raises TypeError: If any subclass in subclasses is not a type.

    Return
    ------
    :return: True if the subclasses are subclasses of the superclass, otherwise False.
    :rtype: bool

    Example Usage
    ~~~~~~~~~~~~~
    >>> is_superclass_of(Exception, TypeError)
    True
    >>> is_superclass_of(int, str)
    False
    """

    # type checks
    if not isinstance(superclass, type):
        raise TypeError("'superclass' must be a type")
    if not all(isinstance(s, type) for s in subclasses):
        raise TypeError("all subclasses given must be types")

    if all(issubclass(sub, superclass) for sub in subclasses):
        return True
    return False


def ensure_superclass_of(superclass, *subclasses, msg=""):
    """
    ensure_superclass_of()
    ----------------------
    Ensures the given subclasses are all subclasses of the superclass.

    Parameters
    ~~~~~~~~~~
    :param superclass: The superclass.
    :type superclass: Type
    :param subclasses: The subclasses to check.
    :type subclasses: Type
    :param msg: The exception message, leave empty to use the default, defaults to ""
    Ex: msg="Not all of the classes: {subs} are subclasses of {super}."
    :type msg: str, optional

    Raises
    ~~~~~~
    :raises TypeError: If superclass is not a type.
    :raises TypeError: If any subclass in subclasses is not a type.
    :raises ValueError: If the subclasses are not subclasses of the superclass.

    Example Usage
    ~~~~~~~~~~~~~
    >>> ensure_superclass_of(Exception, TypeError)
    >>> ensure_superclass_of(int, str)
    ValueError: expected subclasses of 'int', got 'str' instead
    """

    if not is_superclass_of(superclass, *subclasses):
        _msg_chk(msg)

        subclass_names = ", ".join([repr(sub.__name__) for sub in subclasses])

        if msg:
            msg = msg.format(super=repr(superclass.__name__), subs=subclass_names)
        else:
            msg = f"expected subclasses of {repr(superclass.__name__)}, got {subclass_names} instead"

        raise ValueError(msg)


def ensure_callable(*objs, msg=""):
    """
    ensure_callable()
    -----------------
    Ensures the given objects are callable.

    Parameters
    ~~~~~~~~~~
    :param objs: The objects to check.
    :type objs: object
    :param msg: The exception message, leave empty to use the default, defaults to ""
    Ex: msg="{objs} are not all callable."
    :type msg: str, optional

    Raises
    ~~~~~~
    :raises TypeError: If the objects are not callable.

    Example Usage
    ~~~~~~~~~~~~~
    >>> def func(*args, **kwargs):
    ...     return None
    ...
    >>> ensure_callable(func)
    >>> x = 5
    >>> ensure_callable(x)
    TypeError: expected callable objects, got 5 instead
    """

    if all(callable(o) for o in objs):
        return

    _msg_chk(msg)

    obj_names = ", ".join([repr(o) for o in objs])

    if msg:
        msg = msg.format(objs=obj_names)
    else:
        msg = f"expected callable objects, got {obj_names} instead"

    raise TypeError(msg)


def contains_duplicates(*objs):
    """
    contains_duplicates()
    ---------------------
    Determines if the given objects contain duplicate items.

    Parameters
    ~~~~~~~~~~
    :param objs: The objects to check.
    :type objs: Iterable

    Raises
    ~~~~~~
    :raises TypeError: If any of the objects in objs are not an Iterable.

    Return
    ------
    :return: True if the objects contain duplicates, otherwise False.
    :rtype: bool

    Example Usage
    ~~~~~~~~~~~~~
    >>> l1 = [1, 2, 3, 4]
    >>> contains_duplicates(l1)
    False
    >>> l2 = [1, 2, 3, 1]
    >>> contains_duplicates(l2)
    True
    """

    # type checks
    if not all(isinstance(o, Iterable) for o in objs):
        raise TypeError("each obj given must be an Iterable")

    if all(len(o) == len(set(o)) for o in objs):
        return True
    return False


def ensure_no_duplicates(*objs, msg=""):
    """
    ensure_no_duplicates()
    ----------------------
    Ensures the given object has no duplicate items inside.

    Parameters
    ~~~~~~~~~~
    :param objs: The objects to check.
    :type objs: Iterable
    :param msg: The exception message, leave empty to use the default, defaults to ""
    Ex: msg="{objs} contain duplicates."
    :type msg: str, optional

    Raises
    ~~~~~~
    :raises TypeError: If any of the objects in objs are not an Iterable.
    :raises ValueError: If the objects contain duplicate items.

    Example Usage
    ~~~~~~~~~~~~~
    >>> l1 = [1, 2, 3, 4]
    >>> ensure_no_duplicates(l1)
    >>> l2 = [1, 2, 3, 1]
    >>> ensure_no_duplicates(l2)
    ValueError: object(s) [1, 2, 3, 1] contain duplicate items, expected no duplicates
    """

    if contains_duplicates(*objs):
        _msg_chk(msg)

        obj_names = ", ".join(repr(o) for o in objs)

        if msg:
            msg = msg.format(objs=obj_names)
        else:
            msg = (
                f"object(s) {obj_names} contain duplicate items, expected no duplicates"
            )

        raise TypeError(msg)
