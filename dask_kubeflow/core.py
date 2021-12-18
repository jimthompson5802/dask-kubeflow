import logging
import os
import yaml

from kubernetes import client, config, utils

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# get in-cluster config
config.load_incluster_config()

# Client API Interface
api_client = client.ApiClient()

# V1 Core API Interface
v1_api = client.CoreV1Api()


# TODO: assess integrating into dask-kubernetes
class KubeflowCluster:
    # TODO: revise constructor parameter list
    def __init__(self):
        # read in k8s resource template definitions
        fn = os.path.join(os.path.dirname(__file__), 'kubeflow.yaml')
        with open(fn, 'r') as f:
            self.kubeflow_template = yaml.load(f, Loader=yaml.SafeLoader)

        # instantiate the dask scheduler deployment and service
        # TODO: generalize namespace specification
        scheduler_deployment_resource = self.kubeflow_template['kubeflow']['scheduler-deployment-template']
        self.scheduler_deployment = utils.create_from_dict(
            api_client,
            scheduler_deployment_resource,
            namespace='kubeflow-user'
        )[0]

        scheduler_service_resource = self.kubeflow_template['kubeflow']['scheduler-service-template']
        self.scheduler_service = utils.create_from_dict(
            api_client,
            scheduler_service_resource,
            namespace='kubeflow-user'
        )[0]



