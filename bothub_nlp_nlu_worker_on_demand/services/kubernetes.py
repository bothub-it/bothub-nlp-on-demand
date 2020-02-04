from os import path

import yaml
from kubernetes import client, config, utils
from .services import BaseBackend


class KubernetesService(BaseBackend):
    """
    Docker instance
    """

    def connect_service(self):
        config.load_kube_config()
        self.client = client.CoreV1Api()

        self.label_key = "bothub-nlp-wod"
        self.empty = "empty-value"
        return self.client

    def services_list_queue(self):
        running_services = {}

        for service in self.client.list_namespaced_pod('bothub').items:
            service_labels = service.metadata.labels
            if self.label_key in service_labels:
                queue_name = service_labels.get(self.label_key)
                running_services[queue_name] = service
        return running_services

    def apply_deploy(self, queue_language, queue_name, environments):
        constraints = []

        with open(path.join(path.dirname(__file__), "bothub-nlu-worker.yaml")) as f:
            dep = yaml.safe_load(f)
            k8s_apps_v1 = client.AppsV1Api()

            resp = k8s_apps_v1.create_namespaced_deployment(
                body=dep, namespace="bothub")
            print("Deployment created. status='%s'" % resp.metadata.name)
            print(resp)
            print(resp.metadata)


        # if settings.BOTHUB_NLP_NLU_WORKER_ON_DEMAND_RUN_IN_WORKER_NODE:
        #     constraints.append("node.role == worker")
        # self.client.services.create(
        #     settings.BOTHUB_NLP_NLU_WORKER_DOCKER_IMAGE_NAME + f":{queue_language}",
        #     [
        #         "celery",
        #         "worker",
        #         "--autoscale",
        #         "5,3",
        #         "-O",
        #         "fair",
        #         "-A",
        #         "bothub_nlp_nlu_worker.celery_app",
        #         "-c",
        #         "1",
        #         "-l",
        #         "INFO",
        #         "-E",
        #         "-Q",
        #         queue_name,
        #     ],
        #     env=list(
        #         list(filter(lambda v: not v.endswith(self.empty), environments)) +
        #         list([f'BOTHUB_NLP_LANGUAGE_QUEUE={queue_name}']) +
        #         list(['BOTHUB_NLP_SERVICE_WORKER=true'])
        #     ),
        #     labels={self.label_key: queue_name},
        #     networks=settings.BOTHUB_NLP_NLU_WORKER_ON_DEMAND_NETWORKS,
        #     constraints=constraints,
        # )
