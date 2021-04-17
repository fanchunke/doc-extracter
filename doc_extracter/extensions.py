# -*- encoding: utf-8 -*-

# @File        :   extensions.py
# @Time        :   2021/04/13 17:24:25
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import aioredis
from elasticsearch import AsyncElasticsearch

from .config import settings

es = AsyncElasticsearch(hosts=[{"host": settings.ES_HOST, "port": settings.ES_PORT}])


async def create_index(client: AsyncElasticsearch):
    """Creates an index in Elasticsearch if one isn't already there."""
    index = "dahua-docs"
    exists = await client.indices.exists(index)
    if exists:
        return
    await client.indices.create(
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


async def create_pool() -> aioredis.Redis:
    pool = await aioredis.create_redis_pool(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        db=settings.REDIS_DB,
        encoding="utf-8")
    return pool
