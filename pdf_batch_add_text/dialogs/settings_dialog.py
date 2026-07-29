"""文字样式设置对话框"""
import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QFrame, QGridLayout, QHBoxLayout,
    QPushButton, QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit, QCheckBox,
    QColorDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QCursor

from ..config import (
    COLORS, POSITIONS, DEFAULT_FONT_SIZE, DEFAULT_TEXT_COLOR, DEFAULT_POSITION
)


class SettingsDialog(QDialog):
    """文字样式设置对话框"""

    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle("文字样式设置")
        self.setMinimumWidth(400)
        self.settings = settings or {}
        self.current_color = settings.get('color', DEFAULT_TEXT_COLOR) if settings else DEFAULT_TEXT_COLOR
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(28, 24, 28, 24)

        title = QLabel("文字样式设置")
        title.setFont(QFont("", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text']}; border:none; background:transparent;")
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {COLORS['border']}; max-height:1px;")
        layout.addWidget(line)

        form = QGridLayout()
        form.setSpacing(14)
        form.setColumnStretch(1, 1)

        row = 0
        # 字体大小
        lbl_font = QLabel("字体大小")
        lbl_font.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:13px;border:none;background:transparent;")
        form.addWidget(lbl_font, row, 0)
        self.font_size = QSpinBox()
        self.font_size.setRange(6, 200)
        self.font_size.setValue(DEFAULT_FONT_SIZE)
        self.font_size.setFixedWidth(120)
        self.font_size.setMinimumHeight(32)
        self.font_size.setObjectName("dlgSpinbox")
        self.font_size.setToolTip("设置添加文字的字体大小 (6-200pt)")
        form.addWidget(self.font_size, row, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        row += 1

        # 文字颜色
        lbl_color = QLabel("文字颜色")
        lbl_color.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:13px;border:none;background:transparent;")
        form.addWidget(lbl_color, row, 0)
        color_row = QHBoxLayout()
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(44, 30)
        self.color_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.color_btn.clicked.connect(self.choose_color)
        self.color_btn.setToolTip("点击选择文字颜色")
        self.update_color_button()
        color_row.addWidget(self.color_btn)
        color_row.addStretch()
        form.addLayout(color_row, row, 1)
        row += 1

        # 位置
        lbl_pos = QLabel("默认位置")
        lbl_pos.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:13px;border:none;background:transparent;")
        form.addWidget(lbl_pos, row, 0)
        self.position = QComboBox()
        self.position.addItems(list(POSITIONS.keys()))
        self.position.setCurrentText(DEFAULT_POSITION)
        self.position.setMinimumHeight(32)
        self.position.setObjectName("dlgCombo")
        self.position.setToolTip("选择文字在 PDF 页面中的默认添加位置")
        form.addWidget(self.position, row, 1)
        row += 1

        # 透明度
        lbl_op = QLabel("透明度")
        lbl_op.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:13px;border:none;background:transparent;")
        form.addWidget(lbl_op, row, 0)
        self.opacity = QDoubleSpinBox()
        self.opacity.setRange(0.1, 1.0)
        self.opacity.setSingleStep(0.1)
        self.opacity.setValue(1.0)
        self.opacity.setFixedWidth(120)
        self.opacity.setMinimumHeight(32)
        self.opacity.setObjectName("dlgSpinbox")
        self.opacity.setToolTip("文字透明度，1.0 为完全不透明，0.1 为几乎透明")
        form.addWidget(self.opacity, row, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        row += 1

        # 偏移
        lbl_off = QLabel("位置偏移")
        lbl_off.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:13px;border:none;background:transparent;")
        form.addWidget(lbl_off, row, 0)
        off_row = QHBoxLayout()
        self.offset_x = QSpinBox()
        self.offset_x.setRange(-500, 500)
        self.offset_x.setValue(0)
        self.offset_x.setFixedWidth(90)
        self.offset_x.setMinimumHeight(32)
        self.offset_x.setToolTip("水平偏移（正值右移，负值左移）")
        self.offset_y = QSpinBox()
        self.offset_y.setRange(-500, 500)
        self.offset_y.setValue(0)
        self.offset_y.setFixedWidth(90)
        self.offset_y.setMinimumHeight(32)
        self.offset_y.setToolTip("垂直偏移（正值上移，负值下移）")
        off_row.addWidget(QLabel("X:"))
        off_row.addWidget(self.offset_x)
        off_row.addSpacing(10)
        off_row.addWidget(QLabel("Y:"))
        off_row.addWidget(self.offset_y)
        off_row.addStretch()
        form.addLayout(off_row, row, 1)
        row += 1

        # 页码范围
        lbl_page = QLabel("页码范围")
        lbl_page.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:13px;border:none;background:transparent;")
        form.addWidget(lbl_page, row, 0)
        self.page_range = QLineEdit()
        self.page_range.setPlaceholderText("全部 或 1,3,5-10")
        self.page_range.setMinimumHeight(32)
        self.page_range.setObjectName("dlgEdit")
        self.page_range.setToolTip("指定添加文字的页码，如 1,3,5-10；留空则添加到所有页")
        form.addWidget(self.page_range, row, 1)
        row += 1

        # 样式
        lbl_style = QLabel("文字样式")
        lbl_style.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:13px;border:none;background:transparent;")
        form.addWidget(lbl_style, row, 0)
        style_row = QHBoxLayout()
        self.bold = QCheckBox("粗体")
        self.bold.setStyleSheet(f"color:{COLORS['text']};font-size:13px;border:none;background:transparent;")
        self.bold.setToolTip("使用粗体字重")
        self.italic = QCheckBox("斜体")
        self.italic.setStyleSheet(f"color:{COLORS['text']};font-size:13px;border:none;background:transparent;")
        self.italic.setToolTip("使用斜体样式")
        style_row.addWidget(self.bold)
        style_row.addWidget(self.italic)
        style_row.addStretch()
        form.addLayout(style_row, row, 1)

        layout.addLayout(form)
        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("dlgCancelBtn")
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        ok_btn = QPushButton("保存")
        ok_btn.setObjectName("dlgOkBtn")
        ok_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg']};
            }}
            QLineEdit#dlgEdit {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 6px 12px;
                background-color: white;
                color: {COLORS['text']};
                font-size: 13px;
            }}
            QLineEdit#dlgEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
            QComboBox#dlgCombo {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 6px 12px;
                background-color: white;
                color: {COLORS['text']};
                font-size: 13px;
            }}
            QComboBox#dlgCombo:focus {{
                border: 2px solid {COLORS['primary']};
            }}
            QSpinBox#dlgSpinbox, QDoubleSpinBox#dlgSpinbox {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 6px 8px;
                background-color: white;
                color: {COLORS['text']};
                font-size: 13px;
            }}
            QPushButton#dlgCancelBtn {{
                background-color: {COLORS['border_light']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton#dlgCancelBtn:hover {{
                background-color: {COLORS['border']};
            }}
            QPushButton#dlgOkBtn {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton#dlgOkBtn:hover {{
                background-color: {COLORS['primary_hover']};
            }}
        """)

    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.current_color), self)
        if color.isValid():
            self.current_color = color.name()
            self.update_color_button()

    def update_color_button(self):
        self.color_btn.setStyleSheet(
            f"background-color: {self.current_color}; "
            f"border-radius: 6px; border: 2px solid {COLORS['border']};"
        )

    def load_settings(self):
        self.font_size.setValue(self.settings.get('font_size', DEFAULT_FONT_SIZE))
        self.current_color = self.settings.get('color', DEFAULT_TEXT_COLOR)
        self.update_color_button()
        self.position.setCurrentText(self.settings.get('position', DEFAULT_POSITION))
        self.opacity.setValue(self.settings.get('opacity', 1.0))
        self.bold.setChecked(self.settings.get('bold', False))
        self.italic.setChecked(self.settings.get('italic', False))
        self.page_range.setText(self.settings.get('page_range', ''))
        self.offset_x.setValue(self.settings.get('offset_x', 0))
        self.offset_y.setValue(self.settings.get('offset_y', 0))

    def get_settings(self):
        return {
            'font_size': self.font_size.value(),
            'color': self.current_color,
            'position': self.position.currentText(),
            'opacity': self.opacity.value(),
            'bold': self.bold.isChecked(),
            'italic': self.italic.isChecked(),
            'page_range': self.page_range.text(),
            'offset_x': self.offset_x.value(),
            'offset_y': self.offset_y.value(),
        }
