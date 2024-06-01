"""_checks.checks
-----------------
Module used for checking certain cases.
Mainly used for type and value checking function parameters.
"""

def verify_types(v, /, *types, raise_exc=True, exc_msg=""):
    """checks.verify_types
    ----------------------
    Verifies the given value is one of the expected types.
    Either raises a TypeError or returns False depending on raise_exc.

    :param v: The value to check.

    :type v: Any

    :param types: The expected types.

    :type types: Type

    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.

    :type raise_exc: bool, optional

    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - value: The checked value.
    - types: A tuple of the expected types.
    - Ex: exc_msg="{value} is not one of the expected types: {types}."

    :type exc_msg: str, optional

    :return: True if the value is a member of one of the expected types, otherwise False.

    :rtype: bool
    """

    for type_ in types:
        if isinstance(v, type_):
            return True

    type_names = ', '.join([type_.__name__ for type_ in types])

    if exc_msg:
        exc_msg = exc_msg.format(value=repr(v), types=type_names)
    else:
        exc_msg = f"{repr(v)} is not one of the expected types: {type_names}"

    if raise_exc:
        raise TypeError(exc_msg)
    return False


def verify_values(v, /, *values, raise_exc=True, exc_msg=""):
    """checks.verify_values
    -----------------------
    Verifies the given value is one of the expected values.
    Either raises a ValueError or returns False depending on raise_exc.

    :param v: The value to check.

    :type v: Any

    :param values: The expected values.

    :type values: Any

    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.

    :type raise_exc: bool, optional

    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - value: The checked value.
    - values: A tuple of the expected values.
    - Ex: exc_msg="{value} is not one of the expected values: {values}."

    :type exc_msg: str, optional

    :return: True if the value is equal to one of the expected values, otherwise False.

    :rtype: bool
    """

    for value in values:
        if v == value:
            return True

    value_names = ', '.join([repr(value) for value in values])

    if exc_msg:
        exc_msg = exc_msg.format(value=repr(v), values=value_names)
    else:
        exc_msg = f"{repr(v)} is not one of the expected values: {value_names}"

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def verify_in_range(v, /, seq, start=-1, end=-1, *, raise_exc=True, exc_msg=""):
    """checks.verify_in_range
    -------------------------
    Verifies the given value is in the specified range in the sequence provided.
    Either raises a ValueError or returns False depending on raise_exc.

    :param v: The value to check.

    :type v: Any

    :param seq: The sequence to check within.

    :type seq: Sequence

    :param start: The start index of the range to check (inclusive).

    :type start: int, optional

    :param end: The end index of the range to check (inclusive).

    :type end: int, optional

    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.

    :type raise_exc: bool, optional

    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - value: The checked value.
    - seq: The sequence being checked.
    - start: The start index.
    - end: The end index.
    - Ex: exc_msg="{value} is not in the sequence {seq} in the range ({start}, {end})."

    :type exc_msg: str, optional

    :return: True if the value is in the inclusive range in the sequence, otherwise False.

    :rtype: bool
    """

    # set the indexes to the start/end if they are negative
    start = max(start, 0)
    if end < 0:
        end = len(seq)

    if v in seq[start:end]:
        return True

    if exc_msg:
        exc_msg = exc_msg.format(
            value=repr(v),
            seq=repr(seq),
            start=start,
            end=end
        )
    else:
        exc_msg = f"{repr(v)} is not within the range: " \
            + f"({start}, {end}) in {repr(seq)}."

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def verify_truthy(v, /, *, raise_exc=True, exc_msg=""):
    """checks.verify_truthy
    -----------------------
    Verifies the given value is truthy.
    Either raises a ValueError or returns False depending on raise_exc.

    :param v: The value to check.

    :type v: Any

    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.

    :type raise_exc: bool, optional

    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - value: The checked value.
    - Ex: exc_msg="{value} is not truthy."

    :type exc_msg: str, optional

    :return: True if the value is truthy, otherwise False.

    :rtype: bool
    """

    if v:
        return True

    if exc_msg:
        exc_msg = exc_msg.format(value=repr(v))
    else:
        exc_msg = f"{repr(v)} is falsy."

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def verify_not_none(v, /, *, raise_exc=True, exc_msg=""):
    """checks.verify_not_none
    -------------------------
    Verifies the given value is not None.
    Either raises a ValueError or returns False depending on raise_exc.

    :param v: The value to check.

    :type v: Any

    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.

    :type raise_exc: bool, optional

    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - value: The checked value.
    - Ex: exc_msg="{value} is None."

    :type exc_msg: str, optional

    :return: True if the value is not None, otherwise False.

    :rtype: bool
    """

    if v is not None:
        return True

    if exc_msg:
        exc_msg = exc_msg.format(value=repr(v))
    else:
        exc_msg = f"{repr(v)} is None."

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def verify_length(v, min_length, max_length=-1, *, raise_exc=True, exc_msg=""):
    """checks.verify_length
    -----------------------
    Verifies the given value has a length in the specified range provided.
    Either raises a ValueError or returns False depending on raise_exc.

    :param v: The value to check.

    :type v: Any

    :param min_length: The minimum length allowed (inclusive).

    :type min_length: int

    :param max_length: The maximum length allowed (inclusive), defaults to -1.
    - If max_length is negative, there will be no upper length limit.

    :type max_length: int, optional

    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.

    :type raise_exc: bool, optional

    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - value: The checked value.
    - min: The minimum length.
    - max: The maximum length.
    - Ex: exc_msg="len({value}) is not in the range ({min}, {max})."

    :type exc_msg: str, optional

    :return: True if the value's length is within the inclusive range, otherwise False.

    :rtype: bool
    """

    # if the upper limit is not specified, only use a lower limit
    if max_length < 0 and len(v) >= min_length:
        return True
    # otherwise, check the length normally
    if min_length <= len(v) <= max_length:
        return True

    if exc_msg:
        exc_msg = exc_msg.format(
            value=repr(v),
            min=min_length,
            max=max_length
        )
    else:
        exc_msg = f"len({repr(v)}) is not in the range ({min_length}, {max_length})."

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def verify_regex(
    value: str,
    regex: str,
    *,
    raise_exc=True, exc_msg=""
): ...


def verify_key_in_dict(
    d,
    key,
    *,
    raise_exc=True, exc_msg=""
): ...


def verify_contains(
    iterable,
    item,
    *,
    raise_exc=True, exc_msg=""
): ...


def verify_subclass(
    subclass,
    superclass,
    *,
    raise_exc=True, exc_msg=""
): ...


def verify_callable(
    v,
    *,
    raise_exc=True, exc_msg=""
): ...
