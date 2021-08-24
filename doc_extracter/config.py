# -*- encoding: utf-8 -*-

# @File        :   config.py
# @Time        :   2021/04/17 16:38:21
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseSettings, validator


class BrokerType(str, Enum):
    redis = "redis"
    http = "http"
    file = "file"
    amqp = "amqp"

    @classmethod
    def from_url(cls) -> List[str]:
        return [cls.redis.value, cls.http.value, cls.amqp.value]

    @classmethod
    def from_dir(cls) -> List[str]:
        return [cls.file.value]

    @classmethod
    def types(cls) -> List[str]:
        return [t.value for t in cls]


class MessageType(str, Enum):
    pptx = "pptx"
    docx = "docx"
    pdf = "pdf"
    msg = "msg"

    @classmethod
    def types(cls) -> List[str]:
        return [t.value for t in cls]


class BackendType(str, Enum):
    http = "http"

    @classmethod
    def types(cls) -> List[str]:
        return [t.value for t in cls]


class Setttings(BaseSettings):

    BROKER_TYPE: BrokerType
    BROKER_URL: Optional[str]
    BROKER_DIRNAME: Optional[str]

    MESSAGE_TYPE: Union[List[MessageType], str]

    BACKEND_TYPE: BrokerType
    BACKEND_URL: str

    EXCHANGE: Optional[str] = ""
    EXCHANGE_TYPE: Optional[str]
    ROUTING_KEY: Union[List[str], str]
    QUEUE: Optional[str]

    @validator("MESSAGE_TYPE")
    def check_message_type(cls, v, values: dict, **kwargs):
        if isinstance(v, str):
            v = v.split()
        return v

    @validator("ROUTING_KEY")
    def check_routing_key(cls, v, values: dict, **kwargs):
        if isinstance(v, str):
            v = v.split()
        return v

    @validator("BROKER_URL")
    def check_broker_url(cls, v, values: dict, **kwargs):
        broker_type = values.get("BROKER_TYPE")
        if broker_type in BrokerType.from_url() and not v:
            raise ValueError(f"{broker_type} need non empty BROKER_URL")
        return v

    @validator("BROKER_DIRNAME")
    def check_broker_dirname(cls, v, values: dict, **kwargs):
        broker_type = values.get("BROKER_TYPE")
        if broker_type in BrokerType.from_dir() and not v:
            raise ValueError(f"{broker_type} need non empty BROKER_DIRNAME")
        return v

    class Config:
        env_prefix = ""
        env_file: str = "configs/.env"
        env_file_encoding: str = 'utf-8'
