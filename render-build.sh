#!/usr/bin/env bash
# Render 构建脚本：安装中文字体

set -e

echo "=== 安装中文字体 ==="

# 更新包列表
apt-get update

# 安装中文字体
apt-get install -y --no-install-recommends \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    fonts-noto-cjk

# 清理缓存
apt-get clean
rm -rf /var/lib/apt/lists/*

echo "=== 字体安装完成 ==="

# 继续执行 pip 安装
pip install -r requirements.txt
