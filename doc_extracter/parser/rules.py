# -*- encoding: utf-8 -*-

# @File        :   rules.py
# @Time        :   2021/04/13 16:43:08
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   


IGNORE_SYMBOLS = ["\n"]


def preprocess_content(content: str) -> str:
    """ 预处理数据

    Args:
        content (str): 待处理数据
    """
    for symbol in IGNORE_SYMBOLS:
        content = content.replace(symbol, "")
    return content
