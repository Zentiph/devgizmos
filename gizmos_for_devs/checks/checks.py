"""_checks.checks
-----------------
Module used for checking certain cases.
Mainly used for type and value checking function parameters.
"""


def verify_types(v, /, *types, err_msg=""):
    """Verifies the given value is one of the expected types, otherwise raises a TypeError.

    :param v: The value to check.
    :type v: Any
    :param types: The expected types.
    :type types: Type
    :param err_msg: A custom error message if changed, defaults to ""
        - below is a list of supported fields to be used in an unformatted string:
        - value: The checked value.
        - types: A tuple of the expected types.
        - Ex: err_msg="{value} is not one of the expected types: {types}."
    :type err_msg: str, optional
    """

    for type_ in types:
        if isinstance(v, type_):
            return

    type_names = ', '.join([type_.__name__ for type_ in types])

    if err_msg:
        err_msg = err_msg.format(value=repr(v), types=type_names)
    else:
        err_msg = f"{repr(v)} is not one of the expected types: {type_names}"

    raise TypeError(err_msg)


def verify_values(v, /, *values, err_msg=""):
    """Verifies the given value is one of the expected values, otherwise raises a ValueError.

    :param v: The value to check.
    :type v: Any
    :param values: The expected values.
    :type values: Any
    :param err_msg: A custom error message if changed, defaults to ""
        - below is a list of supported fields to be used in an unformatted string:
        - value: The checked value.
        - values: A tuple of the expected values.
        - Ex: err_msg="{value} is not one of the expected values: {values}."
    :type err_msg: str, optional
    """

    for value in values:
        if v == value:
            return

    value_names = ', '.join([repr(value) for value in values])

    if err_msg:
        err_msg = err_msg.format(value=repr(v), values=value_names)
    else:
        err_msg = f"{repr(v)} is not one of the expected values: {value_names}"

    raise ValueError(err_msg)


def verify_in_range(v, seq, start_index=-1, end_index=-1, *, err_msg=""):
    """Verifies the given value is in the specified range in the sequence,
    otherwise raises a ValueError.

    :param v: The value to check.
    :type v: Any
    :param seq: The sequence to check within.
    :type seq: Sequence
    :param start_index: The start index of the range, defaults to -1.
    :type start_index: int
    :param end_index: The end index of the range, defaults to -1.
    :type end_index: int
    :param err_msg: A custom error message if changed, defaults to ""
        - below is a list of supported fields to be used in an unformatted string:
        - value: The checked value.
        - seq: The sequence being checked.
        - start: The start index of the range.
        - end: The end index of the range.
        - Ex: err_msg="{value} is not within the range {start}-{end} in {seq}."
    :type err_msg: str, optional
    """

    if start_index == -1:
        start_index = 0
    if end_index == -1:
        end_index = len(seq) - 1

    if v in seq[start_index:end_index+1]:
        return

    if err_msg:
        err_msg = err_msg.format(
            value=repr(v),
            seq=repr(seq),
            start=start_index,
            end=end_index
        )
    else:
        err_msg = f"{repr(v)} is not within the range: " \
            + f"({start_index}, {end_index}) in {repr(seq)}."

    raise ValueError(err_msg)


def verify_not_none(
    value,
    *,
    err_msg=""
): ...


def verify_length(
    value,
    min_length,
    max_length,
    *,
    err_msg=""
): ...


def verify_not_empty(
    value,
    *,
    err_msg=""
): ...


def verify_regex(
    value: str,
    regex: str,
    *,
    err_msg=""
): ...


def verify_key_in_dict(
    d,
    key,
    *,
    err_msg=""
): ...


def verify_contains(
    iterable,
    item,
    *,
    err_msg=""
): ...


def verify_subclass(
    subclass,
    superclass,
    *,
    err_msg=""
): ...


def verify_callable(
    value,
    *,
    err_msg=""
): ...
