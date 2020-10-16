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
BOTHUB_K8S_TOLERATION_KEY = config(
    "BOTHUB_K8S_TOLERATION_KEY", default="bothubmemorypod"
)

BOTHUB_NLU_VERSION = config("BOTHUB_NLU_VERSION", default=None)
BOTHUB_NLU_CELERY_SCALE = config("BOTHUB_NLU_CELERY_SCALE", default="5,3")

BOTHUB_MULTILANGUAGES =[
        "en",
        "de",
        "es",
        "pt",
        "fr",
        "it",
        "nl",
        "pt_br",
        "id",
        "mn",
        "ar",
        "bn",
        "hi",
        "ru",
        "th",
        "vi",
        "kh",
        "sw",
        "ca",
        "da",
        "el",
        "fa",
        "fi",
        "ga",
        "he",
        "hr",
        "hu",
        "ja",
        "nb",
        "pl",
        "ro",
        "si",
        "sv",
        "te",
        "tr",
        "tt",
        "ur",
        "zh",
        "ha",
        "ka",
        "kk",
        "sq",
        "hy",
        "az",
        "be",
        "bs",
        "bg",
        "cs",
        "ky",
        "mk",
        "sr",
        "uk",
        "uz",
        "ab",
        "aa",
        "af",
        "ak",
        "am",
        "an",
        "as",
        "av",
        "ae",
        "ay",
        "bm",
        "ba",
        "eu",
        "bh",
        "bi",
        "br",
        "my",
        "ch",
        "ce",
        "ny",
        "kw",
        "cv",
        "co",
        "cr",
        "dv",
        "dz",
        "eo",
        "et",
        "ee",
        "fo",
        "fj",
        "ff",
        "gl",
        "gu",
        "ht",
        "hz",
        "ho",
        "ia",
        "ie",
        "ig",
        "ik",
        "io",
        "is",
        "iu",
        "jv",
        "kl",
        "kn",
        "kr",
        "ks",
        "km",
        "ki",
        "rw",
        "kv",
        "kg",
        "ko",
        "ku",
        "kj",
        "la",
        "lb",
        "lg",
        "li",
        "ln",
        "lo",
        "lt",
        "lu",
        "lv",
        "gv",
        "mg",
        "ms",
        "ml",
        "mt",
        "mi",
        "mr",
        "mh",
        "na",
        "nv",
        "nd",
        "ne",
        "ng",
        "nn",
        "no",
        "ii",
        "nr",
        "oc",
        "oj",
        "cu",
        "om",
        "or",
        "os",
        "pa",
        "pi",
        "ps",
        "qu",
        "rm",
        "rn",
        "sa",
        "sc",
        "sd",
        "se",
        "sm",
        "sg",
        "gd",
        "sn",
        "sk",
        "sl",
        "so",
        "st",
        "su",
        "ss",
        "ta",
        "tg",
        "ti",
        "bo",
        "tk",
        "tl",
        "tn",
        "to",
        "tw",
        "ty",
        "ug",
        "ve",
        "vo",
        "wa",
        "cy",
        "wo",
        "fy",
        "xh",
        "yi",
        "yo",
        "za",
        "zu",
    ]

BOTHUB_SPACY_MULTILANG = {
    "queue": BOTHUB_MULTILANGUAGES,
    "image": "xx-SPACY",
    "service_name": "xx-SPACY",
}

BOTHUB_BERT_MULTILANGUAGES = []
for lang in BOTHUB_MULTILANGUAGES:
    BOTHUB_BERT_MULTILANGUAGES.append(lang + '-BERT')

BOTHUB_BERT_MULTILANG = {
    "queue": BOTHUB_BERT_MULTILANGUAGES,
    "image": "xx-BERT",
    "service_name": "xx-BERT",
}
