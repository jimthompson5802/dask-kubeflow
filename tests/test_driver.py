import logging
import sys

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


cluster.close()

print("all done")
