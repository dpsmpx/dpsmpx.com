#!/usr/bin/env python3
"""DECISIONS, TODO и ROADMAP не противоречат друг другу (D-09; CLAUDE.md, «TODO.md и README.md»).

  * DECISIONS.md: номера D-NN с 01 подряд, «следующий свободный номер» —
    наибольший плюс один; у решения есть «Статус», «Дата», «Решение»,
    «Почему», «Проверка»; статус — «принято», «отклонено» или «заменено
    D-NN» с существующим решением; дата ISO не в будущем; в «Проверке» —
    путь к скрипту tools/verify/; метка у принятых решений не повторяется;
  * TODO.md: каждый пункт — «[этап N] …» с N текущего этапа ROADMAP;
    у выполненного плана TODO пуст.

Согласие статуса книги со STATUS, решениями и этапом 5 —
check_book_gate.py; блок состояния README — readme_status.py.

    python3 tools/verify/check_consistency.py

Код возврата: 0 — чисто; 1 — нарушения.
"""
import re
import sys

import docmodel as dm

FIELDS = ("Статус", "Дата", "Решение", "Почему", "Проверка")


def check(root=None):
    r = dm.Report("согласие документов")
    decisions, next_free, errors = dm.load_decisions(root)
    r.extend(errors)
    numbers = []
    marks = {}
    for did, d in decisions.items():
        if not dm.DECISION_ID.match(did):
            r.err(d["line"], f"номер решения не D-NN: {did}")
            continue
        numbers.append(int(did[2:]))
        for field in FIELDS:
            if field not in d["fields"]:
                r.err(d["line"], f"{did}: нет поля «{field}»")
        status = d.get("status") or ""
        m = re.fullmatch(r"заменено (D-\d{2})", status)
        if status not in ("принято", "отклонено") and not m:
            r.err(d["line"], f"{did}: статус не «принято», «отклонено» или «заменено D-NN»: {status!r}")
        if m and (m.group(1) not in decisions or m.group(1) == did):
            r.err(d["line"], f"{did}: заменено несуществующим решением {m.group(1)}")
        date = dm.iso(d.get("date"))
        if date is None or date > dm.today():
            r.err(d["line"], f"{did}: дата не ISO или в будущем: {d.get('date')!r}")
        if not re.search(r"`tools/verify/[A-Za-z0-9_]+\.(py|sh)`", d["text"].split("**Проверка.**")[-1]):
            r.err(d["line"], f"{did}: в «Проверке» нет скрипта tools/verify/ — решение без проверки")
        if d.get("mark") and dm.accepted(d):
            if d["mark"] in marks:
                r.err(d["line"], f"{did}: метка {d['mark']} уже у {marks[d['mark']]}")
            marks[d["mark"]] = did
    if numbers and sorted(numbers) != list(range(1, max(numbers) + 1)):
        r.err(dm.DECISIONS, "номера решений идут не подряд с D-01")
    expected = (max(numbers) + 1) if numbers else 1
    if next_free != expected:
        r.err(dm.DECISIONS, f"«следующий свободный номер» — {next_free}, ждём {expected}")

    stages, errors = dm.load_stages(root)
    r.extend(errors)
    cur = dm.current_stage(stages)
    todo, errors = dm.load_todo(root)
    r.extend(errors)
    for where, stage, text in todo:
        if cur is None:
            r.err(where, "план выполнен или сломан — в TODO не должно быть пунктов")
        elif stage != cur:
            r.err(where, f"пункт этапа {stage}, а текущий — {cur}: работа будущих этапов — в их файлах")

    return r.finish(f"решений {len(decisions)}, пунктов TODO {len(todo)}, текущий этап {cur}")


if __name__ == "__main__":
    sys.exit(check())
