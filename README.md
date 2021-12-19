# Proof-of-Concept: Dask enabled for Kubeflow

## System requirementes
* kubernetes 1.19+
* kubeflow 1.3+

## Development installation
```
git clone https://github.com/jimthompson5802/dask-kubeflow

# install as editable package
pip install -e dask_kubeflow
```

## VSCODE Environment setup
* GIT Extension Pack
* PyLint install (conda)

## High-level Design Outline
Key class: `KubeflowCluster()` with these methods:
* `__init__()`: instantiates the DASK cluster.  Starts scheduler, workers and enables the DASK Scheduler UI.
* `scale()`: scales worker tasks up/down (**to be implemented**)
* `close()`: shuts down the cluster
* `worker_count`: returns tuple containing `(requested_number_of_worker, ready_worker_count)`
* `scheduer_service_address`: returns string to be used by DASK `Client` in connecting to DASK Scheduler.  
* `wait_for_workers()`: method to wait for number of ready workers to equal requested number of workers.