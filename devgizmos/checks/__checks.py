"""
checks.__checks
===============

Module used for checking certain cases.
Mainly used for type and value checking function parameters.
"""

# TODO: add type/value checks

from re import match as re_match


def check_type(value, *types, optional=False, raise_exc=True, exc_msg=""):
    """
    check_type()
    ============
    Verifies the given value is the expected type(s).
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param value: The value to check.
    :type value: Any
    :param types: The expected types.
    :type types: Type
    :param optional: Whether the types are optional, meaning the value can be None, defaults to False.
    :type optional: bool
    :param raise_exc: Whether to raise an exception, defaults to True.
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to "".
    Ex: exc_msg="{value} is not one of the expected types: {types}."
    :type exc_msg: str, optional

    Raises
    ------
    :raises TypeError: If raise_exc is True and the value is not the expected type(s).

    Return
    ------
    :return: True if the value is a member of the expected type(s), otherwise False.
    :rtype: bool

    Example Usage
    -------------
    >>> check_type(10, int)
    True
    >>> check_type(True, (float, str), raise_exc=False)
    False
    >>> check_type(True, (float, str))
    TypeError: True is not one of the expected types: float, str
    """

    if isinstance(value, types):
        return True
    if optional and value is None:
        return True

    type_names = ", ".join([type_.__name__ for type_ in types])

    if exc_msg:
        exc_msg = exc_msg.format(value=repr(value), types=type_names)
    else:
        exc_msg = f"{repr(value)} is not one of the expected types: {type_names}"

    if raise_exc:
        raise TypeError(exc_msg)
    return False


def check_value(value, *values, raise_exc=True, exc_msg=""):
    """
    check_values()
    ==============
    Verifies the given value is the expected value(s).
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param value: The value to check.
    :type value: Any
    :param values: The expected values.
    :type values: Any
    :param raise_exc: Whether to raise an exception, defaults to True.
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to "".
    Ex: exc_msg="{value} is not one of the expected values: {values}."
    :type exc_msg: str, optional

    Raises
    ------
    :raises ValueError: If raise_exc is True and the value is not the expected value(s).

    Return
    ------
    :return: True if the value(s) is/are equal to one of the expected values, otherwise False.
    :rtype: bool

    Example Usage
    -------------
    >>> APPROVED_VALUES = (0, 1, 2, 3)
    >>> check_value(2, APPROVED_VALUES)
    True
    >>> check_value(7, APPROVED_VALUES, raise_exc=False)
    False
    >>> check_value(7, APPROVED_VALUES)
    ValueError: 7 is not one of the expected values: 0, 1, 2, 3
    """

    for v in values:
        if v == value:
            return True

    value_names = ", ".join([repr(value) for value in values])

    if exc_msg:
        exc_msg = exc_msg.format(value=repr(value), values=value_names)
    else:
        exc_msg = f"{repr(value)} is not one of the expected values: {value_names}"

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def check_in_range(value, seq, /, start=0, end=-1, *, raise_exc=True, exc_msg=""):
    """
    check_in_range()
    ================
    Verifies the given value is in the specified range in the sequence provided.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param value: The value to check.
    :type value: Any
    :param seq: The sequence to check within.
    :type seq: Sequence
    :param start: The start index of the range to check (inclusive), defaults to 0.
    :type start: int, optional
    :param end: The end index of the range to check (inclusive), defaults to -1 (checks the whole sequence).
    :type end: int, optional
    :param raise_exc: Whether to raise an exception, defaults to True.
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to "".
    Ex: exc_msg="{value} is not in the sequence {seq} in the range ({start}, {end})."
    :type exc_msg: str, optional

    Raises
    ------
    :raises ValueError: If raise_exc is True and the value is not within the range in the sequence.

    Return
    ------
    :return: True if the value is in the inclusive range in the sequence, otherwise False.
    :rtype: bool

    Example Usage
    -------------
    >>> check_in_range(3, range(0, 4))
    True
    >>> check_in_range(10, range(0, 4), raise_exc=False)
    False
    >>> check_in_range(10, range(0, 4))
    ValueError: expected 10 to be within the range: (0, 4) in range(0, 4)
    """

    if end == -1:
        end = len(seq)

    if value in seq[start:end]:
        return True

    if exc_msg:
        exc_msg = exc_msg.format(value=repr(value), seq=repr(seq), start=start, end=end)
    else:
        exc_msg = (
            f"expected {repr(value)} to be within the range: "
            + f"({start}, {end}) in {repr(seq)}"
        )

    if raise_exc:
        raise ValueError(exc_msg)
    return False


