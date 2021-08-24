# -*- encoding: utf-8 -*-

# @File        :   file.py
# @Time        :   2021/08/22 20:52:06
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import glob
import hashlib
import itertools
import logging
import os
from typing import Iterator, List, Optional

from ..message import Message, NoMoreMessage
from ..utils import get_create_time
from . import Broker

logger = logging.getLogger("doc-extracter")


class FileBroker(Broker):

    def __init__(self, dirname: str, supported_extensions: List[str]) -> None:
        self.dirname = dirname
        self.supported_extensions = supported_extensions

    def publish(self, message: Message):
        return super().publish(message)

    def consume(self) -> Iterator[Optional[Message]]:
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
                "queue": f"{file.split('.')[-1]}",
                "id": hashlib.md5(file.encode("utf-8")).hexdigest(),
                "file": os.path.basename(file),
                "path": file,
                "ext": f".{file.split('.')[-1]}",
            }
            yield Message(**data)
        logger.info("No more message")
        yield NoMoreMessage
