#!/bin/bash

kubectl delete deploy dask-scheduler
kubectl delete service dask-scheduler
kubectl delete service dask-scheduler-ui
kubectl delete virtualservice dask-scheduler
kubectl delete envoyfilter dask-scheduler-add-header
