# -*- encoding: utf-8 -*-

# @File        :   amqp.py
# @Time        :   2021/08/23 19:04:07
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import json
import logging
from typing import Iterator, Optional, List

import pika
from pika.adapters.blocking_connection import BlockingChannel

from ..message import Message
from ..utils import ensure_string
from . import Broker

logger = logging.getLogger("doc-extracter")


class AMQPBroker(Broker):

    def __init__(self, amqp_url: str, exchange: str, exchange_type: str, queue: str, routing_key: List[str], prefetch_count: int = 1):
        self._amqp_url = amqp_url
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.queue = queue
        self.routing_key = routing_key
        self.prefetch_count = prefetch_count

        self.connection: pika.BlockingConnection = None
        self.channel: BlockingChannel = None

        self.connect()

    def connect(self):
        self.connection = pika.BlockingConnection(
            parameters=pika.URLParameters(self._amqp_url)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(self.queue, durable=True)
        if self.exchange:
            self.channel.exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type)
            for key in self.routing_key:
                self.channel.queue_bind(queue=self.queue, exchange=self.exchange, routing_key=key)
        self.channel.basic_qos(prefetch_count=self.prefetch_count)

    def publish(self, message: Message):
        return super().publish(message)

    def consume(self) -> Iterator[Optional[Message]]:
        if not self.channel:
            self.connect()

        for frame, _, message in self.channel.consume(self.queue):
            logger.info(f"message: {ensure_string(message)}")
            if not message:
                yield None
            else:
                try:
                    message = json.loads(message)
                    yield Message(**message)
                    self.channel.basic_ack(frame.delivery_tag)
                except Exception as e:
                    logger.error(f"Invalid message: {message}, error={str(e)}")
                    yield None
        self.connection.close()
        self.connection = None
        self.channel = None
