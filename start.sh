#!/bin/bash
# ============================================
# 多渠道客户反馈智能处理系统 - 一键启动脚本
# ============================================

set -e

echo "============================================"
echo "  多渠道客户反馈智能处理系统 v1.0"
echo "  5-Agent Pipeline: 采集→分析→路由→回复→复盘"
echo "============================================"
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# 1. 安装 Python 依赖
echo "[1/3] 安装 Python 依赖..."
pip install -r requirements.txt -q 2>/dev/null || pip install -r requirements.txt

# 2. 启动后端服务
echo "[2/3] 启动后端服务 (FastAPI + SQLite)..."
echo "  → API: http://localhost:8000"
echo "  → 文档: http://localhost:8000/docs"
echo ""

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

sleep 3

# 3. 启动前端服务（如果有 Node.js）
if command -v node &>/dev/null; then
    echo "[3/3] 启动前端服务 (Vue3 + Vite)..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "  → 安装前端依赖..."
        npm install
    fi
    npm run dev &
    FRONTEND_PID=$
    echo "  → 前端: http://localhost:5173"
else
    echo "[3/3] ⚠️  未检测到 Node.js，跳过前端启动"
    echo "  → 请手动: cd frontend && npm install && npm run dev"
fi

echo ""
echo "============================================"
echo "  系统已启动！"
echo "  后端 API: http://localhost:8000/docs"
echo "  前端界面: http://localhost:5173"
echo "============================================"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待并清理
trap "kill $BACKEND_PID 2>/dev/null; kill $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
