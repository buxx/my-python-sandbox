from threading import Thread

import sys

THREADS = int(sys.argv[2])
DATA = 6000
MODE = sys.argv[1]


def job(shared_data, index):
    chunk = shared_data[index]
    compute1 = [d*2 for d in chunk]
    compute2 = sum(compute1)
    compute3 = ['foo' for i in range(compute2)]
    shared_data['results'][index] = len(compute3)

shared_data = {
    'results': {}
}

current = 0
for i in range(THREADS):
    shared_data[i] = [current+i for i in range(DATA)]

if MODE == 'T':
    threads = []

    for i in range(THREADS):
        threads.append(Thread(target=job, args=(shared_data, i)))
        current = len(shared_data[i])

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

elif MODE == 'S':
    job(shared_data, 0)
    job(shared_data, 1)


print(shared_data['results'])
