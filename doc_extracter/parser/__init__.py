# -*- encoding: utf-8 -*-

# @File        :   __init__.py
# @Time        :   2021/04/17 11:51:14
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import importlib
import os
from typing import Optional

from ..errors import UnSupportedError
from ..message import Message, Result
from .base import BaseParser

_FILENAME_SUFFIX = "_parser"


def process(
    message: Message,
    extension: Optional[str] = None,
    **kwargs
) -> Result:
    if extension:
        ext = extension
    elif message.queue:
        ext = message.queue
    else:
        _, ext = os.path.splitext(message.path)

    if not ext.startswith("."):
        ext = f".{ext}"
    ext = ext.lower()

    rel_module = ext + _FILENAME_SUFFIX
    try:
        filetype_module = importlib.import_module(
            rel_module,
            "doc_extracter.parser"
        )
    except ImportError:
        raise UnSupportedError(f"UnSupported Extension: {ext}")

    parser: BaseParser = filetype_module.Parser
    return parser.extract(message, **kwargs)
