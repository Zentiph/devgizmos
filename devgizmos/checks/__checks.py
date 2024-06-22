"""checks.__checks
-----------------
Module used for checking certain cases.
Mainly used for type and value checking function parameters.
"""

from re import match as re_match


__all__ = [
    "check_types",
    "check_values",
    "check_in_range",
    "check_in_bounds",
    "check_truthy",
    "check_not_none",
    "check_length",
    "check_regexes",
    "check_keys_in_dict",
    "check_contains",
    "check_subclasses",
    "check_callables",
]


def check_types(value, /, *types, optional=False, raise_exc=True, exc_msg=""):
    """checks.check_types
    ----------------------
    Verifies the given value is one of the expected types.
    Either raises a TypeError or returns False depending on raise_exc.

    :param value: The value to check.

    :type value: Any

    :param types: The expected types.

    :type types: Type

    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.

    :type raise_exc: bool, optional

    :param optional: Whether the types are optional, meaning the value can be None, defaults to False.

    :type optional: bool

    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - value: The checked value.
    - types: A tuple of the expected types.
    - Ex: exc_msg="{value} is not one of the expected types: {types}."

    :type exc_msg: str, optional

    :return: True if the value is a member of one of the expected types, otherwise False.

    :rtype: bool
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


def check_values(value, /, *values, raise_exc=True, exc_msg=""):
    """checks.check_values
    -----------------------
    Verifies the given value is one of the expected values.
    Either raises a ValueError or returns False depending on raise_exc.

    :param value: The value to check.

    :type value: Any

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


