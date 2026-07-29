"""依赖检查和图标创建"""
import os
import sys

from ..config import FITZ_AVAILABLE, OPENPYXL_AVAILABLE
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QPen, QBrush, QLinearGradient
from PyQt6.QtCore import QPointF, Qt


def ensure_dependencies():
    """检查必需依赖是否可用"""
    missing = []
    if not FITZ_AVAILABLE:
        missing.append("PyMuPDF")
    if not OPENPYXL_AVAILABLE:
        missing.append("openpyxl")
    if missing:
        return f"缺少依赖库: {', '.join(missing)}\n\n请运行: pip install {' '.join(missing)}"
    return None


def create_app_icon():
    """创建应用图标"""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    gradient = QLinearGradient(0, 0, 64, 64)
    gradient.setColorAt(0, QColor("#5B9BD5"))
    gradient.setColorAt(1, QColor("#4A8BC2"))
    painter.setBrush(QBrush(gradient))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(2, 2, 60, 60, 12, 12)

    painter.setBrush(QBrush(QColor("white")))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(14, 10, 36, 44, 3, 3)

    painter.setPen(QPen(QColor("#5B9BD5")))
    font = QFont("Arial", 8, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(14, 22, 36, 12, Qt.AlignmentFlag.AlignCenter, "PDF")

    painter.setPen(QPen(QColor("#CCCCCC"), 1.5))
    for y in [32, 38, 44]:
        painter.drawLine(20, y, 44, y)

    painter.setBrush(QBrush(QColor("#34C759")))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(QPointF(48, 48), 8, 8)

    painter.setPen(QPen(QColor("white"), 2))
    painter.drawLine(45, 48, 51, 48)
    painter.drawLine(48, 45, 48, 51)

    painter.end()
    return QIcon(pixmap)
