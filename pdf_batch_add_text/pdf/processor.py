"""PDF 处理核心逻辑 - _process_pdf_internal, _find_best_empty_area, _insert_text_on_page, _save_doc"""
import os
import re
import tempfile
import fitz
from datetime import date, datetime

from ..config import POSITIONS, CJK_FONT_RESOURCE_NAME, _TEXT_ALIGN_LEFT, DEFAULT_OPACITY, FITZ_FONT_MAP, DEFAULT_FONT_SIZE
from ..logger import diag_log
from PyQt6.QtGui import QColor



def _is_multi_text_entry(entry):
    """判断是否为多文字条目（dict 且含 'text' 键）"""
    return isinstance(entry, dict) and 'text' in entry


def _resolve_entry_params(entry, worker):
    """解析单个文字条目的参数，返回 (text, r, g, b, font_size, opacity, font_name)
    entry 可以是 dict（多文字条目）或 str（普通文字）
    """
    if isinstance(entry, dict):
        # 多文字条目：每个字段都有独立设置
        text = entry.get('text', '')
        try:
            color = QColor(entry.get('color', '#000000'))
        except Exception:
            color = QColor('#000000')
        r, g, b = color.redF(), color.greenF(), color.blueF()
        font_size = entry.get('font_size', DEFAULT_FONT_SIZE)
        opacity = entry.get('opacity', DEFAULT_OPACITY)
        bold = entry.get('bold', False)
        italic = entry.get('italic', False)

        # 字体名（使用 Worker 的全局字体文件 + bold/italic 标志）
        if worker._font_file:
            font_name = CJK_FONT_RESOURCE_NAME
        else:
            if bold and italic:
                font_name = FITZ_FONT_MAP['bold_italic']
            elif bold:
                font_name = FITZ_FONT_MAP['bold']
            elif italic:
                font_name = FITZ_FONT_MAP['italic']
            else:
                font_name = FITZ_FONT_MAP['regular']
        return text, r, g, b, font_size, opacity, font_name

    # 普通字符串：使用 Worker 全局参数
    text = str(entry)
    r, g, b = worker._r, worker._g, worker._b
    font_size = worker.font_size
    opacity = worker.opacity
    font_name = worker._font_name
    return text, r, g, b, font_size, opacity, font_name


