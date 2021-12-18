# Proof-of-Concept: Dask enabled for Kubeflow

## System requirementes
* kubernetes 1.19+
* kubeflow 1.3+

## Development installation
```
git clone https://github.com/jimthompson5802/dask-kubeflow

# install as editable package
pip install -e dask-kubeflow
```

## VSCODE Environment setup
* GIT Extension Pack
* PyLint install (conda)

## High-level Design Outline
Key class: `KubeflowCluster()` with these methods:
* `__init__()`: instantiates the DASK cluster.  Starts scheduler, workers and enables the DASK Scheduler UI.
* `scale()`: scales worker tasks up/down
* `close()`: shuts down the cluster