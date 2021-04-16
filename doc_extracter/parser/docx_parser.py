# -*- encoding: utf-8 -*-

# @File        :   docx_parser.py
# @Time        :   2021/04/15 17:03:05
# @Author      :   
# @Email       :   
# @Description :   

import logging
import os
import time

import docx

from .rules import preprocess_content
from .utils import get_create_time, get_file_extension

logger = logging.getLogger()


class Parser(object):

    @staticmethod
    def extract(filename: str, **kwargs):
        """ 解析文本

        Args:
            filename (str): `.docx` 为扩展名的文件

        Raises:
            Exception: [description]

        Returns:
            [type]: [description]
        """
        if not filename.endswith(".docx"):
            raise Exception(f"Unsupported file: {filename}")

        start = time.time()
        logger.info(f"开始处理: {filename}")
        document = docx.Document(filename)
        page = 0
        section = []
        for i, paragraph in enumerate(document.paragraphs):
            if paragraph.text:
                page += 1
                section.append({"page": page, "context": paragraph.text})

        cost = time.time() - start
        logger.info(f"处理结束: {filename}, 时间: {cost} s")

        data = {
            "owner": os.path.basename(filename).split("-")[0],
            "file": filename,
            "file_type": get_file_extension(filename),
            "section": section,
            "date": get_create_time(filename)
        }
            
        return data
