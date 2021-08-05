# -*- encoding: utf-8 -*-

# @File        :   msg_parser.py
# @Time        :   2021/08/05 15:37:44
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import logging
import os

import extract_msg
import six
from doc_extracter import Message, Result

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

    @staticmethod
    def extract(message: Message, **kwargs) -> Result:
        """ 解析文本

        Args:
            filename (str): `.pptx` 为扩展名的文件

        Raises:
            Exception: [description]

        Returns:
            [type]: [description]
        """
        filename = message.path
        if not filename.endswith(".msg"):
            raise Exception(f"Unsupported file: {filename}")

        if not os.path.exists(filename):
            raise Exception(f"Not Found: {filename}")

        m = extract_msg.Message(filename)
        context = ensure_bytes(m.subject) + six.b('\n\n') + ensure_bytes(m.body)

        text_runs = [{
            "page": 1,
            "context": context,
        }]

        data = Parser.postprocess(message, text_runs)   
        return data
