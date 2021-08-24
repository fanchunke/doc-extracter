# -*- encoding: utf-8 -*-

# @File        :   worker.py
# @Time        :   2021/08/20 15:39:44
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import logging
import time

from . import parser
from .backend import Backend, HTTPBackend
from .broker import Broker
from .errors import UnSupportedError
from .message import JobStatus, Message, ResultMessage, NoMoreMessage

logger = logging.getLogger("doc-extracter")


class Worker(object):

    def __init__(self, broker: Broker, backend: Backend):
        self.broker = broker
        self.backend = backend
        self.started: bool = False

    def start(self):
        self.started = True
        logger.info("Starting worker")
        while self.started:
            for task_message in self.broker.consume():
                if task_message is None:
                    continue
                elif task_message == NoMoreMessage:
                    self.started = False
                    break

                try:
                    result_message = self.run_task(task_message)
                except Exception as e:
                    logger.error(f"failed to run task message: {task_message}, error: {str(e)}")
                    continue

                # 额外支持的特性
                if task_message.callback:
                    http_backend = HTTPBackend(task_message.callback)
                    try:
                        http_backend.set_result(result_message.id, result_message)
                    except Exception as e:
                        logger.error(f"failed to set callback: {str(e)}")

                try:
                    self.backend.set_result(result_message.id, result_message)
                except Exception as e:
                    logger.error(f"failed to set result message: {str(e)}")
        logger.info("Worker Stopped Successfully")
        self.started = False

    def stop(self):
        self.started = False

    def run_task(self, message: Message) -> ResultMessage:
        start = time.time()
        cost = lambda: time.time() - start
        logger.info(f"开始处理, filename={message.path}, id={message.id}")

        if message.status != JobStatus.not_progress:
            raise Exception(f"任务处于其他状态，不处理。")

        file_id = message.id
        filename = message.path
        try:
            body = parser.process(message)
            # state=1 处理成功
            result = ResultMessage(**body.dict())
            logger.info(f"解析成功, id={file_id}, filename={filename}, cost={cost()}")
        except UnSupportedError as e:
            logger.error(e)
            # state=-1 不支持的类型
            result = ResultMessage(status=JobStatus.unsupported, id=file_id)
            logger.info(f"文件不支持, id={file_id}, filename={filename}, cost={cost()}")
        except Exception as e:
            logger.exception(e)
            # state=2 处理失败
            result = ResultMessage(status=JobStatus.failed, id=file_id)
            logger.info(f"解析失败, id={file_id}, filename={filename}, cost={cost()}")

        return result
