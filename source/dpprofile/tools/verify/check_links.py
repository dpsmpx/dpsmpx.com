#!/usr/bin/env python3
"""Внутренние ссылки ведут туда, где что-то есть.

Ссылка в пустоту хуже её отсутствия: она выглядит как обоснование.
Проверяются все .md репозитория (кроме build/ и блоков кода):

  * markdown-ссылки [текст](путь#якорь) на файлы репозитория — файл есть,
    якорь — заголовок в нём (по правилам GitHub);
  * пути в обратных кавычках `docs/…` и `tools/…` существуют (маска —
    совпадает хоть с одним файлом; часть после «@» — ссылка на коммит
    источника, не путь);
  * номера F-NNNN, I-NNNN, H-NNNN, S-NN, N-NNNN, D-NN определены: факт,
    вывод или гипотеза — файлом, источник — строкой реестра, заметка —
    заголовком в docs/sources/NOTES.md, решение — заголовком в
    docs/direction/DECISIONS.md. Номера чужих журналов пишутся с
    префиксом репозитория (`DPpass:D-24`) и не проверяются.

    python3 tools/verify/check_links.py

Код возврата: 0 — чисто; 1 — висячие ссылки.
"""
import glob
import os
import re
import sys

import docmodel as dm

MD_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
CODE_PATH = re.compile(r"`((?:docs|tools)/[A-Za-z0-9_./*-]*[A-Za-z0-9_*/])[^`]*`")
FENCE = re.compile(r"^```.*?^```", re.S | re.M)


def md_files(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        dirnames[:] = [d for d in dirnames if not (d.startswith(".") or (rel_dir == "." and d == "build"))]
        for name in filenames:
            if name.endswith(".md"):
                out.append(os.path.normpath(os.path.join(rel_dir, name)))
    return sorted(out)


def slugs(text):
    seen, out = {}, set()
    for line in FENCE.sub("", text).split("\n"):
        m = re.match(r"^#{1,6} (.+?)\s*$", line)
        if not m:
            continue
        s = re.sub(r"[^\w\- ]", "", m.group(1).strip().lower()).replace(" ", "-")
        n = seen.get(s, 0)
        out.add(s if n == 0 else f"{s}-{n}")
        seen[s] = n + 1
    return out


def check(root=None):
    root = root or dm.ROOT
    r = dm.Report("внутренние ссылки")
    facts, _, _ = dm.load_facts(root)
    insights, _, _ = dm.load_insights(root)
    registry, _ = dm.load_registry(root)
    notes, _ = dm.load_notes(root)
    decisions, _, _ = dm.load_decisions(root)
    defined = {"F": set(facts), "I": {k for k in insights if k.startswith("I-")},
               "H": {k for k in insights if k.startswith("H-")}, "S": set(registry),
               "N": set(notes), "D": set(decisions)}
    digits = {"F": 4, "I": 4, "H": 4, "S": 2, "N": 4, "D": 2}

    files = md_files(root)
    n_links = 0
    for rel in files:
        text = FENCE.sub("", dm.read(rel, root))
        base = os.path.dirname(rel)
        for n, line in enumerate(text.split("\n"), start=1):
            where = f"{rel}:{n}"
            for target in MD_LINK.findall(line):
                if re.match(r"^[a-z]+:", target):
                    continue
                n_links += 1
                file_part, _, anchor = target.partition("#")
                dest = os.path.normpath(os.path.join(base, file_part)) if file_part else rel
                if not os.path.exists(os.path.join(root, dest)):
                    r.err(where, f"ссылка на несуществующий файл: {target}")
                elif anchor and dest.endswith(".md") and anchor not in slugs(dm.read(dest, root)):
                    r.err(where, f"нет заголовка для якоря #{anchor} в {dest}")
            for p in CODE_PATH.findall(line):
                p = p.split("@")[0]
                if "NN" in p:
                    continue  # шаблон имени: F-NNNN.md, D-NN
                n_links += 1
                if not glob.glob(os.path.join(root, p)):
                    r.err(where, f"нет пути `{p}`")
            for prefix, ids in defined.items():
                for ref in dm.ids_in(line, prefix, digits[prefix]):
                    n_links += 1
                    if ref not in ids:
                        r.err(where, f"номер {ref} нигде не определён")
    return r.finish(f"файлов {len(files)}, ссылок {n_links}")


if __name__ == "__main__":
    sys.exit(check())
