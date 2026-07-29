# PDF批量添加文字 项目记忆

## 项目概况
- **版本**: 4.1.0 (2026-07-28 全面优化)
- **技术栈**: PyQt6 + PyMuPDF(fitz) + openpyxl
- **架构**: 模块化包 `pdf_batch_add_text/`（28个.py文件）+ 旧版单体脚本（已转为启动器）
- **风格**: 浅蓝素描纸质主题

## 核心文件
- `pdf_batch_add_text.py` — 入口启动器（30行，导入新版包）
- `pdf_batch_add_text/main.py` — 应用入口
- `pdf_batch_add_text/main_window.py` — 主窗口（2228行，CSS内联）
- `pdf_batch_add_text/pdf/processor.py` — PDF核心处理逻辑（360行）
- `pdf_batch_add_text/pdf/workers.py` — 处理线程（300行）
- `pdf_batch_add_text/pdf/tools.py` — PDF辅助工具（页码/页脚/文本提取）
- `pdf_batch_add_text/pdf/tools2.py` — PDF增强工具（图片水印/旋转/加密）
- `pdf_batch_add_text/config.py` — 配置常量（v4.1.0）
- `pdf_batch_add_text/logger.py` — 诊断日志（缓冲写入桌面）
- `pdf_batch_add_text/utils/` — 工具模块
- `pdf_batch_add_text/dialogs/` — 对话框模块（8个）
- `pdf_batch_add_text/widgets/` — 自定义控件（2个）

## 新增功能 (v4.1.0)
- **添加页码**: 为所有PDF自动添加页码（可调字号/颜色/透明度/位置/粗体斜体）
- **添加页脚**: 为所有PDF添加自定义页脚文字（全部样式参数可调）
- **文本提取**: 从PDF提取文字，支持预览+保存为.txt/.xlsx
- **PDF工具集按钮**: 主界面新增"🔧 PDF 工具"按钮
- **图片水印**: 为PDF添加图片水印，支持透明度/缩放/位置
- **页面旋转**: 90°/180°/270°旋转，可指定页码范围
- **PDF加密**: 用户密码/所有者密码，控制打印/修改/复制/批注权限
- **PDF增强工具按钮**: 主界面新增"⚡ 增强工具"按钮

## 关键路径
- 检查点: `pdf_batch_add_text/.checkpoints/`
- 水印历史: `pdf_batch_add_text/.checkpoints/watermark_history.json`
- 诊断日志: `~/Desktop/pdf_batch_diag.log`

## 运行方式
```bash
python pdf_batch_add_text.py        # 直接运行启动器
python -m pdf_batch_add_text.main  # 模块化包运行（推荐）
```

## 优化历史
### 2026-07-28 全面优化 (v4.1.0)
- 修复 processor.py 3处 + history.py 2处 + main_window.py 4处 = 9处裸 `except: pass` → `diag_log`
- logger.py diag_flush 增加 stderr fallback
- config.py 版本号 4.0.0→4.1.0，添加 DEFAULT_OPACITY
- workers.py 动态方法绑定从模块级移到 `__init__`（`__get__` 绑定），更安全可靠
- 旧版 pdf_batch_add_text.py（5304行）→ 精简为30行启动器
- main_window.py CSS提取：~240行硬编码CSS → theme.py集中管理，main_window.py减至1966行
- 删除 5个 `__pycache__` 目录（26个.pyc文件），删除 pdf_batch_add_text.py.backup

- `.gitignore` — 排除非项目目录 (.trae/.reasonix/build/dist/spec/__pycache__)
- `push_to_github.bat` — GitHub 推送脚本
- `GITHUB_RELEASE_GUIDE.md` — GitHub Release 发布指南

### 2026-07-29 GitHub 上传 + 自动更新
- 新增 `utils/auto_update.py` — 自动更新模块（GitHub Release API + 24h缓存）
- main_window.py 新增 `_check_update_on_startup` / `_check_update_now` / `_show_update_notification`
- 添加"🔄 检查更新"按钮到状态栏
- Git 初始化 + 首次提交（~63个文件，~7000行）
- 仓库：`https://github.com/Pengpeng11/pdf-batch-add-text`
