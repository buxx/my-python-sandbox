import os
import random
import sys
from multiprocessing import Process, Manager
from multiprocessing.connection import Pipe
from threading import Thread
import argparse
manager = Manager()

parser = argparse.ArgumentParser(description='')

parser.add_argument(
    '-m', '--mode', type=str, help='Mode (Thread, Process, Single)', required=True)
parser.add_argument(
    '-w', '--workers', type=int, help='Worker numbers', required=True)
parser.add_argument(
    '-s', '--shared', type=str, help='Shared type (pipe, dict, manager)', required=True)
parser.add_argument(
    '-d', '--data', type=int, help='Data count', required=False, default=10000)
parser.add_argument(
    '-i', '--iterations', type=int, help='Number of iterations', required=False, default=10)
parser.add_argument(
    '-k', '--keep', help='Keep alive workers', action='store_true', default=False)

args = parser.parse_args()

MODE = args.mode
WORKERS = args.workers
SHARED = args.shared
DATA_COUNT = args.data
ITERATIONS = args.iterations
KEEP = args.keep
random.seed(42)


def get_shared_var(shared, data_count, workers_count):
    if shared == 'dict' or shared == 'pipe':
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
        raise NotImplemented()


def get_result_var(shared):
    if shared == 'dict' or shared == 'pipe':
        return dict()

    if shared == 'manager':
        return manager.dict()

    else:
        raise NotImplemented()


def make_job(shared_data, index, results, cycle_number):
    chunk = shared_data[index]
    sum_ = sum(chunk)

    print('CYCLE {0} WORKER {1}: sum is {2} (pid {3})'.format(
        cycle_number,
        index,
        sum_,
        os.getpid(),
    ))

    compute = 0
    for i in range(sum_):
        compute += i
    results[index] = compute


def make_job_keeper(target, start_conn, recv_conn, shared_data, worker_number, results):
    iteration_number = -1
    while True:
        iteration_number += 1
        shared_data = start_conn.recv()
        if shared_data is False:
            break
        target(shared_data, worker_number, results, iteration_number)
        recv_conn.send(True)


if __name__ == '__main__':
    shared_data = get_shared_var(SHARED, DATA_COUNT, WORKERS)
    results = get_result_var(SHARED)

    if MODE == 'Process':
        if not KEEP:
            for iteration_number in range(ITERATIONS):
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

                shared_data = get_shared_var(SHARED, DATA_COUNT, WORKERS)
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
                    args=(make_job, start_child_conn, recv_child_conn, shared_data, worker_number, results)
                )
                p.start()
                processes.append(p)

            for iteration_number in range(ITERATIONS):
                for start_pipe in start_pipes:
                    start_pipe.send(shared_data)
                for worker_number, recv_pipe in enumerate(recv_pipes):
                    results[worker_number] = recv_pipe.recv()
                shared_data = get_shared_var(SHARED, DATA_COUNT, WORKERS)

            for start_pipe in start_pipes:
                start_pipe.send(False)

        results = results.items()

    elif MODE == 'Thread':
        for iteration_number in range(ITERATIONS):
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

            shared_data = get_shared_var(SHARED, DATA_COUNT, WORKERS)

        results = results.items()

    elif MODE == 'Single':
        for iteration_number in range(ITERATIONS):
            for worker_number in range(WORKERS):
                make_job(shared_data, worker_number, results, iteration_number)
            shared_data = get_shared_var(SHARED, DATA_COUNT, WORKERS)
        results = results.items()

    else:
        raise NotImplemented()

    print(results)
