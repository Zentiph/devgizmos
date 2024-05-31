# FOR REFERENCE ONLY

"""
decorpy
~~~~~~~
Module containing useful decorators for Python scripts. Inspired by Indently.
Decorators include: timer, retry

Created in Python 3.11.5
"""

# TODO:
# add support for multiple logs in one json
# error logging for raise_exceptions=False
# backoff for retry decorator (preset equations or custom with lambda)
# allow users to enter a list of exceptions to pay attention to for retry
#
# more decorators!!!!!!!!
# 1. timeout
# 2. param validation
# 3. singleton
# 4. rate-limiter
# 5. cache
# 6. log (calls, entry, exit, exceptions)
# 7. async WAY LATER
#
# add async as options in other decorators perhaps????

# * imports
from datetime import datetime as _datetime
from functools import wraps as _wraps
from json import dump as _dump
from os import stat as _stat
from time import perf_counter as _perf_counter
from time import sleep as _sleep
from typing import Any as _Any
from typing import Callable as _Callable

__all__ = ['timer', 'retry',
           'KILOBYTES', 'MEGABYTES', 'GIGABYTES', 'TERABYTES', 'PETABYTES', 'EXABYTES',
           'KIBIBYTES', 'MEBIBYTES', 'GIBIBYTES', 'TEBIBYTES', 'PEBIBYTES', 'EXBIBYTES',
           'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'KIB', 'MIB', 'GIB', 'TIB', 'PIB', 'EIB',
           'MICROSECONDS', 'MILLISECONDS', 'MINUTES', 'HOURS', 'DAYS', 'WEEKS',
           'US', 'MS', 'MIN', 'HR', 'D', 'WK']


# * globals
_DEFAULT_DT_FORMAT = "%Y-%m-%d %H:%M:%S"

KILOBYTES = 1e3
# storage units used for the retry decorator (param: logging_config['max_size'])
KB = 1e3
MEGABYTES = 1e6
MB = 1e6  # each unit equals the number of Bytes they represent since the default unit is Bytes
GIGABYTES = 1e9
GB = 1e9
TERABYTES = 1e12
TB = 1e12
PETABYTES = 1e15
PB = 1e15
EXABYTES = 1e18
EB = 1e18

KIBIBYTES = 2**10
KIB = 2**10
MEBIBYTES = 2**20
MIB = 2**20
GIBIBYTES = 2**30
GIB = 2**30
TEBIBYTES = 2**40
TIB = 2**40
PEBIBYTES = 2**50
PIB = 2**50
EXBIBYTES = 2**60
EIB = 2**60

MICROSECONDS = 1e-6
US = 1e-6  # time units for the timeout decorator (param: 'cutoff_time')
MILLISECONDS = 1e-3
MS = 1e-3  # each unit equals the number of seconds they represent since the default unit is seconds
MINUTES = 60
MIN = 60
HOURS = 3600
HR = 3600
DAYS = 86400
D = 86400
WEEKS = 604800
WK = 604800

# * custom exceptions


class _FileSizeExceededError(Exception):
    """FOR INTERNAL USE ONLY. Exception raised when a file size limit is in place and has been exceeded."""

    def __init__(self, file, max_size, msg="Attempted to write to a file whose size limit has been reached."):
        self.msg = msg + f" File: {file}. Max Size: {max_size} Bytes."
        super().__init__(self.msg)


# * helper funcs
def _init_config(config: dict) -> dict:
    """FOR INTERNAL USE ONLY."""

    if config is None:
        config = {'log_file': None, 'max_size': None, 'timestamp': None, 'datetime_format': None,
                  'prevent_file_creation': None, 'raise_exceptions': None}

    return config


