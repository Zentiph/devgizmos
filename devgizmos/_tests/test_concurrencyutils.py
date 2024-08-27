# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring, cell-var-from-loop, invalid-name
# pylint: disable=pointless-string-statement

from threading import Barrier, current_thread, Lock, Thread
from contextlib import contextmanager
import unittest

from ..concurrencyutils import (
    QueueProcessor,
    ReactivationError,
    barrier_sync,
    batch_processor,
    lock_handler,
    periodic_task,
    thread_manager,
)


class TestLockHandler(unittest.TestCase):
    def test_invalid_lock(self):
        invalid_locks = ["what's a lock?", 12564, None, object()]

        for invalid_lock in invalid_locks:
            with self.subTest(lock=invalid_lock):
                with self.assertRaises(TypeError):
                    with lock_handler(invalid_lock):
                        pass

    # tests that the lock is in the state of "Locked"
    def test_lock_locked(self):
        with self.subTest():
            lock = Lock()

            with lock_handler(lock):
                self.assertTrue(lock.locked())


class TestBarrierSync(unittest.TestCase):
    def test_invalid_barriers(self):
        invalid_barriers = ["What is a barrier?", 238821, None, object()]

        for invalid_barrier in invalid_barriers:
            with self.subTest(barrier=invalid_barrier):
                with self.assertRaises(TypeError):
                    with barrier_sync(invalid_barrier):
                        pass

    def test_valid_barriers(self):
        with self.subTest():
            my_barrier = Barrier(2)

            def worker(barrier):
                with barrier_sync(barrier):
                    print(f"Thread {current_thread().name} passed the barrier")

            thread1 = Thread(target=worker, args=(my_barrier,))
            thread2 = Thread(target=worker, args=(my_barrier,))

            thread1.start()
            thread2.start()

            thread1.join(timeout=5)
            thread2.join(timeout=5)

            self.assertFalse(
                thread1.is_alive(), "Thread 1 did not finish within the timeout"
            )
            self.assertFalse(
                thread2.is_alive(), "Thread 1 did not finish within the timeout"
            )


class TestQueueProcessor(unittest.TestCase):
    def test_invalid_start_call(self):
        # pylint: disable=unused-argument
        def process_item(item):
            pass

        qd = QueueProcessor(2, process_item)

        qd.start()

        with self.assertRaises(ReactivationError):
            qd.start()

    # might unit test checking booleans for the last one, but not needed rn
    def test_invalid_params(self):
        # pylint: disable=unused-argument
        def process_item(item):
            pass

        invalid_workers = ["what's a workers", None, object()]

        for invalid_worker in invalid_workers:
            with self.subTest(worker=invalid_worker):
                with self.assertRaises(TypeError):
                    qd = QueueProcessor(invalid_worker, process_item)
                    qd.start()

        invalid_processors = ["what's a object?", None, 12344]

        for invalid_processor in invalid_processors:
            with self.subTest(processor=invalid_processor):
                with self.assertRaises(TypeError):
                    qd = QueueProcessor(1, invalid_processor)
                    qd.start()


class TestThreadManager(unittest.TestCase):
    def test_invalid_target(self):
        invalid_targets = ["target??", None, 71222, int()]

        for invalid_target in invalid_targets:
            with self.subTest(target=invalid_target):
                with self.assertRaises(TypeError):
                    with thread_manager(invalid_target):
                        pass


if __name__ == "__main__":
    unittest.main()