def _process_pdf_internal(self, pdf_path, text, row_num=None):
    """处理单个 PDF

    text 支持三种格式:
    1. str: 单个文字，使用 Worker 全局参数
    2. tuple(str, [(页码范围, 文字), ...]): 默认文字 + 特定页码覆盖
    3. list(dict): 多文字条目，每个 dict 含 {text, color, position, font_size, opacity, bold, italic}
    """
    diag_log(f"_process_pdf_internal: pdf_path={pdf_path}, output_dir={self.output_dir}")
    if not os.path.exists(pdf_path):
        diag_log(f"  FAIL: 文件不存在")
        raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

    doc = None
    try:
        doc = fitz.open(pdf_path)
        # 处理加密 PDF
        if doc.is_encrypted:
            try:
                doc.authenticate("")
            except Exception as e:
                diag_log(f"  尝试解密密钥为空失败: {e}")
            if doc.is_encrypted:
                raise PermissionError(f"PDF 已加密，无法处理: {os.path.basename(pdf_path)}")

        total_pages = len(doc)
        diag_log(f"  PDF 已打开: {total_pages} 页")
        if total_pages == 0:
            raise ValueError("PDF 没有页面")

        # 解析全局页码范围
        global_indices = set(self.get_page_indices(total_pages))
        diag_log(f"  全局页码范围: {sorted(global_indices)}")

        # ── 多文字模式：text 是 list(dict) ──
        if isinstance(text, list) and len(text) > 0 and _is_multi_text_entry(text[0]):
            diag_log(f"  多文字模式: {len(text)} 个文字条目")
            page_success = 0
            page_errors = 0

            for idx in range(total_pages):
                if idx not in global_indices:
                    continue
                try:
                    page = doc[idx]
                    page_ok = True
                    for entry in text:
                        entry_text = entry.get('text', '')
                        if not entry_text or not entry_text.strip():
                            continue
                        text_str, r, g, b, fs, opacity, font_name = _resolve_entry_params(entry, self)
                        position = entry.get('position', self.position)
                        position_key = position if position in POSITIONS else self.position
                        if isinstance(POSITIONS.get(position_key), tuple):
                            px, py = POSITIONS[position_key]
                        else:
                            px, py = self._px, self._py

                        # 临时替换参数以复用 _insert_text_on_page
                        old_r, old_g, old_b = self._r, self._g, self._b
                        old_px, old_py = self._px, self._py
                        old_font_size, old_font_name, old_opacity = self.font_size, self._font_name, self.opacity
                        self._r, self._g, self._b = r, g, b
                        self._px, self._py = px, py
                        self.font_size, self._font_name, self.opacity = fs, font_name, opacity

                        ok = self._insert_text_on_page(page, text_str, r, g, b, px, py)

                        # 恢复参数
                        self._r, self._g, self._b = old_r, old_g, old_b
                        self._px, self._py = old_px, old_py
                        self.font_size, self._font_name, self.opacity = old_font_size, old_font_name, old_opacity

                        if not ok:
                            page_ok = False
                            diag_log(f"  页面 {idx+1} 文字 '{text_str[:20]}' 插入失败")

                    if page_ok:
                        page_success += 1
                    else:
                        page_errors += 1

                except Exception as e:
                    page_errors += 1
                    diag_log(f"  页面 {idx+1} 处理异常: {type(e).__name__}: {e}")

            diag_log(f"  多文字处理完成: 成功 {page_success}/{len(global_indices)} 页, 失败 {page_errors} 页")
            if page_errors > 0 and page_success == 0:
                raise RuntimeError(f"所有页面处理失败 ({page_errors} 页)")

            # 保存 PDF
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            self._seq_counter += 1
            text_for_name = '多文字'
            output_path = self._save_doc(doc, base_name, text_for_name)
            if not output_path:
                raise IOError(f"无法保存 PDF 文件: {base_name}.pdf")
            self.log.emit(f"  保存成功: {output_path} ({os.path.getsize(output_path)} bytes)")
            return

        # ── 单文字/页码覆盖模式 ──
        diag_log(f"  传入 text 类型: {type(text).__name__}, 值: {str(text)[:100]}")
        page_texts = []

        if isinstance(text, tuple) and len(text) == 2 and isinstance(text[1], list):
            default_text, page_texts_cfg = text
            diag_log(f"  默认文字: {default_text}, 特定页码配置: {page_texts_cfg}")
            specific_pages = {}
            for pr_str, txt in page_texts_cfg:
                pr_str = str(pr_str).strip()
                if not pr_str:
                    continue
                parsed_indices = self._parse_page_range(pr_str, total_pages)
                diag_log(f"    页码 '{pr_str}' 解析为: {parsed_indices}")
                for idx in parsed_indices:
                    if idx in global_indices:
                        specific_pages[idx] = txt
            covered = set(specific_pages.keys())
            default_indices = [i for i in range(total_pages) if i in global_indices and i not in covered]
            diag_log(f"  特定页码覆盖: {sorted(covered)}, 默认页: {default_indices}")
            if default_text and default_text.strip() and default_indices:
                page_texts.append((default_indices, default_text))
            for idx, txt in sorted(specific_pages.items()):
                page_texts.append(([idx], txt))
        elif isinstance(text, list):
            for pr_str, txt in text:
                indices = self._parse_page_range(pr_str, total_pages)
                page_texts.append(([i for i in indices if i in global_indices], txt))
        else:
            page_texts = [(list(global_indices), str(text))]

        # 记录最终页面-文字映射
        for pidx, ptxt in page_texts:
            diag_log(f"  最终映射: 页 {[i+1 for i in pidx]} -> {ptxt[:30]}")

        r, g, b = self._r, self._g, self._b
        px, py = self._px, self._py
        diag_log(f"  颜色: ({r:.3f},{g:.3f},{b:.3f}), 位置: {self.position}, 透明度: {self.opacity}")
        diag_log(f"  字体: {self._font_name}, 文件: {self._font_file}, 大小: {self.font_size}pt")

        page_success = 0
        page_errors = 0

        for page_indices, page_text in page_texts:
            for idx in page_indices:
                if idx < 0 or idx >= total_pages:
                    continue
                try:
                    page = doc[idx]
                    if page_text and page_text.strip():
                        ok = self._insert_text_on_page(page, page_text, r, g, b, px, py)
                    else:
                        ok = True
                    if ok:
                        page_success += 1
                    else:
                        page_errors += 1
                        diag_log(f"  页面 {idx}: 文字插入失败")
                except Exception as e:
                    page_errors += 1
                    diag_log(f"  页面 {idx} 处理异常: {type(e).__name__}: {e}")

        diag_log(f"  处理完成: 成功 {page_success}/{total_pages} 页, 失败 {page_errors} 页")
        if page_errors > 0 and page_success == 0:
            raise RuntimeError(f"所有页面处理失败 ({page_errors} 页)")

        # 保存 PDF（多级回退）
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        self._seq_counter += 1
        text_for_name = ""
        if isinstance(text, tuple) and len(text) == 2:
            text_for_name = str(text[0])[:30] if text[0] else ""
        elif isinstance(text, str):
            text_for_name = text[:30]
        output_path = self._save_doc(doc, base_name, text_for_name)
        if not output_path:
            raise IOError(f"无法保存 PDF 文件: {base_name}.pdf")

        self.log.emit(f"  保存成功: {output_path} ({os.path.getsize(output_path)} bytes)")
        print(f"[PDF工具] 保存成功: {output_path} ({os.path.getsize(output_path)} bytes)")
    finally:
        if doc is not None:
            doc.close()


