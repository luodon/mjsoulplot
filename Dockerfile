FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-noto-cjk \
    fonts-wqy-microhei \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "\
import matplotlib; matplotlib.use('Agg'); \
import matplotlib.pyplot as plt; \
import matplotlib.font_manager as fm; \
import numpy as np; \
print('matplotlib/numpy pre-warmed')"

COPY . .

RUN python -c "\
import matplotlib; matplotlib.use('Agg'); \
import matplotlib.font_manager as fm; \
from pathlib import Path; \
font_path = Path('NotoSansSC-Regular.otf'); \
if font_path.exists(): \
    fm.fontManager.addfont(str(font_path)); \
    print('font pre-loaded:', font_path.name)"

EXPOSE 8000

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
