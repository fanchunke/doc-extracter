# -*- encoding: utf-8 -*-

# @File        :   pdf.py
# @Time        :   2021/04/18 22:31:40
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

from dataclasses import asdict
import asyncio
import json
import logging
import logging.config
from concurrent import futures
from concurrent.futures import ProcessPoolExecutor
from doc_extracter.extensions import create_pool
import time

import redis
from elasticsearch import Elasticsearch, helpers

from doc_extracter import Message, Result
from doc_extracter.async_task import AsyncTask
from doc_extracter.logger import LOGGING
from doc_extracter.parser.pdf_parser import Parser

MESSAGE_KEY = "pdf_queue"
RESULT_KEY = "result_queue"

rd = redis.Redis(host="127.0.0.1", port=6379, db=0, encoding="utf-8")
es = Elasticsearch(host="172.17.201.207", port=9200)
executor = ProcessPoolExecutor(10)
task = AsyncTask("pdf", "redis", None, None, 10)

logger = logging.getLogger("doc-extracter")

def extract():
    asyncio.run(task.setup())
    task.pool = asyncio.run(create_pool())
    while True:
        data = rd.brpop(MESSAGE_KEY, 5)
        if not data:
            time.sleep(5)
            continue
        data = data[-1]
        try:
            data = json.loads(data)
            message = Message(**data)
            logger.info(f"开始处理，id={message.id}, filename={message.name}")
            future = executor.submit(process, message)
            result = future.result()
            state = result.get("state")
            if state == 1:
                logger.info(f"处理完成，id={message.id}, filename={message.name}")
            elif state == 2:
                logger.error(f"处理失败，id={message.id}, filename={message.name}")
        except Exception as e:
            logger.exception(e)
            logger.error(f"处理失败，id={message.id}, filename={message.name}")


def process(message: Message):
    result = task._process(message)

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
    helpers.bulk(es, actions=actions)

    if result.get("state") == -1:
        return
    value = {"id": result.get("id"), "state": result.get("state")}
    logger.info(f"写入REDIS，id={result.get('id')}")
    rd.lpush("result_queue", json.dumps(value))

    return result


if __name__ == '__main__':
    logging.config.dictConfig(LOGGING)
    extract()
        