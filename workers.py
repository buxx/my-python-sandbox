import os
import random
import sys
from multiprocessing import Process, Manager
from multiprocessing.connection import Pipe
from threading import Thread
import argparse

import time

manager = Manager()

parser = argparse.ArgumentParser(description='')

parser.add_argument(
    '-m', '--mode', type=str, help='Mode (Thread, Process, Single)', required=True)
parser.add_argument(
    '-w', '--workers', type=int, help='Worker numbers', required=True)
parser.add_argument(
    '-s', '--shared', type=str, help='Shared type (dict, manager)', required=True)
parser.add_argument(
    '-d', '--data', type=int, help='Data count', required=False, default=10000)
parser.add_argument(
    '-i', '--iterations', type=int, help='Number of iterations', required=False, default=10)
parser.add_argument(
    '-k', '--keep', help='Keep alive workers', action='store_true', default=False)
parser.add_argument(
    '-r', '--random', type=int, help='Random seed int', required=False, default=10)
parser.add_argument(
    '-v', '--verbose', help='Verbose', action='store_true', default=False)
parser.add_argument(
    '-p', '--print-result', help='Print result', action='store_true', default=False)

args = parser.parse_args()

MODE = args.mode
WORKERS = args.workers
SHARED = args.shared
DATA_SIZE = args.data
CYCLES = args.iterations
KEEP = args.keep
VERBOSE = args.verbose
RESULT = args.print_result
random.seed(42)

CYCLES_LENGTH = len(str(CYCLES))
CYCLE_FORMAT = '{:' + str(CYCLES_LENGTH) + '}'

if KEEP and MODE != 'Process':
    raise NotImplementedError('You can\t use KEEP for {0} MODE'.format(MODE))

if SHARED != 'manager' and MODE == 'Process':
    raise NotImplementedError('You must use manager SHARED for {0} MODE'.format(MODE))

if VERBOSE:

    print('''BENCHMARK CONFIGURATION:

    * MODE: {mode}
    * WORKERS: {workers}
    * SHARED TYPE: {shared}
    * DATA SIZE: {data_count}
    * CYCLES: {cycles}'''.format(
        mode=MODE,
        workers=WORKERS,
        shared=SHARED,
        data_count=DATA_SIZE,
        cycles=CYCLES,
    ))

    if MODE == 'Process':
        print('* KEEP: {0}'.format(
            'True' if KEEP else 'False'
        ))

    print('')


def get_shared_var(shared, data_count, workers_count):
    if shared == 'dict':
        data = dict()
        for worker_number in range(workers_count):
            data[worker_number] = [random.randint(0, 1000) for i in range(data_count)]
        return data

    elif shared == 'manager':
        data = manager.dict()
        for worker_number in range(workers_count):
            data[worker_number] = [random.randint(0, 1000) for i in range(data_count)]
        return data

    else:
        raise NotImplementedError()


def get_result_var(shared):
    if shared == 'dict':
        return dict()

    if shared == 'manager':
        return manager.dict()

    else:
        raise NotImplementedError()


def make_job(shared_data, index, results, cycle_number):
    start_time = time.time()

    chunk = shared_data[index]
    sum_ = sum(chunk)

    compute = 0
    for i in range(sum_):
        compute += i
    results[index] = compute

    elapsed_time = time.time() - start_time
    if VERBOSE:
        print('CYCLE {0} WORKER {1}: result is {2} (pid {3}, {4}s)'.format(
            CYCLE_FORMAT.format(cycle_number),
            index,
            compute,
            os.getpid(),
            '{:2.6f}'.format(elapsed_time),
        ))


def make_job_keeper(target, start_conn, recv_conn, worker_number):
    iteration_number = -1
    while True:
        iteration_number += 1
        shared_data = start_conn.recv()
        if shared_data is False:
            break
        results = {}
        target(shared_data, worker_number, results, iteration_number)
        recv_conn.send(results[worker_number])


if __name__ == '__main__':
    global_start_time = time.time()
    shared_data = get_shared_var(SHARED, DATA_SIZE, WORKERS)
    results = get_result_var(SHARED)

    if MODE == 'Process':
        if not KEEP:
            for iteration_number in range(CYCLES):
                processes = []

                for worker_number in range(WORKERS):
                    processes.append(Process(
                        target=make_job,
                        args=(shared_data, worker_number, results, iteration_number)
                    ))

                for process in processes:
                    process.start()

                for process in processes:
                    process.join()

                shared_data = get_shared_var(SHARED, DATA_SIZE, WORKERS)

            results = dict(results)
        else:
            processes = []
            start_pipes = []
            recv_pipes = []

            for worker_number in range(WORKERS):
                start_parent_conn, start_child_conn = Pipe()
                recv_parent_conn, recv_child_conn = Pipe()

                start_pipes.append(start_parent_conn)
                recv_pipes.append(recv_parent_conn)

                p = Process(
                    target=make_job_keeper,
                    args=(make_job, start_child_conn, recv_child_conn, worker_number)
                )
                p.start()
                processes.append(p)

            for iteration_number in range(CYCLES):
                for start_pipe in start_pipes:
                    start_pipe.send(shared_data)
                for worker_number, recv_pipe in enumerate(recv_pipes):
                    results[worker_number] = recv_pipe.recv()
                shared_data = get_shared_var(SHARED, DATA_SIZE, WORKERS)

            for start_pipe in start_pipes:
                start_pipe.send(False)

        results = results.items()

    elif MODE == 'Thread':
        for iteration_number in range(CYCLES):
            threads = []

            for worker_number in range(WORKERS):
                threads.append(Thread(
                    target=make_job,
                    args=(shared_data, worker_number, results, iteration_number)
                ))

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            shared_data = get_shared_var(SHARED, DATA_SIZE, WORKERS)

        results = results.items()

    elif MODE == 'Single':
        for iteration_number in range(CYCLES):
            for worker_number in range(WORKERS):
                make_job(shared_data, worker_number, results, iteration_number)
            shared_data = get_shared_var(SHARED, DATA_SIZE, WORKERS)
        results = results.items()

    else:
        raise NotImplementedError()

    global_elapsed_time = time.time() - global_start_time

    if VERBOSE:
        print('')
        print('''RESULTS:''')
        for worker_number in range(WORKERS):
            print('* WORKER {0}: {1}'.format(worker_number, dict(results).get(worker_number)))
        print('')
        print('EXECUTION TIME: {0}s'.format(
            '{:6.6f}'.format(global_elapsed_time),
        ))
    else:
        if RESULT:
            print('{:6.6f}'.format(global_elapsed_time))
