#!/usr/bin/env python3
"""Хронология ссылается только на существующие факты (docs/timeline/TIMELINE.md).

  * строка — дата ISO, событие одной фразой до 160 знаков, номера фактов;
  * каждый номер — существующий активный факт; ссылки на выводы и
    гипотезы в хронологии запрещены — только факты;
  * дата строки равна дате (date) каждого её факта;
  * строки идут по неубыванию даты.

    python3 tools/verify/check_timeline.py

Код возврата: 0 — чисто; 1 — нарушения.
"""
import re
import sys

import docmodel as dm

MAX_EVENT = 160


def check(root=None):
    r = dm.Report("хронология")
    rows, errors = dm.load_timeline(root)
    r.extend(errors)
    facts, _, _ = dm.load_facts(root)
    previous = None
    for where, date_text, event, refs in rows:
        date = dm.iso(date_text)
        if date is None:
            r.err(where, f"дата не ISO: {date_text!r}")
        elif previous and date < previous:
            r.err(where, f"порядок: {date} после {previous}")
        if date:
            previous = date
        if not event:
            r.err(where, "пустое событие")
        if len(event) > MAX_EVENT:
            r.err(where, f"событие длиннее {MAX_EVENT} знаков")
        if re.search(r"\b[IH]-\d{4}\b", " ".join([event] + refs)):
            r.err(where, "в хронологии только факты, без выводов и гипотез")
        if not refs:
            r.err(where, "нет номеров фактов")
        for fid in refs:
            if not dm.FACT_ID.match(fid):
                r.err(where, f"не номер факта: {fid!r}")
            elif fid not in facts:
                r.err(where, f"нет факта {fid}")
            else:
                f = facts[fid][1]
                if not dm.is_active(f):
                    r.err(where, f"факт {fid} заменён — ссылаться на {f.get('superseded_by')}")
                if date and dm.iso(f.get("date")) != date:
                    r.err(where, f"дата строки {date} не равна дате факта {fid} ({f.get('date')})")
    return r.finish(f"строк {len(rows)}")


if __name__ == "__main__":
    sys.exit(check())
