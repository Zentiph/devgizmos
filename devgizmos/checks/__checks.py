"""
checks.__checks
===============

Module used for checking certain cases.
Mainly used for type and value checking function parameters.
"""

from re import match as re_match


def check_type(value, type_or_tuple, /, optional=False, *, raise_exc=True, exc_msg=""):
    """
    check_type
    ==========
    Verifies the given value is the expected type(s).
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param value: The value to check.
    :type value: Any
    :param type_or_tuple: The expected type or a tuple of expected types.
    :type type_or_tuple: Type | Tuple[Type, ...]
    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.\n
    :type raise_exc: bool, optional
    :param optional: Whether the types are optional, meaning the value can be None, defaults to False.
    :type optional: bool
    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - value: The checked value.
    - types: A tuple of the expected types.
    - Ex: exc_msg="{value} is not one of the expected types: {types}."\n
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
    ```python
    >>> check_type(10, int)
    True
    >>> check_type(True, (float, str), raise_exc=False)
    False
    >>> check_type(True, (float, str))
    TypeError: True is not one of the expected types: float, str
    ```
    """

    if isinstance(type_or_tuple, tuple):
        types = type_or_tuple
    else:
        types = (type_or_tuple,)

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


def check_value(value, value_or_tuple, /, *, raise_exc=True, exc_msg=""):
    """
    check_values
    ============
    Verifies the given value is the expected value(s).
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param value: The value to check.
    :type value: Any
    :param value_or_tuple: The expected value or a tuple of expected values.
    :type value_or_tuple: Any | Tuple[Any, ...]
    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.\n
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - value: The checked value.
    - values: A tuple of the expected values.
    - Ex: exc_msg="{value} is not one of the expected values: {values}."\n
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
    ```python
    >>> APPROVED_VALUES = (0, 1, 2, 3)
    >>> check_value(2, APPROVED_VALUES)
    True
    >>> check_value(7, APPROVED_VALUES, raise_exc=False)
    False
    >>> check_value(7, APPROVED_VALUES)
    ValueError: 7 is not one of the expected values: 0, 1, 2, 3
    ```
    """

    if isinstance(value_or_tuple, tuple):
        values = value_or_tuple
    else:
        values = (value_or_tuple,)

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


def check_in_range(value, seq, /, start=None, end=None, *, raise_exc=True, exc_msg=""):
    """
    check_in_range
    ==============
    Verifies the given value is in the specified range in the sequence provided.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param value: The value to check.
    :type value: Any
    :param seq: The sequence to check within.
    :type seq: Sequence
    :param start: The start index of the range to check (inclusive).
    - Will be set to 0 if None.\n
    :type start: int | None, optional
    :param end: The end index of the range to check (inclusive).
    - Will be set to the final index if None.\n
    :type end: int | None, optional
    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.\n
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - value: The checked value.
    - seq: The sequence being checked.
    - start: The start index.
    - end: The end index.
    - Ex: exc_msg="{value} is not in the sequence {seq} in the range ({start}, {end})."\n
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
    ```python
    >>> check_in_range(3, range(0, 4))
    True
    >>> check_in_range(10, range(0, 4), raise_exc=False)
    False
    >>> check_in_range(10, range(0, 4))
    ValueError: 10 is not within the range: (0, 4) in range(0, 4)
    ```
    """

    # set the indexes to the start/end if they are None
    if start is None:
        start = 0
    if end is None:
        end = len(seq)

    if value in seq[start:end]:
        return True

    if exc_msg:
        exc_msg = exc_msg.format(value=repr(value), seq=repr(seq), start=start, end=end)
    else:
        exc_msg = (
            f"{repr(value)} is not within the range: "
            + f"({start}, {end}) in {repr(seq)}"
        )

    if raise_exc:
        raise ValueError(exc_msg)
    return False


