#!/usr/bin/env python3
"""AI-slop style checker for Markdown articles.

Usage:
    python3 scripts/ai_slop_check.py content/zh-tw/posts/<slug>/index.md

Severity:
    ERROR   P1 hard rule violated -> exit 1
    WARNING needs human judgement  -> exit 0
    INFO    statistics             -> exit 0
"""

import argparse
import html
import pathlib
import re
import statistics
import sys

ABSOLUTE = [
    "深入探討", "雙刃劍", "眾所周知", "顯而易見", "不可否認",
    "見證了", "畫卷", "浪潮", "里程碑", "未來可期",
    "革命性", "顛覆性", "前所未有", "重新定義", "劃時代",
    "引人入勝",
]

CONTEXTUAL = [
    "此外", "值得注意的是", "更重要的是", "總而言之",
    "綜上所述", "由此可見", "換句話說", "首先", "其次",
]

LIST_RE = re.compile(r"^(?:[-*+]\s|\d+\.\s)")
SEP_RE = re.compile(r":?-{2,}:?")


def units(text):
    """One unit = one CJK char, one English word, or one digit group."""
    return (
        len(re.findall(r"[\u4e00-\u9fff]", text))
        + len(re.findall(r"[A-Za-z]+", text))
        + len(re.findall(r"\d[\d,.]*", text))
    )


def clean(text):
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[`*_]", "", text)
    return text.strip()


def load(path):
    lines = pathlib.Path(path).read_text(encoding="utf-8").split("\n")
    start = 0
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        start = i + 1

    rows, fence, math = [], False, False
    for n, line in enumerate(lines[start:], start + 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            fence = not fence
            continue
        if stripped.startswith("$$"):
            math = not math
            continue
        if fence or math:
            continue
        rows.append((n, line))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()

    rows = load(args.path)
    prose, tables = [], []
    paragraphs, current = [], 0

    def flush():
        nonlocal current
        if current:
            paragraphs.append(current)
            current = 0

    for n, line in rows:
        stripped = line.strip()
        if not stripped or stripped == "---":
            flush()
            continue
        if stripped.startswith("|"):
            tables.append((n, stripped))
            flush()
            continue
        if stripped.startswith("{{<") or stripped.startswith("#"):
            flush()
            continue
        if stripped.startswith(">"):
            flush()
            continue
        if LIST_RE.match(stripped):
            prose.append((n, LIST_RE.sub("", stripped)))
            flush()
            continue
        prose.append((n, stripped))
        current += len(
            [c for c in re.split(r"(?<=[。！？])", clean(stripped)) if c.strip()]
        )
    flush()

    sentences = []
    for n, line in prose:
        for chunk in re.split(r"(?<=[。！？])", clean(line)):
            if chunk.strip():
                sentences.append((n, chunk.strip()))

    lengths = [units(s) for _, s in sentences]
    median = statistics.median(lengths) if lengths else 0
    errors = []

    for n, s in sentences:
        u = units(s)
        if u > 35:
            errors.append(f"L{n} 句長 {u}（>35）：{s[:60]}")
        elif u > 25:
            print(f"WARNING L{n} 句長 {u}（26–35，確認是否技術句）：{s[:60]}")

    authors = [(n, line) for n, line in rows if not line.strip().startswith(">")]
    scan_text = "\n".join(line for _, line in authors)

    for word in ABSOLUTE:
        hits = [n for n, line in authors if word in line]
        if hits:
            errors.append(f"絕對禁用詞「{word}」：行 {hits}")

    for word in CONTEXTUAL:
        count = scan_text.count(word)
        if count:
            print(f"WARNING 情境禁用詞「{word}」×{count}（確認有無邏輯功能）")

    if re.search(r"我們|筆者", scan_text):
        errors.append("第一人稱（我們／筆者）")
    if re.search(r"我(?!們)", scan_text):
        print("WARNING 出現「我」（確認是否為引文）")

    bold = len(re.findall(r"\*\*[^*]+\*\*", scan_text))
    if bold > 30:
        print(f"WARNING 粗體 {bold} 處（>30）")

    if paragraphs:
        print(f"INFO 最長散文段 {max(paragraphs)} 句")

    for n, line in rows:
        if not line.strip().startswith("{{<"):
            continue
        match = re.search(r'caption="([^"]*)"', line)
        if match:
            u = units(clean(match.group(1)))
            if u > 60:
                print(f"WARNING L{n} caption {u} units（>60）")

    for n, line in tables:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(not c or SEP_RE.fullmatch(c) for c in cells):
            continue
        for cell in cells:
            u = units(clean(cell))
            if u > 35:
                print(f"WARNING L{n} 表格 cell {u} units：{cell[:40]}")

    for message in errors:
        print(f"ERROR {message}")

    over = sum(1 for x in lengths if x > 25)
    print(
        f"INFO 句數 {len(sentences)}｜>25 {over}"
        f"｜中位數 {median:g}｜粗體 {bold}｜表格列 {len(tables)}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