def _find_best_empty_area(self, page, text_width, text_height, margin):
    """内容感知定位：分析页面现有内容（文字块、图片），找到最大空白矩形区域
    返回 (x, y) 坐标，若无合适空白区域则返回 None（回退到原逻辑）
    """
    try:
        page_rect = page.rect
        pw, ph = page_rect.width, page_rect.height

        # 获取页面上的所有文字块
        text_blocks = page.get_text("blocks")

        # 获取图片区域
        images = page.get_images(full=True)
        image_rects = []
        for img in images:
            try:
                xref = img[0]
                rects = page.get_image_rects(xref)
                for r in rects:
                    image_rects.append((r.x0, r.y0, r.x1, r.y1))
            except Exception as e:
                diag_log(f"  获取图片区域失败 (xref={img[0]}): {e}")

        # 合并所有占用区域（文字块 + 图片）
        occupied = []
        for block in text_blocks:
            if len(block) >= 4:
                x0, y0, x1, y1 = block[0], block[1], block[2], block[3]
                if x1 > x0 and y1 > y0:
                    occupied.append((x0 - margin, y0 - margin, x1 + margin, y1 + margin))
        for r in image_rects:
            occupied.append((r[0] - margin, r[1] - margin, r[2] + margin, r[3] + margin))

        # 加上页面边界作为"占用"区域（留出边距）
        occupied.append((-1, -1, margin, ph + 1))
        occupied.append((pw - margin, -1, pw + 1, ph + 1))
        occupied.append((-1, -1, pw + 1, margin))
        occupied.append((-1, ph - margin, pw + 1, ph + 1))

        # 网格搜索策略：在页面上采样多个候选位置，选重叠最小的
        candidates = [
            (margin, margin),
            (pw - text_width - margin, margin),
            (margin, ph - text_height - margin),
            (pw - text_width - margin, ph - text_height - margin),
            ((pw - text_width) / 2, margin),
            ((pw - text_width) / 2, ph - text_height - margin),
            (margin, (ph - text_height) / 2),
            (pw - text_width - margin, (ph - text_height) / 2),
            ((pw - text_width) / 2, (ph - text_height) / 2),
            (pw * 0.25 - text_width/2, ph * 0.25),
            (pw * 0.75 - text_width/2, ph * 0.75),
        ]

        best_pos = None
        min_overlap = float('inf')

        for cx, cy in candidates:
            cx = max(margin, min(cx, pw - text_width - margin))
            cy = max(margin, min(cy, ph - text_height - margin))

            overlap = 0
            cand_rect = (cx, cy, cx + text_width, cy + text_height)
            for ox0, oy0, ox1, oy1 in occupied:
                ix0 = max(cx, ox0)
                iy0 = max(cy, oy0)
                ix1 = min(cx + text_width, ox1)
                iy1 = min(cy + text_height, oy1)
                if ix1 > ix0 and iy1 > iy0:
                    overlap += (ix1 - ix0) * (iy1 - iy0)

            if overlap < min_overlap:
                min_overlap = overlap
                best_pos = (cx, cy)
                if overlap == 0:
                    break

        if best_pos and min_overlap < text_width * text_height * 0.1:
            return best_pos
    except Exception as e:
        diag_log(f"  内容感知定位异常，回退默认: {e}")
    return None