def _handle_logging_config(msg: str, config: dict, json_data: dict | None) -> None:
    """FOR INTERNAL USE ONLY."""

    file_types = (".txt", ".log", ".json")

    log_file = config.get('log_file', '')
    if log_file:
        if not log_file.endswith(".txt") and not log_file.endswith(".log") and not log_file.endswith(".json"):
            raise ValueError(f"param 'logging_config['log_file']' must be one of the following file types: {
                             ', '.join(file_types)}.")

    # determine file type
    file_type = None
    if log_file:
        if log_file.endswith(".txt"):
            file_type = "txt"
        elif log_file.endswith(".log"):
            file_type = "log"
        elif log_file.endswith(".json"):
            file_type = "json"

    if log_file:
        prevent_file_creation = config.get('prevent_file_creation', True)
        raise_exceptions = config.get('raise_exceptions', True)
        # default max size to 5MB if not specified
        max_size = config.get('max_size', 5*MB)

        try:
            file_size = _stat(log_file).st_size
        except FileNotFoundError as e:
            if raise_exceptions and prevent_file_creation:
                raise FileNotFoundError(
                    f"{e!r}" + " (param 'logging_config['prevent_file_creation']' is set to 'True'!)")
            elif prevent_file_creation:
                error = e
                file_size = 0
                print(f"WARNING: {e!r} occurred when attempting to access file: {
                      log_file}. (param 'logging_config['prevent_file_creation']' is set to 'True'!)")
            else:
                file_size = 0

        if file_size < max_size:
            if prevent_file_creation:
                w_mode = 'r+'
            else:
                w_mode = 'a'

            if file_type == "json":
                data = json_data

            try:
                with open(log_file, w_mode) as file:
                    if w_mode == 'r+':
                        file.seek(0, 2)

                    if file_type == "txt" or file_type == "log":
                        file.write(msg + '\n')
                    elif file_type == "json" and data is not None:
                        _dump(data, file, indent=2)
                        file.write('\n')

            except (PermissionError, OSError) as e:
                if raise_exceptions:
                    raise e
                else:
                    error = e
                    print(f"WARNING: {
                          e!r} occurred when attempting to write to file: {log_file}")

        elif raise_exceptions and file_size >= max_size:  # file size error handling
            raise _FileSizeExceededError(file=log_file, max_size=max_size)
        elif file_size:
            print(f"WARNING: {_FileSizeExceededError(
                file=log_file, max_size=max_size)!r}")


