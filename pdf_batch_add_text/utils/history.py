"""水印历史管理 - 智能推荐水印文字"""
import os
import re
import json

from ..config import CHECKPOINT_DIR, WATERMARK_HISTORY_FILE
from ..logger import diag_log


def load_watermark_history():
    """加载用户历史水印文字，用于智能推荐"""
    try:
        if os.path.exists(WATERMARK_HISTORY_FILE):
            with open(WATERMARK_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        diag_log(f"Failed to load watermark history: {e}")
    return []


def save_watermark_history(text):
    """保存水印文字到历史记录"""
    try:
        history = load_watermark_history()
        # 去重：如果已存在则移到最前
        if text in history:
            history.remove(text)
        history.insert(0, text)
        # 只保留最近50条
        history = history[:50]
        os.makedirs(CHECKPOINT_DIR, exist_ok=True)
        with open(WATERMARK_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        diag_log(f"Failed to save watermark history: {e}")


def smart_recommend_text(filename, history):
    """基于文件名+历史记录智能推荐水印文字

    策略：
    1. 文件名包含关键词 → 匹配推荐
    2. 文件名包含日期数字 → 提取日期
    3. 用户历史上最常用的文字
    4. 通用推荐
    """
    name_lower = filename.lower()
    recommendations = []

    # 策略1: 关键词匹配（带上下文）
    keyword_map = [
        (['合同', 'contract', '合约', '协议', 'agreement'], '已审核'),
        (['发票', 'invoice', 'bill', '收据', 'receipt', '报销'], '已报销'),
        (['报告', 'report', '报表', '汇报', 'summary'], '机密文件'),
        (['草案', 'draft', '草稿', '初稿'], '草稿'),
        (['最终', 'final', '定稿', '终版', 'release'], '最终版'),
        (['机密', 'secret', 'confidential', '密级', '绝密'], '严禁外传'),
        (['申请', 'apply', 'application', '申报'], '已批准'),
        (['证书', 'cert', 'certificate', '证明', 'license'], '已验证'),
        (['复印件', 'copy', '副本', '复印'], '复印件'),
        (['归档', 'archive', '存档', '存档件'], '已归档'),
        (['作废', 'void', 'cancel', '废止', '无效'], '已作废'),
        (['模板', 'template', '模板文件', 'sample'], '模板文件'),
        (['签', 'sign', 'signature', '签署'], '已签署'),
        (['预算', 'budget', '财务', 'finance', '账'], '已审批'),
    ]

    matched_keywords = []
    for keywords, text in keyword_map:
        if any(kw in name_lower for kw in keywords):
            matched_keywords.append(text)
            if text not in recommendations:
                recommendations.append(text)

    # 策略2: 提取日期（如文件名包含2024等）
    dates = re.findall(r'(19|20)\d{2}[-_]?(0?[1-9]|1[012])[-_]?(0?[1-9]|[12]\d|3[01])', name_lower)
    dates2 = re.findall(r'(19|20)\d{2}', name_lower)
    if dates or dates2:
        year_text = dates2[0] if dates2 else ''
        if year_text:
            rec = f"FY{year_text}"
            if rec not in recommendations:
                recommendations.append(rec)

    # 策略3: 从历史中推荐与当前文件名语义相关的
    if history:
        for hist_text in history:
            if hist_text not in recommendations:
                # 如果历史文字包含文件名中的关键词
                if any(kw in hist_text.lower() for kw in name_lower.split()):
                    recommendations.append(hist_text)

    # 策略4: 补充通用推荐
    common = ['已审核', '机密文件', '内部资料', '草稿', '已作废', '已验证', '复印件']
    for c in common:
        if c not in recommendations:
            recommendations.append(c)

    # 限制数量
    return recommendations[:6]
