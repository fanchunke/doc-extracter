# -*- encoding: utf-8 -*-

# @File        :   config.py
# @Time        :   2021/04/17 16:38:21
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

from pydantic import BaseSettings


class Setttings(BaseSettings):

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0

    ES_HOST: str
    ES_PORT: int = 9200

    class Config:
        env_prefix = ""
        env_file: str = "configs/.env"
        env_file_encoding: str = 'utf-8'

settings = Setttings()
