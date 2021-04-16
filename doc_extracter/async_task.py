# -*- encoding: utf-8 -*-

# @File        :   async_task.py
# @Time        :   2021/04/16 14:09:43
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import asyncio
import functools
import hashlib
import json
import logging
import operator
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

import aioredis
from elasticsearch import helpers

from .backend.file import FileBackend
from .backend.http import HTTPBackend
from .backend.redis import RedisBackend
from .extensions import create_index, create_pool, es
from .parser.docx_parser import Parser as DocxParser
from .parser.pptx_parser import Parser as PPTXParser

try:
    from .parser.ppt_parser import Parser as PPTParser
except:
    PPTParser = None

logger = logging.getLogger()

SUPPORTED_EXTENSIONS = {
    "pptx": [".pptx"],
    "docx": [".docx"],
}

SUPPORTED_BACKEND = ["files", "http", "redis"]


class AsyncTask(object):

    CHUNK_SIZE = 100
    PUSH_KEY = "sub_queue"

    def __init__(
        self,
        supported_type: str,
        backend: str,
        dirname: Optional[str] = None,
        url: Optional[str] = None,
        workers: int = 1
    ) -> None:
        self.supported_type = supported_type
        if backend not in SUPPORTED_BACKEND:
            raise Exception(f"Unsupported backend: {backend}")
        if backend == "http" and not url:
            raise Exception(f"url required if backend is {backend}")
        if backend == "files" and not dirname:
            raise Exception(f"dirname required if backend is {backend}")
        self.backend = backend
        self.dirname = dirname
        self.url = url
        if workers <= 0:
            raise Exception(f"线程数不合法: {workers}")
        self.workers = workers
        self.queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor(workers)
        self.pool: aioredis.Redis = None

    async def __aenter__(self):
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await es.close()
        if self.pool:
            self.pool = None

    async def setup(self):
        await create_index(es)
        self.pool = await create_pool()

    async def run(self):

        if self.supported_type == "all":
            supported_extensions = functools.reduce(operator.iconcat, SUPPORTED_EXTENSIONS.values(), [])
        else:
            supported_extensions = SUPPORTED_EXTENSIONS.get(self.supported_type)
        if not supported_extensions:
            raise Exception(f"文件扩展不支持: {self.supported_type}")

        supported_extensions = list(set(supported_extensions))

        if self.backend == "files":
            backend = FileBackend(self.dirname, supported_extensions)
        elif self.backend == "http":
            backend = HTTPBackend(self.url)
        elif self.backend == "redis":
            backend = RedisBackend(self.pool)

        logger.info(f"开始任务，线程数: {self.workers}")
        start = time.time()

        loop = asyncio.get_event_loop()

        try:
            # await backend.produce(self.queue)
            loop.create_task(backend.produce(self.queue))
            await self.consume()
        finally:
            await es.close()

        cost = (time.time()) - start
        logger.info(f"任务结束。时间: {cost} s")

    async def consume(self):
        loop = asyncio.get_event_loop()
        chunks = []
        while True:
            while not self.queue.empty():
                task = await self.queue.get()
                result = await loop.run_in_executor(self.executor, self.process, task)
                chunks.append(result)
                if len(chunks) == self.CHUNK_SIZE:
                    await self.handle_result(chunks)
                    chunks = []
        
            if chunks:
                await self.handle_result(chunks)
                chunks = []

            await asyncio.sleep(0.001)

    def process(self, task: dict):
        """ 处理消息

        Args:
            task (dict): [description]

        Examples:
            {
                "id" : "6078f5c55f92aa894f92a427",
                "name" : "rss.xml",
                "path" : "/Users/Joey/.3T/robo-3t/1.3.1/cache/rss.xml",
                "ext" : ".xml",
                "state" : 0
            }

        Raises:
            Exception: [description]

        Returns:
            [type]: [description]
        """
        state = task.get("state")
        if state != 0:
            logger.warning(f"任务处于其他状态，不处理。task: {task}")

        file_id = task.get("id")
        filename = task.get("path")
        ext = task.get("ext")
        try:
            if ext == ".pptx":
                body = PPTXParser.extract(filename)
            elif ext == ".ppt":
                if PPTParser is None:
                    logger.warning(f"当前操作系统不支持 .ppt 后缀文件: {filename}")
                    return
                body = PPTParser.extract(filename)
            elif ext == ".docx":
                body = DocxParser.extract(filename)
            else:
                raise Exception(f"UnSupported: {filename}")

            # state=1 处理成功
            result = {"state": 1, "body": body, "id": file_id}

        except Exception as e:
            logger.exception(e)
            # state=2 处理失败
            result = {"state": 2, "body": {}, "id": file_id}

        return result

    async def handle_result(self, data: List[Dict]):
        # 数据写入 ES
        actions = []
        for item in data:
            if item.get("state") == 2:
                continue
            body = item.get("body") or {}
            actions.append({
                "_index": "dahua-docs",
                "_id": item.get("id"),
                "_source": body
            })

        await helpers.async_bulk(es, actions=actions)

        # 处理结果写入 redis 队列
        for item in data:
            value = {"id": item.get("id"), "state": item.get("state")}
            await self.pool.lpush(self.PUSH_KEY, json.dumps(value))

