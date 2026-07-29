"""智能批量编辑对话框"""
import re

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QGridLayout,
    QLineEdit, QCheckBox, QTableWidget, QTableWidgetItem, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QHeaderView

from ..config import COLORS


class BatchEditDialog(QDialog):
    """批量编辑文字：Find & Replace、前置、追加、正则替换"""

    def __init__(self, tasks, parent=None):
        super().__init__(parent)
        self.tasks = tasks
        self.selected_indices = list(range(len(tasks)))
        self.setWindowTitle("智能批量编辑")
        self.setMinimumSize(750, 500)
        self.resize(800, 550)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("批量编辑文字内容")
        title.setFont(QFont("", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{COLORS['text']}; border:none; background:transparent;")
        layout.addWidget(title)

        # 操作模式
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(10)
        mode_layout.addWidget(QLabel("操作:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "替换文字",
            "前置添加",
            "追加添加",
            "正则替换",
            "清除所有文字",
            "设置统一文字",
        ])
        self.mode_combo.minimumHeight = 34
        self.mode_combo.setStyleSheet(f"""
            QComboBox {{ border:1px solid {COLORS['border']}; border-radius:6px;
            padding:4px 10px; font-size:13px; background:white; color:{COLORS['text']}; }}
            QComboBox:focus {{ border-color:{COLORS['primary']}; }}
        """)
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_combo, stretch=1)
        layout.addLayout(mode_layout)

        # 查找/替换输入区
        input_layout = QGridLayout()
        input_layout.setSpacing(10)

        self.find_label = QLabel("查找:")
        self.find_label.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:13px; border:none; background:transparent;")
        input_layout.addWidget(self.find_label, 0, 0)

        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("输入要查找的文字...")
        self.find_input.setMinimumHeight(36)
        self.find_input.setStyleSheet(f"""
            QLineEdit {{ border:1px solid {COLORS['border']}; border-radius:6px; padding:4px 12px; font-size:13px; background:white; color:{COLORS['text']}; }}
            QLineEdit:focus {{ border:2px solid {COLORS['primary']}; }}
        """)
        self.find_input.textChanged.connect(self._preview_changes)
        input_layout.addWidget(self.find_input, 0, 1)

        self.replace_label = QLabel("替换为:")
        self.replace_label.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:13px; border:none; background:transparent;")
        input_layout.addWidget(self.replace_label, 1, 0)

        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("输入替换文字...")
        self.replace_input.setMinimumHeight(36)
        self.replace_input.setStyleSheet(self.find_input.styleSheet())
        self.replace_input.textChanged.connect(self._preview_changes)
        input_layout.addWidget(self.replace_input, 1, 1)

        # 大小写敏感
        self.case_sensitive = QCheckBox("区分大小写")
        self.case_sensitive.setStyleSheet(f"color:{COLORS['text']}; font-size:12px; border:none; background:transparent;")
        self.case_sensitive.toggled.connect(self._preview_changes)
        input_layout.addWidget(self.case_sensitive, 2, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addLayout(input_layout)

        # 预览表格
        preview_label = QLabel("预览受影响的行:")
        preview_label.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:12px; font-weight:600; border:none; background:transparent;")
        layout.addWidget(preview_label)

        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(4)
        self.preview_table.setHorizontalHeaderLabels(["序号", "原文字", "新文字", "状态"])
        self.preview_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.preview_table.setColumnWidth(0, 40)
        self.preview_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.preview_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.preview_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.preview_table.setColumnWidth(3, 60)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.setStyleSheet(f"""
            QTableWidget {{ border:1px solid {COLORS['border']}; border-radius:6px; font-size:12px; background:white; }}
            QTableWidget::item {{ padding:4px 8px; }}
            QHeaderView::section {{ background:{COLORS['bg']}; padding:6px; font-weight:600; color:{COLORS['text_secondary']}; font-size:11px; border-bottom:1px solid {COLORS['primary']}; }}
        """)
        layout.addWidget(self.preview_table, stretch=1)

        # 统计
        self.stats_label = QLabel("等待预览...")
        self.stats_label.setStyleSheet(f"color:{COLORS['text_muted']}; font-size:11px; border:none; background:transparent;")
        layout.addWidget(self.stats_label)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{ background:{COLORS['border_light']}; color:{COLORS['text_secondary']};
            border:1px solid {COLORS['border']}; border-radius:8px; padding:8px 24px; font-size:13px; font-weight:600; }}
            QPushButton:hover {{ background:{COLORS['border']}; }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        self.apply_btn = QPushButton("应用修改")
        self.apply_btn.setStyleSheet(f"""
            QPushButton {{ background:{COLORS['primary']}; color:white; border:none;
            border-radius:8px; padding:8px 24px; font-size:13px; font-weight:700; }}
            QPushButton:hover {{ background:{COLORS['primary_hover']}; }}
            QPushButton:disabled {{ background:{COLORS['border']}; color:{COLORS['text_muted']}; }}
        """)
        self.apply_btn.setEnabled(False)
        self.apply_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.apply_btn)
        layout.addLayout(btn_layout)

    def _on_mode_changed(self, mode):
        """切换操作模式时更新UI"""
        is_replace = '替换' in mode or '正则' in mode
        self.find_label.setVisible(is_replace)
        self.find_input.setVisible(is_replace)
        self.replace_label.setVisible(True)
        self.replace_input.setVisible(True)
        self.case_sensitive.setVisible(is_replace)
        if mode == "清除所有文字":
            self.replace_label.setVisible(False)
            self.replace_input.setVisible(False)
        elif mode == "设置统一文字":
            self.find_label.setVisible(False)
            self.find_input.setVisible(False)
            self.case_sensitive.setVisible(False)
            self.replace_label.setText("设置文字:")
        else:
            self.replace_label.setText("替换为:" if is_replace else "文字:")
        self._preview_changes()

    def _apply_operation(self, old_text, mode, find_text, replace_text, case_sensitive):
        """对单个文字应用操作"""
        if not old_text:
            return old_text
        if mode == "替换文字":
            if not find_text:
                return old_text
            if case_sensitive:
                return old_text.replace(find_text, replace_text)
            else:
                return old_text.lower().replace(find_text.lower(), replace_text.lower())
        elif mode == "前置添加":
            return replace_text + old_text
        elif mode == "追加添加":
            return old_text + replace_text
        elif mode == "正则替换":
            if not find_text:
                return old_text
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                return re.sub(find_text, replace_text, old_text, flags=flags)
            except re.error:
                return old_text
        elif mode == "清除所有文字":
            return ""
        elif mode == "设置统一文字":
            return replace_text
        return old_text

    def _preview_changes(self):
        """实时预览修改效果"""
        mode = self.mode_combo.currentText()
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        case_sensitive = self.case_sensitive.isChecked()

        self.preview_table.setRowCount(0)
        changed_count = 0
        total = len(self.tasks)
        self.selected_indices = []

        for i, task in enumerate(self.tasks):
            old_text = task.get('text', '')
            new_text = self._apply_operation(old_text, mode, find_text, replace_text, case_sensitive)
            if new_text != old_text:
                self.selected_indices.append(i)
                row = self.preview_table.rowCount()
                self.preview_table.insertRow(row)
                self.preview_table.setItem(row, 0, QTableWidgetItem(str(i + 1)))
                self.preview_table.setItem(row, 1, QTableWidgetItem(old_text[:40] + ('...' if len(old_text) > 40 else '')))
                self.preview_table.setItem(row, 2, QTableWidgetItem(new_text[:40] + ('...' if len(new_text) > 40 else '')))
                status_item = QTableWidgetItem("✓")
                status_item.setForeground(QColor(COLORS['accent']))
                self.preview_table.setItem(row, 3, status_item)
                changed_count += 1

        self.stats_label.setText(f"共 {total} 个任务, 将修改 {changed_count} 个")
        self.apply_btn.setEnabled(changed_count > 0)

    def get_results(self):
        """获取修改后的任务列表"""
        mode = self.mode_combo.currentText()
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        case_sensitive = self.case_sensitive.isChecked()
        for i in self.selected_indices:
            if 0 <= i < len(self.tasks):
                old_text = self.tasks[i].get('text', '')
                self.tasks[i]['text'] = self._apply_operation(old_text, mode, find_text, replace_text, case_sensitive)
        return self.tasks
