from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from pathlib import Path
from mahjong_utils import generate_graph
import asyncio
import threading

app = FastAPI(title="雀魂 PT 推移图")

@app.on_event("startup")
async def warmup():
    async def _warm():
        await asyncio.sleep(0)
        def _do_import():
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import matplotlib.font_manager as fm
            import numpy as np
        threading.Thread(target=_do_import, daemon=True).start()
    asyncio.create_task(_warm())

@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = Path("templates/index.html")
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return HTMLResponse(content="<h1>模板文件不存在</h1>", status_code=500)

@app.get("/api/generate")
async def generate(
    player_name: str = Query(""),
    mode: str = Query("4p"),
    left: int = Query(0),
    right: int = Query(10000),
    top: int = Query(10000)
):
    if not player_name or not player_name.strip():
        return {
            "success": False,
            "error": "请输入玩家名！"
        }
    if right - left < 10:
        return {
            "success": False,
            "error": "右端必须比左端至少大10！"
        }
    img_base64, history_table = generate_graph(player_name, mode, left, right, top)
    return {
        "success": img_base64 is not None,
        "image": img_base64,
        "history": history_table
    }

import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
