# -*- encoding: utf-8 -*-

# @File        :   utils.py
# @Time        :   2021/04/13 17:50:22
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :  

import datetime
import os
import pathlib


def get_create_time(filename: str) -> str:
    fname = pathlib.Path(filename)
    if not fname.exists():
        raise Exception(f"文件不存在")

    ctime = datetime.datetime.fromtimestamp(fname.stat().st_ctime)
    ctime = ctime.strftime("%Y-%m-%d")
    return ctime


def get_file_extension(filename: str) -> str:
    _, extension = os.path.splitext(filename)
    return extension.split(".")[-1]
