#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 批量添加文字工具 - 清新风格版
基于 PyQt6 和 PyMuPDF (fitz)

入口模块

支持两种运行方式:
  python -m pdf_batch_add_text.main
  python pdf_batch_add_text.py  (旧版启动器调用本模块)
"""

import sys
import os

# 当作为 `python -m pdf_batch_add_text.main` 运行时，
# Python 已经将项目根目录加入 sys.path，无需手动添加。
# 但保留兼容性：如果父目录不在路径中则补入（应对旧版直接运行方式）。
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


def main():
    """应用入口"""
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtGui import QFont

    from .config import APP_NAME
    from .utils.ensure import ensure_dependencies, create_app_icon
    from .logger import init_diag_log
    from .main_window import MainWindow

    # 初始化诊断日志
    init_diag_log()

    # 检查依赖
    dep_msg = ensure_dependencies()
    if dep_msg:
        app = QApplication(sys.argv)
        app.setWindowIcon(create_app_icon())
        QMessageBox.critical(None, "缺少依赖", dep_msg)
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setWindowIcon(create_app_icon())
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)

    font = QFont("", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()