# -*- encoding: utf-8 -*-

# @File        :   docx_parser.py
# @Time        :   2021/04/15 17:03:05
# @Author      :   
# @Email       :   
# @Description :   

import logging
import os
from typing import List

import docx

from .base import BaseParser

logger = logging.getLogger("doc-extracter")


class Parser(BaseParser):

    supported_extension = '.docx'

    @classmethod
    def parse(cls, filename: str) -> List[dict]:
        """ 解析 docx

        Args:
            filename (str): `.docx` 为扩展名的文件

        Raises:
            Exception: 不支持的文件类型/文件不存在

        Returns:
            List[dict]: 解析结果
        """
        if not filename.endswith(cls.supported_extension):
            raise Exception(f"Unsupported file: {filename}")

        if not os.path.exists(filename):
            raise Exception(f"Not Found: {filename}")

        section = []
        with open(filename, 'rb') as f:
            document = docx.Document(f)
            for i, paragraph in enumerate(document.paragraphs):
                if paragraph.text:
                    section.append({"page": i+1, "context": paragraph.text})

            # 处理表格
            table_data = []
            for table in document.tables:
                for row in table.rows:
                    table_data.extend([cell.text for cell in row.cells])
            if table_data:
                section.append({"page": 1, "context": "\n".join(table_data)})
        return section
