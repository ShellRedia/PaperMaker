# PaperMaker — 深度学习论文写作助手

## 项目简介
PaperMaker 是一款基于深度学习的论文写作辅助工具，提供数据标注、图表展示、
文本润色、数值统计等功能。前端使用 Vue 3 + Anime.js 构建精美动画交互，
后端使用 Python FastAPI 驱动深度学习模型推理。

## 技术栈
- **前端**: Vue 3 + Vite + Pinia + Tailwind CSS 4 + Anime.js + ECharts + Fabric.js + Monaco Editor
- **后端**: Python FastAPI + SQLAlchemy + SQLite + ONNX Runtime + spaCy
- **桌面**: pywebview (Edge WebView2) + PyInstaller

## 快速开始

### 开发环境
```bash
# 后端
cd backend
pip install -r ../requirements.txt
uvicorn backend.main:app --reload --port 17890

# 前端
cd frontend
npm install
npm run dev
```

### 打包构建
```bash
python build/build_frontend.py
# 输出: dist/PaperMaker.exe
```
