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

logger = logging.getLogger("doc-extracter")


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

        with open(filename, 'rb') as f:
            document = docx.Document(f)
            section = []
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

        data = Parser.postprocess(message, section)
        return data
