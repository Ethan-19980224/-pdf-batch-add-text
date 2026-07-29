"""中文字体查找 - 跨平台检测中文字体文件"""
import os
import sys
import subprocess

from ..logger import diag_log

# 中文字体路径缓存
_CJK_FONT_CACHE = {}  # key: "regular"|"bold", value: 字体文件路径


def find_cjk_font(bold=False):
    """查找系统上的中文字体文件，优先微软雅黑、其次黑体。
    bold=True 时优先查找粗体变体。"""
    cache_key = "bold" if bold else "regular"
    if cache_key in _CJK_FONT_CACHE:
        return _CJK_FONT_CACHE[cache_key]

    if sys.platform == 'win32':
        fonts_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
        if bold:
            candidates = [
                (os.path.join(fonts_dir, 'msyhbd.ttc'), '微软雅黑 Bold'),
                (os.path.join(fonts_dir, 'msyh.ttc'),  '微软雅黑'),
                (os.path.join(fonts_dir, 'simhei.ttf'), '黑体'),
                (os.path.join(fonts_dir, 'msyhbd.ttf'), '微软雅黑 Bold(ttf)'),
            ]
        else:
            candidates = [
                (os.path.join(fonts_dir, 'msyh.ttc'),  '微软雅黑'),
                (os.path.join(fonts_dir, 'msyh.ttf'),  '微软雅黑(ttf)'),
                (os.path.join(fonts_dir, 'simhei.ttf'), '黑体'),
                (os.path.join(fonts_dir, 'simsun.ttc'), '宋体'),
            ]
    elif sys.platform == 'darwin':
        candidates = [
            ('/System/Library/Fonts/PingFang.ttc', '苹方'),
            ('/System/Library/Fonts/PingFangSC.ttc', '苹方 SC'),
            ('/System/Library/Fonts/PingFangHK.ttc', '苹方 HK'),
            ('/System/Library/Fonts/STHeiti Light.ttc', '华文黑体'),
            ('/System/Library/Fonts/STHeiti Medium.ttc', '华文黑体 Medium'),
            ('/System/Library/Fonts/Hiragino Sans GB.ttc', '冬青黑体'),
            ('/Library/Fonts/Arial Unicode.ttf', 'Arial Unicode'),
            ('/System/Library/Fonts/Supplemental/Arial Unicode.ttf', 'Arial Unicode'),
            ('/Library/Fonts/SimHei.ttf', '黑体'),
            ('/Library/Fonts/Microsoft/SimHei.ttf', '黑体'),
        ]
    else:
        candidates = [
            ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 'Noto Sans CJK'),
            ('/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc', 'Noto Sans CJK'),
            ('/usr/share/fonts/wqy-microhei/wqy-microhei.ttc', '文泉驿微米黑'),
        ]

    for path, name in candidates:
        if os.path.exists(path):
            _CJK_FONT_CACHE[cache_key] = path
            diag_log(f"找到中文字体({cache_key}): {name} → {path}")
            return path

    # 通过 fc-list 尝试定位中文字体（Linux/macOS 上常见）
    try:
        result = subprocess.run(
            ["fc-list", ":lang=zh"],
            capture_output=True, text=True, timeout=5, check=False
        )
        if result.returncode == 0 and result.stdout:
            for line in result.stdout.splitlines():
                if ':' in line:
                    path = line.split(':')[0].strip()
                    if os.path.exists(path):
                        _CJK_FONT_CACHE[cache_key] = path
                        diag_log(f"fc-list 找到中文字体({cache_key}): {path}")
                        return path
    except Exception as e:
        diag_log(f"fc-list 查找字体失败: {e}")

    # 如果 bold 没找到，回退到 regular
    if bold and "regular" in _CJK_FONT_CACHE:
        diag_log(f"未找到粗体字体，回退到常规字体")
        return _CJK_FONT_CACHE["regular"]

    diag_log(f"未找到中文字体文件({cache_key})，中文可能无法正常显示")
    return None