# what can ya do
# pylint: disable=too-many-return-statements
def check_in_bounds(
    value, lower, upper, /, inclusive=True, *, raise_exc=True, exc_msg=""
):
    """
    check_in_bounds
    ===============
    Verifies if the given value is within the lower and upper bounds.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param value: The value to check.
    :type value: Number
    :param lower: The lower bound.
    - If None, no lower bound will be set.\n
    :type lower: Number | None
    :param upper: The upper bound.
    - If None, no upper bound will be set.\n
    :type upper: Number | None
    :param inclusive: Whether the bounds are inclusive or exclusive, defaults to True.
    :type inclusive: bool, optional
    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.\n
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - value: The checked value.
    - lower: The lower bound.
    - upper: The upper bound.
    - Ex: exc_msg="{value} is not in the bounds ({lower}, {upper})."\n
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
    ```python
    >>> check_in_bounds(3, 1, 4)
    True
    >>> check_in_bounds(12, 1, 4, raise_exc=False)
    False
    >>> check_in_bounds(12, 1, 4)
    ValueError: 12 must be greater than or equal to 1 and less than or equal to 4
    ```
    """

    def raise_or_return(default):
        if raise_exc:
            raise ValueError(exc_msg or default)
        return False

    if lower is not None and upper is not None:
        if inclusive:
            if lower <= value <= upper:
                return True
            return raise_or_return(
                f"{value} must be greater than or equal to {lower} and less than or equal to {upper}"
            )

        if lower < value < upper:
            return True
        return raise_or_return(
            f"{value} must be greater than {lower} and less than {upper}"
        )

    if lower is not None:
        if inclusive:
            if value >= lower:
                return True
            return raise_or_return(f"{value} must be greater than or equal to {lower}")

        if value > lower:
            return True
        return raise_or_return(f"{value} must be greater than {lower}")

    if upper is not None:
        if inclusive:
            if value <= upper:
                return True
            return raise_or_return(f"{value} must be less than or equal to {upper}")

        if value < upper:
            return True
        return raise_or_return(f"{value} must be less than {upper}")

    # if both bounds are None, return True
    # since there is no upper or lower bound
    return True


def check_truthy(value, *, raise_exc=True, exc_msg=""):
    """
    check_truthy
    ============
    Verifies the given value(s) is/are truthy.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param value: The value to check.
    :type value: Any
    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.\n
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - value: The checked value.
    - Ex: exc_msg="{value} is falsy."\n
    :type exc_msg: str, optional

    Raises
    ------
    :raises ValueError: If raise_exc is True and the value is falsy.

    Return
    ------
    :return: True if the value is truthy, otherwise False.
    :rtype: bool

    Example Usage
    -------------
    ```python
    >>> check_truthy(10)
    True
    >>> check_truthy(0, raise_exc=False)
    False
    >>> check_truthy(0)
    ValueError: 0 is falsy
    ```
    """

    if value:
        return True

    if exc_msg:
        exc_msg = exc_msg.format(value=repr(value))
    else:
        exc_msg = f"{repr(value)} is falsy"

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def check_not_none(value, *, raise_exc=True, exc_msg=""):
    """
    check_not_none
    ==============
    Verifies the given value is not None.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param value: The value to check.
    :type value: Any
    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.\n
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    :type exc_msg: str, optional

    Raises
    ------
    :raises ValueError: If raise_exc is True and the value is None.

    Return
    ------
    :return: True if all of the values are not None, otherwise False.
    :rtype: bool

    Example Usage
    -------------
    ```python
    >>> check_not_none(10)
    True
    >>> check_not_none(None, raise_exc=False)
    False
    >>> check_not_none(None)
    ValueError: Unwanted None value
    ```
    """

    if value is not None:
        return True

    if raise_exc:
        raise ValueError(exc_msg or "Unwanted None value")
    return False


def check_length(value, /, min_length, max_length=-1, *, raise_exc=True, exc_msg=""):
    """
    check_length
    ============
    Verifies the given value has a length in the specified range provided.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param value: The value to check.
    :type value: Sized
    :param min_length: The minimum length allowed (inclusive).
    :type min_length: int
    :param max_length: The maximum length allowed (inclusive), defaults to -1.
    - If max_length is negative, there will be no upper length limit.\n
    :type max_length: int, optional
    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.\n
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - value: The checked value.
    - min: The minimum length.
    - max: The maximum length.
    - Ex: exc_msg="len({value}) is not in the range ({min}, {max})."\n
    :type exc_msg: str, optional

    Raises
    ------
    :raises ValueError: If raise_exc is True and the sized value's length is not in the allowed range.

    Return
    ------
    :return: True if the value's length is within the inclusive range, otherwise False.
    :rtype: bool

    Example Usage
    -------------
    ```python
    >>> check_length([1, 2, 3], 2, 4)
    True
    >>> check_length([0, 1, 2, 3, 4], 1, 3, raise_exc=False)
    False
    >>> check_length([0, 1, 2, 3, 4], 1, 3)
    ValueError: len([0, 1, 2, 3, 4] is not in the range (1, 3))
    ```
    """

    # if the upper limit is not specified, only use a lower limit
    if max_length < 0 and len(value) >= min_length:
        return True
    # otherwise, check the length normally
    if min_length <= len(value) <= max_length:
        return True

    if exc_msg:
        exc_msg = exc_msg.format(value=repr(value), min=min_length, max=max_length)
    else:
        exc_msg = f"len({repr(value)}) is not in the range ({min_length}, {max_length})"

    if raise_exc:
        raise ValueError(exc_msg)
    return False


