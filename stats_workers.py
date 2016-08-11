import os
from collections import OrderedDict

print('''Stratégies:
A. 1 worker avec dict
B. 4 Threads avec dict
C. 4 Threads avec Manager
D. 4 Process avec Manager
E. 4 Process avec Manager, processus daemons

Contextes:
1. 10000 data, 20 cycles
2. 1000 data, 200 cycles
3. 100 data, 1000 cycles
4. 50 data, 5000 cycles
5. 10 data, 10000 cycles''')

print('')

COMMAND = 'python workers.py -m {mode} -w 4 -s {shared} -i {cycles} -d {data} -p {more}'

strategies = OrderedDict([
    ('A', ('Single', 'dict')),
    ('B', ('Thread', 'dict')),
    ('C', ('Thread', 'manager')),
    ('D', ('Process', 'manager')),
    ('E', ('Process', 'manager', '--keep')),
])

contexts = OrderedDict([
    ('1', (10000, 20)),
    ('2', (1000, 200)),
    ('3', (100, 1000)),
    ('4', (50, 5000)),
    ('5', (10, 10000)),
])

for strategy_name, strategy in strategies.items():
    for context_name, context in contexts.items():

        mode = strategy[0]
        shared = strategy[1]
        data = context[0]
        cycles = context[1]
        more = '' if 2 not in strategy else strategy[2]

        exec_ = COMMAND.format(
            mode=mode,
            shared=shared,
            cycles=cycles,
            data=data,
            more=more,
        )

        print('{0}{1}: '.format(
            strategy_name,
            context_name,
        ), end='', flush=True)

        execution_seconds = float(os.popen(exec_).read().rstrip())
        seconds_per_cycle = execution_seconds / cycles

        print('{0}:{1}/cycle ({2})'.format(
            execution_seconds,
            '{:6.9f}'.format(seconds_per_cycle),
            exec_,
        ))
