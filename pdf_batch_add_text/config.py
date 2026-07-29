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
    import fitz
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
# 配色方案 - 浅蓝素描主题 (柔和、低饱和、纸质质感)
# =============================================================================

COLORS = {
    'bg': '#F2F5F9',
    'card': '#FFFFFF',
    'primary': '#7BA7C9',
    'primary_hover': '#6494B5',
    'primary_light': '#E8F0F7',
    'primary_ultra_light': '#F0F5FA',
    'accent': '#8BB5A0',
    'accent_hover': '#7AA38E',
    'accent_light': '#EEF5F1',
    'warning': '#C9A96E',
    'warning_light': '#FAF5EC',
    'danger': '#C4897F',
    'danger_light': '#FBF1EF',
    'text': '#3D4F5F',
    'text_secondary': '#6B8299',
    'text_muted': '#A0B3C4',
    'border': '#D4DFE9',
    'border_light': '#E8EFF5',
    'header_bg': '#6B9ABD',
    'header_bg_end': '#89B4D0',
    'shadow': 'rgba(107, 154, 189, 0.05)',
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
