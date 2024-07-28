"""
info.__info
===========
Contains code information related functionality.
"""

from functools import wraps
from warnings import warn

from ..errguards import ensure_instance_of


def tracer(*, entry_fmt="", exit_fmt=""):
    """
    tracer
    ======
    Logs entries and exits of the decorated function.

    Parameters
    ----------
    :param entry_fmt: Used to enter a custom message format, defaults to "".
    - Leave as an empty string to use the pre-made message, or enter None for no message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - Ex: entry_fmt="Entering func {name} with args={args} and kwargs={kwargs}."\n
    :type entry_fmt: str | None, optional
    :param exit_fmt: Used to enter a custom message format, defaults to "".
    - Leave as an empty string to use the pre-made message, or enter None for no message.
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - returned: The return value of the function.
    - Ex: fmt="Exiting func {name} with args={args} and kwargs={kwargs}; Returned {returned}."\n
    :type exit_fmt: str | None, optional

    Raises
    ------
    :raises TypeError: If entry_fmt is not a str.
    :raises TypeError: If exit_fmt is not a str.

    Example Usage
    -------------
    ```python
    >>> @tracer()
    ... def func(*args, **kwargs):
    ...     return all(args)
    ...
    >>> func(1, 2, word="Hello")
    [TRACER]: ENTERING FUNC func WITH args=(1, 2) AND kwargs={'word': 'Hello'}
    [TRACER]: EXITING FUNC func WITH args=(1, 2) AND kwargs={'word': 'Hello'}; RETURNED True
    True
    ```
    """

    # type checks
    ensure_instance_of(entry_fmt, str, optional=True)
    ensure_instance_of(exit_fmt, str, optional=True)

    if entry_fmt is None and exit_fmt is None:
        warn(
            "Both entry_fmt and exit_fmt are None. No logging will occur.",
            UserWarning,
        )

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if entry_fmt is not None:
                if entry_fmt:
                    print(
                        entry_fmt.format(name=func.__name__, args=args, kwargs=kwargs)
                    )
                else:
                    print(
                        f"[TRACER]: ENTERING FUNC {func.__name__} WITH {args=} AND {kwargs=}"
                    )

            result = func(*args, **kwargs)

            if exit_fmt is not None:
                if exit_fmt:
                    print(
                        exit_fmt.format(
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
