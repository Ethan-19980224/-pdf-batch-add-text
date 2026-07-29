"""水印模板管理对话框"""
import os
from copy import deepcopy

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QHBoxLayout, QPushButton, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

from ..config import COLORS
from ..utils.templates import load_watermark_templates, save_watermark_templates


class WatermarkTemplateDialog(QDialog):
    """水印模板管理对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("水印模板管理")
        self.setMinimumSize(500, 400)
        self.resize(550, 450)
        self.templates = load_watermark_templates()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("水印模板管理")
        title.setFont(QFont("", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{COLORS['text']}; border:none; background:transparent;")
        layout.addWidget(title)

        desc = QLabel("选择一个模板快速应用全部水印设置，或管理自定义模板")
        desc.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:12px; border:none; background:transparent;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # 模板列表
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{ border:1px solid {COLORS['border']}; border-radius:8px; font-size:13px; background:white; }}
            QListWidget::item {{ padding:12px 16px; border-bottom:1px solid {COLORS['border_light']}; }}
            QListWidget::item:hover {{ background:{COLORS['accent_light']}; }}
            QListWidget::item:selected {{ background:{COLORS['primary_light']}; color:{COLORS['primary']}; font-weight:600; }}
        """)
        layout.addWidget(self.list_widget, stretch=1)

        # 按钮
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("➕ 新建模板")
        self.add_btn.setStyleSheet(f"""
            QPushButton {{ background:{COLORS['accent_light']}; color:{COLORS['accent']};
            border:1px solid {COLORS['border']}; border-radius:8px; padding:8px 18px; font-size:13px; font-weight:600; }}
            QPushButton:hover {{ background:{COLORS['accent']}; color:white; }}
        """)
        self.add_btn.clicked.connect(self._add_template)
        btn_layout.addWidget(self.add_btn)

        self.del_btn = QPushButton("🗑️ 删除")
        self.del_btn.setStyleSheet(self.add_btn.styleSheet())
        self.del_btn.clicked.connect(self._del_template)
        btn_layout.addWidget(self.del_btn)

        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{ background:{COLORS['border_light']}; color:{COLORS['text_secondary']};
            border:1px solid {COLORS['border']}; border-radius:8px; padding:8px 24px; font-size:13px; font-weight:600; }}
            QPushButton:hover {{ background:{COLORS['border']}; }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        self.apply_btn = QPushButton("应用选定模板")
        self.apply_btn.setStyleSheet(f"""
            QPushButton {{ background:{COLORS['primary']}; color:white; border:none;
            border-radius:8px; padding:8px 24px; font-size:13px; font-weight:700; }}
            QPushButton:hover {{ background:{COLORS['primary_hover']}; }}
        """)
        self.apply_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.apply_btn)

        layout.addLayout(btn_layout)

        self._refresh_list()

    def _refresh_list(self):
        self.list_widget.clear()
        for t in self.templates:
            name = t.get('name', '未命名')
            color = t.get('color', '#000000')
            pos = t.get('position', '')
            size = t.get('font_size', 24)
            item = QListWidgetItem(f"  {name}  ({pos}, {size}pt)")
            item.setForeground(QColor(color))
            self.list_widget.addItem(item)

    def _add_template(self):
        name, ok = QInputDialog.getText(self, "新建模板", "输入模板名称:", text="")
        if ok and name.strip():
            parent = self.parent()
            if parent and hasattr(parent, 'text_settings'):
                settings = deepcopy(parent.text_settings)
            else:
                settings = {}
            self.templates.append({
                "name": name.strip(),
                "font_size": settings.get('font_size', 36),
                "color": settings.get('color', '#000000'),
                "position": settings.get('position', '右下角'),
                "opacity": settings.get('opacity', 0.3),
                "bold": settings.get('bold', False),
                "italic": settings.get('italic', False),
                "page_range": settings.get('page_range', ''),
                "offset_x": settings.get('offset_x', 0),
                "offset_y": settings.get('offset_y', 0),
                "text": settings.get('text', ''),
            })
            save_watermark_templates(self.templates)
            self._refresh_list()

    def _del_template(self):
        row = self.list_widget.currentRow()
        if row >= 0 and row < len(self.templates):
            name = self.templates[row].get('name', '')
            reply = QMessageBox.question(self, "确认删除", f"确定删除模板「{name}」？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.templates.pop(row)
                save_watermark_templates(self.templates)
                self._refresh_list()

    def get_selected_template(self):
        row = self.list_widget.currentRow()
        if 0 <= row < len(self.templates):
            return self.templates[row]
        return None
