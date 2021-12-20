import logging
import sys

from .core import KubeflowCluster

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Configure stream handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

# Set formatter
formatter = logging.Formatter("%(message)s")
ch.setFormatter(formatter)

logger.addHandler(ch)

logger.debug("entered import for dask_kubeflow")

__all__ = ['KubeflowCluster']
