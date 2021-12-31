# Proof-of-Concept: Dask enabled for Kubeflow

Implementation as separate package from `dask-kubernetes`.  This approach is **DEPRECATED**.

**Only useful assets in this repo are the programs to test kubeflow enabled `dask-kubernetes` modifications.  See `tests` directory.**

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
* Bookmarks


## High-level Design Outline
Key class: `KubeflowCluster()` with these methods:
* `__init__()`: instantiates the DASK cluster.  Starts scheduler, workers and enables the DASK Scheduler UI.
* `scale()`: scales worker tasks up/down
* `close()`: shuts down the cluster
* `worker_count`: returns tuple containing `(requested_number_of_worker, ready_worker_count)`
* `scheduer_service_address`: returns string to be used by DASK `Client` in connecting to DASK Scheduler.  
* `wait_for_workers()`: method to wait for number of ready workers to equal requested number of workers.

## Release History
### Tag: `0.1.0-dev0`
* Proof-of-concept of using k8s api to manipulate DASK k8s resources in `kubeflow` enabled cluster.
* All methods described in the **High-level Design Outline** implemented.  
* Support for `kubeflow` specific constructs, such as `istio` `VirtualService` and `EnvoyFilter`.
* Example [Jupyter Notebook](./dask_kubeflow/examples/dask_kubeflow_demo.ipynb)
