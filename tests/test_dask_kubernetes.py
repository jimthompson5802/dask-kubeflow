from dask_kubernetes import KubeCluster
import os
from time import sleep

print(f'working dir: {os.getcwd()}')

cluster = KubeCluster('worker-spec.yaml', scheduler_service_wait_timeout=120, enable_kubeflow=True)
#print('after Kubecluster'); sleep(10); print('after first sleep, before scale')
cluster.scale(3)  # specify number of workers 
print("waiting after scale"); sleep(10); print('after scale delay')
# cluster.adapt(minimum=1, maximum=100)  # or dynamically scale based on current workload
# cluster.close()
print('all done')