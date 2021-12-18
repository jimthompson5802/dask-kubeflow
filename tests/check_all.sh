#!/bin/bash

echo ">>>deployment"
kubectl get deploy dask-scheduler
echo -e "\n>>> service"
kubectl get service dask-scheduler
echo -e "\n>>> virtualservice"
kubectl get virtualservice dask-scheduler
echo -e "\n>>> envoyfilter"
kubectl get envoyfilter dask-scheduler-add-header
