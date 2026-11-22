#!/usr/bin/env python3
"""Реестр источников, заметки и карта мест — по форме (docs/sources/; D-05).

  * docs/sources/REGISTRY.md: номера S-NN без повторов; вид repo/site/self;
    доступ public/private; адрес и клон по виду; ровно один источник self;
  * docs/sources/NOTES.md: у каждой заметки N-NNNN есть source (из реестра),
    observed (ISO, не позже сегодня), origin, content, verify;
  * docs/sources/MAP.md: источник из реестра вида repo/self, коммит — полный
    SHA, место — путь от корня или tag:ИМЯ;
  * каждый источник из таблицы тегов docs/direction/SCOPE.md есть в реестре.

Что места и коммиты действительно существуют, сверяет check_refs.py по
клонам (полный прогон).

    python3 tools/verify/check_registry.py

Код возврата: 0 — чисто; 1 — нарушения.
"""
import re
import sys

import docmodel as dm


def check(root=None):
    r = dm.Report("реестр источников")
    registry, errors = dm.load_registry(root)
    r.extend(errors)
    selfs = [s for s, v in registry.items() if v["kind"] == "self"]
    if len(selfs) != 1:
        r.err(dm.REGISTRY, f"источник вида self (этот репозиторий) должен быть ровно один, есть {len(selfs)}")

    notes, errors = dm.load_notes(root)
    r.extend(errors)
    for nid, n in sorted(notes.items()):
        where = n["line"]
        for key in dm.NOTE_FIELDS:
            if not n.get(key):
                r.err(where, f"{nid}: нет поля {key}")
        if n.get("source") and n["source"] not in registry:
            r.err(where, f"{nid}: источника {n['source']} нет в реестре")
        if n.get("observed"):
            d = dm.iso(n["observed"])
            if d is None:
                r.err(where, f"{nid}: observed не дата ISO")
            elif d > dm.today():
                r.err(where, f"{nid}: observed позже сегодняшнего дня")

    entries, errors = dm.load_map(root)
    r.extend(errors)
    for where, sid, place, sha, what in entries:
        if sid not in registry or registry[sid]["kind"] not in ("repo", "self"):
            r.err(where, f"{sid}: нет в реестре или не репозиторий")
        if not dm.SHA.match(sha):
            r.err(where, "коммит — полный SHA из 40 знаков")
        if not (re.fullmatch(r"tag:[A-Za-z0-9_.-]+", place)
                or re.fullmatch(r"[A-Za-z0-9_.()\-/]+[A-Za-z0-9_.()-]", place)) or place.startswith("/"):
            r.err(where, f"место не «путь от корня» и не «tag:ИМЯ»: {place!r}")
        if not what:
            r.err(where, "пустое «Что там»")

    tags, errors = dm.load_scope_tags(root)
    r.extend(errors)
    for tag, sources in sorted(tags.items()):
        if not sources:
            r.err(dm.SCOPE, f"у тега {tag} нет источников")
        for s in sources:
            if s not in registry:
                r.err(dm.SCOPE, f"тег {tag}: источника {s} нет в реестре")

    return r.finish(f"источников {len(registry)}, заметок {len(notes)}, мест в карте {len(entries)}")


if __name__ == "__main__":
    sys.exit(check())
