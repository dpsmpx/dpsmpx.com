#!/usr/bin/env python3
"""Факты соответствуют схеме (docs/facts/README.md; D-03, D-04, D-05, D-06).

  * в docs/facts/ — только README.md и F-NNNN.md;
  * front matter в узком подмножестве YAML, текста после него нет;
  * обязательные поля есть, неизвестных нет, значения из перечислений;
  * номера не повторяются и совпадают с именем файла; нет двух фактов с
    одной формулировкой и одним местом в источнике;
  * date и observed — даты ISO, date не позже observed, observed не позже
    сегодняшнего дня (факт не бывает о будущем);
  * формулировка — одна фраза до 300 знаков с точкой в конце;
  * теги проектов — из docs/direction/SCOPE.md;
  * источник есть в реестре, вид ссылки подходит виду источника, ref —
    по форме (docs/sources/CITATION.md, «Ссылки»);
  * метка steam-release — только у наблюдаемого факта о voxelrpg со
    ссылкой на страницу магазина Steam (D-02);
  * замена (status: superseded) — с заменяющим фактом и решением.

    python3 tools/verify/check_facts.py

Код возврата: 0 — чисто; 1 — нарушения.
"""
import re
import sys

import docmodel as dm

REQUIRED = ("id", "kind", "date", "statement", "area", "projects", "basis",
            "source", "source_type", "ref", "observed")
OPTIONAL = ("refines", "marks", "status", "superseded_by", "revised_by")
AREAS = ("project", "process", "result")
BASES = ("observed", "stated")
TYPES = {"commit": ("repo", "self"), "file": ("repo", "self"), "release": ("repo",),
         "url": ("site",), "note": ("repo", "self", "site")}
MARKS = ("steam-release",)
STEAM_STORE = "https://store.steampowered.com/"
MAX_STATEMENT = 300


def check(root=None):
    r = dm.Report("схема фактов")
    facts, errors, extra = dm.load_facts(root)
    r.extend(errors)
    for rel in extra:
        r.err(rel, "посторонний файл: в docs/facts/ только README.md и F-NNNN.md")
    registry, reg_errors = dm.load_registry(root)
    notes, _ = dm.load_notes(root)
    tags, tag_errors = dm.load_scope_tags(root)
    decisions, _, _ = dm.load_decisions(root)
    r.extend(reg_errors + tag_errors)

    seen_ids = {}
    seen_content = {}
    for stem, (rel, f, body) in sorted(facts.items()):
        fid = f.get("id")
        if fid in seen_ids:
            r.err(rel, f"номер {fid} повторяется: {seen_ids[fid]} и {rel}")
        else:
            seen_ids[fid] = rel
        for key in REQUIRED:
            if key not in f:
                r.err(rel, f"нет поля {key}")
        for key in f:
            if key not in REQUIRED + OPTIONAL:
                r.err(rel, f"неизвестное поле {key}")
        if body.strip():
            r.err(rel, "текст после front matter запрещён: факт — только поля")
        if fid is not None and (not dm.FACT_ID.match(str(fid)) or fid != stem):
            r.err(rel, f"id {fid!r} не F-NNNN или не совпадает с именем файла")
        if "kind" in f and f["kind"] != "fact":
            r.err(rel, "kind не fact")

        date, observed = dm.iso(f.get("date")), dm.iso(f.get("observed"))
        if "date" in f and date is None:
            r.err(rel, f"date не дата ISO: {f['date']!r}")
        if "observed" in f and observed is None:
            r.err(rel, f"observed не дата ISO: {f['observed']!r}")
        if date and observed and date > observed:
            r.err(rel, f"date {date} позже observed {observed}: факт не бывает о будущем")
        if observed and observed > dm.today():
            r.err(rel, f"observed {observed} позже сегодняшнего дня")

        st = f.get("statement")
        if isinstance(st, str):
            if len(st) > MAX_STATEMENT:
                r.err(rel, f"statement длиннее {MAX_STATEMENT} знаков ({len(st)})")
            if not st.endswith("."):
                r.err(rel, "statement не оканчивается точкой")
        elif st is not None:
            r.err(rel, "statement — не строка")

        if "area" in f and f["area"] not in AREAS:
            r.err(rel, f"area не из {AREAS}: {f['area']!r}")
        if "basis" in f and f["basis"] not in BASES:
            r.err(rel, f"basis не из {BASES}: {f['basis']!r}")
        projects = f.get("projects")
        if "projects" in f:
            if not isinstance(projects, list) or not projects:
                r.err(rel, "projects — не пустой список тегов")
            else:
                for p in projects:
                    if p not in tags:
                        r.err(rel, f"тег проекта {p!r} не из docs/direction/SCOPE.md")
                if len(set(projects)) != len(projects):
                    r.err(rel, "теги проектов повторяются")

        check_source(r, rel, f, registry, notes)

        if "refines" in f:
            if f["refines"] not in facts or f["refines"] == stem:
                r.err(rel, f"refines {f['refines']!r}: нет такого другого факта")
        marks = f.get("marks", [])
        if "marks" in f and not isinstance(marks, list):
            r.err(rel, "marks — не список")
            marks = []
        for mark in marks:
            if mark not in MARKS:
                r.err(rel, f"метка {mark!r} не из словаря {MARKS}")
        if "steam-release" in marks:
            if (f.get("basis") != "observed" or f.get("source_type") != "url"
                    or not str(f.get("ref", "")).startswith(STEAM_STORE)
                    or "voxelrpg" not in (projects or [])):
                r.err(rel, "метка steam-release — только у basis: observed, source_type: url "
                           f"со страницей {STEAM_STORE}… и тегом voxelrpg (D-02)")

        status = f.get("status", "active")
        if status not in ("active", "superseded"):
            r.err(rel, f"status не active/superseded: {status!r}")
        if status == "superseded":
            by, dec = f.get("superseded_by"), f.get("revised_by")
            if by not in facts or by == stem or not dm.is_active(facts[by][1]):
                r.err(rel, f"superseded_by {by!r}: нет такого активного факта")
            if dec not in decisions or not dm.accepted(decisions[dec]):
                r.err(rel, f"revised_by {dec!r}: нет такого принятого решения (D-06)")
        elif "superseded_by" in f or "revised_by" in f:
            r.err(rel, "superseded_by и revised_by — только при status: superseded")

        key = (f.get("source"), f.get("ref"), st)
        if key in seen_content:
            r.err(rel, f"дубликат факта {seen_content[key]}: тот же источник, место и формулировка")
        else:
            seen_content[key] = stem

    active = sum(1 for _, f, _ in facts.values() if dm.is_active(f))
    return r.finish(f"фактов {len(facts)}, активных {active}")


