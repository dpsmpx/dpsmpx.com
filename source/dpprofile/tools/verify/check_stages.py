#!/usr/bin/env python3
"""Этапы ROADMAP и их критерии выхода честны (docs/direction/ROADMAP/README.md; D-09).

  * этапы нумеруются с 0 подряд; в таблице и в файле этапа — одно
    название и одно состояние;
  * ровно один этап «в работе» (если не выполнены все); до него —
    выполненные с датами по порядку, после — «—»;
  * у каждого критерия есть машинное условие <!-- gate: … -->, и оно
    разбирается;
  * [x] при ложном условии — ошибка; у этапа «в работе» истинное условие
    без [x] — ошибка; у не начатого этапа отметок нет;
  * «выполнен» — только когда отмечены все критерии; этап «в работе» с
    отмеченными всеми критериями — ошибка (отметить выполненным);
  * условие, которое не проверить без полной истории git (копия без git,
    неглубокий клон — `stable:`), у отмеченного критерия — пометка с
    причиной; с --strict (полный прогон) — ошибка с той же причиной.

    python3 tools/verify/check_stages.py [--strict]

Код возврата: 0 — чисто; 1 — нарушения.
"""
import sys

import docmodel as dm


def check(root=None, strict=False):
    r = dm.Report("этапы и критерии")
    stages, errors = dm.load_stages(root)
    r.extend(errors)
    if not stages:
        r.err(dm.ROADMAP, "этапов нет")
        return r.finish("")
    ctx = dm.Context(root)

    if [s["n"] for s in stages] != list(range(len(stages))):
        r.err(dm.ROADMAP, "этапы нумеруются с 0 подряд")
    working = [s for s in stages if s["state"] == "в работе"]
    all_done = all(s["state"].startswith("выполнен") for s in stages)
    if len(working) != 1 and not all_done:
        r.err(dm.ROADMAP, f"этапов «в работе» {len(working)}, нужен ровно один")
    cur = working[0]["n"] if len(working) == 1 else None

    last_done = None
    for s in stages:
        m = dm.STAGE_STATE.match(s["state"])
        if not m:
            r.err(s["line"], f"состояние не «выполнен (дата)», «в работе» или «—»: {s['state']!r}")
            continue
        if s["file_state"] != s["state"]:
            r.err(s["file"], f"состояние в файле ({s['file_state']!r}) не равно таблице ({s['state']!r})")
        if s["file_title"] != (s["n"], s["title"]):
            r.err(s["file"], f"заголовок файла не «# Этап {s['n']} — {s['title']}»")
        if m.group(2):
            done = dm.iso(m.group(2))
            if done is None or done > dm.today():
                r.err(s["line"], "дата выполнения — ISO и не в будущем")
            elif last_done and done < last_done:
                r.err(s["line"], "даты выполнения этапов идут не по порядку")
            else:
                last_done = done
        if cur is not None:
            if s["n"] < cur and not s["state"].startswith("выполнен"):
                r.err(s["line"], f"этап {s['n']} до текущего ({cur}) не выполнен")
            if s["n"] > cur and s["state"] != "—":
                r.err(s["line"], f"этап {s['n']} после текущего ({cur}) — только «—»")

        if not s["criteria"]:
            r.err(s["file"], "нет критериев выхода")
        for where, checked, text, gate in s["criteria"]:
            if not gate:
                r.err(where, "у критерия нет машинного условия <!-- gate: … -->")
                continue
            ctx.unknown = []
            ok, gate_errors = dm.eval_gate(gate, ctx)
            for e in gate_errors:
                r.err(where, e)
            if checked and not ok and ctx.unknown:
                why = "; ".join(ctx.unknown)
                if strict:
                    r.err(where, f"условие не проверить: {why}")
                else:
                    r.note(f"{where}: условие не проверено — {why}")
            elif checked and not ok:
                r.err(where, f"отмечен [x], но условие ложно: {gate}")
            if s["state"] == "в работе" and ok and not checked:
                r.err(where, f"условие выполнено — отметить [x] в этом же коммите: {gate}")
            if s["state"] == "—" and checked:
                r.err(where, "отметка у не начатого этапа")
        if s["state"].startswith("выполнен") and not all(c[1] for c in s["criteria"]):
            r.err(s["file"], "этап «выполнен», но отмечены не все критерии")
        if s["state"] == "в работе" and s["criteria"] and all(c[1] for c in s["criteria"]):
            r.err(s["file"], "все критерии отмечены — этап выполнен: отметить и начать следующий")

    done = sum(1 for s in stages if s["state"].startswith("выполнен"))
    return r.finish(f"этапов {len(stages)}, выполнено {done}, текущий — {cur if cur is not None else 'нет'}")


if __name__ == "__main__":
    sys.exit(check(strict="--strict" in sys.argv[1:]))
