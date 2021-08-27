# -*- encoding: utf-8 -*-

# @File        :   ppt_parser.py
# @Time        :   2021/04/13 19:10:09
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import logging
import os
import platform
from typing import List

from doc_extracter.parser.base import BaseParser

from .pptx_parser import Parser as PPTXParser

if platform.system() != "Windows":
    raise Exception(".ppt 后缀的文件只能在 Windows 环境下运行")
else:
    import win32com.client


logger = logging.getLogger("doc-extracter")

class Parser(BaseParser):

    supported_extension = '.ppt'

    @classmethod
    def parse(cls, filename) -> List[dict]:
        """ 解析 .pptx

        Args:
            filename (str): `.ppt` 为扩展名的文件

        Raises:
            Exception: [description]

        Returns:
            [type]: [description]
        """

        if not os.path.exists(filename):
            raise Exception(f"Not Found: {filename}")

        app = win32com.client.Dispatch("PowerPoint.Application")
        presentation = app.Presentations.Open(filename, WithWindow=False)

        pptx_filename = os.path.join(
            os.path.dirname(filename),
           f"{os.path.splitext(filename)[0]}.pptx"
        )
        presentation.SaveAs(pptx_filename)

        app = presentation = None

        try:
            data = PPTXParser.parse(pptx_filename)
        except Exception as e:
            logger.exception(e)
            raise
        finally:
            os.remove(pptx_filename)

        return data
