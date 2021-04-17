# -*- encoding: utf-8 -*-

# @File        :   docx_parser.py
# @Time        :   2021/04/15 17:03:05
# @Author      :   
# @Email       :   
# @Description :   

import logging
import os

import docx
from doc_extracter import Message, Result

from .base import BaseParser
from .rules import preprocess_content
from .utils import get_create_time, get_file_extension

logger = logging.getLogger()


class Parser(BaseParser):

    @staticmethod
    def extract(message: Message, **kwargs) -> Result:
        """ 解析文本

        Args:
            filename (str): `.docx` 为扩展名的文件

        Raises:
            Exception: [description]

        Returns:
            [type]: [description]
        """
        filename = message.path
        if not filename.endswith(".docx"):
            raise Exception(f"Unsupported file: {filename}")

        if not os.path.exists(filename):
            raise Exception(f"Not Found: {filename}")

        document = docx.Document(filename)
        page = 0
        section = []
        for i, paragraph in enumerate(document.paragraphs):
            if paragraph.text:
                page += 1
                section.append({"page": page, "context": paragraph.text})

        data = Parser.postprocess(message, section)
        return data
