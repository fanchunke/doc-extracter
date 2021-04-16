# -*- encoding: utf-8 -*-

# @File        :   __init__.py
# @Time        :   2021/04/16 11:09:22
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

from abc import ABC, abstractmethod
import asyncio


class Backend(ABC):

    @abstractmethod
    def produce(self, queue: asyncio.Queue):
        ...
