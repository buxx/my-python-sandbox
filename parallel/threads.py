from threading import Thread
import sys

import numpy as np
import sharedmem

THREADS = int(sys.argv[2])
DATA = 6000
MODE = sys.argv[1]
shared = False
if '--shared' in sys.argv:
    shared = True


def job(shared_data):  #, index, results):
    chunk = shared_data
    compute = [d*2 for d in chunk]
    compute = sum(compute)
    compute = [i+1 for i in range(compute)]
    # results[index] = len(compute)

# shared_data = {}
# results = {}

current = 0
if shared:
    print('Shared mem: YES')
    shared_data = sharedmem.empty(DATA, dtype=np.int16)
    for i in range(DATA):
        shared_data[i] = i

    # for i in range(THREADS):
    #     s = sharedmem.empty(DATA, dtype=np.int16)
    #     for ii in range(DATA):
    #         s[ii] = current+ii
    #     shared_data[i] = s
else:
    print('Shared mem: NO')
    shared_data = [None] * DATA
    for i in range(DATA):
        shared_data[i] = i

    # for i in range(THREADS):
    #     shared_data[i] = [current+i for i in range(DATA)]

if MODE == 'T':
    threads = []

    for i in range(THREADS):
        threads.append(Thread(target=job, args=(shared_data, ))) #, i, results)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

elif MODE == 'S':
    for i in range(THREADS):
        job(shared_data)#, i, results)


# print(results)
