import configparser
import cgi

from time import sleep, time
from celery_worker_on_demand import CeleryWorkerOnDemand
from celery_worker_on_demand import Agent
from celery_worker_on_demand import UpWorker
from celery_worker_on_demand import DownWorker
from celery_worker_on_demand import APIHandler

from . import settings

running_services = {}
last_services_lookup = 0


def services_lookup():
    global running_services
    global last_services_lookup
    if (time() - last_services_lookup) < 5:
        return False
    settings.BOTHUB_SERVICE.connect_service()
    running_services = settings.BOTHUB_SERVICE.services_list_queue()
    last_services_lookup = time()
    return True


def get_multilang(queue_name):
    if queue_name in settings.BOTHUB_MULTILANGUAGES:
        multilang = settings.BOTHUB_SPACY_MULTILANG
    elif queue_name in settings.BOTHUB_BERT_MULTILANGUAGES:
        multilang = settings.BOTHUB_BERT_MULTILANG
    else:
        multilang = None
    return multilang


class MyUpWorker(UpWorker):
    def run(self):
        global running_services
        services_lookup()
        multilang = get_multilang(self.queue.name)
        if multilang is not None:
            queue_name = multilang.get("service_name")
            queue_language = multilang.get("image")
            queue_list = ",".join(multilang.get("queue", []))
        else:
            queue_name = self.queue.name
            queue_language = (
                queue_name.split(":")[1] if ":" in queue_name else queue_name
            )
            queue_list = self.queue.name
        service = running_services.get(queue_name)
        if not service:
            settings.BOTHUB_SERVICE.connect_service()
            settings.BOTHUB_SERVICE.apply_deploy(queue_language, queue_name, queue_list)

        while not self.queue.has_worker:
            sleep(1)


class MyDownWorker(DownWorker):
    def run(self):
        global running_services
        services_lookup()
        multilang = get_multilang(self.queue.name)
        if multilang is not None:
            queue_name = multilang.get("service_name")
        else:
            queue_name = self.queue.name
        service = running_services.get(queue_name)
        if service:
            settings.BOTHUB_SERVICE.connect_service()
            settings.BOTHUB_SERVICE.remove_service(service)
            running_services[queue_name] = None


class MyAgent(Agent):
    def flag_down(self, queue):
        global running_services
        ignore_list = self.cwod.config.get("worker-down", "ignore").split(",")

        multilang = get_multilang(self.queue.name)
        if multilang is not None:
            queue_name = multilang.get("service_name")
        else:
            queue_name = queue.name

        if queue_name in ignore_list:
            return False
        if queue.size > 0:
            return False
        if not queue.has_worker:
            return False
        services_lookup()
        service = running_services.get(queue_name)
        if not service:
            return False
        last_interaction = 0
        for worker in queue.workers:
            last_interaction = sorted(
                [
                    last_interaction,
                    (worker.last_task_received_at or 0),
                    (worker.last_task_started_at or 0),
                    (worker.last_task_succeeded_at or 0),
                ],
                reverse=True,
            )[0]
        if last_interaction == 0:
            return False
        last_interaction_diff = time() - last_interaction
        if last_interaction_diff > (
            settings.BOTHUB_NLP_NLU_WORKER_ON_DEMAND_DOWN_TIME * 60
        ):
            return True
        return False


class MyAPIHandler(APIHandler):
    def post_data(self):
        content_type = self.headers.get("content-type")
        if not content_type:
            return {}
        ctype, pdict = cgi.parse_header(content_type)
        if not ctype == "multipart/form-data":
            return {}
        pdict["boundary"] = bytes(pdict.get("boundary", ""), "utf-8")
        parsed = cgi.parse_multipart(self.rfile, pdict)
        return dict(
            map(
                lambda x: (
                    x[0],
                    list(map(lambda x: x.decode(), x[1]))
                    if len(x[1]) > 1
                    else x[1][0].decode(),
                ),
                parsed.items(),
            )
        )

    def do_POST(self):
        if not self.has_permission():
            return
        post_data = self.post_data()
        for key, value in post_data.items():
            section, option = key.split(".", 1)
            self.cwod.config.set(
                section, option, ",".join(value) if isinstance(value, list) else value
            )
        self.cwod.write_config()
        self.do_GET()


class MyDemand(CeleryWorkerOnDemand):
    Agent = MyAgent
    UpWorker = MyUpWorker
    DownWorker = MyDownWorker
    APIHandler = MyAPIHandler

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = configparser.ConfigParser()
        self.config.read_dict({"worker-down": {"ignore": []}})
        self.config.read(settings.BOTHUB_NLP_NLU_WORKER_ON_DEMAND_CONFIG_FILE)

    def write_config(self):
        self.config.write(
            open(settings.BOTHUB_NLP_NLU_WORKER_ON_DEMAND_CONFIG_FILE, "w+")
        )

    def serializer(self):
        data = super().serializer()
        data.update({"config": self.config._sections})
        return data
