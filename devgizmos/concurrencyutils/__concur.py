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
                # TODO: note from zen - this is bad error handling, consider
                # either stopping the task and then raising it or save it to a
                # class attribute for error logging purposes
                # if you choose the 2nd, use _ExcData from codeutils:
                # from ..codeutils.__failuremngr import _ExcData
                print(f"Error occurred during a periodic task: {e}")

            sleep(self.__interval)

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


def batch_processor(data, workers, process_function):
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
                # TODO: note from zen - similar to ln 178 this
                # is bad error handling, consider adding a param to
                # decide whether to suppress exceptions or raise them
                # of course add a finally if any concurrent stuff needs to be stopped
                print(f"Task failed due to an exception: {e}")
                results[index] = None
    return results


# TODO: note from zen - consider adding some @property funcs so users can
# get the workers and process_func of the qp? (just a QOL change)
class QueueProcessor:
    """Class for creating thread-safe queues."""

    def __init__(self, workers, process_function):
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
        [Processed Task 1, Processed Task 2, Processed Task 3]
        """

        # TODO: note from zen - above example usage caused a massive error

        self.__queue = Queue()
        self.__workers = workers
        self.__process_function = process_function
        self.__active_workers = []
        # TODO: note from zen - running does not do anything right now, consider adding checks
        # to prevent start() from being called again if the qp is already running?
        self.__running = False

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
            except Empty:
                continue
            except Exception as e:
                # TODO: note from zen - see line 178
                print(f"An error occurred during queue processing: {e}")
            finally:
                self.__queue.task_done()

    def start(self):
        """
        QueueProcessor().start()
        ------------------------
        Starts the QueueProcessor class.
        """

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
