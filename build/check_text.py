"""Check that the edition's visible text equals the original's.

    python3 build/check_text.py
"""
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def txt(s):
    s = re.sub(r"<head>.*?</head>", "", s, flags=re.S | re.I)
    s = re.sub(r'<div class="transnote">.*?</div>', "", s, flags=re.S)
    s = re.sub(r'<span class="tip"[^>]*></span>|<a class="ref"[^>]*>|</a>', "", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


a = txt(open(os.path.join(ROOT, "3800-h.htm"), "rb").read().decode("latin-1"))
b = txt(open(os.path.join(ROOT, "3800-h-tooltips.html"), encoding="utf-8").read())
if a == b:
    print("text identical (%d characters)" % len(a))
else:
    i = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    print("TEXT DIFFERS at", i)
    print(repr(a[i - 80:i + 80]))
    print(repr(b[i - 80:i + 80]))
    raise SystemExit(1)
