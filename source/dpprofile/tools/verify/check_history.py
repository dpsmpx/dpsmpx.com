#!/usr/bin/env python3
"""Факты и решения не переписываются задним числом (D-06; журнал решений).

По истории git от HEAD:

  * каждый файл факта, когда-либо добавленный в docs/facts/, есть в рабочей
    копии — факты не удаляются и не переименовываются;
  * ядро факта (все поля, кроме status, superseded_by, revised_by) равно его
    первой закоммиченной версии; из поздних полей допустима только
    замена: status: superseded с superseded_by и revised_by;
  * каждое решение D-NN, когда-либо бывшее в docs/direction/DECISIONS.md,
    есть в нём и сейчас.

Нужна полная история. Без git или в неполном (shallow) клоне обычный
режим пропускает проверку с пометкой, режим --strict (полный прогон) —
падает. Внутри DPmetaApp (каталог dpprofile/, D-16) история — два отрезка
(docmodel.history): прежний main DPprofile и коммиты DPmetaApp после
слияния поддерева; основная история DPmetaApp в неё не попадает.

    python3 tools/verify/check_history.py [--strict]

Код возврата: 0 — чисто (или пропуск без --strict); 1 — нарушения.
"""
import re
import sys

import docmodel as dm

MUTABLE = ("status", "superseded_by", "revised_by")


def check(root=None, strict=False):
    root = root or dm.ROOT
    r = dm.Report("история фактов и решений")
    code, shallow = dm.git(["rev-parse", "--is-shallow-repository"], cwd=root)
    if shallow.strip() == "true":
        if strict:
            r.err(root, "неполный (shallow) клон — нужна вся история")
            return r.finish("")
        return r.finish("пропущено: неполный клон")
    if dm.is_git_repo(root):
        code, head = dm.git(["rev-parse", "--verify", "-q", "HEAD"], cwd=root)
        if code != 0:
            return r.finish("пропущено: коммитов ещё нет")
    h = dm.history(root)
    if not h.ok:
        if strict:
            r.err(root, h.problem)
            return r.finish("")
        return r.finish(f"пропущено: {h.problem}")

    paths = sorted(p for p in h.added(dm.FACTS_DIR) if re.fullmatch(r"docs/facts/F-\d+\.md", p))
    for rel in paths:
        if not dm.exists(rel, root):
            r.err(rel, "факт удалён или переименован — факты не удаляются (D-06)")
            continue
        first, prefix = h.first_add(rel)
        code, original = h.show(first, prefix, rel)
        try:
            old, _ = dm.parse_front_matter(original)
            new, _ = dm.parse_front_matter(dm.read(rel, root))
        except dm.DocError as e:
            r.err(rel, f"не разобрать для сравнения: {e}")
            continue
        changed = sorted(k for k in set(old) | set(new)
                         if k not in MUTABLE and old.get(k) != new.get(k))
        if changed:
            r.err(rel, f"изменено ядро факта ({', '.join(changed)}) после коммита {first[:7]} — "
                       "только новый факт и замена старого (D-06)")
        if any(k in old for k in MUTABLE) and old.get("status", "active") != new.get("status", "active"):
            r.err(rel, "статус замены отменён — замена необратима")

    current, _, _ = dm.load_decisions(root)
    ever = set()
    for sha, prefix in h.versions(dm.DECISIONS):
        code, text = h.show(sha, prefix, dm.DECISIONS)
        if code == 0:
            ever |= set(re.findall(r"^### (D-\d+) —", text, re.M))
    for did in sorted(ever - set(current)):
        r.err(dm.DECISIONS, f"решение {did} было в журнале и исчезло — номера не удаляются")

    return r.finish(f"фактов в истории {len(paths)}, решений в истории {len(ever)}")


if __name__ == "__main__":
    sys.exit(check(strict="--strict" in sys.argv[1:]))
