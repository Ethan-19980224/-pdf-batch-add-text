"""多文字配置对话框 - 为同一 PDF 不同位置添加不同文字"""
import os
from copy import deepcopy

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QColorDialog, QDoubleSpinBox,
    QCheckBox, QListWidget, QListWidgetItem, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QCursor

from ..config import COLORS, POSITIONS, DEFAULT_FONT_SIZE, DEFAULT_TEXT_COLOR, DEFAULT_POSITION, DEFAULT_OPACITY


class MultiTextDialog(QDialog):
    """多文字配置对话框：为同一 PDF 不同位置添加不同文字"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("批量多文字配置")
        self.setMinimumSize(680, 580)
        self.resize(720, 600)
        self.texts = []  # [{text, color, position, font_size, opacity, bold, italic, page_range}, ...]
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title = QLabel("批量多文字 — 同一 PDF 不同位置添加不同文字")
        title.setFont(QFont("", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{COLORS['text']}; border:none; background:transparent;")
        layout.addWidget(title)

        desc = QLabel("为每个文字独立设置内容、颜色、大小、位置和页码范围。处理时按列表顺序依次添加到各页。")
        desc.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:12px; border:none; background:transparent;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # 文字列表表格
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "序号", "文字内容", "颜色", "字号(pt)", "位置",
            "透明度", "粗体", "斜体"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for i in range(2, 8):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 45)
        self.table.setColumnWidth(2, 70)
        self.table.setColumnWidth(3, 70)
        self.table.setColumnWidth(4, 90)
        self.table.setColumnWidth(5, 70)
        self.table.setColumnWidth(6, 45)
        self.table.setColumnWidth(7, 45)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                border:1px solid {COLORS['border']}; border-radius:8px;
                background:white; font-size:13px;
            }}
            QTableWidget::item {{ padding:8px 10px; border-bottom:1px solid {COLORS['border_light']}; }}
            QHeaderView::section {{
                background:{COLORS['bg']}; color:{COLORS['text_secondary']};
                border:none; border-bottom:1.5px solid {COLORS['primary']};
                padding:8px; font-weight:600; font-size:12px;
            }}
        """)
        layout.addWidget(self.table, stretch=1)

        # 按钮行
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("➕ 添加文字")
        self.add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_btn.setFixedHeight(38)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background:{COLORS['accent_light']}; color:{COLORS['accent']};
                border:1px solid {COLORS['border']}; border-radius:8px;
                padding:8px 18px; font-size:13px; font-weight:600;
            }}
            QPushButton:hover {{ background:{COLORS['accent']}; color:white; }}
        """)
        self.add_btn.clicked.connect(self._add_entry)
        btn_layout.addWidget(self.add_btn)

        self.del_btn = QPushButton("🗑️ 删除")
        self.del_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.del_btn.setFixedHeight(38)
        self.del_btn.setStyleSheet(self.add_btn.styleSheet())
        self.del_btn.clicked.connect(self._del_entry)
        btn_layout.addWidget(self.del_btn)

        btn_layout.addStretch()

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cancel_btn.setFixedHeight(38)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background:{COLORS['border_light']}; color:{COLORS['text_secondary']};
                border:1px solid {COLORS['border']}; border-radius:8px;
                padding:8px 24px; font-size:13px; font-weight:600;
            }}
            QPushButton:hover {{ background:{COLORS['border']}; }}
        """)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.apply_btn = QPushButton("✓ 应用到任务")
        self.apply_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.apply_btn.setFixedHeight(38)
        self.apply_btn.setStyleSheet(f"""
            QPushButton {{
                background:{COLORS['primary']}; color:white; border:none;
                border-radius:8px; padding:8px 24px; font-size:14px; font-weight:700;
            }}
            QPushButton:hover {{ background:{COLORS['primary_hover']}; }}
            QPushButton:disabled {{ background:{COLORS['border']}; color:{COLORS['text_muted']}; }}
        """)
        self.apply_btn.clicked.connect(self.accept)
        self.apply_btn.setEnabled(False)
        btn_layout.addWidget(self.apply_btn)

        layout.addLayout(btn_layout)

        # 页码范围说明
        note = QLabel("提示: 各文字条目共享当前任务的页码范围设置（主窗口中「设置」面板中的「页码范围」）")
        note.setStyleSheet(f"color:{COLORS['text_muted']}; font-size:11px; border:none; background:transparent;")
        layout.addWidget(note)

    def _add_entry(self):
        """添加一个新文字条目（使用当前任务设置作为默认值）"""
        parent = self.parent()
        if parent and hasattr(parent, 'text_settings'):
            ts = parent.text_settings
            text = ts.get('color', DEFAULT_TEXT_COLOR)
            font_size = ts.get('font_size', DEFAULT_FONT_SIZE)
            position = ts.get('position', DEFAULT_POSITION)
            opacity = ts.get('opacity', DEFAULT_OPACITY)
            bold = ts.get('bold', False)
            italic = ts.get('italic', False)
        else:
            ts = {}
            text = DEFAULT_TEXT_COLOR
            font_size = DEFAULT_FONT_SIZE
            position = DEFAULT_POSITION
            opacity = 1.0
            bold = False
            italic = False

        self.texts.append({
            'text': '', 'color': text, 'position': position,
            'font_size': font_size, 'opacity': opacity,
            'bold': bold, 'italic': italic
        })
        self._refresh_table()
        self.apply_btn.setEnabled(True)
        # 自动跳转到新增行的文字输入框
        self.table.selectRow(self.table.rowCount() - 1)
        self.table.scrollToItem(self.table.item(self.table.rowCount() - 1, 1),
            QTableWidget.ScrollHint.PositionAtCenter)

    def _del_entry(self):
        """删除当前选中的条目"""
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "提示", "请先选中要删除的行")
            return
        row = rows[0].row()
        if row < len(self.texts):
            self.texts.pop(row)
            self._refresh_table()
            self.apply_btn.setEnabled(len(self.texts) > 0)

    def _refresh_table(self):
        """刷新表格内容"""
        self.table.setRowCount(len(self.texts))
        for i, entry in enumerate(self.texts):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.item(i, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # 文字内容
            txt_item = QTableWidgetItem(entry['text'] or "")
            txt_item.setForeground(QColor(entry['color']))
            self.table.setItem(i, 1, txt_item)
            # 颜色
            color_item = QTableWidgetItem(entry['color'])
            color_item.setForeground(QColor(entry['color']))
            self.table.setItem(i, 2, color_item)
            # 字号
            self.table.setItem(i, 3, QTableWidgetItem(str(entry['font_size'])))
            # 位置
            self.table.setItem(i, 4, QTableWidgetItem(entry['position']))
            # 透明度
            self.table.setItem(i, 5, QTableWidgetItem(f"{entry['opacity']:.1f}"))
            # 粗体
            bold_item = QTableWidgetItem("✓" if entry['bold'] else "")
            bold_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 6, bold_item)
            # 斜体
            italic_item = QTableWidgetItem("✓" if entry['italic'] else "")
            italic_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 7, italic_item)

    def _edit_cell(self, row, col):
        """处理单元格双击编辑"""
        if col == 1:  # 文字内容
            item = self.table.item(row, col)
            self.table.editItem(item)
        elif col == 2:  # 颜色 - 打开颜色选择器
            from PyQt6.QtWidgets import QColorDialog
            current = self.texts[row]['color']
            dlg = QColorDialog(QColor(current), self)
            if dlg.exec():
                new_color = dlg.currentColor().name()
                self.texts[row]['color'] = new_color
                self._refresh_table()
        elif col == 3:  # 字号
            item = self.table.item(row, col)
            self.table.editItem(item)
        elif col == 4:  # 位置 - 下拉选择
            self._edit_position(row)
        elif col == 5:  # 透明度
            item = self.table.item(row, col)
            self.table.editItem(item)
        elif col == 6:  # 粗体 - 切换
            self.texts[row]['bold'] = not self.texts[row]['bold']
            self._refresh_table()
        elif col == 7:  # 斜体 - 切换
            self.texts[row]['italic'] = not self.texts[row]['italic']
            self._refresh_table()

    def _edit_position(self, row):
        """弹出位置选择下拉框"""
        from PyQt6.QtWidgets import QInputDialog
        current = self.texts[row]['position']
        pos_list = list(POSITIONS.keys())
        item, ok = QInputDialog.getItem(
            self, "选择位置", "选择文字位置", pos_list,
            pos_list.index(current) if current in pos_list else 0,
            False
        )
        if ok and item:
            self.texts[row]['position'] = item
            self._refresh_table()

    def get_texts(self):
        """返回文字列表"""
        valid = []
        for entry in self.texts:
            text = entry.get('text', '')
            if text and text.strip():
                valid.append(entry)
        return valid

    def clear(self):
        """清空所有文字"""
        self.texts.clear()
        self._refresh_table()
        self.apply_btn.setEnabled(False)