# * decorators
def timer(decimal_places: int = 3, unit: str = 'seconds', print_msg: bool = True, include_params: bool = True,
          include_return: bool = True, msg_format: str = None, logging_config: dict = None
          ) -> _Callable:
    """
    A decorator used to measure the execution time of a function.

    :param decimal_places: Integer that determines the number of digits displayed after the decimal point, defaults to 3.

    :param unit: String that determines the unit of time displayed, defaults to 'seconds'. 
      - Supports: 'microseconds', 'milliseconds', 'seconds', 'minutes', 'hours', 'days', and common abbreviations thereof.

    :param print_msg: Bool that determines whether the output message is printed to the terminal, defaults to True.

    :param include_params: Bool that determines whether or not to include the args and kwargs of the timed function in the output message, defaults to False.

    :param include_return: Bool that determines whether or not to include the return value of the timed function in the output message, defaults to False.

    :param msg_format: String that dictates the formatting of the output message, defaults to None. (If None, a default msg format will be used.)
      - Fields: func_name, execution_time, unit (of time), args, kwargs, return_value, timestamp
      - Usage example:
      - msg_format="({timestamp}) Took {execution_time} {unit} for {func_name} to execute with args: {args} and kwargs: {kwargs} and returned: {return_value}."

    :param logging_config: Dict containing logging configurations with the following keys:
      - 'log_file': String specifying the path to the log file where the output message will be written. If falsy, logs will not be written to a file, defaults to ''.

      - 'max_size': Integer indicating the maximum size of the log file (in Bytes) where logs will no longer be written, defaults to 5e6 (5MB).

      - 'timestamp': Bool indicating whether to prepend a timestamp using datetime or not, defaults to True.

      - 'datetime_format': String specifying the timestamp format, defaults to the default datetime format: "%Y-%m-%d %H:%M:%S".

      - 'prevent_file_creation': Bool indicating whether to prevent log file creation if the given log file path does not exist, defaults to True.

      - 'raise_exceptions': Bool indicating whether to raise exceptions caused by file writing errors or not. If false, exceptions will be printed to the console instead, defaults to True.  

    :return: The decorated function.
    """

    # initializations
    logging_config = _init_config(logging_config)

    if msg_format is None:
        # default message format
        msg_format = "{timestamp} Func '{func_name}' executed in {execution_time} {unit}."
        if include_params:
            msg_format += " Args: {args}, Kwargs: {kwargs}."
        if include_return:
            msg_format += " Returned: {return_value}."

    unit_multipliers = {
        'microseconds': 1e6,
        'us': 1e6,
        'milliseconds': 1e3,
        'ms': 1e3,
        'seconds': 1,
        'secs': 1,
        's': 1,
        'minutes': 1/60,
        'mins': 1/60,
        'm': 1/60,
        'hours': 1/3600,
        'hrs': 1/3600,
        'h': 1/3600,
        'days': 1/86400,
        'd': 1/86400,
    }

    # value check
    if unit not in unit_multipliers:
        raise ValueError(f"param 'unit' must be in: {
                         ', '.join(unit_multipliers.keys())}.")

    time_multiplier = unit_multipliers[unit]

    # value checks cont.
    if decimal_places < 0:
        raise ValueError("param 'decimal_places' must be >= 0.")

    # do the stuff
    def decorator(func: _Callable) -> _Callable:
        @_wraps(func)
        def wrapper(*args, **kwargs) -> _Any:
            error = None

            start_t = _perf_counter()
            result = func(*args, **kwargs)
            end_t = _perf_counter()

            final_t = round((end_t - start_t) *
                            time_multiplier, decimal_places)

            # setup string segments
            timestamp = None
            # default to true if not specified
            if logging_config.get('timestamp', True):
                # default to regular format if not specified
                dt_format = logging_config.get(
                    'datetime_format', _DEFAULT_DT_FORMAT)
                timestamp = f"{_datetime.now().strftime(dt_format)}"

            msg = msg_format.format(
                func_name=func.__name__,
                execution_time=final_t,
                unit=unit,
                args=args if include_params else '',
                kwargs=kwargs if include_params else '',
                return_value=result if include_return else '',
                timestamp=timestamp if timestamp else ''
            )

            if print_msg:
                print(msg)

            json_data_format = {'func': f"{func.__name__}",
                                'execution_time': final_t,
                                'unit': unit,
                                'timestamp': timestamp}
            if include_params:
                json_data_format['params'] = {'args': args, 'kwargs': kwargs}
            if include_return:
                json_data_format['return_val'] = result

            _handle_logging_config(
                msg=msg, config=logging_config, json_data=json_data_format)

            return result
        return wrapper
    return decorator


