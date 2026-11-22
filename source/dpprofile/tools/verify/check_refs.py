#!/usr/bin/env python3
"""Ссылки фактов и карты мест совпадают с клонами источников (D-05; полный прогон).

Клоны кладёт tools/verify/fetch_sources.sh в build/sources/<клон>.git
(каталог можно сменить переменной DPPROFILE_SOURCES); источник вида self —
сам этот репозиторий. Для каждого факта со ссылкой на репозиторий:

  * commit — коммит есть, а date равна дате коммитера (%cs);
  * file — коммит есть, путь на нём есть, date не позже даты коммита;
  * release — коммит есть, тег есть (перемещённый тег — пометка, не
    ошибка), date не раньше даты коммита;

для каждой строки docs/sources/MAP.md — путь или тег есть на коммите.
Нет клона нужного источника — ошибка: полный прогон пропусков не
допускает. Страницы (url) и заметки сетью не проверяются — у них дата
наблюдения (docs/sources/CITATION.md).

    python3 tools/verify/check_refs.py

Код возврата: 0 — всё сошлось; 1 — расхождения или нет клонов.
"""
import os
import sys

import docmodel as dm


def sources_dir(root):
    return os.environ.get("DPPROFILE_SOURCES") or os.path.join(root, "build", "sources")


def repo_dir(sid, registry, root):
    s = registry[sid]
    if s["kind"] == "self":
        h = dm.history(root)  # в DPmetaApp — только история DPprofile (D-16), не весь репозиторий
        return h if h.ok else None
    d = os.path.join(sources_dir(root), s["clone"] + ".git")
    return d if os.path.isdir(d) else None


def commit_date(repo, sha):
    if isinstance(repo, dm.History):
        if repo.locate(sha) is None:
            return None
        repo = repo.where
    code, kind = dm.git(["cat-file", "-t", sha], cwd=repo)
    if code != 0 or kind.strip() != "commit":
        return None
    code, out = dm.git(["log", "-1", "--format=%cs", sha], cwd=repo)
    return dm.iso(out.strip())


def path_at(repo, sha, place):
    if isinstance(repo, dm.History):
        prefix = repo.locate(sha)
        if prefix is None:
            return False
        repo, place = repo.where, prefix + place
    code, out = dm.git(["ls-tree", sha, "--", place], cwd=repo)
    return code == 0 and bool(out.strip())


def tag_commit(repo, tag):
    if isinstance(repo, dm.History):
        repo = repo.where
    code, out = dm.git(["rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}"], cwd=repo)
    return out.strip() if code == 0 else None


def check(root=None):
    root = root or dm.ROOT
    r = dm.Report("сверка ссылок с клонами")
    registry, errors = dm.load_registry(root)
    r.extend(errors)
    facts, _, _ = dm.load_facts(root)
    entries, errors = dm.load_map(root)
    r.extend(errors)

    missing = set()

    def repo_for(where, sid):
        if sid not in registry or registry[sid]["kind"] not in ("repo", "self"):
            return None
        repo = repo_dir(sid, registry, root)
        if repo is None and sid not in missing:
            missing.add(sid)
            if registry[sid]["kind"] == "self":
                r.err(where, f"нет истории источника {sid} (этот репозиторий): {dm.history(root).problem}")
            else:
                r.err(where, f"нет клона источника {sid} ({registry[sid]['address']}) — "
                             "запустить tools/verify/fetch_sources.sh")
        return repo

    checked = 0
    for stem, (rel, f, _) in sorted(facts.items()):
        stype, ref = f.get("source_type"), str(f.get("ref", ""))
        if stype not in ("commit", "file", "release"):
            continue
        repo = repo_for(rel, f.get("source"))
        if repo is None:
            continue
        checked += 1
        date = dm.iso(f.get("date"))
        if stype == "commit":
            sha, place = ref, None
        else:
            place, _, sha = ref.rpartition("@")
        cdate = commit_date(repo, sha)
        if cdate is None:
            r.err(rel, f"нет коммита {sha[:12]} в {f.get('source')}")
            continue
        if stype == "commit" and date != cdate:
            r.err(rel, f"date {date} не равна дате коммита {sha[:7]} ({cdate})")
        if stype == "file":
            if not path_at(repo, sha, place):
                r.err(rel, f"нет файла {place} на коммите {sha[:7]}")
            if date and date > cdate:
                r.err(rel, f"date {date} позже коммита {sha[:7]} ({cdate}), на который ссылается факт")
        if stype == "release":
            at = tag_commit(repo, place)
            if at is None:
                r.err(rel, f"нет тега {place}")
            elif at != sha:
                r.note(f"{rel}: тег {place} теперь на {at[:7]}, а не на {sha[:7]} — факт о дне наблюдения")
            if date and date < cdate:
                r.err(rel, f"date {date} раньше коммита тега ({cdate})")

    for where, sid, place, sha, _ in entries:
        repo = repo_for(where, sid)
        if repo is None:
            continue
        checked += 1
        if commit_date(repo, sha) is None:
            r.err(where, f"нет коммита {sha[:12]} в {sid}")
        elif place.startswith("tag:"):
            at = tag_commit(repo, place[4:])
            if at is None:
                r.err(where, f"нет тега {place[4:]}")
            elif at != sha:
                r.note(f"{where}: тег {place[4:]} теперь на {at[:7]}, а не на {sha[:7]}")
        elif not path_at(repo, sha, place):
            r.err(where, f"нет {place} на коммите {sha[:7]}")

    return r.finish(f"сверено ссылок {checked}")


if __name__ == "__main__":
    sys.exit(check())
