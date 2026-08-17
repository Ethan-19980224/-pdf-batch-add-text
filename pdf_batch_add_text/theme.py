"""CSS 主题模板 - 高级现代 UI 风格
靛蓝紫 + 翡翠绿配色，毛玻璃卡片，微阴影
"""
from .config import COLORS

def _render(css_str: str) -> str:
    try:
        return css_str.format(**{k.replace('-', '_'): v for k, v in COLORS.items()})
    except KeyError:
        return css_str


# =============================================================================
# 全局样式
# =============================================================================

GLOBAL_CSS = """
QMainWindow {
    background-color: {bg};
}
QWidget {
    font-family: "Microsoft YaHei UI", "Segoe UI", "PingFang SC", sans-serif;
}
/* 滚动条 - 极简 */
QScrollBar:vertical {
    background-color: transparent; width: 5px; margin: 0;
}
QScrollBar::handle:vertical {
    background-color: {border}; border-radius: 3px; min-height: 30px;
}
QScrollBar::handle:vertical:hover { background-color: {text_muted}; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background-color: transparent; height: 5px; margin: 0;
}
QScrollBar::handle:horizontal {
    background-color: {border}; border-radius: 3px; min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background-color: {text_muted}; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
"""


# =============================================================================
# 卡片容器 - 毛玻璃效果
# =============================================================================

CARD_CSS = """
background-color: {card};
border: 1px solid {border};
border-radius: 16px;
"""


# =============================================================================
# 输入框
# =============================================================================

INPUT_CSS = """
QLineEdit {
    border: 1.5px solid {border};
    border-radius: 10px;
    padding: 10px 16px;
    background-color: white;
    color: {text};
    font-size: 13px;
    selection-background-color: {primary_light};
}
QLineEdit:hover { border-color: {primary}; }
QLineEdit:focus {
    border: 2px solid {primary};
    padding: 9px 15px;
}
"""


# =============================================================================
# 按钮 - 现代风格
# =============================================================================

PRIMARY_BTN_CSS = """
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {primary}, stop:1 {primary_hover});
    color: white; border: none; border-radius: 10px;
    padding: 12px 28px; font-weight: 700; font-size: 14px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {primary_hover}, stop:1 #4338CA);
}
QPushButton:pressed { background: #4338CA; }
QPushButton:disabled {
    background: {border}; color: {text_muted};
}
"""

SECONDARY_BTN_CSS = """
QPushButton {
    background: {primary_light}; color: {primary};
    border: 1.5px solid {border}; border-radius: 10px;
    padding: 10px 20px; font-weight: 600; font-size: 13px;
}
QPushButton:hover {
    background: {primary}; color: white; border-color: {primary};
}
QPushButton:pressed { background: {primary_hover}; }
"""

SUCCESS_BTN_CSS = """
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {accent}, stop:1 {accent_hover});
    color: white; border: none; border-radius: 12px;
    padding: 14px 32px; font-weight: 700; font-size: 15px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {accent_hover}, stop:1 #047857);
}
QPushButton:disabled {
    background: {border}; color: {text_muted};
}
"""

WARNING_BTN_CSS = """
QPushButton {
    background: {warning_light}; color: {warning};
    border: 1.5px solid {border}; border-radius: 10px;
    padding: 10px 20px; font-weight: 600; font-size: 13px;
}
QPushButton:hover {
    background: {warning}; color: white; border-color: {warning};
}
"""

DANGER_BTN_CSS = """
QPushButton {
    background: {danger_light}; color: {danger};
    border: 1.5px solid {border}; border-radius: 10px;
    padding: 9px 18px; font-weight: 600; font-size: 12px;
}
QPushButton:hover {
    background: {danger}; color: white; border-color: {danger};
}
"""

TOOLBAR_BTN_CSS = """
QPushButton {
    background: transparent; color: {text_secondary};
    border: 1px solid transparent; border-radius: 10px;
    padding: 8px 14px; font-weight: 500; font-size: 12px;
}
QPushButton:hover {
    background: {primary_light}; color: {primary}; border-color: {border};
}
QPushButton:pressed {
    background: {primary}; color: white;
}
"""


# =============================================================================
# 表格
# =============================================================================

