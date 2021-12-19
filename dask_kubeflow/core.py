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
    """
    KubeflowCluster provides interface to a kubeflow enabled kuberenetes cluster.
    """
    def __init__(
        self, 
        namespace: str='kubeflow-user'
    ):
        """
        Parameters:
        :param namespace: kubernetes namespace to run the dask cluster
        """

        self.namespace = namespace

        # read in k8s resource template definitions
        fn = os.path.join(os.path.dirname(__file__), 'kubeflow.yaml')
        with open(fn, 'r') as f:
            self.kubeflow_template = yaml.load(f, Loader=yaml.SafeLoader)

        # instantiate the dask scheduler deployment and service
        scheduler_deployment_resource = self.kubeflow_template['kubeflow']['scheduler-deployment-template']
        self.scheduler_deployment = utils.create_from_dict(
            api_client,
            scheduler_deployment_resource,
            namespace=self.namespace
        )[0]

        scheduler_service_resource = self.kubeflow_template['kubeflow']['scheduler-service-template']
        self.scheduler_service = utils.create_from_dict(
            api_client,
            scheduler_service_resource,
            namespace=self.namespace
        )[0]

        scheduler_ui_service_resource = self.kubeflow_template['kubeflow']['scheduler-ui-service-template']
        self.scheduler_ui_service = utils.create_from_dict(
            api_client,
            scheduler_ui_service_resource,
            namespace=self.namespace
        )[0]

        # istio custom resources
        envoy_filter = self.kubeflow_template['kubeflow']['scheduler-envoyfilter-template']
        self.envoy_filter_object = custom_object_api.create_namespaced_custom_object(
            group=ISTIO_API_GROUP, 
            version=ISTIO_API_VERSION,
            namespace=self.namespace,
            plural='envoyfilters',
            body=envoy_filter
        )

        virtual_service = self.kubeflow_template['kubeflow']['scheduler-virtual-service-template']
        self.virtual_service_object = custom_object_api.create_namespaced_custom_object(
            group=ISTIO_API_GROUP, 
            version=ISTIO_API_VERSION,
            namespace=self.namespace,
            plural='virtualservices',
            body=virtual_service
        )

        # setup workers
        # instantiate the dask worker deployment
        worker_deployment_resource = self.kubeflow_template['kubeflow']['worker-deployment-template']
        self.worker_deployment = utils.create_from_dict(
            api_client,
            worker_deployment_resource,
            namespace=self.namespace
        )[0]

        # # work storage pvc
        # worker_pvc_resource = self.kubeflow_template['kubeflow']['worker-persistentvolumeclaim-template']
        # self.worker_pvc = utils.create_from_dict(
        #     api_client,
        #     worker_pvc_resource,
        #     namespace=self.namespace
        # )[0]

    @property
    def scheduler_service_address(self):
        service_name = self.scheduler_service.metadata.name
        service_port = self.scheduler_service.spec.ports[0].port
        service_address = 'tcp://' + service_name + '.' + self.namespace + '.svc.cluster.local:' + str(service_port)
        return service_address
 
    def close(self):
        """Shutdown the dask cluster """

        # shutdown worker deployment
        v1_app_api.delete_namespaced_deployment(
            self.worker_deployment.metadata.name, 
            namespace=self.namespace
        )
        
        # # remove worker pvc
        # v1_api.delete_namespaced_persistent_volume_claim(
        #     self.worker_pvc.metadata.name, 
        #     namespace=self.namespace
        # )


        # shutdown scheduler deployment
        v1_app_api.delete_namespaced_deployment(
            self.scheduler_deployment.metadata.name, 
            namespace=self.namespace
        )

        # shutdown scheduler service
        v1_api.delete_namespaced_service(
            self.scheduler_service.metadata.name, 
            namespace=self.namespace
        )

        # shutdown scheduler ui service
        v1_api.delete_namespaced_service(
            self.scheduler_ui_service.metadata.name, 
            namespace=self.namespace
        )

        # shutdown istio custom resources
        custom_object_api.delete_namespaced_custom_object(
            group=ISTIO_API_GROUP, 
            version=ISTIO_API_VERSION,
            namespace=self.namespace,
            plural='virtualservices',
            name=self.virtual_service_object['metadata']['name']
        )

        custom_object_api.delete_namespaced_custom_object(
            group=ISTIO_API_GROUP, 
            version=ISTIO_API_VERSION,
            namespace=self.namespace,
            plural='envoyfilters',
            name=self.envoy_filter_object['metadata']['name']
        )
