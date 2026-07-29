@echo off
echo ============================================
echo   PDF 批量添加文字 - GitHub 推送脚本
echo ============================================
echo.

cd /d "%~dp0"

echo [1/3] 添加 GitHub remote...
git remote add origin https://github.com/Ethan-19980224/-pdf-batch-add-text.git 2>nul
if %errorlevel% neq 0 (
    echo remote 已存在，跳过。
)

echo [2/3] 推送代码到 GitHub...
echo.
echo 请在浏览器打开 https://github.com/settings/tokens
echo 创建一个 Personal Access Token (classic)，勾选 "repo" 权限
echo.
echo 把 Token 粘贴到终端提示处当作密码（输入时不显示字符）
echo.
echo.

git push -u origin master

echo.
echo ============================================
echo   推送完成！
echo   仓库地址: https://github.com/Ethan-19980224/-pdf-batch-add-text
echo ============================================
echo.
pause