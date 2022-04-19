

import _thread

def thread_function(param1, param2, param3 = 3):
    # this will run on core 1
    pass

param1 = 1
param2 = 2

# start a new thread on core 1
new_thread = _thread.start_new_thread(thread_function, (param1, param2), {'param3': 3})

# this will run on core 0

