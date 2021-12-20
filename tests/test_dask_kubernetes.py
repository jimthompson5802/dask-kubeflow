from dask_kubernetes import KubeCluster
import os

print(f'working dir: {os.getcwd()}')

cluster = KubeCluster('worker-spec.yaml')
cluster.scale(2)  # specify number of workers explicitly

# cluster.adapt(minimum=1, maximum=100)  # or dynamically scale based on current workload