def check_in_range(value, seq, /, start=-1, end=-1, *, raise_exc=True, exc_msg=""):
    """checks.check_in_range
    -------------------------
    Verifies the given value is in the specified range in the sequence provided.
    Either raises a ValueError or returns False depending on raise_exc.

    :param value: The value to check.

    :type value: Any

    :param seq: The sequence to check within.

    :type seq: Sequence

    :param start: The start index of the range to check (inclusive).
    - Will be set to 0 if negative.

    :type start: int, optional

    :param end: The end index of the range to check (inclusive).
    - Will be set to the final index if negative.

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

    if value in seq[start:end]:
        return True

    if exc_msg:
        exc_msg = exc_msg.format(value=repr(value), seq=repr(seq), start=start, end=end)
    else:
        exc_msg = (
            f"{repr(value)} is not within the range: "
            + f"({start}, {end}) in {repr(seq)}."
        )

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def check_in_bounds(
    value, lower, upper, /, inclusive=True, *, raise_exc=True, exc_msg=""
):
    """checks.check_in_bounds
    -------------------------

    :param value: The value to check.

    :type value: int | float

    :param lower: The lower bound.
    - If None, no lower bound will be set.

    :type lower: int | float | None

    :param upper: The upper bound.
    - If None, no upper bound will be set.

    :type upper: int | float | None

    :param inclusive: Whether the bounds are inclusive or exclusive, defaults to True.

    :type inclusive: bool, optional

    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.

    :type raise_exc: bool, optional

    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - value: The checked value.
    - lower: The lower bound.
    - upper: The upper bound.
    - Ex: exc_msg="{value} is not in the bounds ({lower}, {upper})."

    :type exc_msg: str, optional

    :return: True if the value is within the bounds, otherwise False.

    :rtype: bool
    """

    def _helper(default, exc_msg):
        if raise_exc:
            if exc_msg:
                exc_msg = exc_msg.format(value=value, lower=lower, upper=upper)
            else:
                exc_msg = default

            raise ValueError(exc_msg)
        return False

    # ugly code, but if it works...
    if upper is None:
        if not inclusive:
            if value > lower:
                return True

            _helper(f"{value} must be greater than {lower}.", exc_msg)
        elif value >= lower:
            return True

        _helper(f"{value} must be greater than or equal to {lower}.", exc_msg)

    elif lower is None:
        if not inclusive:
            if value < upper:
                return True

            _helper(f"{value} must be less than {upper}.", exc_msg)
        elif value <= upper:
            return True

        _helper(f"{value} must be less than or equal to {upper}.", exc_msg)

    elif upper and lower:
        if not inclusive:
            if lower < value < upper:
                return True

            _helper(
                f"{value} must be greater than {lower} and less than {upper}.", exc_msg
            )
        elif lower <= value <= upper:
            return True

        _helper(
            f"{value} must be greater than or equal to {lower} and less than or equal to {upper}.",
            exc_msg,
        )

    # if both bounds are None return True since there is no upper or lower bound
    return True


def check_positive(*values, raise_exc=True, exc_msg=""):
    """checks.check_positive
    ------------------------

    :param values: The values to check.

    :type values: int | float

    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.

    :type raise_exc: bool, optional

    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - values: The checked values.
    - Ex: exc_msg="At least one of these values are not positive: {values}."

    :type exc_msg: str, optional

    :return: True if the all of the values are positive, otherwise False.
    """

    if all(v > 0 for v in values):
        return True

    if raise_exc:
        value_names = ", ".join([repr(v) for v in values])

        if exc_msg:
            exc_msg = exc_msg.format(values=value_names)
        else:
            exc_msg = f"At least one of these values are not positive: {value_names}"

        raise ValueError(exc_msg)
    return False


def check_truthy(*values, raise_exc=True, exc_msg=""):
    """checks.check_truthy
    -----------------------
    Verifies the given values are truthy.
    Either raises a ValueError or returns False depending on raise_exc.

    :param values: The values to check.

    :type values: Any

    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.

    :type raise_exc: bool, optional

    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - values: The checked values.
    - Ex: exc_msg="{values} are not all truthy."

    :type exc_msg: str, optional

    :return: True if all of the values are truthy, otherwise False.

    :rtype: bool
    """

    # if all the values in values are truthy, return True
    if all(values):
        return True

    value_names = ", ".join([repr(v) for v in values])

    if exc_msg:
        exc_msg = exc_msg.format(values=value_names)
    else:
        exc_msg = f"At least one of these values are falsy: {value_names}."

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def check_not_none(*values, raise_exc=True, exc_msg=""):
    """checks.check_not_none
    -------------------------
    Verifies the given values are not None.
    Either raises a ValueError or returns False depending on raise_exc.

    :param values: The values to check.

    :type values: Any

    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.

    :type raise_exc: bool, optional

    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - values: The checked values.
    - Ex: exc_msg="{values} are not all not None."

    :type exc_msg: str, optional

    :return: True if all of the values are not None, otherwise False.

    :rtype: bool
    """

    if all(v is not None for v in values):
        return True

    value_names = ", ".join([repr(v) for v in values])

    if exc_msg:
        exc_msg = exc_msg.format(values=value_names)
    else:
        exc_msg = f"At least one of these values are None: {value_names}."

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def check_length(value, /, min_length, max_length=-1, *, raise_exc=True, exc_msg=""):
    """checks.check_length
    -----------------------
    Verifies the given value has a length in the specified range provided.
    Either raises a ValueError or returns False depending on raise_exc.

    :param value: The value to check.

    :type value: Sized

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
    if max_length < 0 and len(value) >= min_length:
        return True
    # otherwise, check the length normally
    if min_length <= len(value) <= max_length:
        return True

    if exc_msg:
        exc_msg = exc_msg.format(value=repr(value), min=min_length, max=max_length)
    else:
        exc_msg = (
            f"len({repr(value)}) is not in the range ({min_length}, {max_length})."
        )

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def check_regexes(string, *regexes, raise_exc=True, exc_msg=""):
    """checks.check_regexes
    ------------------------
    Verifies the given string matches the regexes provided.
    Either raises a ValueError or returns False depending on raise_exc.

    :param string: The string to check.

    :type string: str

    :param regexes: The regexes to compare to.

    :type regexes: str

    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.

    :type raise_exc: bool, optional

    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - string: The checked string.
    - regexes: The regexes to match with.
    - Ex: exc_msg="{string} does not match any of the regexes: {regexes}."

    :type exc_msg: str, optional

    :return: True if the string matches one of the regexes, otherwise False.

    :rtype: bool
    """

    for regex in regexes:
        if re_match(regex, string):
            return True

    regex_names = ", ".join([repr(r) for r in regexes])

    if exc_msg:
        exc_msg = exc_msg.format(string=repr(string), regexes=regex_names)
    else:
        exc_msg = f"{repr(string)} does not match one of the regexes: {regex_names}."

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def check_keys_in_dict(dictionary, *keys, raise_exc=True, exc_msg=""):
    """checks.check_keys_in_dict
    -----------------------------
    Verifies the given dictionary contains the keys provided.
    Either raises a KeyError or returns False depending on raise_exc.

    :param dictionary: The dictionary to check.

    :type dictionary: Dict[Any, Any]

    :param keys: The keys to search for.

    :type keys: Any

    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.

    :type raise_exc: bool, optional

    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - dict: The checked dictionary.
    - keys: The keys to search for.
    - Ex: exc_msg="{dict} does not contain the keys: {keys}."

    :type exc_msg: str, optional

    :return: True if the dictionary contains each of the keys, otherwise False.

    :rtype: bool
    """

    for k in keys:
        if k in dictionary.keys():
            return True

    key_names = ", ".join([repr(k) for k in keys])

    if exc_msg:
        exc_msg = exc_msg.format(dict=repr(dictionary), keys=key_names)
    else:
        exc_msg = f"{repr(dictionary)} does not contain the keys: {key_names}."

    if raise_exc:
        raise KeyError(exc_msg)
    return False


