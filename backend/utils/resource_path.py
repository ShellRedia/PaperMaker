"""资源路径解析 — PyInstaller onefile 兼容"""

import os
import sys
from pathlib import Path


def resource_path(relative_path: str) -> str:
    """
    获取资源文件的绝对路径。
    兼容 PyInstaller onefile (sys._MEIPASS) 和开发模式。
    """
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller onefile: 所有文件解压到临时目录
        base_path = Path(sys._MEIPASS)
    else:
        # 开发模式: 相对于项目根目录
        base_path = Path(__file__).parent.parent.parent

    return str(base_path / relative_path)
