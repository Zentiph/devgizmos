"""
regex.__rtools
--------------
Module containing regex validation functions.
"""

from functools import partial
from re import match as re_match

from ..errguards import ensure_instance_of
from .__regexes import EMAIL, IPV4, IPV6


def matches(regex, *strings):
    """
    matches()
    ---------
    Determines whether the given strings match the regex provided.

    Parameters
    ~~~~~~~~~~
    :param regex: The regex to check.
    :type regex: str
    :param strings: The strings to check.
    :type strings: str

    Raises
    ~~~~~~
    :raises TypeError: If regex is not a str.
    :raises TypeError: If any object in strings is not a str.

    Return
    ~~~~~~
    :return: True if the strings all match the regex, otherwise False.
    :rtype: bool

    Example Usage
    ~~~~~~~~~~~~~
    >>> matches(r'^\\S+@\\S+\\.\\S+$', "name@example.com")
    True
    >>> matches(r'^\\S+@\\S+\\.\\S+$', "hello")
    False
    """

    # type checks
    ensure_instance_of(regex, str)
    for s in strings:
        ensure_instance_of(s, str)

    if all(re_match(regex, s) for s in strings):
        return True
    return False


def ensure_matches(regex, *strings, msg=""):
    """
    ensure_matches()
    ----------------
    Ensures the given strings match the regex provided.

    Parameters
    ~~~~~~~~~~
    :param regex: The regex to compare the strings to.
    :type regex: str
    :param strings: The strings to check.
    :type strings: str
    :param msg: The exception message; leave empty to use the default, defaults to ""
    Ex: msg="{strings} do not match the regex: {regex}."
    :type msg: str, optional

    Raises
    ~~~~~~
    :raises TypeError: If regex is not a str.
    :raises TypeError: If any object in strings is not a str.
    :raises ValueError: If the strings do not match the regex.

    Example Usage
    ~~~~~~~~~~~~~
    >>> ensure_matches(r'^\\S+@\\S+\\.\\S+$', "name@example.com")
    >>> ensure_matches(r'^\\S+@\\S+\\.\\S+$', "hello")
    ValueError: expected strings 'hello' to match the regex: '^\\S+@\\S+\\.\\S+$'
    """

    if not matches(regex, *strings):
        ensure_instance_of(msg, str)

        string_names = ", ".join(repr(s) for s in strings)

        if msg:
            msg = msg.format(strings=string_names, regex=repr(regex))
        else:
            msg = f"expected strings {string_names} to match the regex: {repr(regex)}"

        raise ValueError(msg)


is_email = partial(matches, EMAIL)
is_ipv4 = partial(matches, IPV4)
is_ipv6 = partial(matches, IPV6)


def is_ip(*strings):  # pylint: disable=missing-docstring
    return is_ipv4(*strings) or is_ipv6(*strings)
