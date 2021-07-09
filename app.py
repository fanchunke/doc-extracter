# -*- encoding: utf-8 -*-

# @File        :   app.py
# @Time        :   2021/04/14 11:26:55
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import logging
import logging.config
import logging.handlers
import multiprocessing
from typing import List

import click

from doc_extracter.command import OptionRequiredIf
from doc_extracter.logger import LOGGING
from doc_extracter.task import Task

logging.config.dictConfig(LOGGING)
logger = logging.getLogger("doc-extracter")


def listener_configurer(queue: multiprocessing.Queue):
    h = logging.handlers.QueueHandler(queue)
    logger.addHandler(h)
    logger.setLevel(logging.DEBUG)


def listener_process(queue: multiprocessing.Queue):
    while True:
        try:
            record = queue.get()
            if record is None:
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.exception(e)


def doc_extracter(type, backend, dirname, url):
    try:
        task = Task(type, backend, dirname, url)
        task.run()
        logger.info("结束任务")
    except KeyboardInterrupt as e:
        logger.info("Caught keyboard interrupt. Canceling tasks...")


@click.command()
@click.option(
    '--backend',
    help="获取文件的方式",
    type=click.Choice(["files", "http", "redis"], case_sensitive=False)
)
@click.option(
    '--type',
    help='处理的文件类型',
    type=click.Choice(["pptx", "docx", "pdf", "all"], case_sensitive=False),
)
@click.option(
    '--dirname',
    help='处理的文档目录。如果 `--backend=files`，`--dirname` 为必需参数',
    option="backend",
    value="files",
    cls=OptionRequiredIf
)
@click.option(
    "--url",
    help='获取任务的服务地址。如果 `--backend=http`，`--url` 为必需参数',
    option="backend",
    value="http",
    cls=OptionRequiredIf
)
@click.option(
    '--workers',
    help="worker数",
    type=int,
    default=4
)
def main(type, backend, dirname, url, workers):
    logger.info("开始任务")
    logger.info(f"backend: {backend}, type: {type}, dirname: {dirname}, url: {url}, workers: {workers}")
    queue = multiprocessing.Queue(-1)
    listener = multiprocessing.Process(target=listener_process, args=(queue,))
    listener.start()

    worker_list: List[multiprocessing.Process] = []
    for _ in range(workers):
        worker = multiprocessing.Process(
            target=doc_extracter,
            args=(type, backend, dirname, url,)
        )
        worker_list.append(worker)
        worker.start()
    
    for worker in worker_list:
        try:
            worker.join()
        except KeyboardInterrupt:
            worker.terminate()

    queue.put_nowait(None)
    listener.join()
    logger.info("结束任务")


if __name__ == '__main__':
    main()
