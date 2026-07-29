"""工具函数模块"""
from .fonts import find_cjk_font
from .pages import parse_page_range
from .checkpoint import save_checkpoint, load_checkpoint, clear_checkpoint
from .history import load_watermark_history, save_watermark_history, smart_recommend_text
from .notify import send_system_notification
from .templates import load_watermark_templates, save_watermark_templates
from .ensure import ensure_dependencies, create_app_icon

__all__ = [
    'find_cjk_font', 'parse_page_range',
    'save_checkpoint', 'load_checkpoint', 'clear_checkpoint',
    'load_watermark_history', 'save_watermark_history', 'smart_recommend_text',
    'send_system_notification',
    'load_watermark_templates', 'save_watermark_templates',
    'ensure_dependencies', 'create_app_icon',
]
