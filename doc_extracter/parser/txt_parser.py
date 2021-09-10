# -*- encoding: utf-8 -*-

# @File        :   txt_parser.py
# @Time        :   2021/08/25 10:36:37
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   
  

import logging
import os
from typing import List

import pptx

from .base import BaseParser

logger = logging.getLogger("doc-extracter")


class Parser(BaseParser):

    supported_extension = ['.txt']

    @classmethod
    def parse(cls, filename: str) -> List[dict]:
        """ 解析 .txt

        Args:
            filename (str): `.txt` 为扩展名的文件

        Raises:
            Exception: 不支持的文件类型/文件不存在

        Returns:
            List[dict]: 解析结果
        """

        if not os.path.exists(filename):
            raise Exception(f"Not Found: {filename}")

        sections = []
        with open(filename, 'rb') as f:
            page = 0
            for line in f:
                page += 1
                sections.append({
                    "page": str(page),
                    "context": line.strip().decode("utf-8"),
                })
        return sections
