import os
from time import sleep
from datetime import datetime

from dask_kubernetes import KubeCluster
from dask.distributed import Client
import dask.array as da

print(f'working dir: {os.getcwd()}')

def run_test_case(client, array):
    number_of_workers = len(client.cluster.workers)
    start_time = datetime.now()
    answer = array.mean().compute()
    elpased_time = datetime.now() - start_time
    print(
        '***\n'
        f'* nubmer of workers: {number_of_workers}, '
        f'elapsed time: {elpased_time}, answer: {answer}'
        '\n***'
    )

# start up cluster with 2 workers
cluster = KubeCluster('worker-spec.yaml', n_workers=1, enable_kubeflow=True)
client = Client(cluster)

# Create a large array and calculate the mean
array = da.ones((10000, 1000, 1000), chunks=100)

print("\n\ntest case for one worker")
run_test_case(client, array)

# scale up
print("\n\ntest case for three workers")
cluster.scale(3)
counter = 0
while len(client.cluster.workers) != 3: 
    sleep(1)
    counter += 1
    print(f'scaling...waiting {counter} seconds')
    if counter > 60:
        raise RuntimeError('Scale up operation, did not complete in required time.')
run_test_case(client, array)

# scale down
print("\n\ntest case for two workers")
cluster.scale(2)
counter = 0
while len(client.cluster.workers) != 2: 
    sleep(1)
    counter += 1
    print(f'scaling...waiting {counter} seconds')
    if counter > 60:
        raise RuntimeError('Scale down operation, did not complete in required time.')

run_test_case(client, array)


print('all done')