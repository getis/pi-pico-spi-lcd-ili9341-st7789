"""
Using global variable for inter thread communication
multi thread example
"""

from time import sleep
import _thread


def core0_thread():
    global lock
    while True:
        # try to acquire lock - wait if in use
        lock.acquire()

        print('C')
        sleep(0.5)
        print('O')
        sleep(0.5)
        print('R')
        sleep(0.5)
        print('E')
        sleep(0.5)
        print('0')
        sleep(0.5)

        # release lock
        lock.release()


def core1_thread():
    global lock
    while True:
        # try to acquire lock - wait if in use
        lock.acquire()

        print('c')
        sleep(0.5)
        print('o')
        sleep(0.5)
        print('r')
        sleep(0.5)
        print('e')
        sleep(0.5)
        print('1')
        sleep(0.5)

        # release lock
        lock.release()


# create a global lock
lock = _thread.allocate_lock()

second_thread = _thread.start_new_thread(core1_thread, ())
core0_thread()
