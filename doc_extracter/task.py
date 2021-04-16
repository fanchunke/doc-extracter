# -*- encoding: utf-8 -*-

# @File        :   task.py
# @Time        :   2021/04/13 19:43:29
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import functools
import hashlib
import logging
import operator
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

from elasticsearch import helpers

from .backend.file import FileBackend
from .backend.http import HTTPBackend
from .extensions import es
from .parser.docx_parser import Parser as DocxParser
from .parser.pptx_parser import Parser as PPTXParser

try:
    from .parser.ppt_parser import Parser as PPTParser
except:
    PPTParser = None

logger = logging.getLogger()

SUPPORTED_EXTENSIONS = {
    "pptx": [".pptx", ".ppt"],
    "docx": [".docx"],
}

SUPPORTED_BACKEND = ["files", "http"]


class Task(object):

    CHUNK_SIZE = 100

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

    def run(self):
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

        files = backend.get_tasks()

        logger.info(f"开始任务，线程数: {self.workers}")
        start = time.time()
        with ThreadPoolExecutor(self.workers) as pool:
            tasks = [pool.submit(self.process, file) for file in files]
            chunks = []
            for future in as_completed(tasks):
                chunks.append(future.result())
                # 批量处理结果，减少网络 IO
                if len(chunks) == self.CHUNK_SIZE:
                    self.handle_result(chunks)
                    chunks = []
            if chunks:
                self.handle_result(chunks)
        
        cost = (time.time()) - start
        logger.info(f"任务结束。符合条件的文件共计: {len(tasks)}, 时间: {cost} s")

    def process(self, filename: str):
        try:
            if filename.endswith(".pptx"):
                data = PPTXParser.extract(filename)
            elif filename.endswith(".ppt"):
                if PPTParser is None:
                    logger.warning(f"当前操作系统不支持 .ppt 后缀文件: {filename}")
                    return
                data = PPTParser.extract(filename)
            elif filename.endswith("docx"):
                data = DocxParser.extract(filename)
            else:
                raise Exception(f"UnSupported: {filename}")

            result = {"code": 0, "body": data, "filename": filename}

        except Exception as e:
            logger.exception(e)
            result = {"code": 1, "body": {}, "filename": filename}

        return result

    def handle_result(self, data: List[Dict]):
        # 数据写入 ES
        actions = []
        for item in data:
            if item.get("code") == 1:
                continue
            body = item.get("body") or {}
            actions.append({
                "_index": "docs",
                "_id": hashlib.md5(item.get("filename").encode("utf-8")).hexdigest(),
                "_source": body
            })

        helpers.bulk(es, actions=actions)

        # 处理结果写入 mongo
