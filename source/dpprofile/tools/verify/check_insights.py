#!/usr/bin/env python3
"""Выводы и гипотезы ссылаются на существующие факты (docs/insights/README.md; D-07).

  * в docs/insights/ — только README.md, I-NNNN.md и H-NNNN.md;
  * front matter по схеме; I- — kind: insight с level observed/bounded,
    H- — kind: hypothesis без level;
  * facts — не пустой список существующих активных фактов;
  * bounded — с полем limits, hypothesis — с полем test;
  * recorded не раньше observed каждого факта и не позже сегодня;
  * номера фактов в тексте обоснования — только из поля facts;
  * revised — с заменяющим выводом.

    python3 tools/verify/check_insights.py

Код возврата: 0 — чисто; 1 — нарушения.
"""
import re
import sys

import docmodel as dm

REQUIRED = ("id", "kind", "statement", "facts", "recorded")
OPTIONAL = ("level", "limits", "test", "status", "revised_by")
MAX_STATEMENT = 400


def check(root=None):
    r = dm.Report("ссылки выводов")
    insights, errors, extra = dm.load_insights(root)
    r.extend(errors)
    for rel in extra:
        r.err(rel, "посторонний файл: в docs/insights/ только README.md, I-NNNN.md и H-NNNN.md")
    facts, _, _ = dm.load_facts(root)

    for stem, (rel, f, body) in sorted(insights.items()):
        for key in REQUIRED:
            if key not in f:
                r.err(rel, f"нет поля {key}")
        for key in f:
            if key not in REQUIRED + OPTIONAL:
                r.err(rel, f"неизвестное поле {key}")
        iid = f.get("id")
        pattern = dm.INSIGHT_ID if stem.startswith("I-") else dm.HYPOTHESIS_ID
        if iid != stem or not pattern.match(stem):
            r.err(rel, f"id {iid!r} не совпадает с именем файла или не по форме I-NNNN / H-NNNN")
        kind = f.get("kind")
        if stem.startswith("I-"):
            if kind != "insight":
                r.err(rel, "у I-NNNN kind — insight")
            if f.get("level") not in ("observed", "bounded"):
                r.err(rel, "у вывода level — observed или bounded")
            if f.get("level") == "bounded" and not f.get("limits"):
                r.err(rel, "у ограниченного вывода (bounded) нет поля limits")
            if "test" in f:
                r.err(rel, "поле test — только у гипотезы")
        else:
            if kind != "hypothesis":
                r.err(rel, "у H-NNNN kind — hypothesis")
            if "level" in f:
                r.err(rel, "у гипотезы нет поля level")
            if not f.get("test"):
                r.err(rel, "у гипотезы нет поля test — чем её проверить")

        st = f.get("statement")
        if isinstance(st, str):
            if len(st) > MAX_STATEMENT:
                r.err(rel, f"statement длиннее {MAX_STATEMENT} знаков")
            if not st.endswith("."):
                r.err(rel, "statement не оканчивается точкой")

        refs = f.get("facts")
        if "facts" in f:
            if not isinstance(refs, list) or not refs:
                r.err(rel, "facts — не пустой список F-NNNN")
                refs = []
            for fid in refs:
                if fid not in facts:
                    r.err(rel, f"нет факта {fid}")
                elif not dm.is_active(facts[fid][1]) and f.get("status", "active") == "active":
                    r.err(rel, f"факт {fid} заменён ({facts[fid][1].get('superseded_by')}) — вывод пересмотреть")
        else:
            refs = []

        recorded = dm.iso(f.get("recorded"))
        if "recorded" in f and recorded is None:
            r.err(rel, "recorded не дата ISO")
        if recorded:
            if recorded > dm.today():
                r.err(rel, "recorded позже сегодняшнего дня")
            for fid in refs:
                if fid in facts:
                    obs = dm.iso(facts[fid][1].get("observed"))
                    if obs and recorded < obs:
                        r.err(rel, f"recorded {recorded} раньше, чем записан факт {fid} ({obs})")

        for fid in sorted(set(re.findall(r"\bF-\d{4}\b", body))):
            if fid not in refs:
                r.err(rel, f"в обосновании факт {fid}, которого нет в поле facts")

        status = f.get("status", "active")
        if status not in ("active", "revised"):
            r.err(rel, "status — active или revised")
        if status == "revised":
            by = f.get("revised_by")
            if by not in insights or by == stem:
                r.err(rel, f"revised_by {by!r}: нет такого вывода или гипотезы")
        elif "revised_by" in f:
            r.err(rel, "revised_by — только при status: revised")

    n_ins = sum(1 for k in insights if k.startswith("I-"))
    return r.finish(f"выводов {n_ins}, гипотез {len(insights) - n_ins}")


if __name__ == "__main__":
    sys.exit(check())
