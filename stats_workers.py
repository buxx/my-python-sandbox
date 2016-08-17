import argparse
import json
import os
from collections import OrderedDict

parser = argparse.ArgumentParser(description='')

parser.add_argument(
    '-o', '--output', type=str, help='build html stats', required=False, default='')

args = parser.parse_args()

DOC = '''Stratégies:
A. 1 worker avec dict
B. 4 Threads avec dict
C. 4 Threads avec Manager
D. 4 Process avec Manager
E. 4 Process avec Manager, processus daemons
'''

print(DOC)

print('')

COMMAND = 'python workers.py -m {mode} -w 4 -s {shared} -i {cycles} -d {data} -p {more}'

strategies = OrderedDict([
    ('A', ('Single', 'dict')),
    ('B', ('Thread', 'dict')),
    ('C', ('Thread', 'manager')),
    ('D', ('Process', 'manager')),
    ('E', ('Process', 'manager', '--keep')),
])

data_start = 2000
int_name = 1
contexts_list = []
while data_start >= 1:
    contexts_list.append(
        (str(int_name), (data_start, 100))
    )
    int_name += 1
    data_start -= 100

# contexts = OrderedDict([
#     ('1', (10000, 20)),
#     ('2', (1000, 200)),
#     ('3', (100, 1000)),
#     ('4', (50, 5000)),
#     ('5', (10, 10000)),
# ])

contexts = OrderedDict(contexts_list)
stats = []

for context_name, context in contexts.items():
    context_stats = {'y': '{0}'.format(context_name)}
    for strategy_name, strategy in strategies.items():
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
        context_stats['{0}'.format(strategy_name)] = seconds_per_cycle

        print('{0}:{1}/cycle ({2})'.format(
            execution_seconds,
            '{:6.9f}'.format(seconds_per_cycle),
            exec_,
        ))
    stats.append(context_stats)

if args.output:
    with open(args.output, 'w+') as file:
        print('''
        <!DOCTYPE html>
        <html>
        <head>
          <script src="http://cdnjs.cloudflare.com/ajax/libs/raphael/2.1.0/raphael-min.js"></script>
          <script src="http://code.jquery.com/jquery-1.8.2.min.js"></script>
          <script src="http://cdn.oesmith.co.uk/morris-0.4.1.min.js"></script>
          <meta charset=utf-8 />
          <title>Workers</title>
        </head>
        <body>

            <pre>'''+DOC+'''</pre>

          <div id="js_stats"></div>

          <script>
            Morris.Line({
              element: 'js_stats',
              data: '''+json.dumps(stats)+''',
              xkey: 'y',
              ykeys: '''+json.dumps(['{0}'.format(s) for s in list(strategies.keys())])+''',
              labels: '''+json.dumps(['Strategy {0}'.format(s) for s in list(strategies.keys())])+'''
            });
        </script>

        </body>
        </html>
        ''', file=file)
