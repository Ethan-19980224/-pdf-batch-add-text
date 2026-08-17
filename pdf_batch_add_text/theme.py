"""CSS 主题模板 - 深海蓝 + 金箔奢华风格"""
from .config import COLORS

def _render(css_str: str) -> str:
    try:
        return css_str.format(**{k.replace('-', '_'): v for k, v in COLORS.items()})
    except KeyError:
        return css_str