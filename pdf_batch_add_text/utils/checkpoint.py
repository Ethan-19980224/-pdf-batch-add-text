"""检查点管理 - 保存/恢复处理进度"""
import os
import json
from datetime import datetime

from ..config import CHECKPOINT_DIR, CHECKPOINT_FILE, APP_VERSION
from ..logger import diag_log

CHECKPOINT_TASKS_FILE = os.path.join(CHECKPOINT_DIR, "resume_tasks.json")


def save_checkpoint(output_dir, text_settings, tasks, valid_indices):
    """保存处理进度到硬盘，支持崩溃恢复"""
    try:
        os.makedirs(CHECKPOINT_DIR, exist_ok=True)
        # 只保存必要信息
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'version': APP_VERSION,
            'output_dir': output_dir,
            'text_settings': text_settings,
            'valid_indices': valid_indices,
        }
        with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, ensure_ascii=False, indent=2)
        # tasks 可能较大，单独保存
        tasks_safe = [
            {k: v for k, v in t.items() if k in ('row', 'filename', 'text', 'page_texts', 'pdf_path', 'pages', 'status')}
            for t in tasks
        ]
        with open(CHECKPOINT_TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks_safe, f, ensure_ascii=False, indent=2)
        diag_log(f"检查点已保存: {len(tasks)} 个任务")
    except Exception as e:
        diag_log(f"保存检查点失败: {e}")


def load_checkpoint():
    """恢复检查点，返回 (output_dir, text_settings, tasks, valid_indices) 或 None"""
    try:
        if not os.path.exists(CHECKPOINT_FILE) or not os.path.exists(CHECKPOINT_TASKS_FILE):
            return None
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            cp = json.load(f)
        with open(CHECKPOINT_TASKS_FILE, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        return (
            cp.get('output_dir', ''),
            cp.get('text_settings', {}),
            tasks,
            cp.get('valid_indices', []),
        )
    except Exception as e:
        diag_log(f"读取检查点失败: {e}")
        return None


def clear_checkpoint():
    """清除检查点（处理完成或用户取消恢复时调用）"""
    try:
        for f in [CHECKPOINT_FILE, CHECKPOINT_TASKS_FILE]:
            if os.path.exists(f):
                os.remove(f)
        diag_log("检查点已清除")
    except Exception as e:
        diag_log(f"清除检查点失败: {e}")
