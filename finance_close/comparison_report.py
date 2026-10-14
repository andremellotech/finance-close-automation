"""Visualização local da comparação, com dados e código incorporados."""
import json
from pathlib import Path
import re


def render_comparison(comparison, output):
    web = Path(__file__).resolve().parents[1] / 'web'
    content = {'__CSS__': (web / 'style.css').read_text(encoding='utf-8'), '__JS__': (web / 'comparison.js').read_text(encoding='utf-8'), '__DATA__': json.dumps(comparison, ensure_ascii=False, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c')}
    template = (web / 'comparison-template.html').read_text(encoding='utf-8')
    Path(output).write_text(re.sub(r'__[A-Z_]+__', lambda match: content.get(match[0], match[0]), template), encoding='utf-8')