def check_source(r, rel, f, registry, notes):
    sid, stype, ref = f.get("source"), f.get("source_type"), f.get("ref")
    if sid is None or stype is None or ref is None:
        return
    if sid not in registry:
        r.err(rel, f"источника {sid} нет в реестре docs/sources/REGISTRY.md")
        return
    if stype not in TYPES:
        r.err(rel, f"source_type не из {tuple(TYPES)}: {stype!r}")
        return
    src = registry[sid]
    if src["kind"] not in TYPES[stype]:
        r.err(rel, f"source_type {stype} не подходит источнику {sid} вида {src['kind']}")
    if stype == "commit" and not dm.SHA.match(ref):
        r.err(rel, "ref коммита — полный SHA из 40 знаков")
    elif stype in ("file", "release"):
        place, _, sha = ref.rpartition("@")
        if not place or not dm.SHA.match(sha):
            r.err(rel, f"ref {stype} — «{'путь' if stype == 'file' else 'тег'}@SHA» с полным SHA")
        elif stype == "file" and (place.startswith("/") or ".." in place.split("/")):
            r.err(rel, "ref файла — путь от корня репозитория без «/» в начале и «..»")
    elif stype == "url":
        prefix = "https://" + src["address"].rstrip("/")
        if not (ref == prefix or ref.startswith(prefix + "/") or ref.startswith(prefix + "?")):
            r.err(rel, f"ref url не на адресе источника {sid}: ждём {prefix}…")
    elif stype == "note":
        if not dm.NOTE_ID.match(ref) or ref not in notes:
            r.err(rel, f"ref заметки {ref!r}: нет такой заметки в docs/sources/NOTES.md")
        elif notes[ref].get("source") != sid:
            r.err(rel, f"заметка {ref} — о другом источнике ({notes[ref].get('source')}), не {sid}")


if __name__ == "__main__":
    sys.exit(check())