def retry(attempts: int = 3, delay: int | float = 1, print_msgs: bool = True, include_params: bool = True, include_return: bool = True,
          msg_formats: dict = {
              'attempt_msg': "(Att {attempt_no}/{max_attempts}): Trying func '{func_name}'.",
              'success_msg': "[SUCCESS] (Att {attempt_no}/{max_attempts}): Func '{func_name}' succeeded.",
              'error_msg': "(Att {attempt_no}/{max_attempts}): Func '{func_name}' raised an exception: {error}.",
              'failure_msg': "[FAILURE] (Att {attempt_no}/{max_attempts}): Func '{func_name}' failed.",
              'start_msg': "({timestamp}) Starting attempts on {func_name}. Max Attempts: {max_attempts}.",
              'end_msg': "({timestamp}) Attempts on {func_name} finished after {attempt_no}/{max_attempts} attempts."
          }, logging_config: dict = None
          ) -> _Callable:
    """
    Decorator used to retry functions if they fail.

    :param attempts: The maximum number of attempts, defaults to 3

    :param delay: The delay between each attempt in seconds, defaults to 1.
      - For other units of time, multiply the amount of the unit by the unit constant.
      - Supported units: MICROSECONDS, MILLISECONDS, MINUTES, DAYS, WEEKS, and common abbreviations.
      - Ex: delay=1*MINUTES

    :param print_msgs: Bool that determines whether the output messages are printed to the terminal, defaults to True.

    :param include_params: Bool that determines whether or not to include the args and kwargs of the timed function in the output messages, defaults to True.

    :param include_return: Bool that determines whether or not to include the return value of the timed function in the success output message, defaults to True.

    :param msg_formats: Dict containing formats for each message type used in the decorator with the following keys:
      - 'attempt_msg': Message displayed at the beginning of each attempt.
        - Fields: attempt_no, max_attempts, func_name, args, kwargs
        - Example usage:
        - 'attempt_msg'="Attempt {attempt_no}/{max_attempts}: Running func {func_name}. Args: {args}. Kwargs: {kwargs}."

      - 'success_msg': Message displayed when the function succeeds.
        - Fields: attempt_no, max_attempts, func_name, args, kwargs, return_value
        - Example usage:
        - 'success_msg'="Attempt {attempt_no}/{max_attempts}: Success! Func {func_name} returned {return_value} with args {args} and kwargs {kwargs}."

      - 'error_msg': Message displayed when an exception occurs (not including KeyboardInterrupt).
        - Fields: attempt_no, max_attempts, func_name, args, kwargs, error
        - Example usage:
        - 'error_msg'="Attempt {attempt_no}/{max_attempts}: An error occurred when attempting func {func_name} with args {args} and kwargs {kwargs}: {error}."

      - 'failure_msg': Message displayed when the function fails every attempt.
        - Fields: attempt_no, max_attempts, func_name, args, kwargs
        - Example usage:
        - 'failure_msg'="Attempt {attempt_no}/{max_attempts}: Failure... Func {func_name} failed to complete."

      - 'start_msg': Message displayed before attempting the function with the time attempts began.
        - Fields: max_attempts, func_name, timestamp
        - Example usage:
        - 'start_msg'="{timestamp}: Beginning attempts on {func_name} with {max_attempts} max attempts."

      - 'end_msg': Message displayed after the function has succeeded or failed with the time attempts ended.
        - Fields: attempt_no, max_attempts, func_name, timestamp
        - Example usage:
        - 'end_msg'="{timestamp}: Finished attempts on {func_name} after {attempt_no}/{max_attempts} attempts."

    :param logging_config: Dict containing logging configurations with the following keys:
      - 'log_file': String specifying the path to the log file where the output message will be written. If falsy, logs will not be written to a file, defaults to ''.

      - 'max_size': Integer indicating the maximum size of the log file (in Bytes) where logs will no longer be written, defaults to 5*MEGABYTES.
        - For values in other units such as MB, multiply the amount of the unit by the constant of that unit.
        - Supported units: KILOBYTES, MEGABYTES, GIGABYTES, TERABYTES, PETABYTES, EXABYTES, KIBIBYTES, MEBIBYTES, GIBIBYTES, TEBIBYTES, PEBIBYTES, EXBIBYTES, and common abbreviations.
        - Ex: 'max_size'=2*MEGABYTES.

      - 'timestamp': Bool indicating whether to prepend a timestamp using datetime or not, defaults to True.

      - 'datetime_format': String specifying the timestamp format, defaults to the default datetime format: "%Y-%m-%d %H:%M:%S".

      - 'prevent_file_creation': Bool indicating whether to prevent log file creation if the given log file path does not exist, defaults to True.

      - 'raise_exceptions': Bool indicating whether to raise exceptions caused by file writing errors or not. If false, exceptions will be printed to the console instead, defaults to True.  

    :return: The decorated function.
    """

    # value checks
    if attempts < 1:
        raise ValueError("param 'attempts' must be >= 1.")
    if delay < 0:
        raise ValueError("param 'delay' must be >= 0.")

    # initializations
    logging_config = _init_config(logging_config)

    attempt_msg = msg_formats.get('attempt_msg')
    am_is_def = attempt_msg == "(Att {attempt_no}/{max_attempts}): Trying func '{func_name}'."
    if include_params and am_is_def:  # check if the default is being used
        attempt_msg += " Args: {args}. Kwargs: {kwargs}."

    success_msg = msg_formats.get('success_msg')
    sm_is_def = success_msg == "[SUCCESS] (Att {attempt_no}/{max_attempts}): Func '{func_name}' succeeded."
    if include_params and sm_is_def:
        success_msg += " Args: {args}. Kwargs: {kwargs}."
    if include_return and sm_is_def:
        success_msg += " Returned: {return_value}."

    error_msg = msg_formats.get('error_msg')
    em_is_def = error_msg == "(Att {attempt_no}/{max_attempts}): Func '{func_name}' raised an exception: {error}."
    if include_params and em_is_def:
        error_msg += " Args: {args}. Kwargs: {kwargs}."

    failure_msg = msg_formats.get('failure_msg')
    fm_is_def = failure_msg == "[FAILURE] (Att {attempt_no}/{max_attempts}): Func '{func_name}' failed."
    if include_params and fm_is_def:
        failure_msg += " Args: {args}. Kwargs: {kwargs}."

    start_msg = msg_formats.get('start_msg')
    end_msg = msg_formats.get('end_msg')

    # get real
    def decorator(func: _Callable) -> _Callable:
        @_wraps(func)
        def wrapper(*args, **kwargs) -> _Any:
            start_timestamp = None
            log_timestamps = logging_config.get('timestamps', True)
            if log_timestamps:
                # default to regular format if not specified
                dt_format = logging_config.get(
                    'datetime_format', _DEFAULT_DT_FORMAT)
                start_timestamp = f"{_datetime.now().strftime(dt_format)}"

            f_start_msg = start_msg.format(
                timestamp=start_timestamp,
                func_name=func.__name__,
                max_attempts=attempts
            )

            _handle_logging_config(
                msg=f_start_msg, config=logging_config, json_data=None)

            for attempt in range(1, attempts + 1):
                f_attempt_msg = attempt_msg.format(
                    attempt_no=attempt,
                    max_attempts=attempts,
                    func_name=func.__name__,
                    args=args if include_params else '',
                    kwargs=kwargs if include_params else ''
                )

                if print_msgs:
                    print(f_attempt_msg)

                try:  # do not log each attempt if json is given
                    if not logging_config['log_file'].endswith(".json"):
                        _handle_logging_config(
                            msg=f_attempt_msg, config=logging_config, json_data=None)
                except KeyboardInterrupt:
                    raise
                except Exception:
                    pass

                try:
                    result = func(*args, **kwargs)

                    end_timestamp = None
                    if log_timestamps:
                        end_timestamp = f"{
                            _datetime.now().strftime(dt_format)}"

                    f_end_msg = end_msg.format(
                        timestamp=end_timestamp,
                        func_name=func.__name__,
                        attempt_no=attempt,
                        max_attempts=attempts
                    )

                    f_success_msg = success_msg.format(
                        attempt_no=attempt,
                        max_attempts=attempts,
                        func_name=func.__name__,
                        args=args if include_params else '',
                        kwargs=kwargs if include_params else '',
                        return_value=result if include_return else ''
                    )

                    if print_msgs:
                        print(f_success_msg)
                        print(f_end_msg)

                    json_data_format = {
                        'func': f"{func.__name__}",
                        'attempt_no': attempt,
                        'max_attempts': attempts,
                        'status': 'success',
                    }
                    if include_params:
                        json_data_format['params'] = {
                            'args': args, 'kwargs': kwargs}
                    if include_return:
                        json_data_format['return_value'] = result
                    if log_timestamps:
                        json_data_format['timestamps'] = {
                            'start': start_timestamp, 'end': end_timestamp}

                    _handle_logging_config(
                        msg=f_success_msg, config=logging_config, json_data=json_data_format)
                    _handle_logging_config(
                        msg=f_end_msg + '\n', config=logging_config, json_data=None)

                    return result
                except KeyboardInterrupt:
                    raise
                    # attempt_no, max_attempts, func_name, args, kwargs

                except Exception as e:
                    f_error_msg = error_msg.format(
                        attempt_no=attempt,
                        max_attempts=attempts,
                        func_name=func.__name__,
                        args=args if include_params else '',
                        kwargs=kwargs if include_params else '',
                        error=repr(e)
                    )

                    if attempt == attempts:
                        if print_msgs:
                            print(f_error_msg)

                        end_timestamp = None
                        if log_timestamps:
                            end_timestamp = f"{
                                _datetime.now().strftime(dt_format)}"

                        f_end_msg = end_msg.format(
                            timestamp=end_timestamp,
                            func_name=func.__name__,
                            attempt_no=attempt,
                            max_attempts=attempts
                        )

                        f_failure_msg = failure_msg.format(
                            attempt_no=attempt,
                            max_attempts=attempts,
                            func_name=func.__name__,
                            args=args if include_params else '',
                            kwargs=kwargs if include_params else ''
                        )

                        if print_msgs:
                            print(f_failure_msg)
                            print(f_end_msg)

                        json_data_format = {
                            'func': f"{func.__name__}",
                            'attempt_no': attempt,
                            'max_attempts': attempts,
                            'status': 'failure',
                            'error': {
                                'msg': str(e),
                                'type': type(e).__name__
                            }
                        }

                        if include_params:
                            json_data_format['params'] = {
                                'args': args, 'kwargs': kwargs}
                        if log_timestamps:
                            json_data_format['timestamps'] = {
                                'start': start_timestamp, 'end': end_timestamp}

                        _handle_logging_config(
                            msg=f_failure_msg, config=logging_config, json_data=json_data_format)
                        _handle_logging_config(
                            msg=f_end_msg + '\n', config=logging_config, json_data=None)
                    else:
                        if print_msgs:
                            print(f_error_msg)
                            _handle_logging_config(
                                msg=f_error_msg, config=logging_config, json_data=None)

                        _sleep(delay)

        return wrapper
    return decorator


