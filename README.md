# 雀魂 PT 推移图查询

一个用于查询和可视化雀魂段位战 PT 推移的工具，支持 Web 界面和控制台调用两种方式。

## 环境要求

### Python 版本
- **最低要求**：Python 3.8+
- **推荐版本**：Python 3.10+（本项目测试使用 3.10.20）
- **兼容性**：支持 Python 3.8、3.9、3.10、3.11、3.12

### 系统环境
- **操作系统**：Windows、macOS、Linux
- **网络连接**：需要能访问雀魂牌谱屋 API（https://amae-koromo.com/）
- **内存**：建议 512MB 以上（处理大量对局数据时需要更多内存）

### 依赖版本
项目使用以下依赖的稳定版本：
- fastapi >= 0.92.0
- uvicorn >= 0.20.0
- jinja2 >= 3.1.0
- requests >= 2.28.0
- matplotlib >= 3.6.0
- numpy >= 1.23.0

## 环境搭建

### 1. 创建虚拟环境（推荐）

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 验证安装
```bash
python --version
pip list
```

## 功能特性

- 🌐 **Web 界面**：美观的渐变 UI，支持四麻/三麻查询
- 📊 **PT 推移图**：可视化 PT 变化趋势，带段位颜色填充
- 📋 **段位战历史**：详细的段位战历史表格，包含排名分布和场次信息
- 🎯 **参数配置**：支持自定义对局范围和 PT 上限
- 💻 **控制台调用**：支持命令行方式运行

## 项目结构

```
MJSOUL_plot/
├── main.py              # FastAPI Web 应用
├── mahjong_utils.py     # 数据处理模块（支持控制台调用）
├── requirements.txt     # 依赖包列表
└── templates/
    └── index.html       # 前端页面
```

## 安装依赖

```bash
pip install -r requirements.txt
```

依赖包：
- fastapi
- uvicorn
- jinja2
- requests
- matplotlib
- numpy

## 使用方式

### 1. Web 界面（推荐）

```bash
cd MJSOUL_plot
python main.py
```

然后在浏览器访问：http://127.0.0.1:8000

#### Web 界面功能：
- 输入玩家名查询
- 点击"四麻"或"三麻"按钮查询
- 点击"显示绘图设置"展开高级选项：
  - 左端（开始对局）
  - 右端（结束对局）
  - PT上限

### 2. 控制台调用

```bash
cd MJSOUL_plot
python mahjong_utils.py [玩家名] [3p/4p] [左端] [右端] [PT上限]
```

#### 参数说明：
- `玩家名`：雀魂玩家名（默认：お高）
- `3p/4p`：三麻/四麻（默认：4p）
- `左端`：开始对局数（默认：0）
- `右端`：结束对局数（默认：10000）
- `PT上限`：图表纵轴上限（默认：10000，自动计算历史最高）

#### 示例：
```bash
# 使用默认参数查询お高的四麻
python mahjong_utils.py

# 查询指定玩家的三麻
python mahjong_utils.py 玩家名 3p

# 完整参数
python mahjong_utils.py 玩家名 4p 0 2000 20000
```

#### 输出：
- 控制台显示段位战历史表格
- 保存 `mahjong_pt_graph.png` 图像文件

## 数据来源

数据来自 [雀魂牌谱屋](https://amae-koromo.com/) 使用的 API。

## 段位颜色说明

- 杰位：绿色渐变
- 豪位：黄色/橙色渐变
- 圣位：红色/紫色渐变
- 魂天：蓝色

## 部署指南

### 推荐：Render 免费部署（最简单）

Render 是一个优秀的免费托管平台，非常适合部署这个项目。

#### 前置准备：
1. 有一个 GitHub 账号
2. 将项目代码推送到 GitHub 仓库

#### 详细步骤：

**1. 准备项目文件**
确保你的项目有以下文件（已为你创建好）：
- `main.py` - 主应用
- `mahjong_utils.py` - 工具模块
- `requirements.txt` - 依赖列表
- `templates/index.html` - 前端页面
- `render.yaml` - Render 配置
- `Procfile` - 启动脚本

**2. 推送到 GitHub**
```bash
# 初始化 Git（如果还没有）
git init
git add .
git commit -m "Initial commit"

# 创建 GitHub 仓库后，推送到 GitHub
git remote add origin https://github.com/你的用户名/你的仓库名.git
git branch -M main
git push -u origin main
```

**3. 在 Render 上部署**
1. 访问 [render.com](https://render.com) 并注册/登录
2. 点击右上角 **"New +"** → 选择 **"Web Service"**
3. 连接你的 GitHub 账户，选择该项目仓库
4. 配置部署信息：
   - **Name**: `mjsoul-pt-plot`（或你喜欢的名字）
   - **Region**: 选择离你最近的区域
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `bash render-build.sh`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: 选择 **Free**
5. 点击 **"Create Web Service"**

**4. 等待部署完成**
- Render 会自动构建和部署
- 部署成功后，你会获得一个类似 `https://mjsoul-pt-plot.onrender.com` 的地址
- 首次访问可能需要等待几秒钟（免费版会休眠）

**5. 完成！**
访问分配的域名即可使用！

#### Render 免费版注意事项：
- 每月 750 小时运行时间（足够个人使用）
- 闲置 15 分钟后会休眠，首次请求需要约 30 秒启动
- 带宽足够日常使用

### 其他部署方案

#### Railway
类似 Render，也很简单，有 $5/月免费额度。

#### Fly.io
全球部署，$5/月起。

#### 本地服务器
如果你有自己的服务器，可以使用 Nginx + Gunicorn 部署。

## 常见问题

**Q: 为什么不用 GitHub Pages？**
A: GitHub Pages 只能托管静态文件，不能运行 Python 后端。

**Q: 有办法让 Render 不休眠吗？**
A: 免费版无法避免，但可以用 UptimeRobot 等服务定期 ping 来保持活跃。

**Q: 数据安全吗？**
A: 数据来自公开的雀魂牌谱屋 API，不存储任何敏感信息。

## 许可证

MIT License
