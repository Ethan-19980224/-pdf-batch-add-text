"""PDF 增强工具对话框 - 图片水印 / 页面旋转 / PDF加密"""
import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QLineEdit, QFileDialog,
    QMessageBox, QDoubleSpinBox, QTabWidget,
    QCheckBox, QPlainTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QCursor

from ..config import COLORS, DEFAULT_OPACITY, POSITIONS
from ..pdf.tools2 import add_image_watermark, rotate_pdf, encrypt_pdf
from ..logger import diag_log


class PDFAdvancedDialog(QDialog):
    """PDF 增强工具对话框 — 图片水印 / 页面旋转 / PDF加密"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF 增强工具")
        self.setMinimumSize(520, 520)
        self.resize(560, 560)
        self.output_dir = ""
        self.parent_window = parent
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("PDF 增强工具")
        title.setFont(QFont("", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{COLORS['text']}; border:none; background:transparent;")
        layout.addWidget(title)

        desc = QLabel("为 PDF 添加图片水印、旋转页面或添加密码保护")
        desc.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:12px; border:none; background:transparent;")
        layout.addWidget(desc)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, stretch=1)

        # Tab 1: 图片水印
        self.tab_img_wm = self._build_image_watermark_tab()
        self.tabs.addTab(self.tab_img_wm, "🖼️ 图片水印")

        # Tab 2: 页面旋转
        self.tab_rotate = self._build_rotate_tab()
        self.tabs.addTab(self.tab_rotate, "🔄 页面旋转")

        # Tab 3: PDF加密
        self.tab_encrypt = self._build_encrypt_tab()
        self.tabs.addTab(self.tab_encrypt, "🔒 PDF加密")

    def _build_image_watermark_tab(self):
        tab = QVBoxLayout()
        tab.setSpacing(10)

        lbl = QLabel("选择水印图片")
        lbl.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:13px; border:none; background:transparent;")
        tab.addWidget(lbl)

        img_layout = QHBoxLayout()
        self.img_path = QLineEdit()
        self.img_path.setPlaceholderText("请选择图片文件...")
        self.img_path.setStyleSheet(f"""
            QLineEdit {{ border:1px solid {COLORS['border']}; border-radius:8px;
            padding:8px 12px; background:white; font-size:13px; }}
        """)
        self.img_path.setReadOnly(True)
        img_layout.addWidget(self.img_path, stretch=1)
        self.img_browse = QPushButton("浏览...")
        self.img_browse.setStyleSheet(f"""
            QPushButton {{ background:{COLORS['accent_light']}; color:{COLORS['accent']};
            border:1px solid {COLORS['border']}; border-radius:6px; padding:6px 12px; }}
            QPushButton:hover {{ background:{COLORS['accent']}; color:white; }}
        """)
        self.img_browse.clicked.connect(self._browse_image)
        img_layout.addWidget(self.img_browse)
        tab.addLayout(img_layout)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("透明度"))
        self.wm_opacity = QDoubleSpinBox()
        self.wm_opacity.setRange(0.1, 1.0)
        self.wm_opacity.setValue(0.5)
        self.wm_opacity.setSingleStep(0.1)
        self.wm_opacity.setFixedWidth(65)
        row1.addWidget(self.wm_opacity)
        row1.addWidget(QLabel("缩放"))
        self.wm_scale = QDoubleSpinBox()
        self.wm_scale.setRange(0.1, 5.0)
        self.wm_scale.setValue(1.0)
        self.wm_scale.setSingleStep(0.1)
        self.wm_scale.setFixedWidth(65)
        row1.addWidget(self.wm_scale)
        tab.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("位置"))
        self.wm_position = QComboBox()
        self.wm_position.addItems(["居中", "左上角", "右上角", "左下角", "右下角"])
        self.wm_position.setCurrentText("居中")
        row2.addWidget(self.wm_position)
        row2.addStretch()
        self.wm_repeat = QCheckBox("每页重复")
        self.wm_repeat.setChecked(True)
        row2.addWidget(self.wm_repeat)
        tab.addLayout(row2)

        btn = QPushButton("✓ 添加水印")
        btn.setStyleSheet(f"""
            QPushButton {{ background:{COLORS['primary']}; color:white;
            border:none; border-radius:8px; padding:10px 24px; font-size:14px; font-weight:600; }}
            QPushButton:hover {{ background:{COLORS['primary_hover']}; }}
        """)
        btn.setFixedHeight(42)
        btn.clicked.connect(self._apply_image_watermark)
        tab.addWidget(btn)

        self.wm_status = QLabel("")
        self.wm_status.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:12px; border:none; background:transparent;")
        self.wm_status.setWordWrap(True)
        tab.addWidget(self.wm_status)
        tab.addStretch()

        widget = QWidget()
        widget.setLayout(tab)
        return widget

    def _build_rotate_tab(self):
        tab = QVBoxLayout()
        tab.setSpacing(10)

        lbl = QLabel("旋转所有 PDF 的页面方向")
        lbl.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:13px; border:none; background:transparent;")
        tab.addWidget(lbl)

        row = QHBoxLayout()
        row.addWidget(QLabel("旋转角度"))
        self.rotate_angle = QComboBox()
        self.rotate_angle.addItems(["90° 顺时针", "180° 翻转", "270° 逆时针"])
        self.rotate_angle.setCurrentText("90° 顺时针")
        row.addWidget(self.rotate_angle)
        tab.addLayout(row)

        page_row = QHBoxLayout()
        page_row.addWidget(QLabel("页码范围"))
        self.rotate_range = QLineEdit()
        self.rotate_range.setPlaceholderText("留空=全部页面")
        self.rotate_range.setFixedWidth(200)
        self.rotate_range.setStyleSheet(f"""
            QLineEdit {{ border:1px solid {COLORS['border']}; border-radius:8px;
            padding:6px 10px; font-size:13px; }}
        """)
        page_row.addWidget(self.rotate_range, stretch=1)
        tab.addLayout(page_row)

        btn = QPushButton("✓ 旋转")
        btn.setStyleSheet(f"""
            QPushButton {{ background:{COLORS['primary']}; color:white;
            border:none; border-radius:8px; padding:10px 24px; font-size:14px; font-weight:600; }}
            QPushButton:hover {{ background:{COLORS['primary_hover']}; }}
        """)
        btn.setFixedHeight(42)
        btn.clicked.connect(self._apply_rotate)
        tab.addWidget(btn)

        self.rotate_status = QLabel("")
        self.rotate_status.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:12px; border:none; background:transparent;")
        self.rotate_status.setWordWrap(True)
        tab.addWidget(self.rotate_status)
        tab.addStretch()

        widget = QWidget()
        widget.setLayout(tab)
        return widget

    def _build_encrypt_tab(self):
        tab = QVBoxLayout()
        tab.setSpacing(10)

        lbl = QLabel("为 PDF 添加密码保护")
        lbl.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:13px; border:none; background:transparent;")
        tab.addWidget(lbl)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("用户密码"))
        self.enc_user_pw = QLineEdit()
        self.enc_user_pw.setPlaceholderText("输入密码（可选，无则可直接打开）")
        self.enc_user_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.enc_user_pw.setStyleSheet(f"""
            QLineEdit {{ border:1px solid {COLORS['border']}; border-radius:8px;
            padding:6px 10px; font-size:13px; }}
        """)
        row1.addWidget(self.enc_user_pw, stretch=1)
        tab.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("所有者密码"))
        self.enc_owner_pw = QLineEdit()
        self.enc_owner_pw.setPlaceholderText("用于修改权限")
        self.enc_owner_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.enc_owner_pw.setStyleSheet(self.enc_user_pw.styleSheet())
        row2.addWidget(self.enc_owner_pw, stretch=1)
        tab.addLayout(row2)

        perm_lbl = QLabel("权限控制")
        perm_lbl.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:13px; font-weight:500; border:none; background:transparent;")
        tab.addWidget(perm_lbl)

        perms = [
            ("🖨️", "允许打印", "can_print"),
            ("✏️", "允许修改", "can_modify"),
            ("📋", "允许复制", "can_copy"),
            ("💬", "允许批注", "can_notes"),
        ]
        self.perm_checkboxes = {}
        for icon, label, key in perms:
            cb = QCheckBox(f"{icon} {label}")
            cb.setChecked(key == "can_print")  # 默认只允许打印
            self.perm_checkboxes[key] = cb
            tab.addWidget(cb)

        # 取消全部权限
        deny_all_btn = QPushButton("全部禁止（仅查看）")
        deny_all_btn.setStyleSheet(f"""
            QPushButton {{ background:{COLORS['danger_light']}; color:{COLORS['danger']};
            border:1px solid {COLORS['border']}; border-radius:6px; padding:6px 14px; font-size:12px; }}
            QPushButton:hover {{ background:{COLORS['danger']}; color:white; }}
        """)
        deny_all_btn.clicked.connect(lambda: self._set_all_perms(False))
        tab.addWidget(deny_all_btn)

        btn = QPushButton("✓ 加密")
        btn.setStyleSheet(f"""
            QPushButton {{ background:{COLORS['primary']}; color:white;
            border:none; border-radius:8px; padding:10px 24px; font-size:14px; font-weight:600; }}
            QPushButton:hover {{ background:{COLORS['primary_hover']}; }}
        """)
        btn.setFixedHeight(42)
        btn.clicked.connect(self._apply_encrypt)
        tab.addWidget(btn)

        self.enc_status = QLabel("")
        self.enc_status.setStyleSheet(f"color:{COLORS['text_secondary']}; font-size:12px; border:none; background:transparent;")
        self.enc_status.setWordWrap(True)
        tab.addWidget(self.enc_status)
        tab.addStretch()

        widget = QWidget()
        widget.setLayout(tab)
        return widget

    # ---- 事件处理 ----
    def _browse_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择水印图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif);;所有文件 (*.*)"
        )
        if path:
            self.img_path.setText(path)

    def _get_task_pdfs(self):
        """获取当前任务的 PDF 路径列表"""
        if self.parent_window and hasattr(self.parent_window, 'tasks'):
            return [t['pdf_path'] for t in self.parent_window.tasks
                    if t.get('pdf_path') and os.path.exists(t['pdf_path'])]
        return []

    def _get_output_dir(self):
        if not self.output_dir:
            self.output_dir = os.path.join(os.getcwd(), "pdf_tools_output")
        return self.output_dir

    def _apply_image_watermark(self):
        img_path = self.img_path.text().strip()
        if not img_path:
            QMessageBox.warning(self, "提示", "请选择水印图片文件")
            return
        if not os.path.exists(img_path):
            QMessageBox.warning(self, "提示", f"图片文件不存在:\n{img_path}")
            return

        pdfs = self._get_task_pdfs()
        if not pdfs:
            QMessageBox.warning(self, "提示", "当前没有有效的 PDF 文件")
            return

        output_dir = self._get_output_dir()
        opacity = self.wm_opacity.value()
        scale = self.wm_scale.value()
        position = self.wm_position.currentText()

        results = []
        for pdf_path in pdfs:
            try:
                outs = add_image_watermark(
                    pdf_path, img_path, output_dir,
                    opacity=opacity, x_scale=scale, y_scale=scale,
                    position=position
                )
                if outs:
                    results.append((os.path.basename(pdf_path), outs[0]))
            except Exception as e:
                diag_log(f"  图片水印失败 [{os.path.basename(pdf_path)}]: {e}")

        if results:
            self.wm_status.setText(f"✓ 完成 {len(results)} 个 PDF → {output_dir}")
            self.parent_window.log(f"图片水印: 为 {len(results)} 个 PDF 添加了水印")
        else:
            self.wm_status.setText("⚠ 全部失败")

    def _apply_rotate(self):
        angle_map = {
            "90° 顺时针": 90,
            "180° 翻转": 180,
            "270° 逆时针": 270,
        }
        angle = angle_map.get(self.rotate_angle.currentText(), 90)
        range_str = self.rotate_range.text().strip()

        pdfs = self._get_task_pdfs()
        if not pdfs:
            QMessageBox.warning(self, "提示", "当前没有有效的 PDF 文件")
            return

        output_dir = self._get_output_dir()
        results = []
        for pdf_path in pdfs:
            try:
                outs = rotate_pdf(pdf_path, output_dir, angle, page_range=range_str)
                if outs:
                    results.append((os.path.basename(pdf_path), outs[0]))
            except Exception as e:
                diag_log(f"  PDF旋转失败 [{os.path.basename(pdf_path)}]: {e}")

        if results:
            self.rotate_status.setText(f"✓ 完成 {len(results)} 个 PDF ({angle}°) → {output_dir}")
            self.parent_window.log(f"页面旋转: 为 {len(results)} 个 PDF 旋转了 {angle}°")
        else:
            self.rotate_status.setText("⚠ 全部失败")

    def _apply_encrypt(self):
        user_pw = self.enc_user_pw.text()
        owner_pw = self.enc_owner_pw.text()

        if not user_pw and not owner_pw:
            QMessageBox.warning(self, "提示", "请至少设置一个密码")
            return

        perms = {k: cb.isChecked() for k, cb in self.perm_checkboxes.items()}

        pdfs = self._get_task_pdfs()
        if not pdfs:
            QMessageBox.warning(self, "提示", "当前没有有效的 PDF 文件")
            return

        output_dir = self._get_output_dir()
        results = []
        for pdf_path in pdfs:
            try:
                outs = encrypt_pdf(pdf_path, output_dir, owner_pw or user_pw, user_pw or owner_pw, perms)
                if outs:
                    results.append((os.path.basename(pdf_path), outs[0]))
            except Exception as e:
                diag_log(f"  PDF加密失败 [{os.path.basename(pdf_path)}]: {e}")

        if results:
            self.enc_status.setText(f"✓ 完成 {len(results)} 个 PDF → {output_dir}")
            self.parent_window.log(f"PDF加密: 为 {len(results)} 个 PDF 添加了密码保护")
        else:
            self.enc_status.setText("⚠ 全部失败")

    def _set_all_perms(self, value):
        for cb in self.perm_checkboxes.values():
            cb.setChecked(value)

    def log(self, msg):
        if self.parent_window:
            self.parent_window.log(msg)
