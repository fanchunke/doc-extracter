FROM python:3.8-slim

ENV TZ=Asia/Shanghai

ARG WORKDIR=/home/works/program

# 安装vim和locales
RUN useradd --create-home --shell /bin/bash works \
    && mkdir -p ${WORKDIR}/logs \
    && sed -i "s@http://deb.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list \
    && apt-get -y update \
    && apt-get install --no-install-recommends -y locales build-essential \
    && rm -rf /var/lib/apt/list/* \
    && pip install -U pip \
    && sed -i 's/^# *\(zh_CN.UTF-8\)/\1/' /etc/locale.gen \
    && locale-gen \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo '$TZ' > /etc/timezone

WORKDIR ${WORKDIR}

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

COPY configs ./configs
COPY doc_extracter ./doc_extracter
COPY app.py ./app.py

CMD ["python", "app.py", "--backend=redis", "--type=all"]