# pylint: disable=anomalous-backslash-in-string
def check_regex(string, regex, /, *, raise_exc=True, exc_msg=""):
    """
    check_regex
    ===========
    Verifies the given string matches the regex provided.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param string: The string to check.
    :type string: str
    :param regex: The regex to compare to.
    :type regex: str
    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.\n
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - string: The checked string.
    - regex: The regex to match with.
    - Ex: exc_msg="{string} does not match the regex: {regex}."\n
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
    ```python
    >>> check_regex("name@example.com", r'^\S+@\S+\.\S+$')
    True
    >>> check_regex("hello", r'^\S+@\S+\.\S+$', raise_exc=False)
    False
    >>> check_regex("hello", r'^\S+@\S+\.\S+$')
    ValueError: 'hello' does not match the regex: '^\\S+@\\S+\\.\\S+$'
    ```
    """

    if re_match(regex, string):
        return True

    if exc_msg:
        exc_msg = exc_msg.format(string=repr(string), regex=repr(regex))
    else:
        exc_msg = f"{repr(string)} does not match the regex: {repr(regex)}"

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def check_key_in_dict(dictionary, key_or_tuple, /, *, raise_exc=True, exc_msg=""):
    """
    check_key_in_dict
    =================
    Verifies the given dictionary contains the key(s) provided.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param dictionary: The dictionary to check.
    :type dictionary: Dict[Any, Any]
    :param key_or_tuple: The key to search for or a tuple of keys to search for.
    :type key_or_tuple: Any | Tuple[Any, ...]
    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.\n
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - dict: The checked dictionary.
    - keys: The keys to search for.
    - Ex: exc_msg="{dict} does not contain the keys: {keys}."\n
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
    ```python
    >>> ages = {"Bob": 24, "Martha": 22}
    >>> check_key_in_dict(ages, ("Bob", "Martha"))
    True
    >>> check_key_in_dict(ages, "Kevin", raise_exc=False)
    False
    >>> check_key_in_dict(ages, "Kevin")
    KeyError: "{'Bob': 24, 'Martha': 22} does not contain the keys: 'Kevin'"
    ```
    """

    if isinstance(key_or_tuple, tuple):
        keys = key_or_tuple
    else:
        keys = (key_or_tuple,)

    for k in keys:
        if k in dictionary.keys():
            return True

    key_names = ", ".join([repr(k) for k in keys])

    if exc_msg:
        exc_msg = exc_msg.format(dict=repr(dictionary), keys=key_names)
    else:
        exc_msg = f"{repr(dictionary)} does not contain the keys: {key_names}"

    if raise_exc:
        raise KeyError(exc_msg)
    return False


