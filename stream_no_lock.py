"""
Using global variable for inter thread communication
multi thread example
"""

from time import sleep
import _thread


def core0_thread():
    while True:
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


def core1_thread():
    while True:
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


second_thread = _thread.start_new_thread(core1_thread, ())
core0_thread()
