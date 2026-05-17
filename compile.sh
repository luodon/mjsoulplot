#!/usr/bin/env bash
set -e

echo "=== 安装依赖 ==="
pip install -r requirements.txt
pip install pyinstaller

echo "=== 编译可执行文件 ==="
pyinstaller --onedir \
  --add-data "templates:templates" \
  --add-data "NotoSansSC-Regular.otf:." \
  --add-data "1s.svg:." \
  --hidden-import uvicorn.logging \
  --hidden-import uvicorn.loops.auto \
  --hidden-import uvicorn.protocols.http.auto \
  --hidden-import uvicorn.protocols.websockets.auto \
  --hidden-import uvicorn.middleware.debug \
  --hidden-import uvicorn.middleware.proxy_headers \
  --hidden-import jinja2 \
  --name main \
  main.py

echo "=== 编译完成 ==="
du -sh dist/main/