def timeout(cutoff_time: int | float = 30, print_msg: bool = True, include_params: bool = True,
            msg_format: str = "TODO:", logging_config: dict = None) -> _Callable:
    """
    Decorator used to timeout a function after a specified time interval.

    :param cutoff_time: The time limit for the decorated function to execute in seconds, defaults to 30.
      - For other units of time, multiply the amount of the unit by the unit constant.
      - Supported units: MICROSECONDS, MILLISECONDS, MINUTES, DAYS, WEEKS, and common abbreviations.
      - Ex: cutoff_time=3*MINUTES

    :param print_msg: Bool that determines whether the output message is printed to the terminal, defaults to True.

    :param include_params: Bool that determines whether or not to include the args and kwargs of the timed function in the output message, defaults to False.

    :param msg_format: String that dictates the formatting of the output message, defaults to None. (If None, a default msg format will be used.)
      - 

    :param logging_config: Dict containing logging configurations with the following keys:
      - 'log_file': String specifying the path to the log file where the output message will be written. If falsy, logs will not be written to a file, defaults to ''.

      - 'max_size': Integer indicating the maximum size of the log file (in Bytes) where logs will no longer be written, defaults to 5e6 (5MB).

      - 'timestamp': Bool indicating whether to prepend a timestamp using datetime or not, defaults to True.

      - 'datetime_format': String specifying the timestamp format, defaults to the default datetime format: "%Y-%m-%d %H:%M:%S".

      - 'prevent_file_creation': Bool indicating whether to prevent log file creation if the given log file path does not exist, defaults to True.

      - 'raise_exceptions': Bool indicating whether to raise exceptions caused by file writing errors or not. If false, exceptions will be printed to the console instead, defaults to True.  

    :return: The decorated function.
    """

# placeholder
