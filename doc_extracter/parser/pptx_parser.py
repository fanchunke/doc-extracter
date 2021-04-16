# -*- encoding: utf-8 -*-

# @File        :   pptx_parser.py
# @Time        :   2021/04/13 15:37:44
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import logging
import os
import time

import pptx

from .rules import preprocess_content
from .utils import get_create_time, get_file_extension

logger = logging.getLogger()


class Parser(object):

    @staticmethod
    def extract(filename: str, **kwargs):
        """ 解析文本

        Args:
            filename (str): `.pptx` 为扩展名的文件

        Raises:
            Exception: [description]

        Returns:
            [type]: [description]
        """
        if not filename.endswith(".pptx"):
            raise Exception(f"Unsupported file: {filename}")

        start = time.time()
        logger.info(f"开始处理: {filename}")
        presentation = pptx.Presentation(filename)
        text_runs = []
        for index, slide in enumerate(presentation.slides):
            contents = []
            for shape in slide.shapes:
                if not shape.has_text_frame:
                    continue
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        contents.append(run.text)
            
            origin_contents = "\n\n".join(contents)
            text_runs.append(
                {
                    "page": index + 1,
                    # "origin": origin_contents,
                    # "context": preprocess_content(origin_contents),
                    "context": origin_contents,
                }
            )

        cost = time.time() - start
        logger.info(f"处理结束: {filename}, 时间: {cost} s")

        data = {
            "owner": os.path.basename(filename).split("-")[0],
            "file": filename,
            "file_type": get_file_extension(filename),
            "section": text_runs,
            "date": get_create_time(filename)
        }
            
        return data
