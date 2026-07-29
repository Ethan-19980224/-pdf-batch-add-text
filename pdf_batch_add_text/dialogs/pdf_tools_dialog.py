"""PDF 辅助工具对话框 - 页码/页脚/文本提取"""
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QLineEdit, QFileDialog,
    QMessageBox, QDoubleSpinBox, QCheckBox, QTabWidget,
    QRadioButton, QButtonGroup, QPlainTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from ..config import COLORS, POSITIONS, DEFAULT_FONT_SIZE, DEFAULT_TEXT_COLOR, DEFAULT_POSITION
from ..pdf.tools import add_page_numbers, add_footer, extract_text
from ..logger import diag_log


class PdfToolsDialog(QDialog):
    """PDF 辅助工具对话框 — 页码 / 页脚 / 文本提取"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF 工具集")
        self.setMinimumSize(520, 520)
        self.resize(560, 560)
        self.output_dir = ""
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("PDF 工具集")
        title.setFont(QFont("", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{COLORS['text']}; border:none; background:transparent;")
        layout.addWidget(title)

        desc = QLabel("为 PDF 添加页码、自定义页脚，或提取文字内容")
        desc.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:12px; border:none; background:transparent;")
        layout.addWidget(desc)

        # 标签页
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, stretch=1)

        # === Tab 1: 添加页码 ===
        self.tab_page_num = self._build_page_number_tab()
        self.tabs.addTab(self.tab_page_num, "📄 添加页码")

        # === Tab 2: 添加页脚 ===
        self.tab_footer = self._build_footer_tab()
        self.tabs.addTab(self.tab_footer, "📝 添加页脚")

        # === Tab 3: 提取文本 ===
        self.tab_extract = self._build_extract_tab()
        self.tabs.addTab(self.tab_extract, "📋 提取文本")

    # ---- 构建页码标签页 ----
    def _build_page_number_tab(self):
        tab = QVBoxLayout()
        tab.setSpacing(10)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("起始页码"))
        self.start_num = QSpinBox()
        self.start_num.setRange(0, 9999)
        self.start_num.setValue(1)
        self.start_num.setFixedWidth(70)
        row1.addWidget(self.start_num)
        row1.addStretch()
        row1.addWidget(QLabel("字号"))
        self.pn_font_size = QSpinBox()
        self.pn_font_size.setRange(6, 30)
        self.pn_font_size.setValue(10)
        self.pn_font_size.setFixedWidth(55)
        row1.addWidget(self.pn_font_size)
        tab.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("颜色"))
        self.pn_color = QColorDialog(self)
        self.pn_color_btn = QPushButton()
        self.pn_color_btn.setFixedWidth(50)
        self.pn_color_btn.setStyleSheet(f"background:{DEFAULT_TEXT_COLOR}; border-radius:4px; border:1px solid {COLORS['border']};")
        self.pn_color_btn.clicked.connect(self._choose_pn_color)
        row2.addWidget(self.pn_color_btn)
        row2.addWidget(QLabel("透明度"))
        self.pn_opacity = QDoubleSpinBox()
        self.pn_opacity.setRange(0.1, 1.0)
        self.pn_opacity.setValue(0.7)
        self.pn_opacity.setSingleStep(0.1)
        self.pn_opacity.setFixedWidth(65)
        row2.addWidget(self.pn_opacity)
        row2.addWidget(QLabel("位置"))
        self.pn_position = QComboBox()
        self.pn_position.addItems(["底部居中", "右下角", "底部居中(默认)"])
        self.pn_position.setCurrentText("底部居中")
        row2.addWidget(self.pn_position)
        tab.addLayout(row2)

        style_row = QHBoxLayout()
        style_row.addWidget(QLabel("样式"))
        self.pn_bold = QCheckBox("粗体")
        self.pn_italic = QCheckBox("斜体")
        style_row.addWidget(self.pn_bold)
        style_row.addWidget(self.pn_italic)
        tab.addLayout(style_row)

        btn = QPushButton("✓ 添加页码")
        btn.setStyleSheet(f"""
            QPushButton {{
                background:{COLORS['primary']}; color:white;
                border:none; border-radius:8px; padding:10px 24px; font-size:14px; font-weight:600;
            }}
            QPushButton:hover {{ background:{COLORS['primary_hover']}; }}
        """)
        btn.setFixedHeight(42)
        btn.clicked.connect(self._apply_page_numbers)
        tab.addWidget(btn)

        self.pn_status = QLabel("")
        self.pn_status.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:12px; border:none; background:transparent;")
        self.pn_status.setWordWrap(True)
        tab.addWidget(self.pn_status)
        tab.addStretch()

        widget = QWidget()
        widget.setLayout(tab)
        return widget

    # ---- 构建页脚标签页 ----
    def _build_footer_tab(self):
        tab = QVBoxLayout()
        tab.setSpacing(10)

        lbl = QLabel("页脚文字")
        lbl.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:13px; font-weight:500; border:none; background:transparent;")
        tab.addWidget(lbl)

        self.footer_text = QLineEdit()
        self.footer_text.setPlaceholderText("例如: 机密文件  |  内部资料  |  © 公司名称 2025")
        self.footer_text.setStyleSheet(f"""
            QLineEdit {{
                border:1px solid {COLORS['border']}; border-radius:8px;
                padding:10px 14px; background:white; font-size:13px;
            }}
            QLineEdit:hover {{ border-color:{COLORS['primary']}; }}
            QLineEdit:focus {{ border:1.5px solid {COLORS['primary']}; }}
        """)
        tab.addWidget(self.footer_text)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("字号"))
        self.ft_font_size = QSpinBox()
        self.ft_font_size.setRange(6, 30)
        self.ft_font_size.setValue(10)
        self.ft_font_size.setFixedWidth(55)
        row1.addWidget(self.ft_font_size)
        row1.addWidget(QLabel("颜色"))
        self.ft_color_btn = QPushButton()
        self.ft_color_btn.setFixedWidth(50)
        self.ft_color_btn.setStyleSheet(f"background:{DEFAULT_TEXT_COLOR}; border-radius:4px; border:1px solid {COLORS['border']};")
        self.ft_color_btn.clicked.connect(self._choose_ft_color)
        row1.addWidget(self.ft_color_btn)
        row1.addWidget(QLabel("透明度"))
        self.ft_opacity = QDoubleSpinBox()
        self.ft_opacity.setRange(0.1, 1.0)
        self.ft_opacity.setValue(0.7)
        self.ft_opacity.setSingleStep(0.1)
        self.ft_opacity.setFixedWidth(65)
        row1.addWidget(self.ft_opacity)
        tab.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("位置"))
        self.ft_position = QComboBox()
        self.ft_position.addItems(["底部居中", "右下角"])
        row2.addWidget(self.ft_position)
        row2.addStretch()
        self.ft_bold = QCheckBox("粗体")
        row2.addWidget(self.ft_bold)
        self.ft_italic = QCheckBox("斜体")
        row2.addWidget(self.ft_italic)
        tab.addLayout(row2)

        btn = QPushButton("✓ 添加页脚")
        btn.setStyleSheet(f"""
            QPushButton {{
                background:{COLORS['primary']}; color:white;
                border:none; border-radius:8px; padding:10px 24px; font-size:14px; font-weight:600;
            }}
            QPushButton:hover {{ background:{COLORS['primary_hover']}; }}
        """)
        btn.setFixedHeight(42)
        btn.clicked.connect(self._apply_footer)
        tab.addWidget(btn)

        self.ft_status = QLabel("")
        self.ft_status.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:12px; border:none; background:transparent;")
        self.ft_status.setWordWrap(True)
        tab.addWidget(self.ft_status)
        tab.addStretch()

        widget = QWidget()
        widget.setLayout(tab)
        return widget

    # ---- 构建文本提取标签页 ----
    def _build_extract_tab(self):
        tab = QVBoxLayout()
        tab.setSpacing(10)

        lbl = QLabel("从选中 PDF 提取全部文字内容")
        lbl.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:13px; border:none; background:transparent;")
        tab.addWidget(lbl)

        self.extract_preview = QPlainTextEdit()
        self.extract_preview.setReadOnly(True)
        self.extract_preview.setStyleSheet(f"""
            QPlainTextEdit {{
                background:#2C3E50; color:#B0C4D8; font-family:'Consolas','Monaco',monospace;
                font-size:12px; border-radius:8px; padding:10px; border:1px solid {COLORS['border']};
            }}
        """)
        tab.addWidget(self.extract_preview, stretch=1)

        row = QHBoxLayout()
        self.extract_btn = QPushButton("📋 提取文本")
        self.extract_btn.setStyleSheet(f"""
            QPushButton {{
                background:{COLORS['primary']}; color:white;
                border:none; border-radius:8px; padding:10px 20px; font-size:14px; font-weight:600;
            }}
            QPushButton:hover {{ background:{COLORS['primary_hover']}; }}
        """)
        self.extract_btn.setFixedHeight(42)
        self.extract_btn.clicked.connect(self._extract_text)
        row.addWidget(self.extract_btn)
        row.addStretch()

        self.extract_save = QPushButton("💾 另存为...")
        self.extract_save.setStyleSheet(f"""
            QPushButton {{
                background:{COLORS['accent_light']}; color:{COLORS['accent']};
                border:1px solid {COLORS['border']}; border-radius:8px; padding:8px 18px; font-size:13px; font-weight:600;
            }}
            QPushButton:hover {{ background:{COLORS['accent']}; color:white; }}
        """)
        self.extract_save.clicked.connect(self._save_extracted)
        self._extracted_path = None
        self._extracted_text = ""
        row.addWidget(self.extract_save)
        tab.addLayout(row)

        widget = QWidget()
        widget.setLayout(tab)
        return widget

    # ---- 颜色选择 ----
    def _choose_pn_color(self):
        from PyQt6.QtWidgets import QColorDialog
        dlg = QColorDialog(self.pn_color_btn.palette().color(QColorDialog.ButtonRole.OkButton))
        if dlg.exec():
            self.pn_color_btn.setStyleSheet(f"background:{dlg.currentColor().name()}; border-radius:4px; border:1px solid {COLORS['border']};")

    def _choose_ft_color(self):
        from PyQt6.QtWidgets import QColorDialog
        dlg = QColorDialog(self.ft_color_btn.palette().color(QColorDialog.ButtonRole.OkButton))
        if dlg.exec():
            self.ft_color_btn.setStyleSheet(f"background:{dlg.currentColor().name()}; border-radius:4px; border:1px solid {COLORS['border']};")

    # ---- 执行操作 ----
    def _apply_page_numbers(self):
        """应用页码到所有任务中的 PDF"""
        parent = self.parent()
        if not parent or not hasattr(parent, 'tasks'):
            QMessageBox.warning(self, "提示", "请在主窗口中加载 PDF 任务后使用此工具")
            return

        # 收集有 PDF 路径的任务
        tasks_with_pdf = [(i, t) for i, t in enumerate(parent.tasks) if t.get('pdf_path') and os.path.exists(t['pdf_path'])]
        if not tasks_with_pdf:
            QMessageBox.warning(self, "提示", "当前没有有效的 PDF 文件")
            return

        if not self.output_dir:
            self.output_dir = os.path.join(os.getcwd(), "pdf_tools_output")

        results = []
        start_num = self.start_num.value()
        font_size = self.pn_font_size.value()
        text_color = self.pn_color_btn.styleSheet().split("background:")[1].split(";")[0] if "background:" in self.pn_color_btn.styleSheet() else DEFAULT_TEXT_COLOR
        text_color = text_color.strip()
        if not text_color.startswith("#"):
            text_color = f"#{text_color}"
        opacity = self.pn_opacity.value()
        position = self.pn_position.currentText()
        if position == "底部居中(默认)":
            position = "底部居中"

        for idx, task in tasks_with_pdf:
            try:
                out_paths = add_page_numbers(
                    task['pdf_path'], self.output_dir,
                    start_num=start_num, font_size=font_size,
                    text_color=text_color, position=position,
                    opacity=opacity, bold=self.pn_bold.isChecked(),
                    italic=self.pn_italic.isChecked()
                )
                if out_paths:
                    results.append((task['filename'], out_paths[0]))
            except Exception as e:
                diag_log(f"  添加页码失败 [{task['filename']}]: {e}")

        if results:
            self.pn_status.setText(f"✓ 完成 {len(results)} 个 PDF  →  {self.output_dir}")
            parent.log(f"PDF 工具: 为 {len(results)} 个 PDF 添加了页码")
        else:
            self.pn_status.setText("⚠ 全部失败")

    def _apply_footer(self):
        """应用页脚到所有任务中的 PDF"""
        parent = self.parent()
        if not parent or not hasattr(parent, 'tasks'):
            QMessageBox.warning(self, "提示", "请在主窗口中加载 PDF 任务后使用此工具")
            return

        tasks_with_pdf = [(i, t) for i, t in enumerate(parent.tasks) if t.get('pdf_path') and os.path.exists(t['pdf_path'])]
        if not tasks_with_pdf:
            QMessageBox.warning(self, "提示", "当前没有有效的 PDF 文件")
            return

        footer_text = self.footer_text.text().strip()
        if not footer_text:
            QMessageBox.warning(self, "提示", "请输入页脚文字")
            return

        if not self.output_dir:
            self.output_dir = os.path.join(os.getcwd(), "pdf_tools_output")

        results = []
        font_size = self.ft_font_size.value()
        text_color = self.ft_color_btn.styleSheet().split("background:")[1].split(";")[0] if "background:" in self.ft_color_btn.styleSheet() else DEFAULT_TEXT_COLOR
        text_color = text_color.strip()
        if not text_color.startswith("#"):
            text_color = f"#{text_color}"
        opacity = self.ft_opacity.value()
        position = self.ft_position.currentText()

        for idx, task in tasks_with_pdf:
            try:
                out_paths = add_footer(
                    task['pdf_path'], self.output_dir,
                    footer_text=footer_text, font_size=font_size,
                    text_color=text_color, position=position,
                    opacity=opacity, bold=self.ft_bold.isChecked(),
                    italic=self.ft_italic.isChecked()
                )
                if out_paths:
                    results.append((task['filename'], out_paths[0]))
            except Exception as e:
                diag_log(f"  添加页脚失败 [{task['filename']}]: {e}")

        if results:
            self.ft_status.setText(f"✓ 完成 {len(results)} 个 PDF  →  {self.output_dir}")
            parent.log(f"PDF 工具: 为 {len(results)} 个 PDF 添加了页脚: '{footer_text}'")
        else:
            self.ft_status.setText("⚠ 全部失败")

    def _extract_text(self):
        """从选中的 PDF 提取文本"""
        parent = self.parent()
        selected_row = None
        if parent and hasattr(parent, 'table'):
            sel = parent.table.selectionModel().selectedRows()
            if sel:
                selected_row = sel[0].row()

        if selected_row is not None and selected_row < len(parent.tasks):
            task = parent.tasks[selected_row]
            pdf_path = task.get('pdf_path')
            if not pdf_path or not os.path.exists(pdf_path):
                QMessageBox.warning(self, "提示", "请先选择有效的 PDF 文件")
                return
            try:
                text, path = extract_text(pdf_path)
                self._extracted_text = text
                self._extracted_path = path
                self.extract_preview.setPlainText(text[:5000] + ("..." if len(text) > 5000 else ""))
                parent.log(f"文本提取: {path}")
            except Exception as e:
                QMessageBox.warning(self, "提示", f"提取失败: {e}")
                self.extract_preview.setPlainText(f"提取失败: {e}")
        else:
            QMessageBox.warning(self, "提示", "请在主窗口表格中选中要提取文本的 PDF 行")

    def _save_extracted(self):
        if not self._extracted_text:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "保存提取文本",
            self._extracted_path or "提取文本.txt",
            "文本文件 (*.txt);;Excel 文件 (*.xlsx);;所有文件 (*.*)"
        )
        if path:
            try:
                if path.lower().endswith('.xlsx'):
                    import openpyxl
                    wb = openpyxl.Workbook()
                    ws = wb.active
                    ws.title = "提取文本"
                    for i, line in enumerate(self._extracted_text.splitlines(), 1):
                        ws.cell(row=i, column=1, value=line)
                    wb.save(path)
                else:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(self._extracted_text)
                self.log(f"已保存: {path}")
            except Exception as e:
                QMessageBox.warning(self, "保存失败", str(e))
