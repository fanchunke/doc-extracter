# -*- encoding: utf-8 -*-

# @File        :   app.py
# @Time        :   2021/04/14 11:26:55
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import asyncio
import logging
import logging.config

import click

from doc_extracter.async_task import AsyncTask
from doc_extracter.command import OptionRequiredIf
from doc_extracter.logger import LOGGING

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    '--backend',
    help="获取文件的方式",
    type=click.Choice(["files", "http", "redis"], case_sensitive=False)
)
@click.option(
    '--type',
    help='处理的文件类型',
    type=click.Choice(["pptx", "docx", "all"], case_sensitive=False),
)
@click.option(
    '--dirname',
    help='处理的文档目录。如果 `--backend=files`，`--dirname` 为必需参数',
    option="backend",
    value="files",
    cls=OptionRequiredIf
)
@click.option(
    "--url",
    help='获取任务的服务地址。如果 `--backend=http`，`--url` 为必需参数',
    option="backend",
    value="http",
    cls=OptionRequiredIf
)
@click.option(
    '--workers',
    help="worker数",
    type=int,
    default=10
)
def doc_extracter(type, backend, dirname, url, workers):
    logger.info(f"backend: {backend}, type: {type}, dirname: {dirname}, url: {url}, workers: {workers}")
    loop = asyncio.get_event_loop()
    try:
        asyncio.run(main(type, backend, dirname, url, workers))
    except KeyboardInterrupt as e:
        logger.info("Caught keyboard interrupt. Canceling tasks...")
    finally:
        loop.close()


async def main(type, backend, dirname, url, workers):
    async with AsyncTask(type, backend, dirname, url, workers) as t:
        await t.run()


if __name__ == '__main__':
    logging.config.dictConfig(LOGGING)
    doc_extracter()
