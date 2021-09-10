# -*- encoding: utf-8 -*-

# @File        :   base.py
# @Time        :   2021/04/17 11:58:13
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import tempfile
import urllib.request
from typing import List

from ..message import Message, Result, JobStatus
from ..utils import is_url


def ensure_extension(s: str) -> str:
    return s.split(".")[-1]


class BaseParser(object):

    supported_extension: List[str] = []

    @classmethod
    def extract(cls, message: Message, **kwargs) -> Result:
        cls.preprocess(message)
        if not is_url(message.path):
            contents = cls.parse(message.path)
        else:
            with tempfile.NamedTemporaryFile('wb', suffix=f'.{ensure_extension(message.queue)}') as f:
                cls.save_tempfile(message.path, f.name)
                contents = cls.parse(f.name)
        result = cls.postprocess(message, contents)
        return result

    @classmethod
    def preprocess(cls, message: Message):
        if ensure_extension(message.queue) not in [ensure_extension(item) for item in cls.supported_extension]:
            raise Exception(f"Unsupported file: {message.path}")

    @staticmethod
    def save_tempfile(url: str, tmpfile: str):
        resp = urllib.request.urlopen(url)
        with open(tmpfile, 'wb') as f:
            f.write(resp.read())

    @classmethod
    def postprocess(cls, message: Message, contents: List[dict]) -> Result:
        result = Result(
            id=message.id,
            queue=message.queue,
            status=JobStatus.complete,
            section=contents,
        )
        return result

    @classmethod
    def parse(cls, filename: str) -> List[dict]:
        raise NotImplementedError("not implemented")
