# -*- encoding: utf-8 -*-

# @File        :   async_task.py
# @Time        :   2021/04/16 14:09:43
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import asyncio
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from typing import Dict, List, Optional

import aioredis
from elasticsearch import helpers

from .backend.file import FileBackend
from .backend.http import HTTPBackend
from .backend.redis import RedisBackend
from .errors import UnSupportedError
from .extensions import create_index, create_pool, es
from .parser.docx_parser import Parser as DocxParser
from .parser.pptx_parser import Parser as PPTXParser

try:
    from .parser.ppt_parser import Parser as PPTParser
except:
    PPTParser = None

logger = logging.getLogger()


from . import SUPPORTED_BACKEND, SUPPORTED_EXTENSIONS, Message


class AsyncTask(object):

    CHUNK_SIZE = 100
    RESULT_KEY = "result_queue"

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
        if not self.pool:
            self.pool = await create_pool()

    async def run(self):

        if self.supported_type == "all":
            supported_extensions = SUPPORTED_EXTENSIONS
        elif self.supported_type not in SUPPORTED_EXTENSIONS:
            raise Exception(f"文件扩展不支持: {self.supported_type}")
        else:
            supported_extensions = [self.supported_type]

        supported_extensions = list(set(supported_extensions))

        if self.backend == "files":
            backend = FileBackend(self.dirname, supported_extensions)
        elif self.backend == "http":
            backend = HTTPBackend(self.url)
        elif self.backend == "redis":
            backend = RedisBackend(self.pool, supported_extensions)

        logger.info(f"开始任务，worker 数: {self.workers}")
        start = time.time()

        loop = asyncio.get_event_loop()

        producers = [loop.create_task(backend.produce(self.queue))]
        consumers = [loop.create_task(backend.consume(self.queue, self.process)) for _ in range(self.workers)]
        await asyncio.gather(*producers, *consumers)
        await self.queue.join()

        cost = (time.time()) - start
        logger.info(f"任务结束。时间: {cost} s")

    async def process(self, task: dict):
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(self.executor, self._process, Message(**task))
            await self.handle_result([result])
            logger.info(f"处理成功。id={task.get('id')}")
        except Exception as e:
            logger.error(f"处理失败。id={task.get('id')}, msg={str(e)}")

    def _process(self, task: Message):
        """ 处理消息

        Args:
            task (Message): [description]

        Examples:
            {
                "id" : "6078f5c55f92aa894f92a427",
                "owner": 111111,
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
        start = time.time()
        cost = lambda: time.time() - start
        logger.info(f"开始处理: {task.path}, id={task.id}")

        if task.state != 0:
            logger.warning(f"任务处于其他状态，不处理。task: {task}")
            return

        file_id = task.id
        filename = task.path
        ext = task.ext
        try:
            if ext == ".pptx":
                body = PPTXParser.extract(task)
            elif ext == ".ppt":
                if PPTParser is None:
                    logger.warning(f"当前操作系统不支持 .ppt 后缀文件: {filename}")
                    return
                body = PPTParser.extract(task)
            elif ext == ".docx":
                body = DocxParser.extract(task)
            else:
                raise UnSupportedError(f"UnSupported: {filename}")

            # state=1 处理成功
            result = {"state": 1, "body": asdict(body), "id": file_id}
            logger.info(f"解析成功, id={file_id}, filename={filename}, cost={cost()}")

        except UnSupportedError as e:
            logger.error(e)
            # state=2 不支持的类型
            result = {"state": -1, "body": {}, "id": file_id}
            logger.info(f"文件不支持, id={file_id}, filename={filename}, cost={cost()}")
        except Exception as e:
            logger.exception(e)
            # state=2 处理失败
            result = {"state": 2, "body": {}, "id": file_id}
            logger.info(f"解析失败, id={file_id}, filename={filename}, cost={cost()}")

        return result

    async def handle_result(self, data: List[Dict]):
        # 数据写入 ES
        actions = []
        for item in data:
            body = item.get("body") or {}
            if not body:
                continue
            actions.append({
                "_index": "dahua-docs",
                "_id": item.get("id"),
                "_source": body
            })

        await helpers.async_bulk(es, actions=actions)

        # 处理结果写入 redis 队列
        for item in data:
            if item.get("state") == -1:
                continue
            value = {"id": item.get("id"), "state": item.get("state")}
            await self.pool.lpush(self.RESULT_KEY, json.dumps(value))
