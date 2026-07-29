"""诊断日志 - 写入桌面，方便排查问题"""

import os
import sys
from datetime import datetime

DIAG_LOG_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "pdf_batch_diag.log")

# 诊断日志缓冲区（减少磁盘IO）
_DIAG_BUFFER = []
_DIAG_FLUSH_COUNT = 0


def diag_log(msg):
    """写入诊断日志（缓冲模式，每20条刷盘一次，减少IO开销）"""
    global _DIAG_FLUSH_COUNT
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _DIAG_BUFFER.append(f"[{timestamp}] {msg}\n")
        _DIAG_FLUSH_COUNT += 1
        if _DIAG_FLUSH_COUNT >= 20:
            diag_flush()
    except Exception:
        # 避免日志记录本身出错导致递归或程序崩溃，静默忽略
        pass


def diag_flush():
    """强制将缓冲区日志写入磁盘"""
    global _DIAG_BUFFER, _DIAG_FLUSH_COUNT
    if not _DIAG_BUFFER:
        return
    try:
        with open(DIAG_LOG_PATH, 'a', encoding='utf-8') as f:
            f.writelines(_DIAG_BUFFER)
        _DIAG_BUFFER.clear()
        _DIAG_FLUSH_COUNT = 0
    except Exception as e:
        try:
            print(f"[DIAG ERROR] {e}", file=sys.stderr)
        except Exception:
            pass


def init_diag_log():
    """启动时清空旧日志并写入初始化信息"""
    try:
        import fitz
        fitz_available = True
    except ImportError:
        fitz_available = False

    try:
        import openpyxl
        openpyxl_available = True
    except ImportError:
        openpyxl_available = False

    try:
        with open(DIAG_LOG_PATH, 'w', encoding='utf-8') as f:
            f.write(f"=== PDF 批量添加文字 诊断日志 ===\n")
            f.write(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"操作系统: {sys.platform}\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"工作目录: {os.getcwd()}\n")
            f.write(f"PyMuPDF: {'可用' if fitz_available else '不可用'}\n")
            f.write(f"openpyxl: {'可用' if openpyxl_available else '不可用'}\n")
            f.write("=" * 50 + "\n")
    except Exception as e:
        diag_log(f"Failed to write initial diagnostic log: {e}")
