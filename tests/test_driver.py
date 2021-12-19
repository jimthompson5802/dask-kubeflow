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

wait_return = cluster.wait_for_workers(timeout=3, verbose=True)
print(f'wait for workers short time out: {wait_return}')

wait_return = cluster.wait_for_workers(verbose=True)
print(f'wait for workers long time out: {wait_return}')

# cluster.scale(4)

# wait_for_workers(cluster)

cluster.close()

print("all done")
