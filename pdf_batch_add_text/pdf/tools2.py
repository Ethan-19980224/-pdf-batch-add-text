"""PDF 辅助工具2 - 图片水印 / 页面旋转 / PDF加密"""
import os
import pymupdf as fitz
from datetime import datetime

from ..config import DEFAULT_OPACITY
from ..logger import diag_log


def add_image_watermark(pdf_path, image_path, output_dir,
                        opacity=0.5, page_range="",
                        x_scale=1.0, y_scale=1.0, position="居中"):
    """为 PDF 添加图片水印
    返回输出路径列表
    """
    doc = None
    output_paths = []
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        if total_pages == 0:
            raise ValueError("PDF 没有页面")

        # 解析页码范围
        if page_range:
            indices = _parse_range(page_range, total_pages)
        else:
            indices = list(range(total_pages))

        # 加载水印图片（提取为 xref）
        watermark_xref = doc.insert_file(
            image_path,
            from_page=0,
            to_page=0,
            append=True
        )
        # 获取插入的页面
        img_page = doc[-1]
        # 提取为嵌入图片 xref
        img_rects = img_page.get_images(full=True)
        if not img_rects:
            doc.close()
            raise ValueError(f"无法从 {image_path} 提取图片")
        img_xref = img_rects[0][0]
        img_rect = img_page.get_image_rects(img_xref)[0]

        for idx in indices:
            if idx < 0 or idx >= total_pages:
                continue
            page = doc[idx]
            pw, ph = page.rect.width, page.rect.height
            iw = img_rect.width
            ih = img_rect.height

            # 缩放图片
            scale = min(pw / (iw * x_scale), ph / (ih * y_scale))
            sw, sh = iw * scale * x_scale, ih * scale * y_scale

            # 计算位置
            if position == "居中":
                x = (pw - sw) / 2
                y = (ph - sh) / 2
            elif position == "左上角":
                x, y = 0, 0
            elif position == "右上角":
                x, y = pw - sw, 0
            elif position == "左下角":
                x, y = 0, ph - sh
            elif position == "右下角":
                x, y = pw - sw, ph - sh
            else:
                x, y = (pw - sw) / 2, (ph - sh) / 2

            page.insert_image(
                fitz.Rect(x, y, x + sw, y + sh),
                xref=img_xref,
                overlay=False,
                render=True
            )
            # 设置页面不透明层（水印在底层）
            # 通过调整页面插入顺序实现水印在内容下方

        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_图片水印.pdf")
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{base_name}_{counter}_图片水印.pdf")
            counter += 1
        doc.save(output_path)
        output_paths.append(output_path)
        diag_log(f"  图片水印完成: {output_path}")
        return output_paths
    except Exception as e:
        diag_log(f"  图片水印失败: {e}")
        raise
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass


def rotate_pdf(pdf_path, output_dir, rotation, page_range=""):
    """旋转 PDF 页面
    rotation: 90/180/270 度
    返回输出路径列表
    """
    doc = None
    output_paths = []
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        if total_pages == 0:
            raise ValueError("PDF 没有页面")

        if page_range:
            indices = _parse_range(page_range, total_pages)
        else:
            indices = list(range(total_pages))

        for idx in indices:
            if idx < 0 or idx >= total_pages:
                continue
            page = doc[idx]
            current_rotation = page.rotation
            # 旋转变换：90=顺时针90, 180=180, 270=逆时针90
            new_rotation = (current_rotation + rotation) % 360
            page.set_rotation(new_rotation)
            diag_log(f"  页面 {idx+1}: 旋转 {rotation}° (当前 {current_rotation}° → {new_rotation}°)")

        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_旋转{rotation}.pdf")
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{base_name}_{counter}_旋转{rotation}.pdf")
            counter += 1
        doc.save(output_path)
        diag_log(f"  旋转完成: {output_path}")
        output_paths.append(output_path)
        return output_paths
    except Exception as e:
        diag_log(f"  PDF旋转失败: {e}")
        raise
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass


def encrypt_pdf(pdf_path, output_dir, owner_pw, user_pw="",
                permissions=None, page_range=""):
    """加密 PDF
    permissions: dict {can_print, can_modify, can_copy, can_notes}
    返回输出路径列表
    """
    doc = None
    output_paths = []
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        if total_pages == 0:
            raise ValueError("PDF 没有页面")

        if page_range:
            indices = _parse_range(page_range, total_pages)
            # 提取指定页面为新文档
            new_doc = fitz.open()
            for idx in indices:
                if idx < 0 or idx >= total_pages:
                    continue
                new_doc.insert_pdf(doc, from_page=idx, to_page=idx)
            doc.close()
            doc = new_doc
            total_pages = len(doc)

        if not permissions:
            permissions = {
                "can_print": True,
                "can_modify": False,
                "can_copy": False,
                "can_notes": False
            }

        p = 0
        if permissions.get("can_print"):
            p |= fitz.PDF_PERM_PRINT
        if permissions.get("can_modify"):
            p |= fitz.PDF_PERM_MODIFY
        if permissions.get("can_copy"):
            p |= fitz.PDF_PERM_COPY
        if permissions.get("can_notes"):
            p |= fitz.PDF_PERM_ANNOTATE

        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_加密.pdf")
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{base_name}_{counter}_加密.pdf")
            counter += 1

        doc.save(
            output_path,
            encryption=fitz.PDF_ENCRYPT_AES_256,
            owner_pw=owner_pw,
            user_pw=user_pw,
            permissions=p
        )
        output_paths.append(output_path)
        diag_log(f"  PDF加密完成: {output_path} (用户密码: {'有' if user_pw else '无'}, 权限: {permissions})")
        return output_paths
    except Exception as e:
        diag_log(f"  PDF加密失败: {e}")
        raise
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass


def _parse_range(range_str, total_pages):
    """解析页码范围字符串，如 "1-3,5,8-10" 返回 [0,1,2,4,7,8,9]"""
    indices = []
    parts = range_str.split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            try:
                start, end = part.split("-", 1)
                s, e = int(start.strip()) - 1, int(end.strip()) - 1
                indices.extend(range(max(0, s), min(total_pages, e + 1)))
            except ValueError:
                continue
        else:
            try:
                idx = int(part) - 1
                if 0 <= idx < total_pages:
                    indices.append(idx)
            except ValueError:
                continue
    return sorted(set(indices))
