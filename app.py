# -*- encoding: utf-8 -*-

# @File        :   app.py
# @Time        :   2021/04/14 11:26:55
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import logging
import logging.config

from typing import List

import click

from doc_extracter.backend import HTTPBackend
from doc_extracter.broker import Broker, FileBroker, HTTPBroker, RedisBroker, AMQPBroker
from doc_extracter.client import Client
from doc_extracter.command import OptionRequiredIf
from doc_extracter.config import BackendType, BrokerType, MessageType, Setttings
from doc_extracter.logger import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger("doc-extracter")


@click.command()
@click.option(
    '--conf',
    help="配置文件",
)
@click.option(
    '--message-type',
    help='处理的文件类型',
    envvar="MESSAGE_TYPE",
    # type=click.Choice(MessageType.types(), case_sensitive=False),
    type=click.Path(),
    multiple=True,
    required=False,
)
@click.option(
    '--broker',
    help="获取文件的方式",
    envvar="BROKER_TYPE",
    type=click.Choice(BrokerType.types(), case_sensitive=False)
)
@click.option(
    '--broker-dirname',
    help='处理的文档目录。如果 `--broker=file`，`--broker-dirname` 为必需参数',
    envvar="BROKER_DIRNAME",
    option="broker",
    value="file",
    cls=OptionRequiredIf
)
@click.option(
    "--broker-url",
    help='获取任务的服务地址。如果 `--broker=http` 或 `--broker=redis`，`--broker-url` 为必需参数',
    envvar="BROKER_URL",
    option="broker",
    value="http,redis,amqp",
    cls=OptionRequiredIf
)
@click.option(
    '--backend',
    help="存储任务结果的方式",
    envvar="BACKEND_TYPE",
    type=click.Choice(BrokerType.types(), case_sensitive=False)
)
@click.option(
    "--backend-url",
    help='存储任务结果的服务地址。',
    envvar="BACKEND_URL"
)
@click.option(
    "--exchange",
    help='AMQP Exchange 名称',
    envvar="EXCHANGE",
)
@click.option(
    "--exchange-type",
    help='AMQP Exchange 类型',
    envvar="EXCHANGE_TYPE",
    type=click.Choice(['direct', 'fanouts', 'headers', 'topic'], case_sensitive=False),
    default="direct"
)
@click.option(
    "--routing-key",
    help='AMQP Routing key',
    envvar="ROUTING_KEY",
    multiple=True,
)
@click.option(
    "--queue",
    help='AMQP Queue 名称。如果 `--broker=amqp`，`--queue` 为必需参数',
    envvar="QUEUE",
    option="broker",
    value="amqp",
    cls=OptionRequiredIf
)

def main(
    conf: str,
    message_type: List[str],
    broker: str,
    broker_dirname: str,
    broker_url: str,
    backend: str,
    backend_url: str,
    exchange: str,
    exchange_type: str,
    routing_key: List[str],
    queue: str
):
    if conf:
        settings = Setttings(_env_file=conf)
    else:
        settings = Setttings(
            MESSAGE_TYPE=message_type,
            BROKER_TYPE=broker,
            BROKER_DIRNAME=broker_dirname,
            BROKER_URL=broker_url,
            BACKEND_TYPE=backend,
            BACKEND_URL=backend_url,
            EXCHANGE=exchange,
            EXCHANGE_TYPE=exchange_type,
            ROUTING_KEY=routing_key,
            QUEUE=queue,
        )
    logger.info(f"settings: {settings.dict()}")
    run(settings)


def run(settings: Setttings):
    message_type = settings.MESSAGE_TYPE
    broker = settings.BROKER_TYPE
    dirname = settings.BROKER_DIRNAME
    broker_url = settings.BROKER_URL
    backend = settings.BACKEND_TYPE
    backend_url = settings.BACKEND_URL

    if not message_type:
        message_type = MessageType.types()
    if broker == BrokerType.redis:
        broker: Broker = RedisBroker(broker_url, message_type)
    elif broker == BrokerType.http:
        broker: Broker = HTTPBroker(broker_url, message_type)
    elif broker == BrokerType.file:
        broker: Broker = FileBroker(dirname, message_type)
    elif broker == BrokerType.amqp:
        broker: Broker = AMQPBroker(
            broker_url,
            exchange=settings.EXCHANGE,
            exchange_type=settings.EXCHANGE_TYPE,
            routing_key=settings.ROUTING_KEY,
            queue=settings.QUEUE
        )
    else:
        raise Exception(f"Unsupported broker type: {broker}")

    if backend == BackendType.http:
        backend = HTTPBackend(backend_url)
    else:
        raise Exception(f"Unsupported backend type: {backend}")

    client = Client(broker, backend)
    try:
        client.start_worker()
    except KeyboardInterrupt:
        client.stop_worker()


def run_from_conf(ctx, param, value):
    print(param, value)


if __name__ == '__main__':
    main()
