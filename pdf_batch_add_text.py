#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 批量添加文字工具 - 启动器
将旧版单体脚本重定向到新版模块化包。
用法: python pdf_batch_add_text.py 或 python -m pdf_batch_add_text.main
"""

import sys
import os

# 将项目根目录加入路径，使包可被导入
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# 运行新版模块化应用
try:
    from pdf_batch_add_text.main import main
    main()
except ImportError as e:
    print(f"错误: 无法导入模块化包。请确保在正确的目录中运行。")
    print(f"  详细错误: {e}")
    print(f"  请从项目根目录运行: python -m pdf_batch_add_text.main")
    sys.exit(1)
