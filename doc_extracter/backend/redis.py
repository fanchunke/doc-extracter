# -*- encoding: utf-8 -*-

# @File        :   redis.py
# @Time        :   2021/04/16 13:40:51
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import asyncio
import json
from typing import Iterator

import aioredis

from . import Backend


class RedisBackend(Backend):

    POP_KEY = "pub_queue"

    def __init__(self, pool: aioredis.Redis) -> None:
        self.pool = pool

    async def produce(self, queue: asyncio.Queue):
        while True:
            item = await self.pool.rpop(self.POP_KEY)
            if item:
                await queue.put(json.loads(item))
            else:
                await asyncio.sleep(0.001)
