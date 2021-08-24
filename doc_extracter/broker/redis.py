# -*- encoding: utf-8 -*-

# @File        :   redis.py
# @Time        :   2021/08/22 20:35:33
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import json
import logging
from typing import Iterator, List, Optional

import redis

from ..message import Message
from ..utils import ensure_string
from . import Broker

logger = logging.getLogger("doc-extracter")


class RedisBroker(Broker):

    mapper = {
        "pptx": "ppt",
        "docx": "doc",
    }

    def __init__(self, url: str, supported_extensions: List[str]) -> None:
        self.pool: redis.Redis = redis.from_url(url)
        self.supported_extensions = supported_extensions

    @property
    def keys(self):
        keys = [f"{self.mapper.get(ext, ext)}_queue" for ext in self.supported_extensions]
        return keys

    def publish(self, message: Message):
        return super().publish(message)

    def consume(self) -> Iterator[Optional[Message]]:
        message = self.pool.brpop(self.keys, timeout=1)
        logger.info(f"message: {ensure_string(message)}")
        if not message:
            yield None
        else:
            try:
                message = json.loads(message[-1])
                yield Message(**message)
            except Exception as e:
                logger.error(f"Invalid message: {message}, error={str(e)}")
                yield None
