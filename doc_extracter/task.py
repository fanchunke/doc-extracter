# -*- encoding: utf-8 -*-

# @File        :   task.py
# @Time        :   2021/04/19 03:41:31
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import json
import logging
import logging.config
import logging.handlers
import multiprocessing
import time
from dataclasses import asdict
from typing import List, Optional

import redis
from elasticsearch import Elasticsearch, helpers

from doc_extracter import Message
from doc_extracter.config import Setttings
from doc_extracter.logger import LOGGING

from . import SUPPORTED_BACKEND, SUPPORTED_EXTENSIONS
from .errors import UnSupportedError
from .parser.docx_parser import Parser as DocxParser
from .parser.pdf_parser import Parser as PDFParser
from .parser.pptx_parser import Parser as PPTXParser

try:
    from .parser.ppt_parser import Parser as PPTParser
except:
    PPTParser = None

logging.config.dictConfig(LOGGING)
logger = logging.getLogger("doc-extracter")
settings = Setttings()

class Task(object):

    CHUNK_SIZE = 100
    RESULT_KEY = "result_queue"
    MESSAGE_KEY = ("pdf_queue", "ppt_queue", "doc_queue",)

    def __init__(
        self,
        supported_type: str,
        backend: str,
        dirname: Optional[str] = None,
        url: Optional[str] = None,
        workers: int = 1
    ) -> None:
        self.supported_type = supported_type
        # if backend not in SUPPORTED_BACKEND:
        #     raise Exception(f"Unsupported backend: {backend}")
        # if backend == "http" and not url:
        #     raise Exception(f"url required if backend is {backend}")
        # if backend == "files" and not dirname:
        #     raise Exception(f"dirname required if backend is {backend}")
        if backend != "redis":
            raise Exception("Unsupported backend")
        self.backend = backend
        self.dirname = dirname
        self.url = url
        if workers <= 0:
            raise Exception(f"线程数不合法: {workers}")
        self.workers = workers
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            encoding="utf-8"
        )
        self.es = Elasticsearch(host=settings.ES_HOST, port=settings.ES_PORT)

    def extract(self, queue: multiprocessing.Queue):
        self.logger_configurer(queue)
        while True:
            data = self.redis.brpop(self.MESSAGE_KEY)
            if not data:
                time.sleep(5)
                continue
            data = data[-1]
            try:
                data = json.loads(data)
                message = Message(**data)
                start = time.time()
                cost = lambda: time.time() - start
                logger.info(f"开始处理，id={message.id}, filename={message.name}")
                self.process(message)
            except Exception as e:
                logger.exception(e)
                logger.error(f"处理失败，id={message.id}, filename={message.name}, cost={cost()}")

    def process(self, message: Message):
        result = self._process(message)

        actions = []
        body = result.get("body") or {}
        if not body:
            return
        actions.append({
            "_index": "dahua-docs",
            "_id": result.get("id"),
            "_source": body
        })

        logger.info(f"写入ES，id={result.get('id')}")
        helpers.bulk(self.es, actions=actions)

        if result.get("state") == -1:
            return result
        value = {"id": result.get("id"), "state": result.get("state")}
        logger.info(f"写入REDIS，id={result.get('id')}")
        self.redis.lpush("result_queue", json.dumps(value))

        return result

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
        logger.info(f"开始处理, filename={task.path}, id={task.id}")

        if task.state != 0:
            logger.warning(f"任务处于其他状态，不处理。filename={task.path}, id={task.id}")
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
            elif ext == ".pdf":
                body = PDFParser.extract(task)
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

    @staticmethod
    def logger_configurer(queue: multiprocessing.Queue):
        h = logging.handlers.QueueHandler(queue)
        logger.addHandler(h)
        logger.setLevel(logging.DEBUG)

    @staticmethod
    def logger_listener(queue: multiprocessing.Queue):
        while True:
            while not queue.empty():
                record = queue.get()
                logger = logging.getLogger(record.name)
                logger.handle(record)
            time.sleep(1)

    def run(self):
        logger.info("开始任务")
        queue = multiprocessing.Queue()
        listener = multiprocessing.Process(target=self.logger_listener, args=(queue,))
        listener.start()

        workers: List[multiprocessing.Process] = []

        for _ in range(self.workers):
            worker = multiprocessing.Process(target=self.extract, args=(queue,))
            workers.append(worker)
            worker.start()
        
        for worker in workers:
            worker.join()

        logger.info("结束任务")