# what can ya do
# pylint: disable=too-many-return-statements
def check_in_bounds(
    value, lower, upper, /, *, inclusive=True, raise_exc=True, exc_msg=""
):
    """
    check_in_bounds()
    =================
    Verifies if the given value is within the lower and upper bounds.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param value: The value to check.
    :type value: int | float
    :param lower: The lower bound. If None, no lower bound will be set.
    :type lower: int | float | None
    :param upper: The upper bound. If None, no upper bound will be set.
    :type upper: int | float | None
    :param inclusive: Whether the bounds are inclusive or exclusive, defaults to True.
    :type inclusive: bool, optional
    :param raise_exc: Whether to raise an exception, defaults to True.
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to "".
    Ex: exc_msg="{value} is not in the bounds ({lower}, {upper})."
    :type exc_msg: str, optional

    Raises
    ------
    :raises ValueError: If raise_exc is True and the value is not within the bounds.

    Return
    ------
    :return: True if the value is within the bounds, otherwise False.
    :rtype: bool

    Example Usage
    -------------
    >>> check_in_bounds(3, 1, 4)
    True
    >>> check_in_bounds(12, 1, 4, raise_exc=False)
    False
    >>> check_in_bounds(12, 1, 4)
    ValueError: 12 must be >= 1 and <= 4
    """

    def raise_or_return(default):
        if raise_exc:
            raise ValueError(exc_msg or default)
        return False

    if lower is not None and upper is not None:
        if inclusive:
            if lower <= value <= upper:
                return True
            return raise_or_return(f"{value} must be >= {lower} and <= {upper}")

        if lower < value < upper:
            return True
        return raise_or_return(f"{value} must be > {lower} and < {upper}")

    if lower is not None:
        if inclusive:
            if value >= lower:
                return True
            return raise_or_return(f"{value} must be >= {lower}")

        if value > lower:
            return True
        return raise_or_return(f"{value} must be > {lower}")

    if upper is not None:
        if inclusive:
            if value <= upper:
                return True
            return raise_or_return(f"{value} must be <= {upper}")

        if value < upper:
            return True
        return raise_or_return(f"{value} must be < {upper}")

    # if both bounds are None, return True
    # since there is no upper or lower bound
    return True


# pylint: disable=anomalous-backslash-in-string
def check_regex(regex, *strings, raise_exc=True, exc_msg=""):
    """
    check_regex()
    =============
    Verifies the given string matches the regex provided.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param regex: The regex to compare the strings to.
    :type regex: str
    :param strings: The strings to check.
    :type strings: str
    :param raise_exc: Whether to raise an exception, defaults to True
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    Ex: exc_msg="{strings} do not match the regex: {regex}."
    :type exc_msg: str, optional

    Raises
    ------
    :raises ValueError: If raise_exc is True and the string does not match the regex.

    Return
    ------
    :return: True if the string matches the regex, otherwise False.
    :rtype: bool

    Example Usage
    -------------
    >>> check_regex(r'^\S+@\S+\.\S+$', "name@example.com")
    True
    >>> check_regex(r'^\S+@\S+\.\S+$', "hello", raise_exc=False)
    False
    >>> check_regex(r'^\S+@\S+\.\S+$', "hello")
    ValueError: expected strings 'hello' to match the regex: '^\\S+@\\S+\\.\\S+$'
    """

    if all(re_match(regex, s) for s in strings):
        return True

    string_names = ", ".join(repr(s) for s in strings)

    if exc_msg:
        exc_msg = exc_msg.format(strings=string_names, regex=repr(regex))
    else:
        exc_msg = f"expected strings {string_names} to match the regex: {repr(regex)}"

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def check_keys_in_dict(dictionary, *keys, raise_exc=True, exc_msg=""):
    """
    check_keys_in_dict()
    ====================
    Verifies the given dictionary contains the key(s) provided.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param dictionary: The dictionary to check.
    :type dictionary: Dict[Any, Any]
    :param keys: The keys to search for.
    :type keys: Any
    :param raise_exc: Whether to raise an exception, defaults to True
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    Ex: exc_msg="{dict} does not contain the keys: {keys}."
    :type exc_msg: str, optional

    Raises
    ------
    :raises KeyError: If raise_exc is True and the key(s) is/are not in the dictionary.

    Return
    ------
    :return: True if the dictionary contains each of the keys, otherwise False.
    :rtype: bool

    Example Usage
    -------------
    >>> ages = {"Bob": 24, "Martha": 22}
    >>> check_keys_in_dict(ages, "Bob", "Martha")
    True
    >>> check_keys_in_dict(ages, "Kevin", raise_exc=False)
    False
    >>> check_keys_in_dict(ages, "Kevin")
    KeyError: "expected {'Bob': 24, 'Martha': 22} to contain the keys: 'Kevin'"
    """

    if all(k in dictionary.keys() for k in keys):
        return True

    key_names = ", ".join([repr(k) for k in keys])

    if exc_msg:
        exc_msg = exc_msg.format(dict=repr(dictionary), keys=key_names)
    else:
        exc_msg = f"expected {repr(dictionary)} to contain the keys: {key_names}"

    if raise_exc:
        raise KeyError(exc_msg)
    return False


