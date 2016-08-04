import sys
from multiprocessing import Process, Manager

THREADS = int(sys.argv[2])
DATA = 10000
MODE = sys.argv[1]


def job(shared_data, index, results):
    chunk = shared_data[index]
    compute1 = [d*2 for d in chunk]
    compute2 = sum(compute1)
    compute3 = ['foo' for i in range(compute2)]
    results[index] = len(compute3)

if __name__ == '__main__':
    shared_data = {}
    results = {}

    current = 0

    if MODE == 'T':
        with Manager() as manager:
            shared_data = manager.dict()
            results = manager.dict()

            for i in range(THREADS):
                shared_data[i] = [current+j for j in range(DATA)]

            threads = []

            for i in range(THREADS):
                threads.append(Process(target=job, args=(shared_data, i, results)))

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            results = results.items()
    elif MODE == 'S':
        for i in range(THREADS):
            shared_data[i] = [current+j for j in range(DATA)]

        for i in range(THREADS):
            job(shared_data, i, results)

    print(results)
