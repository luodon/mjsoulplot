#!/usr/bin/env bash
# Render 构建脚本：安装依赖并配置中日文字体

set -e

echo "=== 安装依赖 ==="
pip install -r requirements.txt

echo "=== 初始化 mplfonts 中日文字体 ==="
mplfonts init

echo "=== 构建完成 ==="
