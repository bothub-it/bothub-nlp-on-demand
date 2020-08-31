import docker
from decouple import config as decouple_conf
from .services import BaseBackend
from .. import settings


class DockerService(BaseBackend):
    """
    Docker instance
    """

    def connect_service(self):
        self.client = docker.DockerClient(
            base_url=settings.BOTHUB_NLP_DOCKER_CLIENT_BASE_URL
        )
        self.label_key = "bothub-nlp-wod.name"
        self.empty = "empty-value"
        self.environments = [
            "{}={}".format(var, decouple_conf(var, default=self.empty))
            for var in [
                "ENVIRONMENT",
                "SUPPORTED_LANGUAGES",
                "BOTHUB_ENGINE_URL",
                "BOTHUB_NLP_CELERY_SENTRY_CLIENT",
                "BOTHUB_NLP_CELERY_SENTRY",
                "BOTHUB_NLP_CELERY_BROKER_URL",
                "BOTHUB_NLP_CELERY_BACKEND_URL",
                "BOTHUB_NLP_NLU_AGROUP_LANGUAGE_QUEUE",
                "BOTHUB_NLP_AWS_S3_BUCKET_NAME",
                "BOTHUB_NLP_AWS_ACCESS_KEY_ID",
                "BOTHUB_NLP_AWS_SECRET_ACCESS_KEY",
                "BOTHUB_NLP_AWS_REGION_NAME",
            ]
        ]
        return self.client

    def services_list_queue(self):
        running_services = {}
        for service in self.client.services.list():
            service_labels = service.attrs.get("Spec", {}).get("Labels")
            if self.label_key in service_labels:
                queue_name = service_labels.get(self.label_key)
                running_services[queue_name] = service
        return running_services

    def apply_deploy(self, queue_language, queue_name, queue_list):
        constraints = []
        if settings.BOTHUB_NLP_NLU_WORKER_ON_DEMAND_RUN_IN_WORKER_NODE:
            constraints.append("node.role == worker")
        if '-' in queue_name:
            temp = queue_name.split('-')
            lang = temp[0]
            model = temp[-1]
        else:
            lang = queue_language
            model = None
        self.client.services.create(
            settings.BOTHUB_NLP_NLU_WORKER_DOCKER_IMAGE_NAME
            + f":{settings.BOTHUB_NLU_VERSION}-{queue_language}",
            [
                "celery",
                "worker",
                "--autoscale",
                "5,3" if not model == 'BERT' else '5,5',
                "-O",
                "fair",
                "--workdir",
                "bothub_nlp_nlu_worker",
                "-A",
                "celery_app",
                "-c",
                "1",
                "-l",
                "INFO",
                "-E",
                "-Q",
                queue_list,
            ],
            env=list(
                list(filter(lambda v: not v.endswith(self.empty), self.environments))
                + list([f"BOTHUB_NLP_LANGUAGE_QUEUE={lang}"])
                + list(["BOTHUB_NLP_SERVICE_WORKER=true"])
                + list([f"BOTHUB_LANGUAGE_MODEL={model}"])
            ),
            labels={self.label_key: queue_name},
            networks=settings.BOTHUB_NLP_NLU_WORKER_ON_DEMAND_NETWORKS,
            constraints=constraints,
        )

    def remove_service(self, service):
        service.remove()
