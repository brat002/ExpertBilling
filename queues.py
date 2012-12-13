from kombu import Exchange, Queue

task_exchange = Exchange('tasks', type='direct', delivery=1)
nf_in = [Queue('nf_in', task_exchange, routing_key='nf_in')]
nf_out = [Queue('nf_out', task_exchange, routing_key='nf_out')]


