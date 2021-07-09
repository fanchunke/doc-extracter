# -*- encoding: utf-8 -*-

# @File        :   file.py
# @Time        :   2021/04/16 11:08:58
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import asyncio
import glob
import hashlib
import itertools
import os
from typing import Any, Callable, Coroutine, Iterator, List

from doc_extracter import Message
from doc_extracter.utils import get_create_time

from . import Backend


class FileBackend(Backend):

    def __init__(self, dirname: str, supported_extensions: List[str]) -> None:
        self.dirname = dirname
        self.supported_extensions = supported_extensions

    def consume(self) -> Iterator[Message]:
        if not os.path.exists(self.dirname):
            raise Exception(f"目录不存在: {self.dirname}")

        files = iter([])
        for ext in self.supported_extensions:
            files = itertools.chain(
                files,
                glob.iglob(os.path.join(self.dirname, "**", f"*.{ext}"), recursive=True)
            )

        for file in files:
            data = {
                "id": hashlib.md5(file.encode("utf-8")).hexdigest(),
                "name": os.path.basename(file),
                "path": file,
                "ext": f".{file.split('.')[-1]}",
                "state": 0,
                "owner": file.split("-")[0],
                "date": get_create_time()

            }
            yield Message(**data)
