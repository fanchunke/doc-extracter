# -*- encoding: utf-8 -*-

# @File        :   client.py
# @Time        :   2021/08/23 11:22:12
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

from .broker import Broker
from .backend import Backend
from .worker import Worker


class Client(object):

    def __init__(self, broker: Broker, backend: Backend):
        self.worker = Worker(broker, backend)

    def start_worker(self):
        self.worker.start()

    def stop_worker(self):
        self.worker.stop()
