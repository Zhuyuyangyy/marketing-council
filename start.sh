#!/bin/bash
# ============================================
# MarketingCouncil - 启动脚本 (Linux/macOS)
# ============================================
# 用法:
#   bash start.sh              # 启动后端 (端口8009)
#   bash start.sh frontend      # 打开前端 (手动)
#   bash start.sh demo         # 演示模式 (无需API Key)
#   bash start.sh mock         # Mock LLM 演示
# ============================================

set -e

cd "$(dirname "$0")"
PROJECT_DIR="$(pwd)"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

print_step() { echo -e "${BLUE}[MarketingCouncil]${NC} $1"; }
print_ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error(){ echo -e "${RED}[ERROR]${NC} $1"; }

# Check Python
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON=python3
    elif command -v python &> /dev/null; then
        PYTHON=python
    else
        print_error "Python not found. Please install Python 3.8+"
        exit 1
    fi
    echo "Using: $PYTHON ($($PYTHON --version 2>&1))"
}

# Install dependencies
install_deps() {
    print_step "安装后端依赖..."
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        $PYTHON -m pip install -q -r requirements.txt 2>/dev/null || \
        $PYTHON -m pip install --upgrade pip -q && $PYTHON -m pip install -q -r requirements.txt
        print_ok "依赖安装完成"
    else
        print_warn "requirements.txt not found, skipping"
    fi
}

# Check .env config
check_env() {
    print_step "检查环境配置..."
    if [ -f "$PROJECT_DIR/.env" ]; then
        source "$PROJECT_DIR/.env" 2>/dev/null
        if [ -n "$SPARK_API_KEY" ] && [ -n "$SPARK_API_SECRET" ]; then
            print_ok "讯飞Spark API Key 已配置"
        else
            print_warn "SPARK_API_KEY 未配置，将使用 Mock LLM 演示模式"
        fi
    else
        print_warn ".env 文件不存在，将使用 Mock LLM 演示模式"
        print_warn "如需真实API调用，请创建 .env 并配置 SPARK_APP_ID, SPARK_API_KEY, SPARK_API_SECRET"
    fi
}

# Start backend server
start_backend() {
    print_step "启动后端服务 (端口 8009)..."
    check_python
    install_deps
    check_env

    cd "$PROJECT_DIR/backend"
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  MarketingCouncil 后端${NC}"
    echo -e "${BLUE}  API文档: http://localhost:8009/docs${NC}"
    echo -e "${BLUE}  前端: 打开 frontend/index.html${NC}"
    echo -e "${BLUE}========================================${NC}"

    $PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8009 --reload
}

# Start frontend only
start_frontend() {
    print_step "前端文件位置: $PROJECT_DIR/frontend/"
    echo "请选择打开方式:"
    echo "  1. frontend/index.html       - 完整版前端 (需要后端)"
    echo "  2. frontend/demo_sse.html    - SSE实时演示版 (部分功能可Mock运行)"
    echo ""
    echo "在浏览器中直接打开上述HTML文件即可"
}

# Run mock demo (no backend needed)
run_mock_demo() {
    print_step "Mock演示模式 (不需要后端服务)..."
    check_python

    cd "$PROJECT_DIR"
    export SPARK_API_KEY=""
    export SPARK_API_SECRET=""

    $PYTHON - << 'PYEOF'
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

# Test the mock LLM directly
print("\n=== Testing Mock Spark LLM ===")
from app.core.llm_factory import get_crewai_llm

llm = get_crewai_llm(temperature=0.7)
print(f"LLM Type: {type(llm).__name__}")
print(f"Is Mock: {hasattr(llm, '_MockLLMImpl') or 'mock' in str(type(llm).__name__).lower()}")

# Test call
result = llm("分析一下奶茶店的市场机会")
print(f"\nMock Response:\n{result[:200]}...")

print("\n=== Mock Demo Complete ===")
print("前端演示: 打开 frontend/demo_sse.html 点击 'Mock演示' 按钮")
PYEOF
}

# Run complete demo with backend
run_backend_demo() {
    print_step "启动后端演示模式..."
    check_python
    install_deps
    check_env

    cd "$PROJECT_DIR/backend"
    echo ""
    echo -e "${GREEN}=== MarketingCouncil 演示 ===${NC}"
    echo ""
    echo "1. 后端已启动在 http://localhost:8009"
    echo "2. 打开 http://localhost:8009/docs 查看API文档"
    echo "3. 打开 frontend/index.html 使用前端界面"
    echo "4. 或直接打开 frontend/demo_sse.html 使用SSE演示版"
    echo ""
    echo "注意: 如果没有配置 API Key，系统将使用 Mock LLM"
    echo "     Mock模式下会返回占位分析结果，不会调用真实API"
    echo ""

    $PYTHON -m uvicorn app.main:app --host 0.0.0.0 --port 8009 --reload
}

# Main
COMMAND=${1:-""}

case "$COMMAND" in
    backend|server|"")
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    mock)
        run_mock_demo
        ;;
    demo)
        run_backend_demo
        ;;
    help|--help|-h)
        echo "MarketingCouncil 启动脚本"
        echo ""
        echo "用法: bash start.sh [command]"
        echo ""
        echo "Commands:"
        echo "  (none)   启动后端服务 (默认)"
        echo "  backend  同上"
        echo "  frontend 显示前端文件位置"
        echo "  mock     直接运行Mock演示 (不需要后端)"
        echo "  demo     启动后端演示模式"
        echo "  help     显示此帮助"
        echo ""
        echo "文件:"
        echo "  frontend/index.html    - 完整版前端"
        echo "  frontend/demo_sse.html - SSE实时演示版"
        ;;
    *)
        print_error "未知命令: $COMMAND"
        echo "运行 'bash start.sh help' 查看帮助"
        exit 1
        ;;
esac
