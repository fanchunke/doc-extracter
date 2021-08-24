# -*- encoding: utf-8 -*-

# @File        :   http.py
# @Time        :   2021/08/23 15:00:41
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import logging

from doc_extracter.message import ResultMessage

from . import Backend

logger = logging.getLogger("doc-extracter")


class HTTPBackend(Backend):

    def __init__(self, url: str):
        self.url = url

    def get_result(self, task_id: str) -> ResultMessage:
        return super().get_result(task_id)

    def set_result(self, task_id: str, result: ResultMessage):
        logger.info(f"Result: {result}")
        return super().set_result(task_id, result)
