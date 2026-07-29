"""自动更新模块 - 通过 GitHub Release API 检查更新"""
import os
import sys
import json
import subprocess
import threading
from datetime import datetime

from ..config import APP_VERSION
from ..logger import diag_log

# GitHub 仓库信息（需在 GitHub 上创建同名仓库）
GITHUB_OWNER = "Ethan-19980224"
GITHUB_REPO = "-pdf-batch-add-text"

# API 端点
RELEASES_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
TAG_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/tags/v{APP_VERSION}"

# 更新日志本地缓存路径
VERSION_CACHE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    ".checkpoints",
    "version_cache.json"
)


def _version_tuple(version: str) -> tuple:
    """将版本号 '4.1.0' 转换为 (4, 1, 0)"""
    parts = []
    for p in version.strip().lstrip("v").split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _save_version_cache(data: dict):
    """保存版本缓存"""
    cache_dir = os.path.dirname(VERSION_CACHE_PATH)
    os.makedirs(cache_dir, exist_ok=True)
    with open(VERSION_CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_version_cache() -> dict:
    """加载版本缓存"""
    try:
        if os.path.exists(VERSION_CACHE_PATH):
            with open(VERSION_CACHE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def check_for_update() -> dict:
    """检查 GitHub 最新版本
    返回:
    {
        "has_update": True/False,
        "latest_version": "4.1.1",
        "changelog": "更新内容...",
        "download_url": "https://github.com/...",
        "cached": False
    }
    """
    cache = _load_version_cache()
    cached_at = cache.get("checked_at", "")
    latest = cache.get("latest_version", "")

    # 24小时内使用缓存
    if latest and cached_at:
        try:
            last_check = datetime.fromisoformat(cached_at)
            if (datetime.now() - last_check).total_seconds() < 86400:
                diag_log(f"[AutoUpdate] 使用缓存版本: {latest} (检查于 {cached_at})")
                return {
                    "has_update": _version_tuple(latest) > _version_tuple(APP_VERSION),
                    "latest_version": latest,
                    "changelog": cache.get("changelog", ""),
                    "download_url": cache.get("download_url", ""),
                    "cached": True
                }
        except Exception:
            pass

    try:
        import requests
        headers = {"Accept": "application/vnd.github.v3+json"}
        resp = requests.get(RELEASES_URL, headers=headers, timeout=5)

        if resp.status_code == 200:
            data = resp.json()
            latest_tag = data.get("tag_name", "").lstrip("v")
            body = data.get("body", "暂无更新说明")
            # 获取下载链接
            assets = data.get("assets", [])
            download_url = ""
            if assets:
                # 优先选择 .exe 文件
                for asset in assets:
                    name = asset.get("name", "")
                    if name.endswith(".exe"):
                        download_url = asset.get("browser_download_url", "")
                        break
                if not download_url and assets:
                    download_url = assets[0].get("browser_download_url", "")

            result = {
                "has_update": _version_tuple(latest_tag) > _version_tuple(APP_VERSION),
                "latest_version": latest_tag,
                "changelog": body[:500],
                "download_url": download_url,
                "cached": False
            }

            # 保存到缓存
            _save_version_cache({
                "latest_version": latest_tag,
                "changelog": body[:500],
                "download_url": download_url,
                "checked_at": datetime.now().isoformat()
            })
            diag_log(f"[AutoUpdate] 最新版本: {latest_tag}")
            return result

        elif resp.status_code == 403:
            # API 限速，使用缓存
            diag_log(f"[AutoUpdate] API 限速 (403)，使用缓存")
            return {
                "has_update": latest and _version_tuple(latest) > _version_tuple(APP_VERSION),
                "latest_version": latest,
                "changelog": cache.get("changelog", ""),
                "download_url": cache.get("download_url", ""),
                "cached": True
            }
        else:
            diag_log(f"[AutoUpdate] API 返回 {resp.status_code}")
            return {"has_update": False, "latest_version": APP_VERSION, "changelog": "", "download_url": "", "cached": False}

    except requests.exceptions.Timeout:
        diag_log("[AutoUpdate] 请求超时，使用缓存")
        return {
            "has_update": latest and _version_tuple(latest) > _version_tuple(APP_VERSION),
            "latest_version": latest,
            "changelog": cache.get("changelog", ""),
            "download_url": cache.get("download_url", ""),
            "cached": True
        }
    except requests.exceptions.ConnectionError:
        diag_log("[AutoUpdate] 网络连接失败，跳过更新检查")
        return {"has_update": False, "latest_version": APP_VERSION, "changelog": "", "download_url": "", "cached": False}
    except Exception as e:
        diag_log(f"[AutoUpdate] 检查更新失败: {e}")
        return {"has_update": False, "latest_version": APP_VERSION, "changelog": "", "download_url": "", "cached": False}


def download_and_update(download_url: str, output_dir: str = None):
    """下载最新版本的 .exe 并替换当前文件
    需要管理员权限

    返回 True 表示更新成功，False 表示失败
    """
    if not output_dir:
        output_dir = os.path.dirname(os.path.abspath(__file__))

    target_path = os.path.join(output_dir, "PDF批量添加文字.exe")

    try:
        import requests
        diag_log(f"[AutoUpdate] 开始下载: {download_url}")
        resp = requests.get(download_url, stream=True, timeout=30)

        if resp.status_code != 200:
            diag_log(f"[AutoUpdate] 下载失败: HTTP {resp.status_code}")
            return False

        total = int(resp.headers.get('content-length', 0))
        tmp_path = target_path + ".tmp"
        downloaded = 0

        with open(tmp_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    diag_log(f"[AutoUpdate] 下载进度: {downloaded/total*100:.1f}%")

        # 重命名（替换原文件）
        import shutil
        if os.path.exists(target_path):
            os.remove(target_path)
        shutil.move(tmp_path, target_path)

        diag_log(f"[AutoUpdate] 更新成功: {target_path}")
        return True

    except Exception as e:
        diag_log(f"[AutoUpdate] 更新失败: {e}")
        return False


def check_update_in_background(callback=None):
    """在后台线程中检查更新
    callback: lambda (has_update, latest_version, changelog, download_url)
    """
    def _check():
        result = check_for_update()
        if callback:
            callback(
                result["has_update"],
                result["latest_version"],
                result["changelog"],
                result["download_url"]
            )
    thread = threading.Thread(target=_check, daemon=True)
    thread.start()
    return thread
