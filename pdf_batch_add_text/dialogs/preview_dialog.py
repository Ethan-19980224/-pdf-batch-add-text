"""PDF 预览对话框 - 内嵌渲染页面并叠加文字"""
import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSpinBox, QComboBox, QColorDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QFont, QColor, QPen, QPainter, QPixmap, QImage,
)

from ..config import (
    COLORS, POSITIONS, DEFAULT_FONT_SIZE, DEFAULT_TEXT_COLOR, DEFAULT_POSITION
)
from ..logger import diag_log
from ..utils.fonts import find_cjk_font
import fitz


class PdfPreviewDialog(QDialog):
    """内嵌 PDF 预览对话框，直接在界面中渲染页面并叠加文字"""

    def __init__(self, pdf_path, text, text_settings, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.text = text
        self.text_settings = text_settings.copy()
        self.current_page = 0
        self.total_pages = 0
        self.doc = None
        self.setWindowTitle(f"PDF 预览 - {os.path.basename(pdf_path)}")
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)
        self.setup_ui()
        self.load_pdf()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # 顶部工具栏
        toolbar = QHBoxLayout()

        self.prev_btn = QPushButton("◀ 上一页")
        self.prev_btn.setStyleSheet(f"""
            QPushButton {{ background:{COLORS['primary_light']}; color:{COLORS['primary']};
            border:1px solid {COLORS['border']}; border-radius:6px; padding:6px 14px; font-weight:600; }}
            QPushButton:hover {{ background:{COLORS['primary']}; color:white; border-color:{COLORS['primary']}; }}
        """)
        self.prev_btn.clicked.connect(self.prev_page)
        toolbar.addWidget(self.prev_btn)

        self.page_label = QLabel("第 0/0 页")
        self.page_label.setStyleSheet(f"color:{COLORS['text']}; font-size:13px; font-weight:600; border:none; background:transparent;")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toolbar.addWidget(self.page_label)

        self.next_btn = QPushButton("下一页 ▶")
        self.next_btn.setStyleSheet(self.prev_btn.styleSheet())
        self.next_btn.clicked.connect(self.next_page)
        toolbar.addWidget(self.next_btn)

        toolbar.addStretch()

        # 文字设置快捷调整
        toolbar.addWidget(QLabel("字号:"))
        self.preview_font_size = QSpinBox()
        self.preview_font_size.setRange(6, 200)
        self.preview_font_size.setValue(self.text_settings.get('font_size', DEFAULT_FONT_SIZE))
        self.preview_font_size.setFixedWidth(60)
        self.preview_font_size.valueChanged.connect(self.refresh_preview)
        toolbar.addWidget(self.preview_font_size)

        toolbar.addWidget(QLabel("位置:"))
        self.preview_position = QComboBox()
        self.preview_position.addItems(list(POSITIONS.keys()))
        self.preview_position.setCurrentText(self.text_settings.get('position', DEFAULT_POSITION))
        self.preview_position.currentTextChanged.connect(self.refresh_preview)
        toolbar.addWidget(self.preview_position)

        self.preview_color_btn = QPushButton("颜色")
        self.preview_color_btn.setFixedWidth(60)
        self.preview_color_btn.setStyleSheet(f"""
            background-color:{self.text_settings.get('color', DEFAULT_TEXT_COLOR)};
            border-radius:4px; border:1px solid {COLORS['border']};
        """)
        self.preview_color_btn.clicked.connect(self.choose_preview_color)
        toolbar.addWidget(self.preview_color_btn)

        layout.addLayout(toolbar)

        # 页面显示区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(f"QScrollArea{{border:1px solid {COLORS['border']};border-radius:8px;background:{COLORS['bg']};}}")

        self.page_container = QLabel()
        self.page_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_container.setStyleSheet("background:white;")
        self.scroll_area.setWidget(self.page_container)
        layout.addWidget(self.scroll_area, stretch=1)

        # 底部状态
        status_layout = QHBoxLayout()
        status_info = QLabel("实时预览：调整上方参数后自动刷新")
        status_info.setStyleSheet(f"color:{COLORS['text_muted']}; font-size:11px; border:none; background:transparent;")
        status_layout.addWidget(status_info)
        status_layout.addStretch()

        self.close_btn = QPushButton("关闭预览")
        self.close_btn.setStyleSheet(f"""
            QPushButton {{ background:{COLORS['primary']}; color:white; border:none;
            border-radius:8px; padding:8px 24px; font-weight:600; }}
            QPushButton:hover {{ background:{COLORS['primary_hover']}; }}
        """)
        self.close_btn.clicked.connect(self.accept)
        status_layout.addWidget(self.close_btn)

        layout.addLayout(status_layout)

    def load_pdf(self):
        try:
            self.doc = fitz.open(self.pdf_path)
            self.total_pages = len(self.doc)
            if self.total_pages == 0:
                raise ValueError("PDF 没有页面")
            self.page_label.setText(f"第 1/{self.total_pages} 页")
            self.refresh_preview()
        except Exception as e:
            QMessageBox.warning(self, "打开失败", f"无法打开 PDF:\n{e}")
            self.reject()

    def refresh_preview(self):
        if not self.doc or self.current_page < 0 or self.current_page >= self.total_pages:
            return

        try:
            self.text_settings['font_size'] = self.preview_font_size.value()
            self.text_settings['position'] = self.preview_position.currentText()

            page = self.doc[self.current_page]

            # 渲染页面为图片
            zoom = 1.5
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, colorspace="rgb")
            img_data = pix.tobytes("ppm")

            image = QImage.fromData(img_data, "PPM")

            # 在图片上绘制文字
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

            # 计算文字位置（与 ProcessWorker 一致）
            s = self.text_settings
            font_size = s.get('font_size', DEFAULT_FONT_SIZE) * zoom
            color_hex = s.get('color', DEFAULT_TEXT_COLOR)
            position = s.get('position', DEFAULT_POSITION)
            opacity = s.get('opacity', 1.0)
            offset_x = s.get('offset_x', 0) * zoom
            offset_y = s.get('offset_y', 0) * zoom

            try:
                r_val = int(color_hex[1:3], 16)
                g_val = int(color_hex[3:5], 16)
                b_val = int(color_hex[5:7], 16)
            except (ValueError, IndexError):
                r_val, g_val, b_val = 239, 68, 68

            text_color = QColor(r_val, g_val, b_val)

            page_rect = page.rect
            pw = page_rect.width * zoom
            ph = page_rect.height * zoom

            # 估算文字宽度
            try:
                font_file = find_cjk_font()
                text_w = fitz.get_text_length(
                    self.text, fontname="cjkfont" if font_file else "helv",
                    fontfile=font_file,
                    fontsize=font_size / zoom
                ) * zoom
            except Exception:
                text_w = len(self.text) * font_size * 0.6

            margin = font_size * 0.5

            if position == "智能自动":
                x = pw - text_w - margin
                y = ph - margin
            else:
                px, py = POSITIONS.get(position, (0.95, 0.05))
                if isinstance(px, str):
                    px, py = 0.95, 0.05
                if 0.45 <= px <= 0.55:
                    x = (pw - text_w) / 2
                elif px >= 0.5:
                    x = pw * px - text_w
                else:
                    x = pw * px
                x = max(margin, min(x, pw - text_w - margin))
                x += offset_x
                raw_y = ph * (1 - py)
                y = max(raw_y, font_size + margin)
                y = min(y, ph - margin)
                y -= offset_y

            x = max(2, min(x, pw - 2))
            y = max(font_size, min(y, ph - 2))

            painter.setOpacity(opacity)

            font = QFont("PingFang SC", int(font_size * 0.75))
            painter.setFont(font)
            painter.setPen(QPen(text_color))
            painter.drawText(int(x), int(y), self.text)

            painter.end()

            # 显示
            pixmap = QPixmap.fromImage(image)
            scaled = pixmap.scaled(
                self.scroll_area.viewport().width() - 20,
                self.scroll_area.viewport().height() - 20,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.page_container.setPixmap(scaled)

        except Exception as e:
            self.page_container.setText(f"渲染失败: {e}")
            diag_log(f"预览渲染失败: {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.refresh_preview()

    def choose_preview_color(self):
        current = self.text_settings.get('color', DEFAULT_TEXT_COLOR)
        color = QColorDialog.getColor(QColor(current), self)
        if color.isValid():
            self.text_settings['color'] = color.name()
            self.preview_color_btn.setStyleSheet(
                f"background-color:{color.name()}; border-radius:4px; border:1px solid {COLORS['border']};"
            )
            self.refresh_preview()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.page_label.setText(f"第 {self.current_page+1}/{self.total_pages} 页")
            self.refresh_preview()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.page_label.setText(f"第 {self.current_page+1}/{self.total_pages} 页")
            self.refresh_preview()

    def closeEvent(self, event):
        if self.doc:
            self.doc.close()
        super().closeEvent(event)
