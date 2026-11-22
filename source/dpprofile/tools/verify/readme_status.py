#!/usr/bin/env python3
"""Блок состояния README.md строится из документов, а не пишется руками (D-10).

Блок между <!-- status:begin --> и <!-- status:end --> собирается из
таблицы и критериев docs/direction/ROADMAP/, блока book-gate
docs/book/STATUS.md, счёта фактов, выводов, источников, хронологии,
решений и пунктов TODO.md.

    python3 tools/verify/readme_status.py           # сверить блок с документами
    python3 tools/verify/readme_status.py --write   # переписать блок

Код возврата: 0 — блок совпадает (или переписан); 1 — блок отстал или
меток нет.
"""
import re
import sys

import docmodel as dm

BEGIN, END = "<!-- status:begin -->", "<!-- status:end -->"


def build(root=None):
    ctx = dm.Context(root)
    stages, _ = dm.load_stages(root)
    todo, _ = dm.load_todo(root)
    counts = ctx.counts()
    cur = dm.current_stage(stages)
    done = sum(1 for s in stages if s["state"].startswith("выполнен"))
    lines = [BEGIN,
             "<!-- Строит tools/verify/readme_status.py --write из ROADMAP, STATUS книги и документов — руками не править. -->",
             ""]
    if cur is not None:
        title = next(s["title"] for s in stages if s["n"] == cur)
        lines.append(f"Текущий этап: **{cur} — {title}**; выполнено этапов: **{done} из {len(stages)}**.")
    else:
        lines.append(f"Выполнено этапов: **{done} из {len(stages)}**.")
    lines += ["", "| Этап | Суть | Состояние | Критерии выхода |", "|---|---|---|---|"]
    for s in stages:
        ticked = sum(1 for c in s["criteria"] if c[1])
        lines.append(f"| {s['n']} | {s['title']} | {s['state']} | {ticked} из {len(s['criteria'])} |")
    writing = ctx.status.get("book_writing")
    if writing == "allowed":
        book = (f"работа над текстом разрешена (`book_writing: allowed`, решение "
                f"{ctx.status.get('permission_decision')}, `docs/book/STATUS.md`).")
    else:
        book = "не пишется (`book_writing: forbidden`, `docs/book/STATUS.md`)."
    lines += ["",
              f"- **Книга:** {book}",
              f"- **Документы:** фактов — {len(ctx.facts)} (активных {counts['facts']}), "
              f"выводов — {counts['insights']}, гипотез — {counts['hypotheses']}, "
              f"источников — {counts['sources']}, заметок — {counts['notes']}, "
              f"строк хронологии — {counts['timeline']}, принятых решений — {counts['decisions']}.",
              f"- **TODO:** открытых пунктов — {len(todo)}.",
              END]
    return "\n".join(lines)


def main(argv):
    text = dm.read(dm.README)
    m = re.search(re.escape(BEGIN) + r".*?" + re.escape(END), text, re.S)
    if not m:
        print(f"✗ {dm.README}: нет меток {BEGIN} … {END}")
        return 1
    block = build()
    if "--write" in argv:
        if m.group(0) != block:
            with open(dm.path(dm.README), "w", encoding="utf-8") as f:
                f.write(text[:m.start()] + block + text[m.end():])
            print("✓ блок состояния README: переписан")
        else:
            print("✓ блок состояния README: без изменений")
        return 0
    if m.group(0) != block:
        print(f"✗ {dm.README}: блок состояния отстал от документов — "
              "tools/verify/readme_status.py --write")
        return 1
    print("✓ блок состояния README: совпадает с документами")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
