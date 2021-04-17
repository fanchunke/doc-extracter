# -*- encoding: utf-8 -*-

# @File        :   pptx_parser.py
# @Time        :   2021/04/13 15:37:44
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import logging
import os

import pptx
from doc_extracter import Message, Result

from .base import BaseParser
from .rules import preprocess_content
from .utils import get_create_time, get_file_extension

logger = logging.getLogger("doc-extracter")


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
        if not filename.endswith(".pptx"):
            raise Exception(f"Unsupported file: {filename}")

        if not os.path.exists(filename):
            raise Exception(f"Not Found: {filename}")

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
                    "context": origin_contents,
                }
            )

        data = Parser.postprocess(message, text_runs)   
        return data
