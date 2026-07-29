"""处理线程 - ProcessWorker 和 PageCountWorker"""
import os
import time
import fitz

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QColor

from ..config import (
    POSITIONS, FITZ_FONT_MAP, CJK_FONT_RESOURCE_NAME,
    _TEXT_ALIGN_LEFT
)
from ..logger import diag_log, diag_flush
from ..utils.pages import parse_page_range
from ..utils.fonts import find_cjk_font
from .processor import _find_best_empty_area, _insert_text_on_page, _process_pdf_internal, _save_doc

# 在类定义后将 processor 中的函数绑定为 ProcessWorker 实例方法


class PageCountWorker(QThread):
    """后台加载 PDF 页数，避免主线程阻塞"""
    page_loaded = pyqtSignal(int, str)  # (任务索引, 页数)
    finished_signal = pyqtSignal()

    def __init__(self, tasks, parent=None):
        super().__init__(parent)
        self._task_paths = [(i, t['pdf_path']) for i, t in enumerate(tasks) if t['pdf_path'] and not t.get('pages')]

    def run(self):
        for i, pdf_path in self._task_paths:
            try:
                doc = fitz.open(pdf_path)
                pages = str(len(doc))
                doc.close()
            except Exception:
                pages = "?"
            self.page_loaded.emit(i, pages)
        self.finished_signal.emit()


