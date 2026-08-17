"""
配置与常量
集中管理颜色主题、应用信息、位置映射和默认值。
"""

import os
import sys

# =============================================================================
# 依赖库可用性检测
# =============================================================================

try:
    import pymupdf as fitz
    FITZ_AVAILABLE = True
    try:
        _TEXT_ALIGN_LEFT = fitz.TEXT_ALIGN_LEFT
        _TEXT_ALIGN_CENTER = fitz.TEXT_ALIGN_CENTER
        _TEXT_ALIGN_RIGHT = fitz.TEXT_ALIGN_RIGHT
    except Exception:
        # 兼容性：部分版本可能不支持对齐常量
        _TEXT_ALIGN_LEFT = 0
        _TEXT_ALIGN_CENTER = 1
        _TEXT_ALIGN_RIGHT = 2
except ImportError:
    FITZ_AVAILABLE = False
    _TEXT_ALIGN_LEFT = 0
    _TEXT_ALIGN_CENTER = 1
    _TEXT_ALIGN_RIGHT = 2

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

# =============================================================================
# 配色方案 - 深海蓝 + 金箔 (奢华高级感)
# =============================================================================

COLORS = {
    # 主背景
    'bg': '#F5F0E8',
    'card': '#FFFFFF',
    'card_bg': '#F5F0E8',  # 卡片背景色

    # 主色调 - 深海蓝
    'primary': '#2D3A6E',
    'primary_hover': '#1E2A4A',
    'primary_light': '#E8EAF0',
    'primary_ultra_light': '#F3F4F8',
    'primary_dark': '#162040',

    # 金箔点缀
    'gold': '#D4A442',
    'gold_light': '#E8C35A',
    'gold_dark': '#B8892A',
    'gold_bg': '#FEF8E8',

    # 辅助色 - 翡翠绿
    'accent': '#2D9574',
    'accent_hover': '#1E7A5E',
    'accent_light': '#E8F5F0',

    # 警告/危险
    'warning': '#D4A442',
    'warning_light': '#FEF8E8',
    'danger': '#EF4444',
    'danger_light': '#FEF2F2',

    # 文字
    'text': '#1E2A4A',
    'text_secondary': '#9A8F80',
    'text_muted': '#C4B8A8',
    'text_light': '#EBE4D8',

    # 边框
    'border': '#EBE4D8',
    'border_light': '#F5F0E8',

    # 头部渐变
    'header_bg': '#2D3A6E',
    'header_bg_end': '#1E2A4A',

    # 阴影
    'shadow': 'rgba(30, 42, 74, 0.06)',
    'shadow_medium': 'rgba(30, 42, 74, 0.12)',
    'shadow_dark': 'rgba(22, 32, 64, 0.25)',
    'shadow_deep': 'rgba(22, 32, 64, 0.35)',
}

APP_NAME = "PDF 批量添加文字"
APP_VERSION = "4.1.1"

DEFAULT_FONT_SIZE = 14
DEFAULT_TEXT_COLOR = "#EF4444"
DEFAULT_POSITION = "右下角"
DEFAULT_OPACITY = 1.0

POSITIONS = {
    "左上角": (0.05, 0.95),
    "右上角": (0.95, 0.95),
    "左下角": (0.05, 0.05),
    "右下角": (0.95, 0.05),
    "居中": (0.5, 0.5),
    "顶部居中": (0.5, 0.95),
    "底部居中": (0.5, 0.05),
    "智能自动": "AUTO",  # 特殊标记：内容感知自动定位
}

# PyMuPDF 内置字体名称映射（仅用于 fontfile 缺失时的回退）
FITZ_FONT_MAP = {
    "regular": "helv",
    "bold": "hebo",
    "italic": "heob",
    "bold_italic": "hebi",
}

# 当使用 fontfile 时，fontname 必须是合法的资源名（不含空格、不含特殊字符）
CJK_FONT_RESOURCE_NAME = "cjkfont"

# 检查点文件路径（用于中断恢复）
CHECKPOINT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".checkpoints")
CHECKPOINT_FILE = os.path.join(CHECKPOINT_DIR, "checkpoint.json")

# 水印模板文件路径
TEMPLATE_DIR = os.path.join(CHECKPOINT_DIR, "templates")

# 水印历史文件路径
WATERMARK_HISTORY_FILE = os.path.join(CHECKPOINT_DIR, "watermark_history.json")


def get_app_dir():
    """获取应用目录（模块所在目录）"""
    return os.path.dirname(os.path.abspath(__file__))


def get_data_dir():
    """获取用户数据目录"""
    return CHECKPOINT_DIR
