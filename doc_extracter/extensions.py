# -*- encoding: utf-8 -*-

# @File        :   extensions.py
# @Time        :   2021/04/13 17:24:25
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

from elasticsearch import Elasticsearch


def create_index(client: Elasticsearch):
    """Creates an index in Elasticsearch if one isn't already there."""
    client.indices.create(
        index="docs",
        body={
            # "settings": {"number_of_shards": 1},
            "mappings": {
                "properties": {
                    "owner": {"type": "keyword"},
                    "file_type": {"type": "keyword"},
                }
            },
        },
        ignore=400,
    )

es = Elasticsearch(hosts=[{"host": "172.17.201.207", "port": 9200}])
create_index(es)
print(es.count())
