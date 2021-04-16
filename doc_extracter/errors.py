# -*- encoding: utf-8 -*-

# @File        :   errors.py
# @Time        :   2021/04/16 19:58:57
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   


class CustomError(Exception):

    def __init__(self, message: str, code: str = "0") -> None:
        self.message = message
        self.code = code


class UnSupportedError(CustomError):
    pass
