#!/bin/bash

mkdir  -p /var/log/fast-msg
ENV_DIR="/www/fast-msg"
REQUIREMENTS_FILE="requirements.txt"
MAIN_SCRIPT="main.py"

# 检查虚拟环境目录是否存在
if [ -d "$ENV_DIR" ]; then
    echo "Virtual environment directory already exists: $ENV_DIR"
    exit 1
fi

# 创建虚拟环境
python3 -m venv "$ENV_DIR"

# 安装依赖包
"$ENV_DIR/bin/python3" -m pip install -r "$REQUIREMENTS_FILE"

# 运行主脚本
"$ENV_DIR/bin/python3" "$MAIN_SCRIPT"


