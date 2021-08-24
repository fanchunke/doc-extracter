# 文档处理

## 快速开始

```bash
cd doc_extracter
```

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 修改配置

```
cd ../configs
vim .env
```

3. 查看帮助

```bash
python app.py --help

Usage: app.py [OPTIONS]

Options:
  --conf TEXT                     配置文件
  --message-type PATH             处理的文件类型
  --broker [redis|http|file|amqp]
                                  获取文件的方式
  --broker-dirname TEXT           处理的文档目录。如果 `--broker=file`，`--broker-
                                  dirname` 为必需参数

  --broker-url TEXT               获取任务的服务地址。如果 `--broker=http` 或
                                  `--broker=redis`，`--broker-url` 为必需参数

  --backend [redis|http|file|amqp]
                                  存储任务结果的方式
  --backend-url TEXT              存储任务结果的服务地址。
  --exchange TEXT                 AMQP Exchange 名称
  --exchange-type [direct|fanouts|headers|topic]
                                  AMQP Exchange 类型
  --routing-key TEXT              AMQP Routing key
  --queue TEXT                    AMQP Queue 名称。如果 `--broker=amqp`，`--queue`
                                  为必需参数

  --help                          Show this message and exit.
```

4. 运行程序

```bash
python app.py --configs/.env
```

## 使用方法

目前，项目使用 `broker` 和 `backend`，支持多种方式的数据接入。

1. Broker

支持：

- redis
- http
- file
- amqp

如果需要增加新的 `broker`，实现 `broker.Broker` 接口即可。

2. Backend

支持:

- http：将结果通过 HTTP 接口的方式写入

如果需要增加新的 `backend`，实现 `backend.Backend` 接口即可。

3. 参数

参数支持：命令行直接传参、环境变量传参。

命令行参数说明见 `快速开始` 。

环境变量传参支持以下参数:

```conf
BROKER_TYPE = "amqp"
BROKER_URL = "amqp://localhost:5672"
BROKER_DIRNAME = ""
MESSAGE_TYPE = ""
BACKEND_TYPE = "http"
BACKEND_URL = "http://127.0.0.1/"

# AMQP Broker Settings
EXCHANGE = "doc-extracter"
EXCHANGE_TYPE = "direct"
ROUTING_KEY = ["pptx", "docx", "pdf", "msg"]
QUEUE = "msg_queue"
```

## 部署

目前支持两种启动方式。

1. 直接运行命令行

命令行支持直接传入配置文件

```bash
python app.py --conf=configs/.env
```

也支持命令行传参

```bash
python app.py --broker=redis --broker-url=redis://localhost:6379/0 --backend=http --backend-url=http://127.0.0.1
```

2. Docker 部署

可以直接通过 `docker-compose` 部署。命令行参数可通过环境变量注入。