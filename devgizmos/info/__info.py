"""
info.__info
===========
Contains code information related functionality.
"""

from functools import wraps
from warnings import warn

from ..errguards import ensure_instance_of


def tracer(*, entry_msg="", exit_msg=""):
    """
    tracer()
    --------
    Logs entries and exits of the decorated function.

    Parameters
    ~~~~~~~~~~
    :param entry_msg: Used to enter a custom message format, defaults to "".
    Ex: entry_msg="Entering func {name} with args={args} and kwargs={kwargs}."
    :type entry_msg: str | None, optional
    :param exit_msg: Used to enter a custom message format, defaults to "".
    Ex: exit_msg="Exiting func {name} with args={args} and kwargs={kwargs}; Returned {returned}."
    :type exit_msg: str | None, optional

    Raises
    ~~~~~~
    :raises TypeError: If entry_msg is not a str.
    :raises TypeError: If exit_msg is not a str.

    Example Usage
    ~~~~~~~~~~~~~
    >>> @tracer()
    ... def func(*args, **kwargs):
    ...     return all(args)
    ...
    >>> func(1, 2, word="Hello")
    [TRACER]: ENTERING FUNC func WITH args=(1, 2) AND kwargs={'word': 'Hello'}
    [TRACER]: EXITING FUNC func WITH args=(1, 2) AND kwargs={'word': 'Hello'}; RETURNED True
    True
    """

    # type checks
    ensure_instance_of(entry_msg, str, optional=True)
    ensure_instance_of(exit_msg, str, optional=True)

    if entry_msg is None and exit_msg is None:
        warn(
            "Both entry_msg and exit_msg are None. No logging will occur.",
            UserWarning,
        )

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if entry_msg is not None:
                if entry_msg:
                    print(
                        entry_msg.format(name=func.__name__, args=args, kwargs=kwargs)
                    )
                else:
                    print(
                        f"[TRACER]: ENTERING FUNC {func.__name__} WITH {args=} AND {kwargs=}"
                    )

            result = func(*args, **kwargs)

            if exit_msg is not None:
                if exit_msg:
                    print(
                        exit_msg.format(
                            name=func.__name__,
                            args=args,
                            kwargs=kwargs,
                            returned=result,
                        )
                    )
                else:
                    print(
                        f"[TRACER]: EXITING FUNC {func.__name__} WITH {args=} AND {kwargs=}; RETURNED {result}"
                    )

            return result

        return wrapper

    return decorator
