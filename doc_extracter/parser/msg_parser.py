# -*- encoding: utf-8 -*-

# @File        :   msg_parser.py
# @Time        :   2021/08/05 15:37:44
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import logging
import os
from typing import List

import extract_msg
import six

from .base import BaseParser

logger = logging.getLogger("doc-extracter")


def ensure_bytes(string):
    """Normalize string to bytes.
    `ExtractMsg.Message._getStringStream` can return unicode or bytes depending
    on what is originally stored in message file.
    This helper functon makes sure, that bytes type is returned.
    """
    if isinstance(string, six.string_types):
        return string.encode('utf-8')
    return string


class Parser(BaseParser):

    supported_extension = '.msg'

    @classmethod
    def parse(cls, filename: str) -> List[dict]:
        """ 解析 .msg

        Args:
            filename (str): `.msg` 为扩展名的文件

        Raises:
            Exception: 不支持的文件类型/文件不存在

        Returns:
            List[dict]: 解析结果
        """
        if not filename.endswith(cls.supported_extension):
            raise Exception(f"Unsupported file: {filename}")

        if not os.path.exists(filename):
            raise Exception(f"Not Found: {filename}")

        text_runs = []
        with extract_msg.Message(filename) as m:
            context: bytes = ensure_bytes(m.subject) + six.b('\n\n') + ensure_bytes(m.body)
            text_runs = [{
                "page": 1,
                "context": context.decode("utf-8"),
            }]
        return text_runs
