# -*- encoding: utf-8 -*-

# @File        :   __init__.py
# @Time        :   2021/08/22 22:04:38
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import abc
from typing import Iterator, Optional

from doc_extracter.message import Message


class Broker(abc.ABC):
    """ Broker interface """

    @abc.abstractmethod
    def publish(self, message: Message):
        pass

    @abc.abstractmethod
    def consume(self) -> Iterator[Optional[Message]]:
        pass


from .amqp import AMQPBroker
from .file import FileBroker
from .http import HTTPBroker
from .redis import RedisBroker
