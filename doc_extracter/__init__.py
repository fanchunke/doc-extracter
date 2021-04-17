# -*- encoding: utf-8 -*-

# @File        :   __init__.py
# @Time        :   2021/04/17 11:09:20
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

from dataclasses import dataclass
from typing import List

SUPPORTED_EXTENSIONS = ["pptx", "docx", "pdf"]
SUPPORTED_BACKEND = ["files", "http", "redis"]

@dataclass
class Message(object):
    id: str
    owner: int
    name: str
    path: str
    ext: str
    date: str
    state: int = 0


@dataclass
class Result(object):
    owner: int
    file: str
    file_type: str
    section: List[dict]
    date: str
