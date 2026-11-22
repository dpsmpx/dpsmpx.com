#!/usr/bin/env python3
"""Самопроверка: каждая проверка падает на испорченной копии репозитория (D-08).

Проверка, которая ни разу не падала, может молча пропускать всё. Здесь
репозиторий копируется во временный каталог (без .git и build/), в копию
вносится одно нарушение, и нужная проверка обязана упасть с ожидаемым
сообщением. Сначала — чистая копия: все быстрые проверки на ней проходят.
Проверки истории работают на временном репозитории git.

    python3 tools/verify/selftest.py [-v]

Код возврата: 0 — все нарушения пойманы; 1 — какая-то проверка не упала
или упала не тем.
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

import docmodel as dm

V = "tools/verify"
QUICK = ["check_facts", "check_registry", "check_insights", "check_timeline", "check_links",
         "check_forbidden", "check_stages", "check_consistency", "check_book_gate", "readme_status"]


# ---------------------------------------------------------------- помощники

def copy_repo(dst):
    shutil.copytree(dm.ROOT, dst, ignore=shutil.ignore_patterns(".git", "build", "__pycache__"))


def run(root, script, *args, env=None):
    e = dict(os.environ, **(env or {}))
    p = subprocess.run([sys.executable, os.path.join(root, V, script + ".py"), *args],
                       cwd=root, capture_output=True, text=True, env=e)
    return p.returncode, p.stdout + p.stderr


def p(root, rel):
    return os.path.join(root, rel)


def read(root, rel):
    with open(p(root, rel), encoding="utf-8") as f:
        return f.read()


def write(root, rel, text):
    os.makedirs(os.path.dirname(p(root, rel)) or ".", exist_ok=True)
    with open(p(root, rel), "w", encoding="utf-8") as f:
        f.write(text)


def append(root, rel, text):
    write(root, rel, read(root, rel).rstrip("\n") + "\n" + text + "\n")


def sub(root, rel, pattern, repl, count=1):
    text = read(root, rel)
    new, n = re.subn(pattern, repl, text, count=count, flags=re.M)
    if n == 0:
        raise AssertionError(f"в {rel} нет «{pattern}» — самопроверка устарела")
    write(root, rel, new)


def fact(root, pred=lambda f: True):
    """(относительный путь, поля) первого факта, подходящего под условие."""
    for path in sorted(glob.glob(p(root, "docs/facts/F-*.md"))):
        fields, _ = dm.parse_front_matter(open(path, encoding="utf-8").read())
        if pred(fields):
            return os.path.relpath(path, root), fields
    raise AssertionError("нет подходящего факта — самопроверка устарела")


def earliest_fact(root):
    best = None
    for path in sorted(glob.glob(p(root, "docs/facts/F-*.md"))):
        fields, _ = dm.parse_front_matter(open(path, encoding="utf-8").read())
        if best is None or fields["date"] < best["date"]:
            best = fields
    return best


def git(root, *args):
    subprocess.run(["git", "-c", "user.name=selftest", "-c", "user.email=selftest@localhost",
                    "-c", "commit.gpgsign=false", *args], cwd=root, check=True,
                   capture_output=True, text=True)


def git_repo(root):
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "основа")


def git_commit(root, message="правка"):
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)


def subtree_repo(tmp, name, mutate=None):
    """DPprofile каталогом sub/ в чужом репозитории, как в DPmetaApp (D-16): (каталог, опора).

    Опора — main «прежнего репозитория» до слияния поддерева; mutate — правка уже
    внутри внешнего репозитория, с коммитом там.
    """
    base = os.path.join(tmp, name + "-base")
    copy_repo(base)
    git_repo(base)
    onto = subprocess.run(["git", "rev-parse", "HEAD"], cwd=base, capture_output=True, text=True).stdout.strip()
    outer = os.path.join(tmp, name + "-outer")
    os.makedirs(outer)
    write(outer, "README.md", "# внешний репозиторий\n")
    git_repo(outer)
    git(outer, "fetch", "-q", base, "HEAD")
    git(outer, "merge", "-q", "-s", "ours", "--no-commit", "--allow-unrelated-histories", "FETCH_HEAD")
    git(outer, "read-tree", "--prefix=sub/", "-u", "FETCH_HEAD")
    git(outer, "commit", "-q", "-m", "слияние поддерева")
    root = os.path.join(outer, "sub")
    if mutate:
        mutate(root)
        git_commit(outer)
    return root, onto


def rewrite_fact(r):
    rel, _ = fact(r)
    sub(r, rel, r"^statement: .*$", "statement: Другая формулировка того же факта.")


def remove_and_restore_rewritten(r):
    """Каталог удалён одним коммитом внешнего репозитория и возвращён с переписанным фактом."""
    outer, aside = os.path.dirname(r), r + "-aside"
    shutil.move(r, aside)
    git_commit(outer, "каталог удалён")
    shutil.move(aside, r)
    rewrite_fact(r)


def self_commit_facts(r):
    """Пути двух фактов источника S-00 типа commit."""
    out = []
    for path in sorted(glob.glob(p(r, "docs/facts/F-*.md"))):
        f, _ = dm.parse_front_matter(open(path, encoding="utf-8").read())
        if f.get("source") == "S-00" and f.get("source_type") == "commit":
            out.append(os.path.relpath(path, r))
    if len(out) < 2:
        raise AssertionError("нет двух фактов S-00 типа commit — самопроверка устарела")
    return out[:2]


def insight(root, name, lines, body=""):
    write(root, f"docs/insights/{name}.md", "---\n" + "\n".join(lines) + "\n---\n" + body)


# ---------------------------------------------------------------- нарушения

def t_fact_missing_field(r):
    rel, _ = fact(r)
    sub(r, rel, r"^basis: .*\n", "")


def t_fact_bad_date(r):
    rel, _ = fact(r)
    sub(r, rel, r"^date: .*$", "date: 2026-13-45")


def t_fact_duplicate_id(r):
    rel, _ = fact(r)
    write(r, "docs/facts/F-9999.md", read(r, rel))


def t_fact_unknown_source(r):
    rel, _ = fact(r)
    sub(r, rel, r"^source: .*$", "source: S-99")


def t_fact_bad_commit_ref(r):
    rel, _ = fact(r, lambda f: f.get("source_type") == "commit")
    sub(r, rel, r"^ref: .*$", "ref: abc123")


def t_fact_future(r):
    rel, _ = fact(r)
    sub(r, rel, r"^date: .*$", "date: 2099-01-01")


def t_fact_unknown_tag(r):
    rel, _ = fact(r)
    sub(r, rel, r"^projects: .*$", "projects: [nosuchproject]")


def t_fact_body(r):
    rel, _ = fact(r)
    append(r, rel, "Пояснение к факту.")


def t_fact_yaml_unsafe(r):
    rel, _ = fact(r)
    sub(r, rel, r"^statement: .*$", "statement: Записано: проект начат.")


def t_fact_url_host(r):
    rel, _ = fact(r, lambda f: f.get("source_type") == "url")
    sub(r, rel, r"^ref: .*$", "ref: https://example.com/page")


def t_fact_steam_mark(r):
    rel, _ = fact(r, lambda f: f.get("source_type") == "commit")
    append_field(r, rel, "marks: [steam-release]")


def t_fact_superseded_alone(r):
    rel, _ = fact(r)
    append_field(r, rel, "status: superseded")


def append_field(r, rel, line):
    text = read(r, rel)
    head, sep, rest = text.partition("\n---\n")
    write(r, rel, head + "\n" + line + sep + rest)


def t_insight_missing_fact(r):
    insight(r, "I-9001", ["id: I-9001", "kind: insight", "level: observed",
                          "statement: Вывод без опоры.", "facts: [F-9998]", "recorded: 2026-10-04"])


def t_insight_bounded_no_limits(r):
    _, f = fact(r)
    insight(r, "I-9002", ["id: I-9002", "kind: insight", "level: bounded",
                          "statement: Ограниченный вывод.", f"facts: [{f['id']}]",
                          f"recorded: {f['observed']}"])


def t_hypothesis_no_test(r):
    _, f = fact(r)
    insight(r, "H-9001", ["id: H-9001", "kind: hypothesis", "statement: Гипотеза.",
                          f"facts: [{f['id']}]", f"recorded: {f['observed']}"])


def t_insight_body_ref(r):
    _, f = fact(r)
    other = fact(r, lambda g: g["id"] != f["id"])[1]["id"]
    insight(r, "I-9003", ["id: I-9003", "kind: insight", "level: observed",
                          "statement: Наблюдаемый вывод.", f"facts: [{f['id']}]",
                          f"recorded: {f['observed']}"],
            body=f"\n## Обоснование\n\nОпирается ещё и на {other}.\n")


def t_forbidden_hype_fact(r):
    rel, _ = fact(r)
    sub(r, rel, r"^statement: .*$", "statement: Невероятный рост проекта.")


def t_forbidden_inference_fact(r):
    rel, _ = fact(r)
    sub(r, rel, r"^statement: .*$", "statement: Следовательно проект завершён.")


def t_forbidden_prescriptive_method(r):
    _, f = fact(r)
    append(r, dm.METHOD, f"| Каждый проект должен вести журнал решений | VoxelRPG | {f['id']} |")


def t_forbidden_hype_readme(r):
    append(r, dm.README, "Лучший в мире метод.")


def t_link_broken(r):
    append(r, dm.README, "[раздел](docs/nope.md)")


def t_link_undefined_id(r):
    append(r, dm.README, "См. F-9998.")


def t_link_missing_path(r):
    append(r, dm.README, "Подробно — `docs/nope/x.md`.")


def t_timeline_missing_fact(r):
    append(r, dm.TIMELINE, "| 2099-01-01 | Событие | F-9998 |")


def t_timeline_date_mismatch(r):
    _, f = fact(r)
    append(r, dm.TIMELINE, f"| 2099-01-01 | Событие | {f['id']} |")


def t_timeline_unsorted(r):
    f = earliest_fact(r)
    append(r, dm.TIMELINE, f"| 2099-01-01 | Последнее | {fact(r)[1]['id']} |")
    append(r, dm.TIMELINE, f"| {f['date']} | Раннее после позднего | {f['id']} |")


def t_timeline_insight(r):
    append(r, dm.TIMELINE, "| 2099-01-01 | Вывод в хронологии | I-0001 |")


def t_registry_bad_access(r):
    sub(r, dm.REGISTRY, r"\| (public|private) \|", "| secret |")


def t_registry_note_field(r):
    sub(r, dm.NOTES, r"^- verify: .*\n", "")


def t_scope_unknown_source(r):
    sub(r, dm.SCOPE, r"\| (S-\d\d)(, S-\d\d)* \|$", "| S-77 |")


def t_stage_false_tick(r):
    sub(r, "docs/direction/ROADMAP/stage-5.md", r"^- \[ \]", "- [x]")


def t_stage_two_working(r):
    sub(r, dm.ROADMAP, r"^(\| 5 \| .*\| )— \|$", r"\1в работе |")
    sub(r, "docs/direction/ROADMAP/stage-5.md", r"^Состояние: —$", "Состояние: в работе")


def t_stage_no_gate(r):
    sub(r, "docs/direction/ROADMAP/stage-0.md", r"\s*<!-- gate: .*-->$", "")


def t_todo_wrong_stage(r):
    append(r, dm.TODO, "- [этап 99] Пункт чужого этапа.")


def t_decisions_next_number(r):
    sub(r, dm.DECISIONS, r"\(сейчас — \*\*(\d+)\*\*\)", "(сейчас — **999**)")


def t_decisions_bad_status(r):
    sub(r, dm.DECISIONS, r"^- \*\*Статус:\*\* принято$", "- **Статус:** обсуждается")


def t_book_chapter_file(r):
    write(r, "docs/book/chapter-01.md", "# Глава 1\n")


def t_book_outline_prose(r):
    append(r, dm.OUTLINE, "Это абзац прозы о том, как всё начиналось, и он не пункт списка.")


def t_book_status_allowed(r):
    sub(r, dm.STATUS, r"^book_writing: forbidden$", "book_writing: allowed")


def t_book_draft_elsewhere(r):
    write(r, "notes/черновик-1.md", "текст\n")


def t_book_chapter_heading(r):
    append(r, dm.METHOD, "## Глава 1. Начало")


def t_readme_stale(r):
    sub(r, dm.README, r"фактов — \d+", "фактов — 100500")


def t_history_rewrite(r):
    git_repo(r)
    rewrite_fact(r)
    git_commit(r)


def t_history_delete(r):
    git_repo(r)
    rel, _ = fact(r)
    os.remove(p(r, rel))
    git_commit(r)


def t_history_decision_removed(r):
    git_repo(r)
    sub(r, dm.DECISIONS, r"^### (D-\d+) — ", "### Удалено — ")
    git_commit(r)


def t_history_strict_no_git(r):
    pass


def t_refs_no_clones(r):
    os.makedirs(p(r, "build/empty-sources"), exist_ok=True)


def t_refs_wrong_date(r):
    rel, f = fact(r, lambda g: g.get("source_type") == "commit" and g.get("source") != "S-00")
    sub(r, rel, r"^date: .*$", "date: 2000-01-01")


def t_refs_missing_file(r):
    rel, f = fact(r, lambda g: g.get("source_type") == "file")
    sha = f["ref"].rpartition("@")[2]
    sub(r, rel, r"^ref: .*$", f"ref: docs/nope.md@{sha}")


TESTS = [
    ("факт без поля", t_fact_missing_field, "check_facts", (), None, "нет поля basis"),
    ("дата не ISO", t_fact_bad_date, "check_facts", (), None, "date не дата ISO"),
    ("номер факта повторяется", t_fact_duplicate_id, "check_facts", (), None, "повторяется"),
    ("источник не из реестра", t_fact_unknown_source, "check_facts", (), None, "нет в реестре"),
    ("ref коммита не SHA", t_fact_bad_commit_ref, "check_facts", (), None, "полный SHA"),
    ("факт о будущем", t_fact_future, "check_facts", (), None, "факт не бывает о будущем"),
    ("тег не из SCOPE", t_fact_unknown_tag, "check_facts", (), None, "не из docs/direction/SCOPE.md"),
    ("текст после полей", t_fact_body, "check_facts", (), None, "текст после front matter"),
    ("значение ломает YAML", t_fact_yaml_unsafe, "check_facts", (), None, "ломают YAML"),
    ("url не на адресе источника", t_fact_url_host, "check_facts", (), None, "не на адресе источника"),
    ("метка steam-release не там", t_fact_steam_mark, "check_facts", (), None, "steam-release"),
    ("замена без решения", t_fact_superseded_alone, "check_facts", (), None, "superseded_by"),
    ("вывод без факта", t_insight_missing_fact, "check_insights", (), None, "нет факта F-9998"),
    ("bounded без limits", t_insight_bounded_no_limits, "check_insights", (), None, "limits"),
    ("гипотеза без test", t_hypothesis_no_test, "check_insights", (), None, "нет поля test"),
    ("факт в обосновании вне facts", t_insight_body_ref, "check_insights", (), None, "в обосновании факт"),
    ("оценка в факте", t_forbidden_hype_fact, "check_forbidden", (), None, r"\(hype\)"),
    ("вывод в факте", t_forbidden_inference_fact, "check_forbidden", (), None, r"\(inference\)"),
    ("предписание в методе", t_forbidden_prescriptive_method, "check_forbidden", (), None, r"\(prescriptive\)"),
    ("оценка в README", t_forbidden_hype_readme, "check_forbidden", (), None, r"\(hype\)"),
    ("битая ссылка", t_link_broken, "check_links", (), None, "несуществующий файл"),
    ("неопределённый номер", t_link_undefined_id, "check_links", (), None, "F-9998 нигде не определён"),
    ("несуществующий путь", t_link_missing_path, "check_links", (), None, "нет пути"),
    ("хронология: нет факта", t_timeline_missing_fact, "check_timeline", (), None, "нет факта F-9998"),
    ("хронология: чужая дата", t_timeline_date_mismatch, "check_timeline", (), None, "не равна дате факта"),
    ("хронология: порядок", t_timeline_unsorted, "check_timeline", (), None, "порядок"),
    ("хронология: вывод", t_timeline_insight, "check_timeline", (), None, "только факты"),
    ("реестр: доступ", t_registry_bad_access, "check_registry", (), None, "доступ не public/private"),
    ("заметка без поля", t_registry_note_field, "check_registry", (), None, "нет поля verify"),
    ("SCOPE: источник не из реестра", t_scope_unknown_source, "check_registry", (), None, "S-77 нет в реестре"),
    ("этап: ложная отметка", t_stage_false_tick, "check_stages", (), None, "не начатого|условие ложно"),
    ("этап: два в работе", t_stage_two_working, "check_stages", (), None, "нужен ровно один"),
    ("этап: критерий без условия", t_stage_no_gate, "check_stages", (), None, "нет машинного условия"),
    ("TODO: чужой этап", t_todo_wrong_stage, "check_consistency", (), None, "пункт этапа 99"),
    ("решения: следующий номер", t_decisions_next_number, "check_consistency", (), None, "следующий свободный номер"),
    ("решения: статус", t_decisions_bad_status, "check_consistency", (), None, "статус не"),
    ("книга: файл главы", t_book_chapter_file, "check_book_gate", (), None, "chapter-01.md"),
    ("книга: проза в outline", t_book_outline_prose, "check_book_gate", (), None, "проза"),
    ("книга: allowed без шлюза", t_book_status_allowed, "check_book_gate", (), None, "allowed без факта"),
    ("книга: черновик вне docs/book", t_book_draft_elsewhere, "check_book_gate", (), None, "черновик"),
    ("книга: заголовок главы", t_book_chapter_heading, "check_book_gate", (), None, "заголовок главы"),
    ("README: блок отстал", t_readme_stale, "readme_status", (), None, "отстал"),
    ("история: факт переписан", t_history_rewrite, "check_history", ("--strict",), None, "изменено ядро"),
    ("история: факт удалён", t_history_delete, "check_history", ("--strict",), None, "удалён"),
    ("история: решение исчезло", t_history_decision_removed, "check_history", ("--strict",), None, "исчезло"),
    ("история: без git строго", t_history_strict_no_git, "check_history", ("--strict",), None, "не репозиторий git"),
    # Отмеченное `stable:` без истории git: обычный прогон — пометка, полный — ошибка с причиной.
    ("этап: условие без истории строго", t_history_strict_no_git, "check_stages", ("--strict",), None,
     "условие не проверить: stable:.*не репозиторий git"),
    ("клоны: нет клонов", t_refs_no_clones, "check_refs", (),
     {"DPPROFILE_SOURCES": "build/empty-sources"}, "нет клона"),
]

# Нужны клоны источников (tools/verify/fetch_sources.sh): без них — пропуск;
# полный прогон без клонов и так падает на check_refs.py.
CLONES = os.environ.get("DPPROFILE_SOURCES") or os.path.join(dm.ROOT, "build", "sources")
CLONE_TESTS = [
    ("клоны: дата не та", t_refs_wrong_date, "check_refs", (), {"DPPROFILE_SOURCES": CLONES},
     "не равна дате коммита"),
    ("клоны: нет файла на коммите", t_refs_missing_file, "check_refs", (), {"DPPROFILE_SOURCES": CLONES},
     "нет файла docs/nope.md"),
]


def main(argv):
    verbose = "-v" in argv
    failures = []
    tests = list(TESTS)
    if os.path.isdir(CLONES) and os.listdir(CLONES):
        tests += CLONE_TESTS
    else:
        print(f"  · клонов источников нет ({CLONES}) — проверки check_refs по клонам пропущены")
    total = len(tests)
    with tempfile.TemporaryDirectory(prefix="dpprofile-selftest-") as tmp:
        clean = os.path.join(tmp, "clean")
        copy_repo(clean)
        for script in QUICK:
            code, out = run(clean, script)
            if code != 0:
                failures.append(f"чистая копия: {script} упал\n{out.strip()}")
        for i, (name, mutate, script, args, env, expected) in enumerate(tests):
            root = os.path.join(tmp, f"t{i:02d}")
            copy_repo(root)
            try:
                mutate(root)
            except AssertionError as e:
                failures.append(f"{name}: {e}")
                continue
            if env:
                env = {k: os.path.join(root, v) for k, v in env.items()}  # абсолютный путь остаётся
            code, out = run(root, script, *args, env=env)
            if code == 0:
                failures.append(f"{name}: {script} не упал")
            elif not re.search(expected, out):
                failures.append(f"{name}: {script} упал, но без «{expected}»:\n{out.strip()[:600]}")
            elif verbose:
                print(f"  ✓ {name} → {script}")
            shutil.rmtree(root, ignore_errors=True)
        # Каталог в чужом репозитории (D-16): история — прежний main и коммиты после слияния.
        root, onto = subtree_repo(tmp, "subtree")
        code, out = run(root, "check_history", "--strict", env={"DPPROFILE_PRE_MOVE_HEAD": onto})
        if code != 0 or not re.search(r"фактов в истории [1-9]", out):
            failures.append(f"подкаталог: чистая история не прошла\n{out.strip()[:600]}")
        for name, mutate in (("подкаталог: факт переписан", rewrite_fact),
                             ("подкаталог: каталог удалён и возвращён с переписанным фактом",
                              remove_and_restore_rewritten)):
            total += 1
            root, onto = subtree_repo(tmp, f"subtree-{total}", mutate)
            code, out = run(root, "check_history", "--strict", env={"DPPROFILE_PRE_MOVE_HEAD": onto})
            if code == 0 or "изменено ядро" not in out or "исчезло" in out:
                failures.append(f"{name}: check_history не поймал как надо\n{out.strip()[:600]}")
            elif verbose:
                print(f"  ✓ {name} → check_history")
        # Неглубокий клон: граница истории выглядит правкой OUTLINE — причина названа, а не «условие ложно».
        total += 1
        origin = os.path.join(tmp, "shallow-origin")
        copy_repo(origin)
        git_repo(origin)
        append(origin, dm.TODO, "")
        git_commit(origin, "вторая")
        shallow = os.path.join(tmp, "shallow")
        git(tmp, "clone", "-q", "--depth", "1", "file://" + origin, shallow)
        code, out = run(shallow, "check_stages", "--strict")
        if code == 0 or "неглубокий клон" not in out or "условие ложно" in out:
            failures.append(f"неглубокий клон: check_stages не назвал причину\n{out.strip()[:600]}")
        elif verbose:
            print("  ✓ неглубокий клон → check_stages")
        code, out = run(shallow, "check_stages")
        if code != 0 or "условие не проверено" not in out:
            failures.append(f"неглубокий клон: обычный прогон — не пометка\n{out.strip()[:600]}")
        # S-00 — только коммиты истории DPprofile: опора есть, коммит внешнего репозитория — нет.
        total += 1
        root, onto = subtree_repo(tmp, "subtree-self")
        foreign = subprocess.run(["git", "rev-parse", "HEAD^1"], cwd=os.path.dirname(root),
                                 capture_output=True, text=True).stdout.strip()
        mine, other = self_commit_facts(root)
        sub(root, mine, r"^ref: .*$", f"ref: {onto}")
        sub(root, other, r"^ref: .*$", f"ref: {foreign}")
        os.makedirs(p(root, "build/empty-sources"), exist_ok=True)
        code, out = run(root, "check_refs", env={"DPPROFILE_PRE_MOVE_HEAD": onto,
                                                 "DPPROFILE_SOURCES": p(root, "build/empty-sources")})
        if f"нет коммита {foreign[:12]} в S-00" not in out or f"нет коммита {onto[:12]}" in out:
            failures.append(f"подкаталог: S-00 — чужой коммит принят или свой отвергнут\n{out.strip()[:600]}")
        elif verbose:
            print("  ✓ подкаталог: S-00 — коммит внешнего репозитория → check_refs")
    if failures:
        for f in failures:
            print(f"✗ {f}")
        print(f"✗ самопроверка: не поймано {len(failures)} из {total}")
        return 1
    print(f"✓ самопроверка: чистая копия проходит, нарушений поймано {total} из {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
