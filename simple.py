# -*- encoding: utf-8 -*-

# @File        :   simple.py
# @Time        :   2021/04/18 22:31:40
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import logging
import logging.config
import logging.handlers
import multiprocessing
import time
from typing import List

from doc_extracter.logger import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger("doc-extracter")


from doc_extracter.task import Task


def logger_configurer(queue: multiprocessing.Queue):
    h = logging.handlers.QueueHandler(queue)
    logger.addHandler(h)
    logger.setLevel(logging.DEBUG)


def logger_listener(queue: multiprocessing.Queue):
    while True:
        try:
            while not queue.empty():
                record = queue.get()
                logger = logging.getLogger(record.name)
                logger.handle(record)
            time.sleep(1)
        except KeyboardInterrupt:
            break


def doc_extracter(type, backend, dirname, url, workers, queue):
    try:
        task = Task(type, backend, dirname, url, workers)
        task.extract(queue)
        logger.info("结束任务")
    except KeyboardInterrupt as e:
        logger.info("Caught keyboard interrupt. Canceling tasks...")


def main(type, backend, dirname, url, workers):
    logger.info("开始任务")
    logger.info(f"backend: {backend}, type: {type}, dirname: {dirname}, url: {url}, workers: {workers}")
    queue = multiprocessing.Queue()
    listener = multiprocessing.Process(target=logger_listener, args=(queue,))
    listener.start()

    worker_list: List[multiprocessing.Process] = []

    for _ in range(workers):
        worker = multiprocessing.Process(
            target=doc_extracter,
            args=(type, backend, dirname, url, workers, queue,)
        )
        worker_list.append(worker)
        worker.start()
    
    for worker in worker_list:
        try:
            worker.join()
        except KeyboardInterrupt:
            worker.terminate()

    logger.info("结束任务")


if __name__ == '__main__':
    backend = "redis"
    type = "all"
    dirname = url = None
    workers = 10
    main(type, backend, dirname, url, workers)
