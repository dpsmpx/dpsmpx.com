#!/usr/bin/env python3
"""Нет оценочных формулировок, выводов в фактах и предписаний в методе (D-07).

Списки — tools/verify/forbidden_claims.txt. Где что проверяется:

  * hype (оценки, лозунги, прогнозы успеха) — все документы docs/,
    README.md, TODO.md, CLAUDE.md;
  * inference (маркеры вывода и догадки) — файлы фактов F-NNNN.md и
    события хронологии: факт — без интерпретаций;
  * prescriptive (предписания) — описание метода docs/method/.

Блоки кода не проверяются.

    python3 tools/verify/check_forbidden.py

Код возврата: 0 — чисто; 1 — нарушения.
"""
import glob
import os
import re
import sys

import docmodel as dm

LIST = "tools/verify/forbidden_claims.txt"
FENCE = re.compile(r"^```.*?^```", re.S | re.M)


def load_patterns(root):
    patterns = {"hype": [], "inference": [], "prescriptive": []}
    for n, line in enumerate(dm.read(LIST, root).split("\n"), start=1):
        if not line.strip() or line.startswith("#"):
            continue
        cls, sep, rx = line.partition(": ")
        if not sep or cls not in patterns:
            raise SystemExit(f"✗ {LIST}:{n}: строка не «класс: выражение»")
        patterns[cls].append(re.compile(rx, re.I))
    return patterns


def files(root, *masks):
    out = []
    for mask in masks:
        out += sorted(os.path.relpath(p, root) for p in glob.glob(os.path.join(root, mask)))
    return out


def scan(r, root, rel, patterns, cls, only=None):
    text = FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), dm.read(rel, root))
    for n, line in enumerate(text.split("\n"), start=1):
        if only and not only(line):
            continue
        for rx in patterns:
            m = rx.search(line)
            if m:
                r.err(f"{rel}:{n}", f"запрещённая формулировка ({cls}): «{m.group(0)}»")


def check(root=None):
    root = root or dm.ROOT
    r = dm.Report("запрещённые формулировки")
    patterns = load_patterns(root)
    hype = files(root, "docs/facts/*.md", "docs/timeline/*.md", "docs/insights/*.md",
                 "docs/method/*.md", "docs/book/*.md", "docs/sources/*.md", "docs/direction/*.md",
                 "docs/direction/ROADMAP/*.md", "README.md", "TODO.md", "CLAUDE.md")
    for rel in hype:
        scan(r, root, rel, patterns["hype"], "hype")
    for rel in files(root, "docs/facts/F-*.md"):
        scan(r, root, rel, patterns["inference"], "inference")
    if dm.exists(dm.TIMELINE, root):
        scan(r, root, dm.TIMELINE, patterns["inference"], "inference",
             only=lambda line: line.startswith("|"))
    for rel in files(root, "docs/method/*.md"):
        scan(r, root, rel, patterns["prescriptive"], "prescriptive")
    return r.finish(f"проверено файлов {len(set(hype))}, выражений "
                    f"{sum(len(v) for v in patterns.values())}")


if __name__ == "__main__":
    sys.exit(check())
