import os
from time import sleep
from datetime import datetime

from dask_kubernetes import KubeCluster
from dask.distributed import Client
from distributed.core import Status
import dask.array as da

print(f'working dir: {os.getcwd()}')

def run_test_case(client, array):
    number_of_workers = count_ready_workers(client)
    start_time = datetime.now()
    answer = array.mean().compute()
    elpased_time = datetime.now() - start_time
    print(
        '***\n'
        f'* number of workers: {number_of_workers}, '
        f'elapsed time: {elpased_time}, answer: {answer}'
        '\n***'
    )

def count_ready_workers(client):
    count = 0
    for c in client.cluster.workers:
        if client.cluster.workers[c].status == Status.running:
            count += 1
    return count

# start up cluster with 1 workers
cluster = KubeCluster('worker-spec.yaml', n_workers=1, enable_kubeflow=True)
client = Client(cluster, timeout=90)  # extend timeout for docker image download

# Create a large array and calculate the mean
array = da.ones((10000, 1000, 1000), chunks=100)

print("\n\ntest case for one worker")
run_test_case(client, array)

# scale up
print("\n\ntest case for three workers")
cluster.scale(3)
counter = 0
while True:
    ready_worker_count = count_ready_workers(client) 
    sleep(1)
    counter += 1
    print(f'scaling...ready workers: {ready_worker_count}...waiting {counter} seconds')
    if ready_worker_count == 3:
        break
    elif counter > 60:
        raise RuntimeError('Scale up operation, did not complete in required time.')
run_test_case(client, array)

# scale down
print("\n\ntest case for two workers")
cluster.scale(2)
counter = 0
while True:
    ready_worker_count = count_ready_workers(client) 
    sleep(1)
    counter += 1
    print(f'scaling...ready workers: {ready_worker_count}...waiting {counter} seconds')
    if ready_worker_count == 2:
        break
    elif counter > 60:
        raise RuntimeError('Scale up operation, did not complete in required time.')
run_test_case(client, array)

# retrieve log files
logs = cluster.get_logs()

client.close()
cluster.close()
print('all done')