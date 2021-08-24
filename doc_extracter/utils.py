# -*- encoding: utf-8 -*-

# @File        :   utils.py
# @Time        :   2021/04/13 17:50:22
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :  

import asyncio
import datetime
import os
import pathlib
import time
from typing import AsyncGenerator

import six


def get_create_time(filename: str) -> str:
    fname = pathlib.Path(filename)
    if not fname.exists():
        raise Exception(f"文件不存在")

    ctime = datetime.datetime.fromtimestamp(fname.stat().st_ctime)
    ctime = ctime.strftime("%Y-%m-%d %H:%M:%S")
    return ctime


def get_file_extension(filename: str) -> str:
    _, extension = os.path.splitext(filename)
    return extension.split(".")[-1]


def poll(step: float = 0.5) -> AsyncGenerator[float, None]:
    loop = asyncio.get_event_loop()
    start = loop.time()
    while True:
        before = loop.time()
        yield before - start
        after = loop.time()
        wait = max([0, step - after + before])
        time.sleep(wait)


def ensure_string(string):
    if isinstance(string, six.binary_type):
        return string.decode('utf-8')
    return string
