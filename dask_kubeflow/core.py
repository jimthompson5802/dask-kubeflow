import logging
import os
from time import sleep
from typing import Tuple
import yaml

from kubernetes import client, config, utils

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
        self.requested_replicas = worker_deployment_resource['spec']['replicas']
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

    def scale(self, count: int) -> None:
        """
        Adjust number of workers

        Parameters:
        :param count: Number of workers requested

        Return:
        None
        """
        worker_deployment_name = self.worker_deployment.metadata.name

        scale_spec = client.V1ScaleSpec(replicas=count)
        self.requested_replicas = count

        scale_metadata = client.V1ObjectMeta(name=worker_deployment_name, namespace=self.namespace)

        v1_app_api.replace_namespaced_deployment_scale(
            name=worker_deployment_name,
            namespace=self.namespace,
            body=client.V1Scale(metadata=scale_metadata, spec=scale_spec),
            pretty='true'
        )

    @property
    def scheduler_service_address(self) -> str:
        """Retrieve scheduler service location"""
        service_name = self.scheduler_service.metadata.name
        service_port = self.scheduler_service.spec.ports[0].port
        service_address = 'tcp://' + service_name + '.' + self.namespace + '.svc.cluster.local:' + str(service_port)
        return service_address

    @property
    def worker_count(self) -> Tuple['requested_count', 'ready_count']:
        """Retrieve worker counts"""
        worker_deployment = v1_app_api.read_namespaced_deployment(
            name=self.worker_deployment.metadata.name,
            namespace=self.namespace
        )
        return self.requested_replicas, \
                worker_deployment.status.ready_replicas if not worker_deployment.status.ready_replicas is None else 0
 
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

    def wait_for_workers(self, timeout: int=900, verbose: bool=False) -> bool:
        """Wait for requested workers to be come active
        Parameters:
        :param timeout: Number of seconds to wait for workers to be come active
        :param verbose: True print periodic progress message, False no messages
                        progress message printed once per second for first 10 seconds
                        after which message printed every ten seconds.

        Return:
        bool: True if requested workers are active, False if time out occurred before workers are active
        """
        counter = 0
        while True:
            requested_workers, ready_workers = self.worker_count
            if verbose and ((counter < 10) or (counter >= 10 and counter % 10 == 0 and counter < 120) or
                (counter >= 120 and counter % 30 == 0) ):
                logger.info(f'wait time: {counter} (sec), requested workers: {requested_workers}, ready workers: {ready_workers}')
            if (requested_workers > 0) and (requested_workers == ready_workers):
                return True
            else:
                counter += 1
                if counter >= timeout:
                    return False
            sleep(1)