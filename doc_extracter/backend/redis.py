# -*- encoding: utf-8 -*-

# @File        :   redis.py
# @Time        :   2021/04/16 13:40:51
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

from . import Backend

from typing import Iterator


class RedisBackend(Backend):

    def __init__(self, chunk_size) -> None:
        super().__init__()

    def get_tasks(self) -> Iterator:
        return super().get_tasks()