from os import path

import yaml
from kubernetes import client, config
from decouple import config as decouple_conf
from .services import BaseBackend
from .. import settings


class KubernetesService(BaseBackend):
    """
    Kubernetes instance
    """

    def connect_service(self):
        config.load_kube_config()
        self.client = client.CoreV1Api()

        self.label_key = "bothub-nlp-wod"
        self.empty = "empty-value"
        self.environments = [
            {"name": var, "value": decouple_conf(var, default=self.empty)}
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
                "BOTHUB_K8S_TOLERATION_KEY",
            ]
        ]
        return self.client

    def services_list_queue(self):
        running_services = {}

        k8s_apps_v1 = client.AppsV1Api()

        for service in k8s_apps_v1.list_namespaced_deployment("bothub").items:
            service_labels = service.spec.template.metadata.labels

            if (
                self.label_key in service_labels
                and "track" in service_labels
                and service_labels.get("track") == settings.BOTHUB_ENVIRONMENT
            ):
                queue_name = service_labels.get(self.label_key)
                running_services[queue_name] = service
        return running_services

    def apply_deploy(self, queue_language, queue_name, queue_list):
        with open(path.join(path.dirname(__file__), "bothub-nlu-worker.yaml")) as f:
            dep = yaml.safe_load(f)
            dep["metadata"][
                "name"
            ] = f"bothub-nlp-nlu-worker-{queue_language.replace('pt_br', 'pt-br')}-{settings.BOTHUB_ENVIRONMENT}"
            dep["metadata"]["labels"][
                "k8s-app"
            ] = f"bothub-nlp-nlu-worker-{queue_language.replace('pt_br', 'pt-br')}"
            dep["spec"]["selector"]["matchLabels"]["bothub-nlp-wod"] = queue_language
            dep["spec"]["selector"]["matchLabels"][
                "track"
            ] = settings.BOTHUB_ENVIRONMENT
            dep["spec"]["selector"]["matchLabels"][
                "k8s-app"
            ] = f"bothub-nlp-nlu-worker-{queue_language.replace('pt_br', 'pt-br')}"
            dep["spec"]["template"]["metadata"]["labels"][
                "bothub-nlp-wod"
            ] = queue_language
            dep["spec"]["template"]["metadata"]["labels"][
                "track"
            ] = settings.BOTHUB_ENVIRONMENT
            dep["spec"]["template"]["metadata"]["labels"][
                "k8s-app"
            ] = f"bothub-nlp-nlu-worker-{queue_language.replace('pt_br', 'pt-br')}"
            dep["spec"]["template"]["metadata"]["labels"][
                "name"
            ] = f"bothub-nlp-nlu-worker-{queue_language.replace('pt_br', 'pt-br')}"
            for index, container in enumerate(
                dep["spec"]["template"]["spec"]["containers"]
            ):
                container.update(
                    {
                        "name": f"bothub-nlp-nlu-worker-{queue_language.replace('pt_br', 'pt-br')}"
                    }
                )
                container.update(
                    {
                        "image": f"{settings.BOTHUB_NLP_NLU_WORKER_DOCKER_IMAGE_NAME}:{settings.BOTHUB_NLU_VERSION}-{queue_language}"
                    }
                )
                container.update(
                    {
                        "command": [
                            "celery",
                            "worker",
                            "--autoscale",
                            "5,3",
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
                        ]
                    }
                )
                if '-' in queue_name:
                    model = queue_name.split('-')[-1]
                else:
                    model = None
                container.update(
                    {
                        "env": list(
                            list(
                                filter(
                                    lambda v: not v.get("value").endswith(self.empty),
                                    self.environments,
                                )
                            )
                            + list(
                                [
                                    {
                                        "name": "BOTHUB_NLP_LANGUAGE_QUEUE",
                                        "value": queue_name,
                                    }
                                ]
                            )
                            + list(
                                [{"name": "BOTHUB_NLP_SERVICE_WORKER", "value": "true"}]
                            )
                            + list(
                                [{"name": "BOTHUB_LANGUAGE_MODEL", "value": model}]
                            )
                        )
                    }
                )

            dep["spec"]["template"]["spec"]["tolerations"] = list(
                [
                    {
                        "key": settings.BOTHUB_K8S_TOLERATION_KEY,
                        "operator": "Equal",
                        "value": "false",
                        "effect": "NoExecute",
                    }
                ]
            )

            k8s_apps_v1 = client.AppsV1Api()
            k8s_apps_v1.create_namespaced_deployment(body=dep, namespace="bothub")

    def remove_service(self, service):
        k8s_apps_v1 = client.AppsV1Api()
        k8s_apps_v1.delete_namespaced_deployment(
            name=service.metadata.name,
            namespace=service.metadata.namespace,
            body=client.V1DeleteOptions(
                propagation_policy="Foreground", grace_period_seconds=0
            ),
        )
