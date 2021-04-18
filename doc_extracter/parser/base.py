# -*- encoding: utf-8 -*-

# @File        :   base.py
# @Time        :   2021/04/17 11:58:13
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

from typing import List
from doc_extracter import Message, Result


class BaseParser(object):

    @staticmethod
    def postprocess(message: Message, contents: List[dict]) -> Result:
        result = Result(
            owner=message.owner,
            file=message.name,
            path=message.path,
            file_type=message.ext,
            section=contents,
            date=message.date
        )
        return result
