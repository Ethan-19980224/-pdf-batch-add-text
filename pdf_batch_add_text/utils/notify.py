"""系统通知 - 跨平台发送桌面通知"""
import os
import sys
import subprocess

from ..logger import diag_log


def send_system_notification(title, message):
    """发送系统通知（macOS/Windows/Linux）"""
    try:
        # 安全转义消息中的特殊字符
        safe_msg = message.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'").replace('\n', ' ')
        safe_title = title.replace('"', '\\"').replace("'", "\\'")
        if sys.platform == 'darwin':
            subprocess.Popen([
                'osascript', '-e',
                f'display notification "{safe_msg}" with title "{safe_title}"'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform == 'win32':
            try:
                from ctypes import windll
                windll.user32.MessageBoxTimeoutW(0, message, title, 0x40, 0, 3000)
            except Exception as e:
                diag_log(f"发送系统通知失败 (win32): {e}")
        else:
            subprocess.Popen(['notify-send', title, message],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        diag_log(f"发送系统通知失败: {e}")
