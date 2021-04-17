# -*- encoding: utf-8 -*-

# @File        :   pdf_parser.py
# @Time        :   2021/04/17 20:02:25
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import os
from typing import List

import pdfplumber
import fitz
from doc_extracter import Message, Result

from .base import BaseParser


class Parser(BaseParser):

    @staticmethod
    def extract(message: Message, method="PyMuPDF", **kwargs) -> Result:
        """ 解析文本

        Args:
            filename (str): `.pdf` 为扩展名的文件

        Raises:
            Exception: [description]

        Returns:
            [type]: [description]
        """
        filename = message.path
        if not filename.endswith(".pdf"):
            raise Exception(f"Unsupported file: {filename}")

        if not os.path.exists(filename):
            raise Exception(f"Not Found: {filename}")
        
        if method == "pdfplumber":
            contents = Parser.extract_from_pdfplumber(filename)
        elif method == "PyMuPDF":
            contents = Parser.extract_from_pymupdf(filename)
        else:
            raise Exception(f"Unsupported method: {method}")

        data = Parser.postprocess(message, contents)   
        return data

    @staticmethod
    def extract_from_pdfplumber(filename: str) -> List[dict]:
        contents = []
        with pdfplumber.open(filename) as pdf:
            for index, page in enumerate(pdf.pages):
                contents.append({
                    "page": index + 1,
                    "context": page.extract_text()
                })
        return contents

    @staticmethod
    def extract_from_pymupdf(filename: str) -> List[dict]:
        contents = []
        with fitz.Document(filename) as pdf:
            for index, page in enumerate(pdf):
                contents.append({
                    "page": index + 1,
                    "context": page.get_text("text")
                })

        return contents
