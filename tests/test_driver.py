import logging
import sys
from time import sleep

# TODO: fix up import to remove core submodule
from dask_kubeflow.core import KubeflowCluster


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure stream handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)

# Set formatter
formatter = logging.Formatter("%(message)s")
ch.setFormatter(formatter)

logger.addHandler(ch)



logger.info('entered dask_kubeflow')

cluster = KubeflowCluster()

print(cluster.scheduler_service_address)

while True:
    requested_workers, ready_workers = cluster.worker_count
    print(f'requested workers: {requested_workers}, ready workers: {ready_workers}')
    if (requested_workers > 0) and (requested_workers == ready_workers):
        break
    sleep(1)
    
cluster.close()

print("all done")
