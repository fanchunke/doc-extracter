# -*- encoding: utf-8 -*-

# @File        :   __init__.py
# @Time        :   2021/04/16 11:09:22
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

from abc import ABC, abstractmethod
import asyncio
from typing import Callable, Coroutine, Any


class Backend(ABC):

    @abstractmethod
    async def produce(self, queue: asyncio.Queue):
        ...

    @abstractmethod
    async def consume(self, queue: asyncio.Queue, callback: Callable[..., Coroutine[Any, Any, Any]]):
        ...
