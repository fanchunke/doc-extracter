# -*- encoding: utf-8 -*-

# @File        :   http.py
# @Time        :   2021/08/22 20:56:50
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

from typing import Iterator, List, Optional

from ..message import Message
from . import Broker


class HTTPBroker(Broker):

    def __init__(self, url: str, supported_extensions: List[str]) -> None:
        self.url = url
        self.supported_extensions = supported_extensions

    def publish(self, message: Message):
        return super().publish(message)

    def consume(self) -> Iterator[Optional[Message]]:
        return super().consume()
