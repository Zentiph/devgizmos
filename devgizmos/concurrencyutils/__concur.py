"""
concurrencyutils.__concur
==================
Module containing tools for threading.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from functools import wraps
from time import sleep
from typing import Union
from threading import Event, Thread, Lock, Barrier
from queue import Queue, Empty

from ..errguards import ensure_instance_of


class ReactivationError(Exception):
    """
    ReactivationError
    -----------------
    Exception to raise if a QueueProcessor's start() method is called when
    its start() method has been previously called and before its stop() method has been called.
    """


@contextmanager
def thread_manager(target, *args, **kwargs):
    """
    thread_manager()
    ----------------
    Context manager that ensures that threads are properly started and terminated.

    Parameters
    ~~~~~~~~~~
    :param target: A function or method that is being threaded.
    :type target: Callable[..., Any]
    :param args: The arguments passed to the function.
    :type args: Tuple[Any]
    :param kwargs: The keyword arguments passed to the function.
    :type kwargs: Any

    Example Usage
    ~~~~~~~~~~~~~
    >>> import time
    >>>
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
    lock_handler()
    --------------
    Context manager that handles acquiring and releasing a lock.

    Parameters
    ~~~~~~~~~~
    :param lock: The lock that is being managed.
    :type lock: threading.Lock

    Example Usage
    ~~~~~~~~~~~~~
    >>> import threading
    >>>
    >>> lock = threading.Lock()
    >>> with lock_handler(lock):
    ...     print("Lock acquired")
    ...
    Lock acquired
    """

    # type check
    ensure_instance_of(lock, Lock)

    lock.acquire()
    try:
        yield
    finally:
        lock.release()


@contextmanager
def barrier_sync(barrier):
    """
    barrier_sync()
    --------------
    Context manager that uses to a barrier to synchronize multiple threads.

    Parameters
    ~~~~~~~~~~
    :param barrier: The barrier being managed.
    :type barrier: threading.Barrier

    Example Usage
    ~~~~~~~~~~~~~
    >>> import threading
    >>>
    >>> barrier = threading.Barrier(3)
    >>> def worker(barrier):
    ...     print("Waiting at the barrier")
    ...     with barrier_handler(barrier):
    ...         print("Barrier reached")
    ...
    >>> threads = [threading.Thread(target=worker, args=(barrier,)) for _ in range(3)]
    >>> for thread in threads:
    ...     thread.start()
    ...
    >>> for thread in threads:
    ...     thread.join()
    ...
    Waiting at the barrier
    Waiting at the barrier
    Waiting at the barrier
    Barrier reached
    Barrier reached
    Barrier reached
    """

    ensure_instance_of(barrier, Barrier)

    barrier.wait()
    yield


class PeriodicTask:
    """The main functionality of the decorator, periodic_task."""

    def __init__(self, interval, func, *args, **kwargs):
        """
        PeriodicTask()
        --------------
        The main functionality of the decorator, periodic_task.

        Parameters
        ~~~~~~~~~~
        :param interval: The time in seconds between each function call.
        :type interval: Union[int, float]
        :param func: The function being modified by the decorator.
        :type func: F
        :param args: The arguments passed to the function.
        :type args: Any
        :param kwargs: The keyword arguments passed to the function.
        :type kwargs: Any
        """

        # type checks
        ensure_instance_of(interval, Union[int, float])

        self.__interval = interval
        self.__func = func
        self.__args = args
        self.__raise_exceptions = False
        self.__kwargs = kwargs
        self.__stop_event = Event()
        self.__thread = Thread(target=self.__target)
        self.__thread.daemon = True  # background thread

    def __target(self):
        """
        PeriodicTask().__target()
        -------------------------
        The thread's target, a private function only used in PeriodicTask.
        """

        while not self.__stop_event.is_set():
            try:
                self.__func(*self.__args, **self.__kwargs)
            except Exception as e:
                if self.__raise_exceptions:
                    self.stop()
                    raise RuntimeError(
                        f"An error occurred during queue processing: {e}"
                    ) from e

                self.stop()
                print(f"Error occurred during a periodic task: {e}")

            sleep(self.__interval)

    @property
    def raise_exceptions(self):
        """
        PeriodicTask().raise_exceptions
        -------------------------------
        Returns whether the PeriodicTask should raise or suppress exceptions.

        Return
        ~~~~~~
        :return: Whether to raise or suppress exceptions.
        :rtype: bool
        """

        return self.__raise_exceptions

    @raise_exceptions.setter
    def raise_exceptions(self, re, /):
        """
        PeriodicTask().raise_exceptions()
        ---------------------------------
        Sets whether the PeriodicTask should raise or suppress exceptions.

        Parameters
        ~~~~~~~~~~
        :param re: Whether to raise or suppress exceptions.
        :type re: bool
        """

        # type checks
        ensure_instance_of(re, bool)

        self.__raise_exceptions = re

    def start(self):
        """
        PeriodicTask().start()
        ----------------------
        Starts the threading process.
        """

        self.__thread.start()

    def stop(self):
        """
        PeriodicTask().stop()
        ---------------------
        A manual function that allows the user to stop the function.
        """

        self.__stop_event.set()
        self.__thread.join()


def periodic_task(interval):
    """
    @periodic_task()
    ----------------
    Runs a decorated function periodically within a specified interval through a background thread.

    Parameters
    ~~~~~~~~~~
    :param interval: The time in seconds between each function call.
    :type interval: Union[int, float]

    Example Usage
    ~~~~~~~~~~~~~
    >>> import time
    >>>
    >>> @periodic_task(2)
    ... def my_task():
    ...     print("Task is running...")
    ...
    >>> task_instance = my_task()
    >>> try:
    ...     time.sleep(4)
    ... finally:
    ...     task_instance.stop() # Stop the periodic task
    ...     print("Task has stopped.")
    ...
    Task is running...
    Task is running...
    Task has stopped.
    """

    # type checks
    ensure_instance_of(interval, Union[int, float])

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            task = PeriodicTask(interval, func, *args, **kwargs)
            task.start()
            wrapper.stop = task.stop
            return task

        return wrapper

    return decorator


def batch_processor(data, workers, process_function, raise_exceptions=False):
    """
    batch_processor()
    -----------------
    Processes data in batches using concurrent.futures.

    Parameters
    ~~~~~~~~~~
    :param data: List of data items to be processed.
    :type data: Iterable[Any]
    :param workers: Number of working threads/processes to use.
    :type workers: int
    :param process_function: The function that processes each item.
    :type process_function: F
    :param raise_exceptions: Allows an exception should be suppressed or raised. Defaults to False.
    :type raise_exceptions: bool

    Return
    ~~~~~~
    :return: List of results from processing each data item.
    :rtype: List[Any]

    Example Usage
    ~~~~~~~~~~~~~
    >>> def process_data(item):
    ...     return item * item
    ...
    >>> data = [1, 2, 4, 5, 10]
    >>> processed_data = batch_processor(data, 5, process_data)
    >>> print(processed_data)
    [1, 4, 16, 25, 100]
    """

    # type checks
    ensure_instance_of(workers, int)

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
                if raise_exceptions:
                    raise RuntimeError(
                        f"An error occurred during queue processing: {e}"
                    ) from e

                print(f"Task failed due to an exception: {e}")
                results[index] = None
    return results


class QueueProcessor:
    """Class for creating thread-safe queues."""

    def __init__(self, workers, process_function, raise_exceptions=False):
        """
        QueueProcessor()
        ----------------
        Automates the process of creating a thread-safe queue.

        Parameters
        ~~~~~~~~~~
        :param workers: The amount of threads to be created.
        :type workers: int
        :param process_function: The function that processes each item.
        :type process_function: F
        :param raise_exceptions: Allows an exception should be suppressed or raised. Defaults to False.
        :type raise_exceptions: bool

        Raises
        ~~~~~~
        :raises ReactivationError: If the start() method is called twice before the stop() method has been called.

        Example Usage
        ~~~~~~~~~~~~~
        >>> import threading
        >>>
        >>> results = []
        >>> results_lock = threading.Lock()
        >>>
        >>> def process_item(item):
        ...     result = f"Processed {item}"
        ...     with results_lock:
        ...         results.append(result)
        ...
        >>> # Use the QueueProcessor
        >>> qp = QueueProcessor(workers=3, process_function=process_item)
        >>> qp.start()
        >>>
        >>> for i in range(3):
        ...     qp.add_task(f"Task {i}")
        ...
        >>> qp.stop()
        print(results)
        [Processed Task 0, Processed Task 1, Processed Task 2]
        """

        self.__queue = Queue()
        self.__workers = workers
        self.__process_function = process_function
        self.__active_workers = []
        self.__running = False
        self.__raise_exceptions = raise_exceptions

    @property
    def workers(self):
        """
        QueueProcessor().workers
        ----------------------------
        Returns the list of active workers.
        """
        return self.__active_workers

    @property
    def process_func(self):
        """
        QueueProcessor().workers
        ----------------------------
        Returns the process function's name.
        """
        return self.__process_function.__name__

    def _consumer(self):
        """
        QueueProcessor()._consumer()
        ----------------------------
        Manages how each item is supposed to be processed and breaks when an item is None.
        """

        while True:
            try:
                item = self.__queue.get(timeout=1)

                if item is None:
                    break

                self.__process_function(item)
                self.__queue.task_done()
            except Empty:
                continue
            except Exception as e:
                if self.__raise_exceptions:
                    self.stop()
                    raise RuntimeError(
                        f"An error occurred during queue processing: {e}"
                    ) from e

                print(f"An error occurred during queue processing: {e}")

    def start(self):
        """
        QueueProcessor().start()
        ------------------------
        Starts the QueueProcessor class.
        """

        if self.__running:
            raise ReactivationError(
                "'QueueProcessor.start()' was called when QueueProcessor was already activated."
            )

        self.__running = True
        for _ in range(self.__workers):
            worker = Thread(target=self._consumer)
            worker.start()
            self.__active_workers.append(worker)

    def stop(self):
        """
        QueueProcessor().stop()
        -----------------------
        Stops the queue for the QueueProcessor.
        """

        for _ in range(self.__workers):
            self.__queue.put(None)

        for worker in self.__active_workers:
            worker.join()

        self.__active_workers = []
        self.__running = False

    def add_task(self, item):
        """
        QueueProcessor().add_task()
        ---------------------------
        Adds an item to be processed.
        """

        self.__queue.put(item)
