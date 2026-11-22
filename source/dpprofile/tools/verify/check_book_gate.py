#!/usr/bin/env python3
"""Шлюз книги: без выпуска VoxelRPG в Steam и решения — ни строки прозы (D-01, D-02).

  * блок book-gate в docs/book/STATUS.md: book_writing — forbidden или
    allowed; steam_release_fact — none или активный факт с меткой
    steam-release; permission_decision — none или принятое решение с
    меткой book-permission, которое ссылается на этот факт и принято не
    раньше его даты;
  * allowed — только когда заданы и факт, и решение, а этап 5 ROADMAP
    начат; forbidden — этап 5 не выполнен;
  * пока forbidden: в docs/book/ только STATUS.md, OUTLINE.md и
    NON_GOALS.md; нигде в репозитории нет файлов и каталогов с именами
    вроде chapter, draft, глава, черновик; заголовков «Глава …» нет вне
    OUTLINE.md;
  * всегда: OUTLINE.md и NON_GOALS.md — только заголовки, пункты списка
    до 140 знаков, вводные строки «>» до первого раздела и комментарии;
    абзацев прозы нет; в STATUS.md вне блока — не больше 40 строк.

    python3 tools/verify/check_book_gate.py

Код возврата: 0 — чисто; 1 — нарушения.
"""
import os
import re
import sys

import docmodel as dm

BOOK_DIR = "docs/book"
ALLOWED_FILES = {"STATUS.md", "OUTLINE.md", "NON_GOALS.md"}
STRUCTURE_ONLY = ("docs/book/OUTLINE.md", "docs/book/NON_GOALS.md")
DRAFT_NAME = re.compile(r"chapter|draft|manuscript|глав[аы]|черновик|рукопис", re.I)
CHAPTER_HEADING = re.compile(r"^#{1,6}\s+(Глава|Chapter)\b", re.I)
MAX_ITEM = 140
MAX_STATUS_LINES = 40


def check(root=None):
    root = root or dm.ROOT
    r = dm.Report("шлюз книги")
    status, errors = dm.load_status(root)
    r.extend(errors)
    facts, _, _ = dm.load_facts(root)
    decisions, _, _ = dm.load_decisions(root)
    stages, _ = dm.load_stages(root)
    stage5 = next((s for s in stages if s["n"] == 5), None)

    writing = status.get("book_writing")
    fact_id = status.get("steam_release_fact")
    dec_id = status.get("permission_decision")
    if writing not in ("forbidden", "allowed"):
        r.err(dm.STATUS, f"book_writing — forbidden или allowed, а не {writing!r}")
    fact = None
    if fact_id and fact_id != "none":
        if fact_id not in facts:
            r.err(dm.STATUS, f"steam_release_fact {fact_id}: нет такого факта")
        else:
            fact = facts[fact_id][1]
            if not dm.is_active(fact) or "steam-release" not in (fact.get("marks") or []):
                r.err(dm.STATUS, f"steam_release_fact {fact_id}: факт не активен или без метки steam-release")
    if dec_id and dec_id != "none":
        d = decisions.get(dec_id)
        if not d:
            r.err(dm.STATUS, f"permission_decision {dec_id}: нет такого решения")
        else:
            if not dm.accepted(d) or d.get("mark") != "book-permission":
                r.err(dm.STATUS, f"permission_decision {dec_id}: решение не принято или без метки book-permission")
            if fact_id in (None, "none") or fact_id not in d["text"]:
                r.err(dm.STATUS, f"решение {dec_id} не ссылается на факт о выпуске (steam_release_fact)")
            if fact and dm.iso(d.get("date")) and dm.iso(fact.get("date")) \
                    and dm.iso(d["date"]) < dm.iso(fact["date"]):
                r.err(dm.STATUS, f"решение {dec_id} принято раньше выпуска ({fact.get('date')})")

    if writing == "allowed":
        if fact_id in (None, "none") or dec_id in (None, "none"):
            r.err(dm.STATUS, "book_writing: allowed без факта о выпуске и решения (D-02)")
        if not stage5 or stage5["state"] == "—":
            r.err(dm.STATUS, "book_writing: allowed, а этап 5 ROADMAP не начат")
    elif writing == "forbidden":
        if stage5 and stage5["state"].startswith("выполнен"):
            r.err(dm.STATUS, "этап 5 выполнен, а book_writing — forbidden")
        check_closed(r, root)

    for rel in STRUCTURE_ONLY:
        if dm.exists(rel, root):
            check_structure(r, rel, dm.read(rel, root))
        else:
            r.err(rel, "файла нет")
    if dm.exists(dm.STATUS, root):
        text = re.sub(r"<!-- book-gate:begin -->.*?<!-- book-gate:end -->", "",
                      dm.read(dm.STATUS, root), flags=re.S)
        lines = [l for l in text.split("\n") if l.strip()]
        if len(lines) > MAX_STATUS_LINES:
            r.err(dm.STATUS, f"вне блока book-gate {len(lines)} строк (до {MAX_STATUS_LINES}): статус, не текст")

    return r.finish(f"book_writing: {writing}")


def check_closed(r, root):
    book = os.path.join(root, BOOK_DIR)
    if os.path.isdir(book):
        for name in sorted(os.listdir(book)):
            if name not in ALLOWED_FILES:
                r.err(f"{BOOK_DIR}/{name}", "пока книга не пишется, в docs/book/ только "
                                            + ", ".join(sorted(ALLOWED_FILES)))
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        dirnames[:] = [d for d in dirnames
                       if not d.startswith(".") and not (rel_dir == "." and d == "build")
                       and os.path.normpath(os.path.join(rel_dir, d)) != "tools/verify"]
        for name in dirnames + filenames:
            if DRAFT_NAME.search(name):
                r.err(os.path.normpath(os.path.join(rel_dir, name)),
                      "имя похоже на черновик книги — до шлюза D-02 таких файлов нет")
        for name in filenames:
            rel = os.path.normpath(os.path.join(rel_dir, name))
            if not name.endswith(".md") or rel == "docs/book/OUTLINE.md":
                continue
            for n, line in enumerate(dm.read(rel, root).split("\n"), start=1):
                if CHAPTER_HEADING.match(line):
                    r.err(f"{rel}:{n}", "заголовок главы вне OUTLINE.md — до шлюза D-02 глав нет")


def check_structure(r, rel, text):
    in_fence, seen_section = False, False
    for n, line in enumerate(text.split("\n"), start=1):
        where = f"{rel}:{n}"
        if line.startswith("```"):
            r.err(where, "блоки кода в документе книги запрещены")
            continue
        if not line.strip():
            continue
        if re.match(r"^#{1,4} \S", line):
            if line.startswith("## "):
                seen_section = True
            if len(line) > 120:
                r.err(where, "заголовок длиннее 120 знаков")
            continue
        if re.match(r"^(  )?- \S", line):
            if len(line.strip()) > MAX_ITEM:
                r.err(where, f"пункт длиннее {MAX_ITEM} знаков — это уже проза")
            continue
        if line.startswith("> ") and not seen_section:
            continue
        if re.fullmatch(r"\s*<!--.*-->\s*", line):
            continue
        r.err(where, "проза: здесь только заголовки и короткие пункты (D-01, D-02)")


if __name__ == "__main__":
    sys.exit(check())
