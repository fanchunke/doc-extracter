# -*- encoding: utf-8 -*-

# @File        :   redis.py
# @Time        :   2021/04/16 13:40:51
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import json
import logging
import time
from typing import Iterator, List

import redis

from doc_extracter import Message

from . import Backend

logger = logging.getLogger("doc-extracter")


class RedisBackend(Backend):

    mapper = {
        "pptx": "ppt",
        "docx": "doc",
        "pdf": "pdf",
        "msg": "msg",
    }

    def __init__(self, pool: redis.Redis, supported_extensions: List[str]) -> None:
        self.pool = pool
        self.supported_extensions = supported_extensions
        self.keys = self.get_keys()

    def get_keys(self) -> List[str]:
        keys = []
        for ext in self.supported_extensions:
            if ext not in self.mapper:
                raise Exception(f"UnSupported file type: {ext}")
            keys.append(f"{self.mapper.get(ext)}_queue")
        return keys

    def consume(self) -> Iterator[Message]:
        while True:
            message = self.pool.brpop(self.keys, timeout=5)
            logger.info(f"message: {message}")
            if not message:
                time.sleep(5)
                continue
            try:
                message = json.loads(message[-1])
                yield Message(**message)
            except Exception as e:
                logger.error(f"处理失败, message={message}, error={str(e)}")