TABLE_CSS = """
QTableWidget {
    border: 1px solid {border}; border-radius: 12px;
    background-color: white;
    gridline-color: {border_light};
    font-size: 13px;
    selection-background-color: {primary_light};
    selection-color: {text};
    alternate-background-color: {primary_ultra_light};
}
QTableWidget::item {
    padding: 6px 8px; border-bottom: 1px solid {border_light};
}
QTableWidget::item:selected {
    background-color: {primary_light}; color: {primary};
    font-weight: 600;
}
QHeaderView::section {
    background-color: {border_light};
    padding: 10px 8px; border: none;
    border-bottom: 2px solid {primary};
    font-weight: 700; color: {text_secondary};
    font-size: 12px; text-transform: uppercase;
}
QLineEdit {
    padding: 4px; border: 1px solid {primary};
    border-radius: 4px; background: white; font-size: 13px;
}
"""


# =============================================================================
# 日志区域 - 代码编辑器风格
# =============================================================================

LOG_CSS = """
QPlainTextEdit {
    background-color: #1E1E2E;
    color: #CDD6F4;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 12px;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid {border};
    selection-background-color: rgba(99, 102, 241, 0.3);
}
"""


# =============================================================================
# 进度条
# =============================================================================

PROGRESS_CSS = """
QProgressBar {
    border: none; border-radius: 8px;
    text-align: center;
    background-color: {border_light};
    color: {text_secondary};
    font-size: 11px; font-weight: 600;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {primary}, stop:1 {accent});
    border-radius: 8px;
}
"""


# =============================================================================
# 深色侧边栏
# =============================================================================

SIDEBAR_CSS = """
QWidget#sidebar {
    background-color: {sidebar};
    border: none; border-radius: 0;
}
QPushButton#sidebar_btn {
    background: transparent; color: {text_light};
    border: none; border-radius: 10px;
    padding: 12px 16px; font-weight: 500; font-size: 13px;
    text-align: left;
}
QPushButton#sidebar_btn:hover {
    background: {sidebar_hover}; color: white;
}
QPushButton#sidebar_btn:checked {
    background: {sidebar_active}; color: white;
    font-weight: 700;
}
QLabel#sidebar_label {
    color: {text_light}; font-size: 10px;
    font-weight: 600; text-transform: uppercase;
    letter-spacing: 1px;
    padding: 8px 16px 4px; border: none;
}
"""


# =============================================================================
# 标签页
# =============================================================================

TAB_CSS = """
QTabWidget::pane {
    border: 1px solid {border}; border-radius: 12px;
    background: white; padding: 4px;
}
QTabBar::tab {
    background: {border_light}; color: {text_secondary};
    border: none; border-radius: 8px;
    padding: 8px 18px; font-weight: 600; font-size: 12px;
    margin: 2px;
}
QTabBar::tab:selected {
    background: {primary_light}; color: {primary};
    font-weight: 700;
}
QTabBar::tab:hover {
    background: {primary_ultra_light}; color: {primary};
}
"""


# =============================================================================
# 分组框
# =============================================================================

GROUP_CSS = """
QGroupBox {
    border: 1px solid {border}; border-radius: 12px;
    margin-top: 16px; padding: 16px 12px 12px;
    font-weight: 700; font-size: 13px; color: {text};
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px; margin-left: 12px;
    background: {card}; color: {primary};
}
"""


# =============================================================================
# 组合框
# =============================================================================

COMBO_CSS = """
QComboBox {
    border: 1.5px solid {border}; border-radius: 10px;
    padding: 8px 14px; background: white;
    color: {text}; font-size: 13px;
}
QComboBox:hover { border-color: {primary}; }
QComboBox::drop-down {
    border: none; width: 28px;
}
QComboBox::down-arrow {
    image: none; border: none;
}
QComboBox QAbstractItemView {
    border: 1px solid {border}; border-radius: 8px;
    background: white; selection-background-color: {primary_light};
    selection-color: {primary}; padding: 4px;
}
"""


# =============================================================================
# 复选框/单选
# =============================================================================

CHECKBOX_CSS = """
QCheckBox {
    spacing: 8px; font-size: 13px; color: {text};
}
QCheckBox::indicator {
    width: 18px; height: 18px; border-radius: 4px;
    border: 1.5px solid {border};
    background: white;
}
QCheckBox::indicator:hover { border-color: {primary}; }
QCheckBox::indicator:checked {
    background: {primary}; border-color: {primary};
}
QCheckBox::indicator:checked:hover { background: {primary_hover}; }
"""