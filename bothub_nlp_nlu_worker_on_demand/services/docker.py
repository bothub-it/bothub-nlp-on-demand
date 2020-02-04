import docker
from .services import BaseBackend
from .. import settings


class DockerService(BaseBackend):
    """
    Docker instance
    """

    def connect_service(self):
        self.client = docker.DockerClient(base_url=settings.BOTHUB_NLP_DOCKER_CLIENT_BASE_URL)
        self.label_key = "bothub-nlp-wod.name"
        self.empty = "empty-value"
        return self.client

    def services_list_queue(self):
        running_services = {}
        for service in self.client.services.list():
            service_labels = service.attrs.get("Spec", {}).get("Labels")
            if self.label_key in service_labels:
                queue_name = service_labels.get(self.label_key)
                running_services[queue_name] = service
        return running_services

    def apply_deploy(self, queue_language, queue_name, environments):
        constraints = []
        if settings.BOTHUB_NLP_NLU_WORKER_ON_DEMAND_RUN_IN_WORKER_NODE:
            constraints.append("node.role == worker")
        self.client.services.create(
            settings.BOTHUB_NLP_NLU_WORKER_DOCKER_IMAGE_NAME + f":{queue_language}",
            [
                "celery",
                "worker",
                "--autoscale",
                "5,3",
                "-O",
                "fair",
                "-A",
                "bothub_nlp_nlu_worker.celery_app",
                "-c",
                "1",
                "-l",
                "INFO",
                "-E",
                "-Q",
                queue_name,
            ],
            env=list(
                list(filter(lambda v: not v.endswith(self.empty), environments)) +
                list([f'BOTHUB_NLP_LANGUAGE_QUEUE={queue_name}']) +
                list(['BOTHUB_NLP_SERVICE_WORKER=true'])
            ),
            labels={self.label_key: queue_name},
            networks=settings.BOTHUB_NLP_NLU_WORKER_ON_DEMAND_NETWORKS,
            constraints=constraints,
        )
