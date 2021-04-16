# -*- encoding: utf-8 -*-

# @File        :   http.py
# @Time        :   2021/04/16 11:28:03
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

from typing import Iterator

from . import Backend


class HTTPBackend(Backend):

    def __init__(self, url) -> None:
        self.url = url

    def get_tasks(self) -> Iterator:
        return []
