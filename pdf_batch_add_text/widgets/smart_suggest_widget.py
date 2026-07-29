"""智能推荐面板 - 显示在表格下方"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QCursor

from ..config import COLORS


class SmartSuggestWidget(QWidget):
    """智能推荐面板 - 显示在表格下方"""

    text_selected = pyqtSignal(str)  # 用户选中推荐文字时发射

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("smartSuggestWidget")
        self.setVisible(False)
        self.setFixedHeight(36)
        self.setStyleSheet(f"""
            QWidget#smartSuggestWidget {{
                background-color: {COLORS['primary_ultra_light']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 2px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(8, 2, 8, 2)

        label = QLabel("💡 推荐:")
        label.setStyleSheet(f"color:{COLORS['primary']};font-size:11px;font-weight:600;border:none;background:transparent;")
        layout.addWidget(label)
        self._btn_layout = layout
        self._buttons = []

    def show_suggestions(self, suggestions, callback):
        """显示推荐文字按钮"""
        self._clear_buttons()
        for text in suggestions:
            btn = QPushButton(text[:12] + ('...' if len(text) > 12 else ''))
            btn.setToolTip(text)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: white; color:{COLORS['primary']};
                    border:1px solid {COLORS['border']}; border-radius:4px;
                    padding:2px 8px; font-size:11px; font-weight:500;
                }}
                QPushButton:hover {{
                    background:{COLORS['primary']}; color:white; border-color:{COLORS['primary']};
                }}
            """)
            btn.clicked.connect(lambda checked, t=text: self.text_selected.emit(t))
            self._btn_layout.addWidget(btn)
            self._buttons.append(btn)
        self._btn_layout.addStretch()
        self.setVisible(True)

    def hide_suggestions(self):
        self.setVisible(False)
        self._clear_buttons()

    def _clear_buttons(self):
        for btn in self._buttons:
            self._btn_layout.removeWidget(btn)
            btn.deleteLater()
        self._buttons.clear()
