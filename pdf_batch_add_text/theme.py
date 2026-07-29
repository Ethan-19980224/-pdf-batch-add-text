"""CSS 主题模板 - 集中管理所有 UI 样式表
使用 Python f-string 模板，通过 .format(colors) 或模板变量替换。
所有 {primary}、{text} 等占位符在 render() 方法中替换。
"""

from .config import COLORS

def _render(css_str: str) -> str:
    """将 CSS 模板中的 {key} 替换为 COLORS 中的值"""
    try:
        return css_str.format(**{k.replace('-', '_'): v for k, v in COLORS.items()})
    except KeyError as e:
        # 未匹配到的占位符原样保留
        return css_str


# =============================================================================
# 全局样式表
# =============================================================================

GLOBAL_CSS = """
QMainWindow {{
    background-color: {bg};
}}
/* 滚动条 */
QScrollBar:vertical {{
    background-color: transparent;
    width: 6px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background-color: {border};
    border-radius: 3px;
    min-height: 40px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {text_muted};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}
QScrollBar:horizontal {{
    background-color: transparent;
    height: 6px;
    margin: 0px;
}}
QScrollBar::handle:horizontal {{
    background-color: {border};
    border-radius: 3px;
    min-width: 40px;
}}
QScrollBar::handle:horizontal:hover {{
    background-color: {text_muted};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
"""


# =============================================================================
# 卡片容器
# =============================================================================

CARD_CSS = """
background-color: {card};
border: 1px solid {border};
border-radius: 14px;
"""


# =============================================================================
# 输入框
# =============================================================================

INPUT_CSS = """
QLineEdit {{
    border: 1px solid {border};
    border-radius: 8px;
    padding: 10px 14px;
    background-color: white;
    color: {text};
    font-size: 13px;
    selection-background-color: {primary_light};
    selection-color: {text};
}}
QLineEdit:hover {{
    border-color: {primary};
}}
QLineEdit:focus {{
    border: 1.5px solid {primary};
    padding: 9px 13px;
}}
QLineEdit[readOnly="true"] {{
    background-color: {border_light};
    color: {text_secondary};
}}
"""


# =============================================================================
# 按钮样式
# =============================================================================

PRIMARY_BTN_CSS = """
QPushButton {{
    background-color: {primary};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 11px 26px;
    font-weight: 600;
    font-size: 14px;
}}
QPushButton:hover {{
    background-color: {primary_hover};
}}
QPushButton:pressed {{
    background-color: {primary_hover};
}}
QPushButton:disabled {{
    background-color: {border};
    color: {text_muted};
}}
"""

SECONDARY_BTN_CSS = """
QPushButton {{
    background-color: {primary_light};
    color: {primary};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: 600;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {primary};
    color: white;
    border-color: {primary};
}}
"""

SUCCESS_BTN_CSS = """
QPushButton {{
    background-color: {accent};
    color: white;
    border: none;
    border-radius: 10px;
    padding: 14px 28px;
    font-weight: 700;
    font-size: 15px;
}}
QPushButton:hover {{
    background-color: {accent_hover};
}}
QPushButton:disabled {{
    background-color: {border};
    color: {text_muted};
}}
"""

WARNING_BTN_CSS = """
QPushButton {{
    background-color: {warning_light};
    color: {warning};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: 600;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {warning};
    color: white;
    border-color: {warning};
}}
"""

DANGER_BTN_CSS = """
QPushButton {{
    background-color: {danger_light};
    color: {danger};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 9px 16px;
    font-weight: 600;
    font-size: 12px;
}}
QPushButton:hover {{
    background-color: {danger};
    color: white;
    border-color: {danger};
}}
"""


# =============================================================================
# 表格
# =============================================================================

TABLE_CSS = """
QTableWidget {{
    border: none;
    background-color: white;
    gridline-color: {border_light};
    font-size: 13px;
    selection-background-color: {primary};
    selection-color: white;
    alternate-background-color: {primary_ultra_light};
}}
QTableWidget::item {{
    padding: 6px 4px;
    border-bottom: 1px solid {border_light};
}}
QTableWidget::item:selected {{
    background-color: {primary};
    color: white;
}}
QHeaderView::section {{
    background-color: {bg};
    padding: 10px 8px;
    border: none;
    border-bottom: 1.5px solid {primary};
    font-weight: 600;
    color: {text_secondary};
    font-size: 12px;
}}
QLineEdit {{
    padding: 4px;
    border: 1px solid {primary};
    border-radius: 2px;
    background: white;
    font-size: 13px;
}}
"""


# =============================================================================
# 日志区域
# =============================================================================

LOG_CSS = """
QPlainTextEdit {{
    background-color: #2C3E50;
    color: #B0C4D8;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 12px;
    border-radius: 8px;
    padding: 14px;
    border: 1px solid {border};
}}
"""


# =============================================================================
# 进度条
# =============================================================================

PROGRESS_CSS = """
QProgressBar {{
    border: none;
    border-radius: 10px;
    text-align: center;
    background-color: {border_light};
    color: {text_secondary};
    font-size: 11px;
    font-weight: 600;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {header_bg}, stop:1 {header_bg_end});
    border-radius: 10px;
}}
"""
