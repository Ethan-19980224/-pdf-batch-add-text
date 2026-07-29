"""PDF 智能预检对话框"""
import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QHeaderView

from ..config import COLORS
import fitz


class PreflightDialog(QDialog):
    """处理前预检PDF文件，提前发现潜在问题"""

    def __init__(self, tasks, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF 智能预检")
        self.setMinimumSize(700, 450)
        self.resize(750, 500)
        self.tasks = tasks
        self.issues = []
        self.setup_ui()
        self._run_checks()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("📋 PDF 智能预检报告")
        title.setFont(QFont("", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{COLORS['text']}; border:none; background:transparent;")
        layout.addWidget(title)

        self.summary_label = QLabel("正在检测...")
        self.summary_label.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:12px; border:none; background:transparent;")
        layout.addWidget(self.summary_label)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["文件名", "PDF 路径", "页数", "文件大小", "状态"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 60)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 80)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 100)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{ border:1px solid {COLORS['border']}; border-radius:6px; font-size:12px; background:white; }}
            QTableWidget::item {{ padding:4px 8px; }}
            QHeaderView::section {{ background:{COLORS['bg']}; padding:6px; font-weight:600; color:{COLORS['text_secondary']}; font-size:11px; border-bottom:1px solid {COLORS['primary']}; }}
        """)
        layout.addWidget(self.table, stretch=1)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.continue_btn = QPushButton("继续处理")
        self.continue_btn.setStyleSheet(f"""
            QPushButton {{ background:{COLORS['primary']}; color:white; border:none;
            border-radius:8px; padding:8px 24px; font-size:13px; font-weight:700; }}
            QPushButton:hover {{ background:{COLORS['primary_hover']}; }}
        """)
        self.continue_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.continue_btn)

        cancel_btn = QPushButton("取消处理")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{ background:{COLORS['border_light']}; color:{COLORS['text_secondary']};
            border:1px solid {COLORS['border']}; border-radius:8px; padding:8px 24px; font-size:13px; font-weight:600; }}
            QPushButton:hover {{ background:{COLORS['border']}; }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _run_checks(self):
        """执行预检"""
        self.table.setRowCount(0)
        ok_count = 0
        warn_count = 0
        err_count = 0
        total_size = 0

        for i, task in enumerate(self.tasks):
            pdf_path = task.get('pdf_path', '')
            filename = task.get('filename', '')
            status = "✅ 正常"
            status_color = COLORS['accent']

            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(filename))
            self.table.setItem(row, 1, QTableWidgetItem(pdf_path if pdf_path else "未指定"))

            if not pdf_path or not os.path.exists(pdf_path):
                status = "❌ 文件不存在"
                status_color = '#EF4444'
                err_count += 1
                self.table.setItem(row, 2, QTableWidgetItem("-"))
                self.table.setItem(row, 3, QTableWidgetItem("-"))
            elif os.path.getsize(pdf_path) == 0:
                status = "⚠️ 空文件"
                status_color = '#F59E0B'
                warn_count += 1
                self.table.setItem(row, 2, QTableWidgetItem("-"))
                self.table.setItem(row, 3, QTableWidgetItem("0 B"))
            else:
                try:
                    doc = fitz.open(pdf_path)
                    page_count = len(doc)
                    file_size = os.path.getsize(pdf_path)
                    total_size += file_size
                    size_str = f"{file_size/1024:.0f} KB" if file_size < 1024*1024 else f"{file_size/1024/1024:.1f} MB"

                    # 检查是否加密
                    if doc.is_encrypted:
                        status = "🔒 已加密"
                        status_color = '#F59E0B'
                        warn_count += 1
                    elif page_count == 0:
                        status = "⚠️ 无页面"
                        status_color = '#F59E0B'
                        warn_count += 1
                    else:
                        ok_count += 1

                    self.table.setItem(row, 2, QTableWidgetItem(str(page_count)))
                    self.table.setItem(row, 3, QTableWidgetItem(size_str))
                    doc.close()
                except Exception as e:
                    status = f"❌ 读取失败"
                    status_color = '#EF4444'
                    err_count += 1
                    self.table.setItem(row, 2, QTableWidgetItem("-"))
                    self.table.setItem(row, 3, QTableWidgetItem("-"))

            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor(status_color))
            self.table.setItem(row, 4, status_item)

        total = len(self.tasks)
        total_size_str = f"{total_size/1024:.0f} KB" if total_size < 1024*1024 else f"{total_size/1024/1024:.1f} MB"
        self.summary_label.setText(
            f"共扫描 {total} 个文件，总计 {total_size_str}　"
            f"✅ 正常 {ok_count}　⚠️ 警告 {warn_count}　❌ 错误 {err_count}"
        )
