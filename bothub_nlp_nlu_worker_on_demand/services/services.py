# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


from abc import ABCMeta, abstractmethod


class BaseBackend(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.client = None
        self.label_key = None
        self.empty = None
        self.environments = None

    @abstractmethod
    def connect_service(self):
        pass

    @abstractmethod
    def services_list_queue(self):
        pass

    @abstractmethod
    def apply_deploy(self, queue_language, queue_name, queue_list):
        pass

    @abstractmethod
    def remove_service(self, service):
        pass
