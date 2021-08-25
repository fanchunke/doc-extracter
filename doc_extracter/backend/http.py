# -*- encoding: utf-8 -*-

# @File        :   http.py
# @Time        :   2021/08/23 15:00:41
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import json
import logging

import requests

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
        resp = requests.post(
            self.url,
            json=result.dict()
        )

        content = resp.content.decode("utf-8")
        logger.info(f"Response: {content}")

        if resp.status_code != 200:
            raise Exception(f"回传结果失败, status: {resp.status_code}")
        try:
            data = json.loads(content)
        except:
            raise Exception(f"回传结果返回的不是一个有效的 json")
        else:
            code = data.get('code')
            if code != 200:
                raise Exception(f"回传结果失败, code: {code}")
