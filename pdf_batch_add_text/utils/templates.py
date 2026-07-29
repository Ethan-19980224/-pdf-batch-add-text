"""水印模板管理 - 加载和保存水印模板"""
import os
import json

TEMPLATES_FILE = os.path.join(os.path.expanduser("~"), ".pdf_batch_tool", "templates.json")

_DEFAULT_TEMPLATES = [
    {
        "name": "红章合同",
        "font_size": 72, "color": "#EF4444", "position": "居中",
        "opacity": 0.25, "bold": True, "italic": False,
        "page_range": "", "offset_x": 0, "offset_y": 0,
        "text": "已审核"
    },
    {
        "name": "财务发票",
        "font_size": 48, "color": "#F59E0B", "position": "右下角",
        "opacity": 0.35, "bold": False, "italic": False,
        "page_range": "", "offset_x": -30, "offset_y": -30,
        "text": "已报销"
    },
    {
        "name": "机密文件",
        "font_size": 60, "color": "#3B82F6", "position": "居中",
        "opacity": 0.3, "bold": True, "italic": True,
        "page_range": "1-", "offset_x": 0, "offset_y": 0,
        "text": "机密文件"
    },
    {
        "name": "普通水印",
        "font_size": 36, "color": "#9CA3AF", "position": "右下角",
        "opacity": 0.3, "bold": False, "italic": False,
        "page_range": "", "offset_x": 0, "offset_y": 0,
        "text": "样例"
    },
]


def load_watermark_templates():
    """加载水印模板列表"""
    if not os.path.exists(TEMPLATES_FILE):
        os.makedirs(os.path.dirname(TEMPLATES_FILE), exist_ok=True)
        with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(_DEFAULT_TEMPLATES, f, ensure_ascii=False, indent=2)
        return list(_DEFAULT_TEMPLATES)
    try:
        with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return list(_DEFAULT_TEMPLATES)


def save_watermark_templates(templates):
    """保存水印模板列表"""
    try:
        os.makedirs(os.path.dirname(TEMPLATES_FILE), exist_ok=True)
        with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False
