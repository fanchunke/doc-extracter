# -*- encoding: utf-8 -*-

# @File        :   xls_parser.py
# @Time        :   2021/09/09 18:09:44
# @Author      :   junsi
# @Email       :
# @Description :  pip install xlrd==1.2.0


import logging
import os
from typing import List

import xlrd

from .base import BaseParser

logger = logging.getLogger("doc-extracter")


class Parser(BaseParser):
    supported_extension = ['.xls', '.xlsx']

    @classmethod
    def parse(cls, filename: str) -> List[dict]:
        """ 解析 .xls
        Args:
            filename (str): `.xls` 为扩展名的文件
        Raises:
            Exception: 不支持的文件类型/文件不存在
        Returns:
            List[dict]: 解析结果
        """

        if not os.path.exists(filename):
            raise Exception(f"Not Found: {filename}")

        with open(filename, 'rb') as f:
            context = cls.xlrd_excel_body(f.name, f.read())

        return context

    @classmethod
    def xlrd_excel_body(cls, file_name: str, file_contents: bytes):
        wb = xlrd.open_workbook(
            filename=file_name,
            file_contents=file_contents
        )
        restful = []
        table = wb.sheets()
        table_sheets = wb.sheet_names()

        for sheets_index, sheets in enumerate(table):
            """获取所有行数 数据条目"""

            rows = sheets.nrows
            header = sheets.row_values(0)
            for row in range(rows):
                # if row == 0: continue  # 跳过首行
                for col, line in enumerate(header):
                    row_values = sheets.row_values(row)[col]
                    if not row_values: continue
                    restful.append({
                        'page': "({sheets}, {row}, {col})".format(
                            sheets=table_sheets[sheets_index], row=row, col=col
                        ),
                        'context': row_values
                    })

        return restful
