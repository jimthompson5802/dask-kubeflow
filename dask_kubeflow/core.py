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
v1_app_api = client.AppsV1Api()
custom_object_api = client.CustomObjectsApi(api_client)

# Global constants
ISTIO_API_GROUP = 'networking.istio.io'
ISTIO_API_VERSION = 'v1alpha3'


# TODO: assess integrating into dask-kubernetes
class KubeflowCluster:
    # TODO: revise constructor parameter list
    def __init__(self):
        # read in k8s resource template definitions
        fn = os.path.join(os.path.dirname(__file__), 'kubeflow.yaml')
        with open(fn, 'r') as f:
            self.kubeflow_template = yaml.load(f, Loader=yaml.SafeLoader)

        # TODO: generalize namespace specification
        # instantiate the dask scheduler deployment and service
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

        # istio custom resources
        self.envoy_filter = self.kubeflow_template['kubeflow']['scheduler-envoyfilter-template']
        envoy_filter_object = custom_object_api.create_namespaced_custom_object(
            group=ISTIO_API_GROUP, 
            version=ISTIO_API_VERSION,
            namespace='kubeflow-user',
            plural='envoyfilters',
            body=envoy_filter
        )

        self.virtual_service = self.kubeflow_template['kubeflow']['scheduler-virtual-service-template']
        virtual_service_object = custom_object_api.create_namespaced_custom_object(
            group=ISTIO_API_GROUP, 
            version=ISTIO_API_VERSION,
            namespace='kubeflow-user',
            plural='virtualservices',
            body=virtual_service
)

    def close(self):
        # TODO: remove hardcoding of namespace
        # shutdown scheduler deployment
        v1_app_api.delete_namespaced_deployment('dask-scheduler', namespace='kubeflow-user')

        # shutdown scheduler service
        v1_api.delete_namespaced_service('dask-scheduler', namespace='kubeflow-user')

        api_custom_object.delete_namespaced_custom_object(
            group=ISTIO_API_GROUP, 
            version=ISTIO_API_VERSION,
            namespace='kubeflow-user',
            plural='virtualservices',
            name='dask-scheduler'
        )

        api_custom_object.delete_namespaced_custom_object(
            group=ISTIO_API_GROUP, 
            version=ISTIO_API_VERSION,
            namespace='kubeflow-user',
            plural='envoyfilters',
            name='add-header'
        )