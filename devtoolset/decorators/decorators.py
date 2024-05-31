"""decorators.decorators
------------------------

Module containing decorators for the package.
"""


from functools import wraps
from time import perf_counter_ns

__all__ = [
    "timer",

]

TIMER_UNITS = ("ns", "us", "ms", "s")


def timer(unit="ns", precision=0, *, msg_format=""):
    """decorators.timer
    -------------------
    Standard timer decorator.

    Parameters
    ----------
    :param unit: The unit of time to use, defaults to "ns"
        - Supported units are "ns", "us", "ms", "s"
        - If an invalid unit is provided, unit will default to "ns".

    :type unit: str, optional

    :param precision: The precision to use when rounding the time, defaults to 0

    :type precision: int, optional

    :param msg_format: Used to enter a custom message format, defaults to ""
        - Enter an unformatted string with the following fields to include their values
        - name: The name of the function.
        - elapsed: The time elapsed by the function's execution.
        - unit: The unit used in the timing.
        - args: The arguments passed to the function.
        - kwargs: The keyword arguments passed to the function.
        - returned: The return value of the function.
        - Ex: msg_format="Func {name} took {elapsed} {unit} to run and returned {returned}."

    :type msg_format: str, optional
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            local_unit = unit.lower()
            if local_unit not in TIMER_UNITS:
                local_unit = "ns"

            funcname = func.__name__

            start_time = perf_counter_ns()
            result = func(*args, **kwargs)

            delta = perf_counter_ns() - start_time
            elapsed = delta / (1000 ** TIMER_UNITS.index(local_unit))
            rounded = round(elapsed, precision)

            if msg_format:
                msg = msg_format.format(
                    name=funcname,
                    elapsed=rounded,
                    unit=unit,
                    args=args,
                    kwargs=kwargs,
                    returned=repr(result)
                )
            else:
                msg = f"[TIMER]: {funcname} RAN IN {rounded} {local_unit}"

            print(msg)
            return result

        return wrapper

    return decorator
