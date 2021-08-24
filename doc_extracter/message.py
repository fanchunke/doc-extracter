# -*- encoding: utf-8 -*-

# @File        :   message.py
# @Time        :   2021/08/23 09:58:11
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional


class JobStatus(int, Enum):
    #: no more job
    no_more_jobs = -2
    #: unsupported file
    unsupported = -1
    #: job not in progress
    not_progress = 0
    #: job is complete, result is available
    complete = 1
    # job failed
    failed = 2


class Message(BaseModel):
    id: str = Field(..., title="消息ID")
    queue: str = Field(..., title="队列名")
    file: str = Field(..., title="文件名")
    path: str = Field(..., title="文件路径/URL")
    ext: str = Field(..., title="文件扩展类型")
    callback: Optional[str] = Field(None, title="处理结果回调地址")
    status: JobStatus = Field(JobStatus.not_progress, title="文件处理状态")


NoMoreMessage = Message(id="", queue="", file="", path="", ext="", state=JobStatus.no_more_jobs)


class Result(BaseModel):
    id: str = Field(..., title="消息ID")
    queue: str = Field(..., title="队列名")
    status: JobStatus = Field(JobStatus.not_progress, title="文件处理状态")
    section: List[dict] = Field([], title="文件解析内容")


class ResultMessage(Result):
    pass


class TaskMessage(BaseModel):
    id: str = Field(..., title="任务ID")
    task: str = Field(..., title="任务名")
    args: list = Field(..., title="任务位置参数")
    kwargs: dict = Field(..., title="任务关键字参数")
    retries: int = Field(..., title="重试次数")
    eta: str = Field(..., title="eta")
    expires: float = Field(..., title="")
