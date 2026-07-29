# 创建 GitHub Release 指南

## 首次操作（一次性）

### 1. 创建 GitHub 仓库

在浏览器打开：https://github.com/Pengpeng11

点击 "New" 创建新仓库：
- Repository name: `pdf-batch-add-text`
- Description: PDF 批量添加文字 — 同一 PDF 同时添加多处文字
- Public: ✅
- 不要勾选 "Add a README file"（代码已经在本地）

### 2. 设置 Git 用户信息

```bash
cd "Z:\软件开发\PDF批量添加文字"
git config user.name "Pengpeng11"
git config user.email "你的GitHub邮箱"
```

### 3. 推送代码

运行 `push_to_github.bat`，或在终端：
```bash
git push -u origin master
```
密码用 Personal Access Token（在 https://github.com/settings/tokens 生成，勾选 repo 权限）。

### 4. 创建首个 Release（支持自动更新）

首次推送后：

1. 打开 https://github.com/Pengpeng11/pdf-batch-add-text/releases
2. 点击 "Create a new release"
3. **Tag version**: `v4.1.0`（必须以 v 开头，与 config.py 中 APP_VERSION 一致）
4. **Release title**: `v4.1.0 - PDF 批量添加文字`
5. **Description**: 粘贴 CHANGELOG 内容
6. 上传 `PDF批量添加文字.exe` 作为 attachment
7. 点击 "Publish release"

**自动更新原理：**
- 应用启动时自动调用 `https://api.github.com/repos/Pengpeng11/pdf-batch-add-text/releases/latest`
- 比较远程 tag 版本与本地版本
- 若远程版本更高，状态栏显示更新提醒
- 点击"🔄 检查更新"按钮可手动检查

### 发布新版本时

1. 修改 `pdf_batch_add_text/config.py` 中的 `APP_VERSION`
2. 提交代码并 push
3. 在 GitHub 创建新 Release（tag 必须匹配 APP_VERSION）
4. 上传新的 .exe 到 release assets
5. 已运行的用户启动时自动检测到新版本