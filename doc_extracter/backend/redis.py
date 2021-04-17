# -*- encoding: utf-8 -*-

# @File        :   redis.py
# @Time        :   2021/04/16 13:40:51
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import asyncio
import json
import logging
from typing import Any, Callable, Coroutine, List

import aioredis

from . import Backend

logger = logging.getLogger(__name__)


class RedisBackend(Backend):

    mapper = {
        "pptx": "ppt",
        "docx": "doc",
    }

    def __init__(self, pool: aioredis.Redis, supported_extensions: List[str]) -> None:
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

    async def produce(self, queue: asyncio.Queue):
        pass

    async def consume(
        self,
        queue: asyncio.Queue,
        callback: Callable[..., Coroutine[Any, Any, Any]]
    ):
        while True:
            task = await self.pool.brpop(*self.keys, timeout=5)
            if not task:
                await asyncio.sleep(10)
                continue
            try:
                task = json.loads(task[-1])
                await callback(task)
            except Exception as e:
                logger.error(f"处理失败, message={task}, error={str(e)}")
