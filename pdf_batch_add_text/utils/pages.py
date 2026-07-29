"""页码范围解析 - 将页码范围字符串解析为 0-based 页面索引列表"""

# 页码范围解析结果缓存（避免同一字符串重复解析）
_PAGE_RANGE_CACHE = {}


def parse_page_range(pr, total_pages):
    """解析页码范围字符串，返回 0-based 页面索引列表（支持缓存）"""
    key = (str(pr).strip(), total_pages)
    if key in _PAGE_RANGE_CACHE:
        return _PAGE_RANGE_CACHE[key]
    pr_str = key[0]
    if pr_str in ("", "全部", "all", "All"):
        result = list(range(total_pages))
        _PAGE_RANGE_CACHE[key] = result
        return result
    indices = []
    try:
        for part in pr_str.split(','):
            part = part.strip()
            if not part:
                continue
            if '-' in part:
                start, end = part.split('-', 1)
                start = int(start.strip()) - 1
                end = int(end.strip())
                indices.extend(range(max(0, start), min(end, total_pages)))
            else:
                idx = int(part.strip()) - 1
                if 0 <= idx < total_pages:
                    indices.append(idx)
    except (ValueError, AttributeError):
        result = list(range(total_pages))
        _PAGE_RANGE_CACHE[key] = result
        return result
    result = sorted(set(indices)) if indices else list(range(total_pages))
    _PAGE_RANGE_CACHE[key] = result
    return result
