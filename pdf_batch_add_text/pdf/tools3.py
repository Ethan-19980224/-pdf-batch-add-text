"""PDF 高级工具 - 合并、拆分、压缩、PDF转图片、图片转PDF"""
import os
import pymupdf as fitz
from ..logger import diag_log


def merge_pdfs(pdf_paths, output_dir, output_name="合并结果"):
    """合并多个 PDF 为一个
    返回输出路径
    """
    if not pdf_paths:
        return None

    doc = None
    try:
        doc = fitz.open()
        for pdf_path in pdf_paths:
            if not os.path.exists(pdf_path):
                diag_log(f"  [合并] 跳过不存在文件: {pdf_path}")
                continue
            try:
                src = fitz.open(pdf_path)
                doc.insert_pdf(src)
                src.close()
                diag_log(f"  [合并] 已加入: {os.path.basename(pdf_path)} ({len(src)} 页)")
            except Exception as e:
                diag_log(f"  [合并] 插入失败 {os.path.basename(pdf_path)}: {e}")

        if len(doc) == 0:
            raise ValueError("没有有效的 PDF 可合并")

        output_path = os.path.join(output_dir, f"{output_name}.pdf")
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{output_name}_{counter}.pdf")
            counter += 1

        doc.save(output_path)
        diag_log(f"  [合并] 完成: {output_path} ({len(doc)} 页)")
        return output_path
    except Exception as e:
        diag_log(f"  [合并] 失败: {e}")
        raise
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass


def split_pdf(pdf_path, output_dir, split_mode="every", page_count=1):
    """拆分 PDF
    split_mode: "every" 每 N 页一份, "range" 按页码范围
    page_count: 每份页数（every 模式）
    返回输出路径列表
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

    doc = None
    output_paths = []
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        if total_pages == 0:
            raise ValueError("PDF 没有页面")

        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        part = 0

        for start in range(0, total_pages, page_count):
            end = min(start + page_count, total_pages)
            part += 1

            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=start, to_page=end - 1)

            output_path = os.path.join(output_dir, f"{base_name}_第{part}部分.pdf")
            counter = 1
            while os.path.exists(output_path):
                output_path = os.path.join(output_dir, f"{base_name}_第{part}部分_{counter}.pdf")
                counter += 1

            new_doc.save(output_path)
            new_doc.close()
            output_paths.append(output_path)
            diag_log(f"  [拆分] 第{part}部分: 第{start+1}-{end}页 → {os.path.basename(output_path)}")

        diag_log(f"  [拆分] 完成: 共 {part} 份文件")
        return output_paths
    except Exception as e:
        diag_log(f"  [拆分] 失败: {e}")
        raise
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass


def compress_pdf(pdf_path, output_dir, quality=85):
    """压缩 PDF（降低图片质量、清理冗余数据）
    quality: 图片质量 1-100，越低压缩越大
    返回输出路径
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

    doc = None
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        if total_pages == 0:
            raise ValueError("PDF 没有页面")

        # 压缩：遍历每页，压缩图片
        for page_num in range(total_pages):
            page = doc[page_num]
            images = page.get_images(full=True)
            for img in images:
                xref = img[0]
                try:
                    pix = fitz.Pixmap(doc, xref)
                    if pix.width > 100 and pix.height > 100:
                        # 用 JPEG 压缩重编码
                        pix_out = fitz.Pixmap(pix, 0)  # 降采样
                        doc.replace_image(xref, pix_out)
                except Exception:
                    pass

        # 构建输出路径
        output_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_压缩.pdf")
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_压缩{counter}.pdf")
            counter += 1

        doc.save(output_path, garbage=4, deflate=True, clean=True)

        original_size = os.path.getsize(pdf_path)
        new_size = os.path.getsize(output_path)
        ratio = (1 - new_size / original_size) * 100
        diag_log(f"  [压缩] 完成: {output_path} ({original_size/1024:.0f}KB → {new_size/1024:.0f}KB, 减小{ratio:.0f}%)")
        return output_path
    except Exception as e:
        diag_log(f"  [压缩] 失败: {e}")
        raise
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass


def pdf_to_images(pdf_path, output_dir, dpi=150, fmt="png"):
    """PDF 转图片，每页一张
    dpi: 输出分辨率
    fmt: "png" 或 "jpeg"
    返回图片路径列表
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

    doc = None
    output_paths = []
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        if total_pages == 0:
            raise ValueError("PDF 没有页面")

        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        ext = ".png" if fmt == "png" else ".jpg"

        for i in range(total_pages):
            page = doc[i]
            zoom = dpi / 72
            matrix = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=matrix)

            output_path = os.path.join(output_dir, f"{base_name}_第{i+1}页{ext}")
            counter = 1
            while os.path.exists(output_path):
                output_path = os.path.join(output_dir, f"{base_name}_第{i+1}页_{counter}{ext}")
                counter += 1

            pix.save(output_path)
            output_paths.append(output_path)

        diag_log(f"  [PDF转图片] 完成: {total_pages} 页 → {output_dir}")
        return output_paths
    except Exception as e:
        diag_log(f"  [PDF转图片] 失败: {e}")
        raise
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass


def images_to_pdf(image_paths, output_dir, output_name="图片转PDF"):
    """多张图片合并为一个 PDF
    返回输出路径
    """
    if not image_paths:
        raise ValueError("没有图片文件")

    doc = None
    try:
        doc = fitz.open()
        for img_path in image_paths:
            if not os.path.exists(img_path):
                diag_log(f"  [图片转PDF] 跳过不存在文件: {img_path}")
                continue
            try:
                img = fitz.open(img_path)
                rect = img[0].rect
                page = doc.new_page(width=rect.width, height=rect.height)
                page.insert_image(rect, filename=img_path)
                img.close()
                diag_log(f"  [图片转PDF] 已加入: {os.path.basename(img_path)}")
            except Exception as e:
                diag_log(f"  [图片转PDF] 插入失败 {os.path.basename(img_path)}: {e}")

        if len(doc) == 0:
            raise ValueError("没有有效的图片可转换")

        output_path = os.path.join(output_dir, f"{output_name}.pdf")
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{output_name}_{counter}.pdf")
            counter += 1

        doc.save(output_path)
        diag_log(f"  [图片转PDF] 完成: {output_path} ({len(doc)} 页)")
        return output_path
    except Exception as e:
        diag_log(f"  [图片转PDF] 失败: {e}")
        raise
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass