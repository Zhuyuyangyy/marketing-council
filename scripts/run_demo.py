#!/usr/bin/env python3
"""
MarketingCouncil Demo Launcher
启动脚本 - 委托至项目根目录的 run_demo.py

用法:
    python scripts/run_demo.py --mock
    python scripts/run_demo.py --list-agents
    python scripts/run_demo.py --test-api
    python scripts/run_demo.py --topic "自定义主题"
"""

import subprocess
import sys
import os


def main():
    # 定位项目根目录的 run_demo.py
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    demo_script = os.path.join(project_root, "run_demo.py")

    if not os.path.exists(demo_script):
        print(f"[ERROR] 找不到演示脚本: {demo_script}")
        sys.exit(1)

    # Windows下强制UTF-8输出（解决emoji编码问题）
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    extra_args = ["-X", "utf8"] if sys.platform == "win32" else []

    # 传递所有参数给根目录的 run_demo.py
    cmd = [sys.executable] + extra_args + [demo_script] + sys.argv[1:]
    sys.exit(subprocess.call(cmd, env=env))


if __name__ == "__main__":
    main()