def _insert_text_on_page(self, page, text, r, g, b, px, py):
    """在单个页面上插入文字，返回是否成功"""
    rect = page.rect
    page_width = rect.width
    page_height = rect.height

    # 智能自适应：如果文字超宽则自动缩小字号
    font_size = self.font_size
    for attempt in range(3):
        try:
            text_width = fitz.get_text_length(
                text, fontname=self._font_name, fontfile=self._font_file, fontsize=font_size
            )
        except Exception:
            text_width = len(text) * font_size * (1.0 if self._font_file else 0.6)
        max_width = page_width * 0.92
        if text_width <= max_width or font_size <= 6:
            break
        font_size = int(font_size * (max_width / text_width))
        if font_size < 6:
            font_size = 6
            break

    text_height = font_size * 1.2
    margin = font_size * 0.5

    # --- 智能内容感知定位 ---
    if self.position == "智能自动" or (px, py) == POSITIONS.get("智能自动"):
        smart_pos = self._find_best_empty_area(page, text_width, text_height, margin)
        if smart_pos:
            x, y = smart_pos
            diag_log(f"    智能定位: 找到空白区 ({x:.0f}, {y:.0f})")
        else:
            x = page_width - text_width - margin
            y = page_height - margin - text_height
            diag_log(f"    智能定位: 无空白区，回退右下角")
    else:
        # --- 原有逻辑：固定位置 ---
        if 0.45 <= px <= 0.55:
            x = (page_width - text_width) / 2
        elif px >= 0.5:
            x = page_width * px - text_width
        else:
            x = page_width * px
        x = max(margin, min(x, page_width - text_width - margin))
        x += self.offset_x
        x = max(2, min(x, page_width - 2))

        raw_y = page_height * (1 - py)
        y = max(raw_y, text_height + margin)
        y = min(y, page_height - margin)
        y -= self.offset_y
        y = max(text_height, min(y, page_height - 2))

    # 方案1: insert_text
    inserted = page.insert_text(
        fitz.Point(x, y), text,
        fontname=self._font_name,
        fontfile=self._font_file,
        fontsize=font_size,
        color=(r, g, b),
        fill_opacity=self.opacity,
    )
    if font_size != self.font_size:
        diag_log(f"    auto-scaled: {self.font_size}pt → {font_size}pt (text_width={text_width:.0f}, page_width={page_width:.0f})")
    diag_log(f"    insert_text 返回: {inserted}, 文字='{text[:20]}', 坐标=({x:.0f},{y:.0f})")
    if inserted > 0:
        return True

    # 方案2: insert_textbox
    try:
        textbox_rect = fitz.Rect(x, y - text_height, x + text_width + 50, y + margin)
        rc = page.insert_textbox(
            textbox_rect, text,
            fontname=self._font_name,
            fontfile=self._font_file,
            fontsize=font_size,
            color=(r, g, b),
            fill_opacity=self.opacity,
            align=_TEXT_ALIGN_LEFT,
        )
        if rc > 0:
            return True
    except Exception as tb_err:
        diag_log(f"  insert_textbox 异常: {tb_err}")

    # 最终回退: 画可见标记
    try:
        marker = fitz.Rect(x - 5, y - text_height - 5, x + 5, y + 5)
        page.draw_rect(marker, color=(r, g, b), fill=(r, g, b), fill_opacity=self.opacity)
    except Exception as e:
        diag_log(f"  绘制标记失败 (x={x:.0f}, y={y:.0f}): {e}")
    return False


def _save_doc(self, doc, base_name, text_for_name=""):
    """多级回退保存，返回最终路径或 None（支持命名模板）"""
    today = date.today()
    now = datetime.now()
    filename = self.naming_template
    replacements = {
        '{original}': base_name,
        '{原文件名}': base_name,
        '{text}': text_for_name.replace('/', '_').replace('\\', '_') if text_for_name else 'watermark',
        '{文字}': text_for_name.replace('/', '_').replace('\\', '_') if text_for_name else 'watermark',
        '{date}': today.strftime('%Y%m%d'),
        '{日期}': today.strftime('%Y%m%d'),
        '{date_short}': today.strftime('%y%m%d'),
        '{date_iso}': today.strftime('%Y-%m-%d'),
        '{time}': now.strftime('%H%M%S'),
        '{时间}': now.strftime('%H%M%S'),
        '{seq}': str(self._seq_counter),
        '{序号}': str(self._seq_counter),
        '{seq:03d}': f'{self._seq_counter:03d}',
        '{序号:03d}': f'{self._seq_counter:03d}',
        '{seq:04d}': f'{self._seq_counter:04d}',
        '{序号:04d}': f'{self._seq_counter:04d}',
    }
    for key, val in replacements.items():
        filename = filename.replace(key, val)
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    fallbacks = [
        os.path.abspath(self.output_dir),
        os.path.join(os.getcwd(), "output"),
        os.path.join(os.path.expanduser("~"), "Desktop", "PDF输出"),
        os.path.join(os.path.expanduser("~"), "Documents", "PDF输出"),
        os.path.join(tempfile.gettempdir(), "PDF输出"),
    ]
    for i, out_dir in enumerate(fallbacks):
        try:
            os.makedirs(out_dir, exist_ok=True)
            output_path = os.path.join(out_dir, filename)
            counter = 1
            while os.path.exists(output_path):
                name, ext = os.path.splitext(filename)
                output_path = os.path.join(out_dir, f"{name}_{counter}{ext}")
                counter += 1
            doc.save(output_path)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                diag_log(f"  保存成功 (第{i+1}级): {output_path} ({os.path.getsize(output_path)} bytes)")
                self.output_paths.append(output_path)
                return output_path
            else:
                diag_log(f"  第{i+1}级保存后文件无效: {output_path}")
        except Exception as e:
            diag_log(f"  第{i+1}级保存失败: {type(e).__name__}: {e}")
            continue
    return None