class ProcessWorker(QThread):
    progress = pyqtSignal(int, int)
    status = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    task_status = pyqtSignal(int, str)  # (任务索引, 状态文字)
    log = pyqtSignal(str)

    def __init__(self, tasks, output_dir, font_size, text_color, position,
                 page_range, opacity, bold, italic, offset_x, offset_y,
                 naming_template="{original}.pdf"):
        super().__init__()

        # 动态绑定 PDF 核心处理函数为实例方法（从 processor.py 注入）
        # 这样避免在 processor.py 中引用 ProcessWorker 类，保持模块解耦
        self._process_pdf_internal = _process_pdf_internal.__get__(self, ProcessWorker)
        self._find_best_empty_area = _find_best_empty_area.__get__(self, ProcessWorker)
        self._insert_text_on_page = _insert_text_on_page.__get__(self, ProcessWorker)
        self._save_doc = _save_doc.__get__(self, ProcessWorker)

        self.tasks = [
            {k: t[k] for k in ('pdf_path', 'text', 'page_texts', 'row')}
            for t in tasks
        ]
        if output_dir and output_dir.strip():
            abs_path = os.path.abspath(output_dir)
            parent = os.path.dirname(abs_path)
            if os.path.isdir(parent) or os.path.isdir(abs_path):
                self.output_dir = abs_path
            else:
                self.output_dir = os.path.abspath(os.path.join(os.getcwd(), "output"))
        else:
            self.output_dir = os.path.abspath(os.path.join(os.getcwd(), "output"))
        self.font_size = font_size
        self.text_color = text_color
        self.position = position
        self.page_range = str(page_range) if page_range is not None else ''
        try:
            self.opacity = float(opacity)
        except (ValueError, TypeError):
            self.opacity = 1.0
        self.bold = bold
        self.italic = italic
        self.offset_x = offset_x
        self.offset_y = offset_y
        diag_log(f"ProcessWorker 参数: page_range={repr(self.page_range)}, opacity={self.opacity}")
        self._is_running = True
        self.output_paths = []
        self.naming_template = naming_template
        self._seq_counter = 0

    def stop(self):
        self._is_running = False

    def _parse_page_range(self, pr, total_pages):
        return parse_page_range(pr, total_pages)

    def get_page_indices(self, total_pages):
        result = parse_page_range(self.page_range, total_pages)
        diag_log(f"get_page_indices: page_range={repr(self.page_range)}, total={total_pages}, 结果={result[:20]}{'...' if len(result) > 20 else ''}")
        return result

    def _init_font_name(self):
        """初始化 PyMuPDF 可用的字体资源名"""
        if self._font_file:
            try:
                fitz.Font(fontfile=self._font_file)
                diag_log(f"字体预加载成功: {self._font_file}")
                return CJK_FONT_RESOURCE_NAME
            except Exception as e:
                diag_log(f"字体加载失败: {self._font_file}, 错误: {e}")
        # 无中文字体时回退到内置字体
        if self.bold and self.italic:
            return FITZ_FONT_MAP["bold_italic"]
        elif self.bold:
            return FITZ_FONT_MAP["bold"]
        elif self.italic:
            return FITZ_FONT_MAP["italic"]
        else:
            return FITZ_FONT_MAP["regular"]

    def run(self):
        total = len(self.tasks)
        if total == 0:
            self.finished_signal.emit(True, "没有待处理的任务")
            return

        success_count = 0
        fail_count = 0
        self._results = [None] * total

        # 预计算不变量
        color = QColor(self.text_color)
        self._r, self._g, self._b = color.redF(), color.greenF(), color.blueF()
        self._px, self._py = POSITIONS.get(self.position, (0.95, 0.05))
        self._font_file = find_cjk_font(bold=self.bold)
        self._font_name = self._init_font_name()

        task_defs = []
        for i, task in enumerate(self.tasks):
            pdf_path = task['pdf_path']
            text = task['text']
            page_texts = task.get('page_texts', [])
            row_num = task.get('row', i + 1)

            if page_texts:
                process_text = (text if text and text.strip() else "", page_texts)
            else:
                process_text = text

            is_empty_tuple = isinstance(process_text, tuple) and not process_text[0].strip() and not process_text[1]
            # 多文字模式：text 是 list(dict)，只要非空且不全是空字符串就有效
            is_empty_multi = isinstance(process_text, list) and len(process_text) > 0 and all(
                isinstance(e, dict) and not e.get('text', '').strip() for e in process_text
            )
            if not process_text or is_empty_tuple or is_empty_multi or (isinstance(process_text, str) and not process_text.strip()):
                self._results[i] = ('skip', row_num)
                self.log.emit(f"[{row_num}] 跳过: 文字为空")
                self.task_status.emit(i, "跳过")
                continue

            task_defs.append((i, pdf_path, process_text, row_num))

        # 智能决定并行度
        cpu_count = os.cpu_count() or 4
        num_workers = min(cpu_count, max(1, len(task_defs) // 2))

        if len(task_defs) <= 3 or num_workers <= 1:
            self._process_sequential(task_defs)
        else:
            self._process_parallel(task_defs, num_workers)

        # 汇总所有结果
        for r in self._results:
            if r is None:
                continue
            if r[0] == 'success':
                success_count += 1
            elif r[0] == 'fail':
                fail_count += 1

        result = f"完成! 成功: {success_count}, 失败: {fail_count}"
        self.status.emit(result)
        diag_flush()
        self.finished_signal.emit(fail_count == 0, result)

    def _process_sequential(self, task_defs):
        """单线程顺序处理（小批量场景）"""
        total = len(self.tasks)
        done = sum(1 for r in self._results if r is not None)
        for i, pdf_path, process_text, row_num in task_defs:
            if not self._is_running:
                self.status.emit("处理已取消")
                self.finished_signal.emit(False, "用户取消")
                return
            self._process_one(i, pdf_path, process_text, row_num, total, done)
            done += 1

    def _process_parallel(self, task_defs, num_workers):
        """多线程并行处理（大批量场景）"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        total = len(self.tasks)
        done = sum(1 for r in self._results if r is not None)
        self._timings = []
        self._start_global = time.time()
        self._eta_timer = time.time()

        self.status.emit(f"并行处理 {len(task_defs)} 个文件 ({num_workers} 线程)...")
        self.log.emit(f"启动 {num_workers} 个线程并行处理 {len(task_defs)} 个文件")

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_map = {}
            for i, pdf_path, process_text, row_num in task_defs:
                future = executor.submit(self._process_one_worker, i, pdf_path, process_text, row_num)
                future_map[future] = i

            for future in as_completed(future_map):
                if not self._is_running:
                    executor.shutdown(wait=False, cancel_futures=True)
                    self.status.emit("处理已取消")
                    self.finished_signal.emit(False, "用户取消")
                    return
                i = future_map[future]
                try:
                    result = future.result()
                    self._results[i] = result
                    done += 1
                    self.progress.emit(done, total)
                except Exception as e:
                    self._results[i] = ('fail', i)
                    done += 1
                    self.progress.emit(done, total)

    def _process_one_worker(self, i, pdf_path, process_text, row_num):
        """单个PDF处理（在工作线程池中执行）"""
        try:
            self._process_pdf_internal(pdf_path, process_text, row_num)
            self.log.emit(f"  [{row_num}] 成功")
            self.task_status.emit(i, "成功")
            diag_log(f"  成功 [{row_num}]")
            return ('success', row_num)
        except Exception as e:
            err_str = str(e)
            retryable = any(k in err_str for k in ['写入', '权限', '拒绝', '被占用', 'Permission', 'denied', 'locked'])
            if retryable:
                diag_log(f"  [{row_num}] 遇到可重试错误，等待2秒后重试: {err_str}")
                time.sleep(2)
                try:
                    self._process_pdf_internal(pdf_path, process_text, row_num)
                    self.log.emit(f"  [{row_num}] 重试成功")
                    self.task_status.emit(i, "成功")
                    diag_log(f"  重试成功 [{row_num}]")
                    return ('success', row_num)
                except Exception as e2:
                    err_str = str(e2)
            diag_log(f"  失败 [{row_num}]: {err_str}")
            self.log.emit(f"  [{row_num}] 失败: {err_str}")
            self.task_status.emit(i, "失败")
            return ('fail', row_num)

    def _process_one(self, i, pdf_path, process_text, row_num, total, done):
        """单个PDF顺序处理（主线程中调用，含状态更新）"""
        self.status.emit(f"正在处理: {os.path.basename(pdf_path)} ...")
        self.log.emit(f"[{row_num}] 处理: {os.path.basename(pdf_path)}")
        self.task_status.emit(i, "处理中...")
        diag_log(f"处理 [{row_num}/{total}]: {os.path.basename(pdf_path)}")

        t0 = time.time()
        try:
            diag_log(f"  Worker 传入 process_pdf: type={type(process_text).__name__}, value={str(process_text)[:100]}")
            self._process_pdf_internal(pdf_path, process_text, row_num)
            self.log.emit(f"  成功")
            self.task_status.emit(i, "成功")
            diag_log(f"  成功 [{row_num}]")
            self._results[i] = ('success', row_num)
        except Exception as e:
            err_str = str(e)
            retryable = any(k in err_str for k in ['写入', '权限', '拒绝', '被占用', 'Permission', 'denied', 'locked'])
            if retryable:
                diag_log(f"  [{row_num}] 遇到可重试错误，等待2秒后重试: {err_str}")
                self.log.emit(f"  写入错误，2秒后重试...")
                time.sleep(2)
                try:
                    self._process_pdf_internal(pdf_path, process_text, row_num)
                    self.log.emit(f"  重试成功")
                    self.task_status.emit(i, "成功")
                    self._results[i] = ('success', row_num)
                    diag_log(f"  重试成功 [{row_num}]")
                    self.progress.emit(done + 1, total)
                    return
                except Exception as e2:
                    err_str = str(e2)
            self.log.emit(f"  失败: {err_str}")
            self.task_status.emit(i, "失败")
            diag_log(f"  失败 [{row_num}]: {type(e).__name__}: {e}")
            self._results[i] = ('fail', row_num)

        elapsed = time.time() - t0
        self._timings.append(elapsed)

        # ETA 估计
        remaining = total - done
        if self._timings and remaining > 0:
            avg_time = sum(self._timings) / len(self._timings)
            eta_seconds = avg_time * remaining
            if eta_seconds >= 60:
                eta_str = f" 预计剩余 {eta_seconds/60:.1f} 分钟"
            else:
                eta_str = f" 预计剩余 {eta_seconds:.0f} 秒"
            self.status.emit(f"正在处理: {os.path.basename(pdf_path)} ...{eta_str}")

        self.progress.emit(done + 1, total)

