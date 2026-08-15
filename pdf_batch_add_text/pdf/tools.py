"""PDF 辅助工具 - 页码、页脚、文本提取"""
import os
import re
import pymupdf as fitz
from datetime import datetime

from ..config import (
    COLORS, POSITIONS, DEFAULT_FONT_SIZE, DEFAULT_TEXT_COLOR,
    FITZ_FONT_MAP, CJK_FONT_RESOURCE_NAME
)
from ..logger import diag_log
from ..utils.fonts import find_cjk_font


def _get_font_name(opacity, bold, italic):
    """根据样式获取字体名"""
    font_file = find_cjk_font(bold=bold)
    if font_file:
        try:
            fitz.Font(fontfile=font_file)
            return CJK_FONT_RESOURCE_NAME
        except Exception:
            pass
    if bold and italic:
        return FITZ_FONT_MAP["bold_italic"]
    elif bold:
        return FITZ_FONT_MAP["bold"]
    elif italic:
        return FITZ_FONT_MAP["italic"]
    else:
        return FITZ_FONT_MAP["regular"]


def add_page_numbers(pdf_path, output_dir, start_num=1, font_size=10,
                     text_color="#888888", position="底部居中", opacity=0.7,
                     bold=False, italic=False):
    """为 PDF 每页添加页码
    返回输出路径列表
    """
    doc = None
    output_paths = []
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        if total_pages == 0:
            raise ValueError("PDF 没有页面")

        font_name = _get_font_name(opacity, bold, italic)
        r = int(text_color[1:3], 16) / 255
        g = int(text_color[3:5], 16) / 255
        b = int(text_color[5:7], 16) / 255

        for idx in range(total_pages):
            if idx < 0 or idx >= total_pages:
                continue
            page = doc[idx]
            rect = page.rect
            page_width = rect.width
            page_height = rect.height

            page_num = start_num + idx
            text = f"— {page_num} —"
            # get_text_length 不支持自定义字体名，使用内置字体测量宽度
            measure_font = "helv" if font_name == CJK_FONT_RESOURCE_NAME else font_name
            text_width = fitz.get_text_length(text, fontname=measure_font, fontsize=font_size)

            # 位置计算
            if position == "底部居中":
                x = (page_width - text_width) / 2
                y = page_height - font_size * 1.5
            elif position == "右下角":
                x = page_width - text_width - font_size
                y = page_height - font_size * 1.5
            else:
                x = (page_width - text_width) / 2
                y = page_height - font_size * 1.5

            try:
                page.insert_text(
                    fitz.Point(x, y), text,
                    fontname=font_name, fontsize=font_size,
                    color=(r, g, b), fill_opacity=opacity
                )
            except Exception as e:
                diag_log(f"  页面 {idx+1} 添加页码失败: {e}")

        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_页码.pdf")
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{base_name}_{counter}_页码.pdf")
            counter += 1
        doc.save(output_path)
        output_paths.append(output_path)
        diag_log(f"  页码添加完成: {output_path}")
        return output_paths

    finally:
        if doc is not None:
            doc.close()


def add_footer(pdf_path, output_dir, footer_text, font_size=10,
               text_color="#888888", position="底部居中", opacity=0.7,
               bold=False, italic=False):
    """为 PDF 每页添加自定义页脚文字
    返回输出路径列表
    """
    if not footer_text:
        raise ValueError("页脚文字不能为空")

    doc = None
    output_paths = []
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        if total_pages == 0:
            raise ValueError("PDF 没有页面")

        font_name = _get_font_name(opacity, bold, italic)
        r = int(text_color[1:3], 16) / 255
        g = int(text_color[3:5], 16) / 255
        b = int(text_color[5:7], 16) / 255
        # get_text_length 不支持自定义字体名，使用内置字体测量宽度
        measure_font = "helv" if font_name == CJK_FONT_RESOURCE_NAME else font_name

        for idx in range(total_pages):
            page = doc[idx]
            rect = page.rect
            page_width = rect.width
            page_height = rect.height

            text_width = fitz.get_text_length(footer_text, fontname=measure_font, fontsize=font_size)

            if position == "底部居中":
                x = (page_width - text_width) / 2
                y = page_height - font_size * 1.5
            elif position == "右下角":
                x = page_width - text_width - font_size
                y = page_height - font_size * 1.5
            else:
                x = (page_width - text_width) / 2
                y = page_height - font_size * 1.5

            try:
                page.insert_text(
                    fitz.Point(x, y), footer_text,
                    fontname=font_name, fontsize=font_size,
                    color=(r, g, b), fill_opacity=opacity
                )
            except Exception as e:
                diag_log(f"  页面 {idx+1} 添加页脚失败: {e}")

        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_页脚.pdf")
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{base_name}_{counter}_页脚.pdf")
            counter += 1
        doc.save(output_path)
        output_paths.append(output_path)
        diag_log(f"  页脚添加完成: {output_path}")
        return output_paths

    finally:
        if doc is not None:
            doc.close()


def extract_text(pdf_path, output_path=None):
    """从 PDF 提取文字
    返回 (文本内容, 输出路径)
    """
    doc = None
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        if total_pages == 0:
            raise ValueError("PDF 没有页面")

        extracted = []
        for idx in range(total_pages):
            page = doc[idx]
            text = page.get_text()
            extracted.append(f"===== 第 {idx+1} 页 =====\n{text}\n")

        all_text = "\n".join(extracted)
        if not all_text.strip():
            raise ValueError("PDF 中未检测到可提取的文字")

        if output_path is None:
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_path = os.path.join(os.path.dirname(pdf_path), f"{base_name}_提取文本.txt")

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"提取自: {os.path.basename(pdf_path)}\n")
            f.write(f"提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总页数: {total_pages}\n")
            f.write("=" * 50 + "\n\n")
            f.write(all_text)

        diag_log(f"  文本提取完成: {output_path} ({len(all_text)} chars)")
        return (all_text, output_path)

    finally:
        if doc is not None:
            doc.close()
