"""decorators.decorators
------------------------
Module containing decorators.
"""

from functools import wraps
from platform import system
from time import perf_counter_ns, sleep

from ..checks import verify_types, verify_values

if system() in ("Darwin", "Linux"):
    # pylint: disable=no-name-in-module
    from signal import SIGALRM, alarm, signal  # type: ignore
elif system() == "Windows":
    # pylint: disable=no-name-in-module
    from threading import Thread
else:
    raise Exception("What OS are you on!?!?!")


__all__ = ["timer", "retry", "timeout"]

TIMER_UNITS = ("ns", "us", "ms", "s")


def timer(unit="ns", precision=0, *, msg_format=""):
    """decorators.timer
    -------------------
    Times how long function it is decorated to takes to run.

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

    # type checks
    verify_types(unit, str)
    verify_types(precision, int)
    verify_types(msg_format, str)

    # value checks
    verify_values(unit, *TIMER_UNITS)

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

            msg = None
            if msg_format:
                msg = msg_format.format(
                    name=funcname,
                    elapsed=rounded,
                    unit=unit,
                    args=args,
                    kwargs=kwargs,
                    returned=repr(result),
                )
            elif msg_format == "":
                msg = f"[TIMER]: {funcname} RAN IN {rounded} {local_unit}"

            if msg:
                print(msg)

            return result

        return wrapper

    return decorator


def retry(
    max_attempts=3,
    delay=1,
    *,
    exceptions=(Exception,),
    raise_last=True,
    success_msg_format="",
    failure_msg_format="",
):
    """decorators.retry
    -------------------
    Retries a function if it fails up until the number of attempts is reached.

    :param max_attempts: The maximum number of times to attempt running the decorated function,
    including the first time, defaults to 3

    :type max_attempts: int, optional

    :param delay: The time in seconds to wait after each retry, defaults to 1

    :type delay: int, optional

    :param exceptions: A tuple of the exceptions to catch and retry on, defaults to (Exception,)

    :type exceptions: Tuple[Type[Exception], ...], optional

    :param raise_last: Whether to raise the final exception raised when all attempts fail,
    defaults to True

    :type raise_last: bool, optional

    :param success_msg_format: Used to enter a custom success message format, defaults to ""
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - attempts: The number of attempts that ran.
    - max_attempts: The maximum number of attempts allotted.
    - exceptions: The exceptions to be caught.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - returned: The return value of the function.
    - Ex: success_msg_format="Func {name} took {attempts}/{max_attempts} attempts to run."

    :type success_msg_format: str, optional

    :param failure_msg_format: Used to enter a custom failure message format, defaults to ""
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - attempts: The current number of attempts.
    - max_attempts: The maximum number of attempts allotted.
    - exceptions: The exceptions to be caught.
    - raised: The exception raised.
    - args: The arguments passed to the function.
    - kwargs: The keyword arguments passed to the function.
    - Ex: failure_msg_format="Func {name} failed at attempt {attempts}/{max_attempts}."

    :type failure_msg_format: str, optional

    """

    # type checks
    verify_types(max_attempts, int)
    verify_types(delay, int, float)
    verify_types(exceptions, tuple)
    for exc in exceptions:
        verify_types(exc, type)
    verify_types(raise_last, bool)
    verify_types(success_msg_format, str)
    verify_types(failure_msg_format, str)

    # value checks
    if max_attempts < 1:
        raise ValueError("max_attempts cannot be less than 1.")
    if delay < 0:
        raise ValueError("delay cannot be less than 0.")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            funcname = func.__name__
            attempts = 0

            while attempts < max_attempts:
                try:
                    result = func(*args, **kwargs)

                    msg = None
                    if success_msg_format:
                        msg = success_msg_format.format(
                            name=funcname,
                            attempts=attempts + 1,
                            max_attempts=max_attempts,
                            exceptions=exceptions,
                            args=args,
                            kwargs=kwargs,
                            returned=repr(result),
                        )
                    elif success_msg_format == "":
                        msg = f"[RETRY]: {funcname} SUCCESSFULLY RAN AFTER {attempts + 1}/{max_attempts} ATTEMPTS"

                    if msg:
                        print(msg)

                    return result

                except exceptions as e:
                    attempts += 1

                    msg = None
                    if failure_msg_format:
                        msg = failure_msg_format.format(
                            name=funcname,
                            attempts=attempts,
                            max_attempts=max_attempts,
                            exceptions=exceptions,
                            raised=repr(e),
                            args=args,
                            kwargs=kwargs,
                        )
                    elif failure_msg_format == "":
                        msg = f"[RETRY]: {funcname} FAILED AT ATTEMPT {attempts}/{max_attempts}; RAISED {repr(e)}"

                        if msg:
                            print(msg)

                    if attempts >= max_attempts and raise_last:
                        raise

                    sleep(delay)

            return None

        return wrapper

    return decorator


def timeout(cutoff, *, success_msg_format="", failure_msg_format=""):
    """decorators.timeout
    ---------------------
    Times out a function if it takes longer than the cutoff time to complete.
    Utilizes signal on Linux or MacOS; utilizes threading on Windows.
    Raises a TimeoutError by default. Enter a different exception type
    to change the exception, or None to not raise an exception.

    :param cutoff: The cutoff time, in seconds.

    :type cutoff: Union[int, float]

    :param success_msg_format: Used to enter a custom success message format if changed, defaults to ""
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - cutoff: The cutoff time.

    :type success_msg_format: str, optional

    :param failure_msg_format: Used to enter a custom failure message format if changed, defaults to ""
    - Enter an unformatted string with the following fields to include their values
    - name: The name of the function.
    - cutoff: The cutoff time.

    :type failure_msg_format: str, optional
    """

    # type checks
    verify_types(cutoff, int, float)
    verify_types(success_msg_format, str)
    verify_types(failure_msg_format, str)

    # value checks
    if cutoff < 0:
        raise ValueError("cutoff cannot be less than 0.")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            funcname = func.__name__

            if system() in ("Darwin", "Linux"):

                def _handle_timeout(signum, frame):
                    raise TimeoutError(
                        f"Function {funcname} timed out after {cutoff} seconds."
                    )

                original_handler = signal(SIGALRM, _handle_timeout)
                alarm(cutoff)

                try:
                    result = func(*args, **kwargs)
                    alarm(0)

                    msg = None
                    if success_msg_format:
                        msg = success_msg_format.format(name=funcname, cutoff=cutoff)
                    elif success_msg_format == "":
                        msg = f"[TIMEOUT]: {funcname} SUCCESSFULLY RAN IN UNDER {cutoff} SECONDS"

                    if msg:
                        print(msg)

                    return result

                except TimeoutError:
                    alarm(0)

                    msg = None
                    if failure_msg_format:
                        msg = failure_msg_format.format(name=funcname, cutoff=cutoff)
                    elif failure_msg_format == "":
                        msg = f"[TIMEOUT]: {funcname} TIMED OUT AFTER {cutoff} SECONDS"

                    if msg:
                        print(msg)

                    raise

                finally:
                    signal(SIGALRM, original_handler)

            if system() == "Windows":
                # initialize as lists to allow for modifications in nests
                result = [None]
                exc_raised = [False]

                def target():
                    try:
                        result[0] = func(*args, **kwargs)
                    except Exception as e:
                        result[0] = e
                        exc_raised[0] = True

                thread = Thread(target=target)
                thread.daemon = True
                thread.start()
                thread.join(cutoff)
                if thread.is_alive():
                    thread.join()

                    msg = None
                    if failure_msg_format:
                        msg = failure_msg_format.format(name=funcname, cutoff=cutoff)
                    elif failure_msg_format == "":
                        msg = f"[TIMEOUT]: {funcname} TIMED OUT AFTER {cutoff} SECONDS"
                    if msg:
                        print(msg)

                    raise TimeoutError(
                        f"Function {funcname} timed out after {cutoff} seconds."
                    )

                # handle unexpected exceptions
                if exc_raised[0]:
                    # pylint: disable=raising-bad-type
                    raise result[0]

                msg = None
                if success_msg_format:
                    msg = success_msg_format.format(name=funcname, cutoff=cutoff)
                elif success_msg_format == "":
                    msg = f"[TIMEOUT]: {funcname} SUCCESSFULLY RAN IN UNDER {cutoff} SECONDS"

                if msg:
                    print(msg)

                return result[0]

        return wrapper

    return decorator
