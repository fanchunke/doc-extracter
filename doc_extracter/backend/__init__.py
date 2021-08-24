# -*- encoding: utf-8 -*-

# @File        :   __init__.py
# @Time        :   2021/08/23 09:50:48
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import abc

from doc_extracter.message import ResultMessage


class Backend(abc.ABC):
    """ Backend interface """

    @abc.abstractmethod
    def set_result(self, task_id: str, result: ResultMessage):
        pass

    @abc.abstractmethod
    def get_result(self, task_id: str) -> ResultMessage:
        pass


from .http import HTTPBackend
