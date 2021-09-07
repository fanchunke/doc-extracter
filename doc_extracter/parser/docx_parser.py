# -*- encoding: utf-8 -*-

# @File        :   docx_parser.py
# @Time        :   2021/04/15 17:03:05
# @Author      :   
# @Email       :   
# @Description :   

import logging
import os
from typing import List
import zipfile
from lxml import etree

import docx

from .base import BaseParser

logger = logging.getLogger("doc-extracter")


class Parser(BaseParser):

    supported_extension = '.docx'

    @classmethod
    def parse(cls, filename: str, method="xml") -> List[dict]:
        """ 解析 docx

        Args:
            filename (str): `.docx` 为扩展名的文件

        Raises:
            Exception: 不支持的文件类型/文件不存在

        Returns:
            List[dict]: 解析结果
        """

        if not os.path.exists(filename):
            raise Exception(f"Not Found: {filename}")

        if method == 'xml':
            return XMLParser.parse(filename)
        else:
            return CustomParser.parse(filename)


class XMLParser(object):

    @classmethod
    def parse(cls, filename: str) -> List[dict]:
        with zipfile.ZipFile(filename) as f:
            xml_content = f.read("word/document.xml")
        tree = etree.fromstring(xml_content)

        section = []
        for index, paragraph in enumerate(cls._iterparagraphs(tree)):
            content = [text.strip() for text in cls._itertext(paragraph) if text.strip()]
            if content:
                section.append({"page": str(index + 1), "context": "".join(content)})
        return section

    @classmethod
    def _iterparagraphs(cls, my_etree):
        """Iterator to go through xml tree's text nodes"""
        for node in my_etree.iter(tag=etree.Element):
            if cls._check_element_is(node, 'p'):
                yield node

    @classmethod
    def _itertext(cls, my_etree):
        """Iterator to go through xml tree's text nodes"""
        for node in my_etree.iter(tag=etree.Element):
            if cls._check_element_is(node, 't'):
                yield node.text

    @classmethod
    def _check_element_is(cls, element, type_char):
        word_schema = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        return element.tag == '{%s}%s' % (word_schema, type_char)


class CustomParser(object):

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

        if not os.path.exists(filename):
            raise Exception(f"Not Found: {filename}")

        section = []
        with open(filename, 'rb') as f:
            document = docx.Document(f)
            for i, paragraph in enumerate(document.paragraphs):
                if paragraph.text:
                    section.append({"page": str(i+1), "context": paragraph.text})

            # 处理表格
            table_data = []
            for table in document.tables:
                for row in table.rows:
                    table_data.extend([cell.text for cell in row.cells])
            if table_data:
                section.append({"page": "1", "context": "\n".join(table_data)})
        return section
