# -*- encoding: utf-8 -*-

# @File        :   extensions.py
# @Time        :   2021/04/13 17:24:25
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import redis
from elasticsearch import Elasticsearch

from .config import Setttings


def init_redis(settings: Setttings) -> redis.Redis:
    rd = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        encoding="utf-8"
    )
    return rd


def init_es(settings: Setttings) -> Elasticsearch:
    es = Elasticsearch(host=settings.ES_HOST, port=settings.ES_PORT)
    create_index(es)
    return es


def create_index(client: Elasticsearch):
    """Creates an index in Elasticsearch if one isn't already there."""
    index = "dahua-docs"
    exists = client.indices.exists(index)
    if exists:
        return
    client.indices.create(
        index=index,
        body={
            'settings': {
                'number_of_shards': 1,
                'number_of_replicas': 1,
            },
            'mappings': {
                'properties': {
                    'owner': {'type': 'keyword'},
                    'file': {'type': 'text', 'analyzer': 'jieba_index'},
                    'file_type': {'type': 'keyword', 'index': False},
                    'date': {'type': 'date', "format": "yyyy-MM-dd HH:mm:ss",
                            'index': False},
                    'section': {
                        'type': 'nested',
                        'properties': {
                            'page': {'type': 'text', 'index': False},
                            'context': {'type': 'text', 'analyzer': 'jieba_index'},
                        }
                    }
                },
            },
        },
    )
