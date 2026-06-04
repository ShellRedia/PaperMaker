"""
PaperMaker 桌面启动器

职责:
1. 检测空闲端口
2. 程序化启动 uvicorn (FastAPI)
3. Health check 等待后端就绪
4. 启动 pywebview 桌面窗口

打包命令:
    pyinstaller build/PaperMaker.spec --clean --noconfirm
"""

import sys
import time
import socket
import threading
import traceback
import urllib.request
from pathlib import Path

# ── crash 日志 ──
CRASH_LOG = Path.home() / "AppData" / "Roaming" / "PaperMaker" / "crash.log"


def setup_crash_handler():
    """全局异常捕获 — 写入 crash 日志方便排查 PyInstaller 问题"""
    def handler(exc_type, exc_value, exc_tb):
        CRASH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(CRASH_LOG, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"[PaperMaker Crash] {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"sys.executable: {sys.executable}\n")
            f.write(f"sys._MEIPASS: {getattr(sys, '_MEIPASS', 'N/A')}\n")
            f.write(f"sys.argv: {sys.argv}\n")
            traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = handler


setup_crash_handler()


def find_free_port(start: int = 17890) -> int:
    """在指定起始端口范围内查找空闲端口"""
    port = start
    while port < start + 100:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
        port += 1
    raise RuntimeError("无法找到空闲端口 (17890-17989)")


def start_uvicorn(app, host: str, port: int):
    """在后台线程启动 uvicorn"""
    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="info")


def wait_for_server(url: str, timeout: float = 15.0) -> bool:
    """轮询等待服务就绪"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(url, timeout=0.5)
            return True
        except Exception:
            time.sleep(0.15)
    return False


def main():
    print("[PaperMaker] 正在启动...", flush=True)

    # ── 1. 初始化 AppData 目录 ──
    from backend.utils.file_manager import file_manager
    file_manager.ensure_directories()

    # ── 2. 找空闲端口 ──
    port = find_free_port()
    print(f"[PaperMaker] 使用端口: {port}", flush=True)

    # ── 3. 创建 FastAPI 应用 ──
    from backend.main import create_app
    app = create_app()

    # ── 4. 启动后端服务 ──
    server_thread = threading.Thread(
        target=start_uvicorn,
        args=(app, "127.0.0.1", port),
        daemon=True,
    )
    server_thread.start()

    # ── 5. 等待服务就绪 ──
    health_url = f"http://127.0.0.1:{port}/health"
    print(f"[PaperMaker] 等待后端就绪...", flush=True)
    if not wait_for_server(health_url):
        print(f"[PaperMaker] 错误: 后端服务启动超时 (15s)", flush=True)
        sys.exit(1)

    print(f"[PaperMaker] 后端服务已就绪", flush=True)
    print(f"[PaperMaker] 启动桌面窗口...", flush=True)

    # ── 6. 启动 pywebview 桌面窗口 ──
    import webview

    # pywebview 6.x+ 不再支持 http_server 参数，直接运行
    window = webview.create_window(
        title="PaperMaker — 深度学习论文写作助手",
        url=f"http://127.0.0.1:{port}",
        width=1400,
        height=900,
        min_size=(1024, 680),
        confirm_close=True,
    )

    webview.start(debug=True)


if __name__ == "__main__":
    main()
