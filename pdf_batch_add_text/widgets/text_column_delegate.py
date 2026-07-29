"""表格委托 - 仅允许编辑"添加文字"列，状态列根据选中状态自动切换颜色"""
from PyQt6.QtWidgets import QStyledItemDelegate, QStyle, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPen, QFont

from ..config import COLORS


class TextColumnDelegate(QStyledItemDelegate):
    """只允许第2列(添加文字)可编辑，其他列禁止编辑；状态列根据选中状态自动切换颜色"""

    def __init__(self, editable_column, parent=None):
        super().__init__(parent)
        self.editable_column = editable_column

    def createEditor(self, parent, option, index):
        if index.column() == self.editable_column:
            editor = QLineEdit(parent)
            editor.setStyleSheet(f"border:2px solid {COLORS['primary']};border-radius:4px;padding:2px 6px;font-size:13px;background:white;")
            editor.setMinimumHeight(option.rect.height())
            return editor
        return None

    def updateEditorGeometry(self, editor, option, index):
        """确保编辑器大小与单元格一致，防止变形"""
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        """自定义绘制：状态列(col=6)和PDF路径列(col=5)在非选中时使用彩色文字"""
        col = index.column()
        if col == 6:
            # 状态列
            text = index.data(Qt.ItemDataRole.DisplayRole) or ""
            if option.state & QStyle.StateFlag.State_Selected:
                super().paint(painter, option, index)
            else:
                color = QColor(COLORS['text'])
                if text == "成功":
                    color = QColor(COLORS['accent'])
                elif "失败" in text:
                    color = QColor(COLORS['danger'])
                elif "处理中" in text:
                    color = QColor(COLORS['primary'])
                elif text == "就绪":
                    color = QColor(COLORS['accent'])
                # 绘制背景
                painter.save()
                painter.fillRect(option.rect, option.backgroundBrush)
                # 绘制文字
                painter.setPen(QPen(color))
                painter.setFont(option.font)
                painter.drawText(option.rect.adjusted(6, 0, 0, 0),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
                painter.restore()
                return
        elif col == 5:
            # PDF路径列
            text = index.data(Qt.ItemDataRole.DisplayRole) or ""
            if option.state & QStyle.StateFlag.State_Selected:
                super().paint(painter, option, index)
            elif text == "未找到":
                painter.save()
                painter.fillRect(option.rect, option.backgroundBrush)
                painter.setPen(QPen(QColor(COLORS['danger'])))
                painter.setFont(option.font)
                painter.drawText(option.rect.adjusted(6, 0, 0, 0),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
                painter.restore()
                return
        super().paint(painter, option, index)
