"""
concurrencyutils.__concur
==================
Module containing tools for threading.
"""

# --imports-- #
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from functools import wraps
from time import sleep
from typing import Union
from threading import Event, Thread, Lock, Barrier

from ..checks import check_type


@contextmanager
def thread_manager(target, *args, **kwargs):
    """
    thread_manager
    ==============
    Context manager that ensures that threads are properly started and terminated.

    Parameters
    ----------
    :param target: A function or method that is being threaded.
    :type target: Callable[..., Any]
    :param args: The arguments passed to the function.
    :type args: Tuple[Any]
    :param kwargs: The keyword arguments passed to the function.
    :type kwargs: Any

    Example Usage
    -------------
    ```python
    >>> import time
    >>> def worker():
    ...     print("Thread is working!")
    ...     time.sleep(2)
    ...     print("Thread is finishing.")
    ...
    >>> with thread_manager(worker):
    ...     print("Main thread is doing work.")
    ...
    Thread is working!
    Main thread is doing work.
    Thread is finishing.
    ```
    """
    thread = Thread(target=target, args=args, kwargs=kwargs)
    thread.start()

    try:
        yield thread
    finally:
        thread.join()


@contextmanager
def lock_handler(lock):
    """
    lock_handler
    ============
    Context manager that handles acquiring and releasing a lock.

    Parameters
    ----------
    :param lock: The lock that is being managed.
    :type lock: threading.Lock

    Example Usage
    -------------
    ```python
    >>> from threading import Lock
    >>> my_lock = Lock()
    >>> with lock_manager(lock):
    ...     print("Lock acquired")
    ...
    Lock acquired
    ```
    """

    # type check
    check_type(lock, Lock)

    lock.acquire()
    try:
        yield
    finally:
        lock.release()


@contextmanager
def barrier_sync(barrier):
    """
    barrier_sync
    ============
    Context manager that uses to a barrier to synchronize multiple threads.

    Parameters
    ----------
    :param barrier: The barrier being managed.
    :type barrier: threading.Barrier

    Example Usage
    -------------
    ```python
    >>> from threading import Barrier, Thread
    >>> barrier = Barrier(3)
    >>> def worker(barrier):
    ...     print("Waiting at the barrier")
    ...     with barrier_handler(barrier):
    ...         print("Barrier reached")
    ...
    >>> threads = [Thread(target=worker, args=(barrier,)) for _ in range(3)]
    >>> for thread in threads:
    ...     thread.start()
    >>> for thread in threads:
    ...     thread.join()
    ...
    Waiting at the barrier
    Waiting at the barrier
    Waiting at the barrier
    Barrier reached
    Barrier reached
    Barrier reached
    ```
    """
    check_type(barrier, Barrier)

    barrier.wait()
    yield


class PeriodicTask:
    """
    PeriodicTask
    ============
    The main functionality of the decorator, periodic_running_task.

    Parameters
    ----------
    :param interval: The time in seconds between each function call.
    :type interval: Union[int, float]
    :param func: The function being modified by the decorator.
    :type func: F
    :param args: The arguments passed to the function.
    :type args: Tuple[Any, ...]
    :param kwargs: The keyword arguments passed to the function.
    :type kwargs: Any
    """

    def __init__(self, interval, func, *args, **kwargs):
        """The Constructor method."""
        # typecheck
        check_type(interval, Union[int, float])

        self.interval = interval
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.stop_event = Event()
        self.thread = Thread(target=self._target)
        self.thread.daemon = True  # background thread

    def _target(self):
        """The thread's target, a private function only used in PeriodicTask."""
        while not self.stop_event.is_set():
            try:
                self.func(*self.args, **self.kwargs)
            except Exception as e:
                print(f"Error occured during a periodic task: {e}")

            sleep(self.interval)

    def start(self):
        """Starts the threading process."""
        self.thread.start()

    def stop(self):
        """A manual function that allows the user to stop the function."""
        self.stop_event.set()
        self.thread.join()


def periodic_running_task(interval):
    """
    periodic_running_task
    =====================
    Runs a decorated function periodically within a specified interval through a background thread.

    Parameters
    ----------
    :param interval: The time in seconds between each function call.
    :type interval: Union[int, float]

    Example Usage
    -------------
    ```python
    >>> import time
    >>> @periodic_running_task(2)
    ... def my_task():
    ...     print("Task is running...")
    ...
    >>> TASK_INSTANCE = my_task()
    ... try:
    ...     time.sleep(4)
    ... finally:
    >>>     TASK_INSTANCE.stop() # Stop the periodic task
    ...     print("Task has stopped.")
    Task is running...
    Task is running...
    Task has stopped.
    ```
    """
    # typecheck
    check_type(interval, Union[int, float])

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            task = PeriodicTask(interval, func, *args, **kwargs)
            task.start()
            wrapper.stop = task.stop
            return task

        return wrapper

    return decorator


def batch_processer(data, workers, process_function):
    """
    batch_processer
    ===============
    Allows multiple tasks to be excuted to an amount of workers to be completed.
    Processes data in batches using concurrent futures.

    Parameters
    ----------
    :param data: List of data items to be processed.
    :type data: Iterable[Any]
    :param workers: Number of working threads/processes to use.
    :type workers: int

    Returns
    -------
    :return: List of results from processing each data item.
    :rtype: List[Any]

    Example Usage
    -------------
    >>> def process_data(item):
    ...     return item * item
    ...
    >>> data = [1, 2, 4, 5, 10]
    >>> processed_data = batch_processer(data, 5, process_data)
    >>> print(processed_data)
    [1, 4, 16, 25, 100]
    """

    # type checks
    check_type(workers, int)

    results = [None] * len(data)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(process_function, item): index
            for index, item in enumerate(data)
        }

        for future in as_completed(futures):
            index = futures[future]
            try:
                results[index] = future.result()
            except Exception as e:
                print(f"Task failed due to an exception: {e}")
                results[index] = None
    return results