def check_contains(iterable, item_or_tuple, /, *, raise_exc=True, exc_msg=""):
    """
    check_contains
    ==============
    Verifies the given iterable contains the item(s) provided.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param iterable: The iterable to check.
    :type iterable: Iterable
    :param item_or_tuple: The item to search for or a tuple of items to search for.
    :type item_or_tuple: Any | Tuple[Any, ...]
    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.\n
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - iter: The checked iterable.
    - items: The items to search for.
    - Ex: exc_msg="{iter} does not contain the items: {items}."\n
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
    ```python
    >>> check_contains((0, 1, 2, 3), 3)
    True
    >>> check_contains(('a', 'b', 'c', 'd'), 'e', raise_exc=False)
    False
    >>> check_contains(('a', 'b', 'c', 'd'), 'e')
    ValueError: ('a', 'b', 'c', 'd') does not contain the items: 'e'
    ```
    """

    if isinstance(item_or_tuple, tuple):
        items = item_or_tuple
    else:
        items = (item_or_tuple,)

    for i in items:
        if i in iterable:
            return True

    item_names = ", ".join([repr(i) for i in items])

    if exc_msg:
        exc_msg = exc_msg.format(iter=repr(iterable), items=item_names)
    else:
        exc_msg = f"{repr(iterable)} does not contain the items: {item_names}"

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def check_subclass(superclass, subclass_or_tuple, /, *, raise_exc=True, exc_msg=""):
    """
    check_subclass
    ==============
    Verifies the given subclass(es) is/are (a) subclass(es) of the superclass.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param superclass: The superclass.
    :type superclass: Type
    :param subclass_or_tuple: The subclass or a tuple of subclasses to check.
    :type subclass_or_tuple: Type | Tuple[Type, ...]
    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.\n
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - super: The superclass.
    - subs: The subclasses.
    - Ex: exc_msg="Not all of the classes: {subs} are subclasses of {super}."\n
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
    ```python
    >>> check_subclass(Exception, TypeError)
    True
    >>> check_subclass(int, str, raise_exc=False)
    False
    >>> check_subclass(int, str)
    ValueError: int is not a superclass of all the classes: str
    ```
    """

    if isinstance(subclass_or_tuple, tuple):
        subclasses = subclass_or_tuple
    else:
        subclasses = (subclass_or_tuple,)

    if all(issubclass(sub, superclass) for sub in subclasses):
        return True

    subclass_names = ", ".join([sub.__name__ for sub in subclasses])

    if exc_msg:
        exc_msg = exc_msg.format(super=superclass.__name__, subs=subclass_names)
    else:
        exc_msg = f"{superclass.__name__} is not a superclass of all the classes: {subclass_names}"

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def check_callable(obj_or_tuple, /, *, raise_exc=True, exc_msg=""):
    """
    check_callable
    ==============
    Verifies the given object(s) is/are callable.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param obj_or_tuple: The object or a tuple of objects to check.
    :type obj_or_tuple: object | Tuple[object, ...]
    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.\n
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - objs: The checked objects.
    - Ex: exc_msg="{objs} are not all callable."\n
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
    ```python
    >>> def func(*args, **kwargs):
    ...     return None
    ...
    >>> check_callable(func)
    True
    >>> x = 5
    >>> check_callable(x, raise_exc=False)
    False
    >>> check_callable(x)
    TypeError: One of these objects is not callable: 5
    ```
    """

    if isinstance(obj_or_tuple, tuple):
        objs = obj_or_tuple
    else:
        objs = (obj_or_tuple,)

    if all(callable(o) for o in objs):
        return True

    obj_names = ", ".join([repr(o) for o in objs])

    if exc_msg:
        exc_msg = exc_msg.format(objs=obj_names)
    else:
        exc_msg = f"One of these objects is not callable: {obj_names}"

    if raise_exc:
        raise TypeError(exc_msg)
    return False


def check_no_duplicates(obj, /, *, raise_exc=True, exc_msg=""):
    """
    check_no_duplicates
    ===================
    Verifies the given object has no duplicate items inside.
    Returns a boolean if raise_exc is False, otherwise raises an exception.

    Parameters
    ----------
    :param obj: The object to check.
    :type obj: object
    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.\n
    :type raise_exc: bool, optional
    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - obj: The checked object.
    - Ex: exc_msg="{obj} contains duplicates."\n
    :type exc_msg: str, optional

    Raises
    ------
    :raises ValueError: If raise_exc is True and the object contains duplicate items.

    Return
    ------
    :return: True if the object does not contain duplicates, otherwise False.
    :rtype: bool

    Example Usage
    -------------
    ```python
    >>> l1 = [1, 2, 3, 4]
    >>> check_no_duplicates(l1)
    True
    >>> l2 = [1, 2, 3, 1]
    >>> check_no_duplicates(l2, raise_exc=False)
    False
    >>> check_no_duplicates(l2)
    ValueError: [1, 2, 3, 1] contains duplicate items
    ```
    """

    if len(obj) == len(set(obj)):
        return True

    if exc_msg:
        exc_msg = exc_msg.format(obj=repr(obj))
    else:
        exc_msg = f"{repr(obj)} contains duplicate items"

    if raise_exc:
        raise TypeError(exc_msg)
    return False
