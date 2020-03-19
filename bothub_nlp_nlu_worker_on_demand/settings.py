from pydoc import locate
from decouple import config


def get_service(path):
    """
    Path Example: bothub_nlp_nlu_worker_on_demand.services.docker.DockerService
    """
    return locate(path)()


SERVICE_OPTIONS = {
    "docker": "bothub_nlp_nlu_worker_on_demand.services.docker.DockerService",
    "kubernetes": "bothub_nlp_nlu_worker_on_demand.services.kubernetes.KubernetesService",
}

BOTHUB_NLP_DOCKER_CLIENT_BASE_URL = config(
    "BOTHUB_NLP_DOCKER_CLIENT_BASE_URL", default="unix://var/run/docker.sock"
)

BOTHUB_NLP_NLU_WORKER_ON_DEMAND_API_PORT = config(
    "BOTHUB_NLP_NLU_WORKER_ON_DEMAND_API_PORT", default=2658, cast=int
)

BOTHUB_NLP_NLU_WORKER_DOCKER_IMAGE_NAME = config(
    "BOTHUB_NLP_NLU_WORKER_DOCKER_IMAGE_NAME", default="bothubit/bothub-nlp"
)

BOTHUB_NLP_NLU_WORKER_ON_DEMAND_DOWN_TIME = config(
    "BOTHUB_NLP_NLU_WORKER_ON_DEMAND_DOWN_TIME", cast=int, default=10
)

BOTHUB_NLP_NLU_WORKER_ON_DEMAND_NETWORKS = config(
    "BOTHUB_NLP_NLU_WORKER_ON_DEMAND_NETWORKS",
    cast=lambda v: [s.strip() for s in v.split(",")],
    default="bothub-nlp",
)

BOTHUB_NLP_NLU_WORKER_ON_DEMAND_RUN_IN_WORKER_NODE = config(
    "BOTHUB_NLP_NLU_WORKER_ON_DEMAND_RUN_IN_WORKER_NODE", cast=bool, default=False
)

BOTHUB_NLP_NLU_WORKER_ON_DEMAND_CONFIG_FILE = config(
    "BOTHUB_NLP_NLU_WORKER_ON_DEMAND_CONFIG_FILE",
    default="bothub-nlp-nlu-worker-on-demand.cfg",
)

BOTHUB_NLP_NLU_WORKER_ON_DEMAND_API_BASIC_AUTHORIZATION = config(
    "BOTHUB_NLP_NLU_WORKER_ON_DEMAND_API_BASIC_AUTHORIZATION", default=None
)

BOTHUB_SERVICE = get_service(
    path=config(
        "BOTHUB_SERVICE",
        cast=lambda value: SERVICE_OPTIONS.get(
            value, "bothub_nlp_nlu_worker_on_demand.services.docker.DockerService"
        ),
    )
)

BOTHUB_ENVIRONMENT = config("ENVIRONMENT", default="production")
