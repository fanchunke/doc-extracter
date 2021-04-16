# -*- encoding: utf-8 -*-

# @File        :   app.py
# @Time        :   2021/04/14 11:26:55
# @Author      :   fanchunke
# @Email       :   fanchunke@laiye.com
# @Description :   

import logging
import logging.config

import click

from doc_extracter.command import OptionRequiredIf
from doc_extracter.logger import LOGGING
from doc_extracter.task import Task

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    '--backend',
    help="获取文件的方式",
    type=click.Choice(["files", "http"])
)
@click.option(
    '--type',
    default="ppt",
    help='处理的文件类型。如果 `--backend=files`，`--type` 为必需参数',
    type=click.Choice(["pptx", "docx", "all"]),
    option="backend",
    value="files",
    cls=OptionRequiredIf
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
    help="线程数",
    type=int,
    default=10
)
def doc_extracter(type, backend, dirname, url, workers):
    logger.info(f"backend: {backend}, type: {type}, dirname: {dirname}, url: {url}, workers: {workers}")
    task = Task(type, backend, dirname, url, workers)
    task.run()


if __name__ == '__main__':
    logging.config.dictConfig(LOGGING)
    doc_extracter()