def check_contains(iterable, *items, raise_exc=True, exc_msg=""):
    """
    check_contains()
    ================
    Verifies the given iterable contains the item(s) provided.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param iterable: The iterable to check.
    :type iterable: Iterable
    :param items: The items to search for.
    :type items: Any
    :param raise_exc: Whether to raise an exception, defaults to True
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    Ex: exc_msg="{iter} does not contain the items: {items}."
    :type exc_msg: str, optional

    Raises
    ------
    :raises: ValueError: If raise_exc is True and the iterable does not contain the item(s).

    Return
    ------
    :return: True if the iterable contains the item(s), otherwise False.
    :rtype: bool

    Example Usage
    -------------
    >>> check_contains((0, 1, 2, 3), 3)
    True
    >>> check_contains(('a', 'b', 'c', 'd'), 'e', raise_exc=False)
    False
    >>> check_contains(('a', 'b', 'c', 'd'), 'e')
    ValueError: expected ('a', 'b', 'c', 'd') to contain the items: 'e'
    """

    if all(i in iterable for i in items):
        return True

    item_names = ", ".join([repr(i) for i in items])

    if exc_msg:
        exc_msg = exc_msg.format(iter=repr(iterable), items=item_names)
    else:
        exc_msg = f"expected {repr(iterable)} to contain the items: {item_names}"

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def check_subclass(superclass, *subclasses, raise_exc=True, exc_msg=""):
    """
    check_subclass()
    ================
    Verifies the given subclass(es) is/are (a) subclass(es) of the superclass.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param superclass: The superclass.
    :type superclass: Type
    :param subclasses: The subclasses to check.
    :type subclasses: Type
    :param raise_exc: Whether to raise an exception, defaults to True
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    Ex: exc_msg="Not all of the classes: {subs} are subclasses of {super}."
    :type exc_msg: str, optional

    Raises
    ------
    :raises ValueError: If the subclass(es) is/are not (a) subclass(es) of the superclass.

    Return
    ------
    :return: True if the subclass(es) is/are (a) subclass(es) of the superclass, otherwise False.
    :rtype: bool

    Example Usage
    -------------
    >>> check_subclass(Exception, TypeError)
    True
    >>> check_subclass(int, str, raise_exc=False)
    False
    >>> check_subclass(int, str)
    ValueError: expected subclasses of 'int', got 'str' instead
    """

    if all(issubclass(sub, superclass) for sub in subclasses):
        return True

    subclass_names = ", ".join([repr(sub.__name__) for sub in subclasses])

    if exc_msg:
        exc_msg = exc_msg.format(super=repr(superclass.__name__), subs=subclass_names)
    else:
        exc_msg = f"expected subclasses of {repr(superclass.__name__)}, got {subclass_names} instead"

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def check_callable(*objs, raise_exc=True, exc_msg=""):
    """
    check_callable()
    ================
    Verifies the given object(s) is/are callable.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param objs: The objects to check.
    :type objs: object
    :param raise_exc: Whether to raise an exception, defaults to True
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    Ex: exc_msg="{objs} are not all callable."
    :type exc_msg: str, optional

    Raises
    ------
    :raises TypeError: If raise_exc is True and the object(s) is/are not callable.

    Return
    ------
    :return: True if the object(s) is/are callable, otherwise False.
    :rtype: bool

    Example Usage
    -------------
    >>> def func(*args, **kwargs):
    ...     return None
    ...
    >>> check_callable(func)
    True
    >>> x = 5
    >>> check_callable(x, raise_exc=False)
    False
    >>> check_callable(x)
    TypeError: expected callable objects, got 5 instead
    """

    if all(callable(o) for o in objs):
        return True

    obj_names = ", ".join([repr(o) for o in objs])

    if exc_msg:
        exc_msg = exc_msg.format(objs=obj_names)
    else:
        exc_msg = f"expected callable objects, got {obj_names} instead"

    if raise_exc:
        raise TypeError(exc_msg)
    return False


def check_no_duplicates(*objs, raise_exc=True, exc_msg=""):
    """
    check_no_duplicates()
    =====================
    Verifies the given object has no duplicate items inside.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param objs: The objects to check.
    :type objs: object
    :param raise_exc: Whether to raise an exception, defaults to True
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    Ex: exc_msg="{objs} contain duplicates."
    :type exc_msg: str, optional

    Raises
    ------
    :raises ValueError: If raise_exc is True and the objects contain duplicate items.

    Return
    ------
    :return: True if the object does not contain duplicates, otherwise False.
    :rtype: bool

    Example Usage
    -------------
    >>> l1 = [1, 2, 3, 4]
    >>> check_no_duplicates(l1)
    True
    >>> l2 = [1, 2, 3, 1]
    >>> check_no_duplicates(l2, raise_exc=False)
    False
    >>> check_no_duplicates(l2)
    ValueError: objects [1, 2, 3, 1] contain duplicate items, expected no duplicates
    """

    if all(len(o) == len(set(o)) for o in objs):
        return True

    obj_names = ", ".join(repr(o) for o in objs)

    if exc_msg:
        exc_msg = exc_msg.format(objs=obj_names)
    else:
        exc_msg = f"objects {obj_names} contain duplicate items, expected no duplicates"

    if raise_exc:
        raise TypeError(exc_msg)
    return False
