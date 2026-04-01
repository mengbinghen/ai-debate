#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ---- Check Python ----
if ! command -v python3 &>/dev/null; then
    error "未找到 python3，请先安装 Python 3.10+"
fi

PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    error "Python 版本过低 ($PY_VERSION)，需要 3.10+"
fi
info "Python $PY_VERSION ✓"

# ---- Check dependencies ----
if ! python3 -c "import streamlit" 2>/dev/null; then
    warn "未检测到依赖包，正在安装..."
    pip3 install -r requirements.txt || error "依赖安装失败，请手动运行: pip install -r requirements.txt"
    info "依赖安装完成 ✓"
fi

# ---- Load .env ----
if [ -f .env ]; then
    set -a
    source .env
    set +a
    info "已加载 .env 配置 ✓"
fi

# ---- Check API key ----
MISSING=()
[ -z "${DEEPSEEK_API_KEY:-}" ] && MISSING+=("DEEPSEEK_API_KEY")
[ -z "${DASHSCOPE_API_KEY:-}" ] && MISSING+=("DASHSCOPE_API_KEY")

if [ ${#MISSING[@]} -ne 0 ]; then
    warn "以下 API Key 未设置: ${MISSING[*]}"
    warn "可在 .env 文件中配置，或通过环境变量传入"
    warn "仅配置其中一个也可运行（需在界面上选择对应的模型供应商）"
fi

# ---- Start ----
PORT="${STREAMLIT_PORT:-8501}"
info "启动 AI 辩论赛系统 (端口: $PORT)..."
info "访问 http://localhost:$PORT"
info "按 Ctrl+C 停止"
echo ""

exec python3 -m streamlit run frontend/app.py \
    --server.port "$PORT" \
    --server.headless true
