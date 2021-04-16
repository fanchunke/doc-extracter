# 文档处理

## 快速开始

```bash
cd doc_extracter
```

1. 查看帮助

```bash
python app.py --help

Usage: app.py [OPTIONS]

Options:
  --backend [files|http]  获取文件的方式
  --type [pptx|docx|all]  处理的文件类型。如果 `--backend=files`，`--type` 为必需参数
  --dirname TEXT          处理的文档目录。如果 `--backend=files`，`--dirname` 为必需参数
  --url TEXT              获取任务的服务地址。如果 `--backend=http`，`--url` 为必需参数
  --workers INTEGER       线程数
  --help                  Show this message and exit.
```

2. 运行程序

```bash
python app.py --backend=files --dirname=/Users/fanchunke/Desktop/tmp/test-pdf --type=all
```

