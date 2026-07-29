"""对话框模块"""
from .batch_edit_dialog import BatchEditDialog
from .settings_dialog import SettingsDialog
from .preview_dialog import PdfPreviewDialog
from .template_dialog import WatermarkTemplateDialog
from .preflight_dialog import PreflightDialog
from .pdf_tools_dialog import PdfToolsDialog
from .multi_text_dialog import MultiTextDialog

from .pdf_advanced_dialog import PDFAdvancedDialog

__all__ = [
    'BatchEditDialog',
    'SettingsDialog',
    'PdfPreviewDialog',
    'WatermarkTemplateDialog',
    'PreflightDialog',
    'PdfToolsDialog',
    'MultiTextDialog',
    'PDFAdvancedDialog',
]
