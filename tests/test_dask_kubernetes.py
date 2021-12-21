from dask_kubernetes import KubeCluster
import os

print(f'working dir: {os.getcwd()}')

cluster = KubeCluster('worker-spec.yaml', scheduler_service_wait_timeout=120, enable_kubeflow=True)
cluster.scale(2)  # specify number of workers explicitly

# cluster.adapt(minimum=1, maximum=100)  # or dynamically scale based on current workload