def check_contains(iterable, *items, raise_exc=True, exc_msg=""):
    """checks.check_contains
    -------------------------
    Verifies the given iterable contains the items provided.
    Either raises a ValueError or returns False depending on raise_exc.

    :param iterable: The iterable to check.

    :type iterable: Iterable

    :param items: The items to search for.

    :type items: Any

    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.

    :type raise_exc: bool, optional

    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - iter: The checked iterable.
    - items: The items to search for.
    - Ex: exc_msg="{iter} does not contain the items: {items}."

    :type exc_msg: str, optional

    :return: True if the iterable contains each of the items, otherwise False.

    :rtype: bool
    """

    for i in items:
        if i in iterable:
            return True

    item_names = ", ".join([repr(i) for i in items])

    if exc_msg:
        exc_msg = exc_msg.format(iter=repr(iterable), items=item_names)
    else:
        exc_msg = f"{repr(iterable)} does not contain the items: {item_names}."

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def check_subclasses(superclass, *subclasses, raise_exc=True, exc_msg=""):
    """checks.check_subclasses
    ---------------------------
    Verifies the given subclasses are all subclasses of the superclass.
    Either raises a ValueError or returns False depending on raise_exc.

    :param superclass: The superclass.

    :type superclass: Type

    :param subclasses: The subclasses to check.

    :type subclasses: Type

    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.

    :type raise_exc: bool, optional

    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - super: The superclass.
    - subs: The subclasses.
    - Ex: exc_msg="Not all of the classes: {subs} are subclasses of {super}."

    :type exc_msg: str, optional

    :return: True if each of the subclasses are subclasses of the superclass, otherwise False.

    :rtype: bool
    """

    if all(issubclass(sub, superclass) for sub in subclasses):
        return True

    subclass_names = ", ".join([repr(sub) for sub in subclasses])

    if exc_msg:
        exc_msg = exc_msg.format(super=repr(superclass), subs=subclass_names)
    else:
        exc_msg = f"{repr(superclass)} is not a superclass of all the classes: {subclass_names}."

    if raise_exc:
        raise ValueError(exc_msg)
    return False


def check_callables(*objs, raise_exc=True, exc_msg=""):
    """checks.check_callables
    --------------------------
    Verifies the given objects are callable.
    Either raises a TypeError or returns False depending on raise_exc.

    :param objs: The objects to check.

    :type objs: object

    :param raise_exc: Whether to raise an exception, defaults to True
    - If True, the corresponding exception will be raised.
    - If False, will return False instead of raising an exception.

    :type raise_exc: bool, optional

    :param exc_msg: A custom exception message if changed, defaults to ""
    - Below is a list of supported fields to be used in an unformatted string:
    - objs: The checked objects.
    - Ex: exc_msg="{objs} are not all callable."

    :type exc_msg: str, optional

    :return: True if each of the objects are callable, otherwise False.

    :rtype: bool
    """

    if all(callable(o) for o in objs):
        return True

    obj_names = ", ".join([repr(o) for o in objs])

    if exc_msg:
        exc_msg = exc_msg.format(objs=obj_names)
    else:
        exc_msg = f"At least one of these objects is not callable: {obj_names}."

    if raise_exc:
        raise TypeError(exc_msg)
    return False
