# -*- encoding: utf-8 -*-

# @File        :   redis.py
# @Time        :   2021/04/16 13:40:51
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import asyncio
import json
from typing import Iterator, Callable, Coroutine, Any

import aioredis

from . import Backend


class RedisBackend(Backend):

    POP_KEY = "pub_queue"

    def __init__(self, pool: aioredis.Redis) -> None:
        self.pool = pool

    async def produce(self, queue: asyncio.Queue):
        return

    async def consume(self, queue: asyncio.Queue, callback: Callable[..., Coroutine[Any, Any, Any]]):
        while True:
            task = await self.pool.brpop(self.POP_KEY)
            task = json.loads(task[-1])
            await callback([task])
