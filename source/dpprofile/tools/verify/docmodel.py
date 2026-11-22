#!/usr/bin/env python3
"""Общая модель документов DPprofile для проверок tools/verify/.

Разбор строгий (D-04). Front matter — узкое подмножество YAML:

    ---
    ключ: значение
    ключ: [a, b]
    ---

Ключ — [a-z_]+, по строке на ключ, без повторов. Значение — одна строка;
список — в квадратных скобках, элементы [A-Za-z0-9_.-]+. Чтобы файл
оставался корректным YAML, в значении нет «: » и « #», и оно не
начинается со служебных знаков YAML. Всё, что вне подмножества, — ошибка,
а не «как-нибудь разобралось».

Модуль ничего не печатает и не завершает процесс: загрузчики возвращают
данные и список ошибок, решают проверки.

    python3 tools/verify/docmodel.py clones   # строки «клон адрес» для fetch_sources.sh
"""
import datetime
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FACTS_DIR = "docs/facts"
INSIGHTS_DIR = "docs/insights"
REGISTRY = "docs/sources/REGISTRY.md"
NOTES = "docs/sources/NOTES.md"
MAP = "docs/sources/MAP.md"
SCOPE = "docs/direction/SCOPE.md"
DECISIONS = "docs/direction/DECISIONS.md"
ROADMAP_DIR = "docs/direction/ROADMAP"
ROADMAP = ROADMAP_DIR + "/README.md"
TIMELINE = "docs/timeline/TIMELINE.md"
METHOD = "docs/method/METHOD.md"
STATUS = "docs/book/STATUS.md"
OUTLINE = "docs/book/OUTLINE.md"
TODO = "TODO.md"
README = "README.md"
RUN_SH = "tools/verify/run.sh"

FACT_ID = re.compile(r"^F-\d{4}$")
INSIGHT_ID = re.compile(r"^I-\d{4}$")
HYPOTHESIS_ID = re.compile(r"^H-\d{4}$")
SOURCE_ID = re.compile(r"^S-\d{2}$")
NOTE_ID = re.compile(r"^N-\d{4}$")
DECISION_ID = re.compile(r"^D-\d{2}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
ITEM = re.compile(r"^[A-Za-z0-9_.-]+$")
KEY_LINE = re.compile(r"^([a-z_]+): (.*)$")
YAML_START = tuple("-?:,[]{}#&*!|>'\"%@`")


class DocError(Exception):
    pass


def path(rel, root=None):
    return os.path.join(root or ROOT, rel)


def read(rel, root=None):
    with open(path(rel, root), encoding="utf-8") as f:
        return f.read()


def exists(rel, root=None):
    return os.path.exists(path(rel, root))


def iso(value):
    """Дата ISO YYYY-MM-DD или None."""
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def today():
    override = os.environ.get("DPPROFILE_TODAY")
    return iso(override) if override else datetime.date.today()


# ---------------------------------------------------------------- front matter

def parse_front_matter(text):
    """(поля, тело) или DocError."""
    if "\r" in text:
        raise DocError("переводы строк CR запрещены")
    lines = text.split("\n")
    if not lines or lines[0] != "---":
        raise DocError("файл не начинается с front matter («---»)")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise DocError("front matter не закрыт («---»)")
    fields = {}
    for n, line in enumerate(lines[1:end], start=2):
        m = KEY_LINE.match(line)
        if not m:
            raise DocError(f"строка {n} вне схемы front matter: {line!r}")
        key, raw = m.group(1), m.group(2)
        if key in fields:
            raise DocError(f"поле {key} повторяется")
        if raw != raw.strip() or raw == "":
            raise DocError(f"поле {key}: пустое значение или пробелы по краям")
        if "\t" in raw:
            raise DocError(f"поле {key}: табуляция")
        if raw.startswith("["):
            if not raw.endswith("]"):
                raise DocError(f"поле {key}: список не закрыт «]»")
            inner = raw[1:-1].strip()
            items = [] if inner == "" else [x.strip() for x in inner.split(",")]
            for it in items:
                if not ITEM.match(it):
                    raise DocError(f"поле {key}: элемент списка вне схемы: {it!r}")
            fields[key] = items
        else:
            if raw.startswith(YAML_START):
                raise DocError(f"поле {key}: значение начинается со служебного знака YAML")
            if ": " in raw or " #" in raw or raw.endswith(":"):
                raise DocError(f"поле {key}: «: », « #» или «:» в конце ломают YAML — перефразировать")
            fields[key] = raw
    body = "\n".join(lines[end + 1:])
    return fields, body


def load_docs(directory, pattern, root=None):
    """{id-из-имени-файла: (относительный путь, поля, тело)}, ошибки, лишние файлы."""
    docs, errors, extra = {}, [], []
    base = path(directory, root)
    if not os.path.isdir(base):
        return docs, [(directory, "каталога нет")], extra
    for name in sorted(os.listdir(base)):
        rel = f"{directory}/{name}"
        if name == "README.md":
            continue
        stem, ext = os.path.splitext(name)
        if ext != ".md" or not pattern.match(stem):
            extra.append(rel)
            continue
        try:
            fields, body = parse_front_matter(read(rel, root))
        except DocError as e:
            errors.append((rel, str(e)))
            continue
        docs[stem] = (rel, fields, body)
    return docs, errors, extra


def load_facts(root=None):
    return load_docs(FACTS_DIR, re.compile(r"^F-\d+$"), root)


def load_insights(root=None):
    return load_docs(INSIGHTS_DIR, re.compile(r"^[IH]-\d+$"), root)


def is_active(fields):
    return fields.get("status", "active") == "active"


# ---------------------------------------------------------------- таблицы

def table_rows(text, header):
    """Строки markdown-таблицы, заголовок которой совпадает с header (список ячеек)."""
    lines = text.split("\n")
    want = [h.strip() for h in header]
    for i, line in enumerate(lines):
        if split_row(line) == want:
            rows = []
            for j, row in enumerate(lines[i + 2:], start=i + 3):
                if not row.startswith("|"):
                    break
                rows.append((j, split_row(row)))
            return rows
    return None


def split_row(line):
    line = line.strip()
    if not (line.startswith("|") and line.endswith("|")):
        return None
    return [c.strip() for c in line[1:-1].split("|")]


def ids_in(text, prefix, digits):
    return re.findall(rf"(?<![\w:]){prefix}-\d{{{digits}}}\b", text)


# ---------------------------------------------------------------- источники

REGISTRY_HEADER = ["Источник", "Вид", "Адрес", "Доступ", "Клон", "Что это"]


def load_registry(root=None):
    """{S-NN: {kind, address, access, clone, what, line}}, ошибки."""
    out, errors = {}, []
    if not exists(REGISTRY, root):
        return out, [(REGISTRY, "файла нет")]
    rows = table_rows(read(REGISTRY, root), REGISTRY_HEADER)
    if rows is None:
        return out, [(REGISTRY, "нет таблицы с заголовком " + " | ".join(REGISTRY_HEADER))]
    for n, cells in rows:
        where = f"{REGISTRY}:{n}"
        if cells is None or len(cells) != 6:
            errors.append((where, "в строке реестра не 6 ячеек"))
            continue
        sid, kind, address, access, clone, what = cells
        if not SOURCE_ID.match(sid):
            errors.append((where, f"номер источника не S-NN: {sid!r}"))
            continue
        if sid in out:
            errors.append((where, f"источник {sid} повторяется"))
            continue
        if kind not in ("repo", "site", "self"):
            errors.append((where, f"{sid}: вид не repo/site/self: {kind!r}"))
        if access not in ("public", "private"):
            errors.append((where, f"{sid}: доступ не public/private: {access!r}"))
        address = address.strip("`")
        clone = clone.strip("`")
        if kind in ("repo", "self") and not re.fullmatch(r"github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", address):
            errors.append((where, f"{sid}: адрес репозитория не github.com/владелец/имя: {address!r}"))
        if kind == "site" and not re.fullmatch(r"[a-z0-9.-]+\.[a-z]{2,}(/[A-Za-z0-9_./-]*)?", address):
            errors.append((where, f"{sid}: адрес сайта не «хост[/путь]»: {address!r}"))
        if kind == "repo" and not re.fullmatch(r"[a-z0-9_.-]+", clone):
            errors.append((where, f"{sid}: у репозитория нет имени клона"))
        if kind != "repo" and clone != "—":
            errors.append((where, f"{sid}: клон бывает только у вида repo (иначе «—»)"))
        if not what:
            errors.append((where, f"{sid}: пустое «Что это»"))
        out[sid] = {"kind": kind, "address": address, "access": access,
                    "clone": clone, "what": what, "line": where}
    return out, errors


NOTE_FIELDS = ("source", "observed", "origin", "content", "verify")


def load_notes(root=None):
    """{N-NNNN: {поле: значение}}, ошибки."""
    out, errors = {}, []
    if not exists(NOTES, root):
        return out, [(NOTES, "файла нет")]
    current, line_no = None, 0
    for n, line in enumerate(read(NOTES, root).split("\n"), start=1):
        m = re.match(r"^### (N-\d+)\s*$", line)
        if m:
            current = m.group(1)
            if not NOTE_ID.match(current):
                errors.append((f"{NOTES}:{n}", f"номер заметки не N-NNNN: {current}"))
            if current in out:
                errors.append((f"{NOTES}:{n}", f"заметка {current} повторяется"))
            out[current] = {"line": f"{NOTES}:{n}"}
            continue
        if line.startswith("## ") or line.startswith("# "):
            current = None
            continue
        if current:
            fm = re.match(r"^- ([a-z]+): (.+)$", line)
            if fm:
                key, value = fm.group(1), fm.group(2).strip()
                if key not in NOTE_FIELDS:
                    errors.append((f"{NOTES}:{n}", f"{current}: неизвестное поле {key}"))
                elif key in out[current]:
                    errors.append((f"{NOTES}:{n}", f"{current}: поле {key} повторяется"))
                else:
                    out[current][key] = value
    return out, errors


MAP_HEADER = ["Источник", "Место", "Коммит", "Что там"]


def load_map(root=None):
    """[(строка, S-NN, место, sha, описание)], ошибки."""
    out, errors = [], []
    if not exists(MAP, root):
        return out, [(MAP, "файла нет")]
    rows = table_rows(read(MAP, root), MAP_HEADER)
    if rows is None:
        return out, [(MAP, "нет таблицы с заголовком " + " | ".join(MAP_HEADER))]
    for n, cells in rows:
        where = f"{MAP}:{n}"
        if cells is None or len(cells) != 4:
            errors.append((where, "в строке карты не 4 ячейки"))
            continue
        sid, place, sha, what = (c.strip("`") if i < 3 else c for i, c in enumerate(cells))
        out.append((where, sid, place, sha, what))
    return out, errors


def load_scope_tags(root=None):
    """{тег: [S-NN]}, ошибки."""
    out, errors = {}, []
    if not exists(SCOPE, root):
        return out, [(SCOPE, "файла нет")]
    rows = table_rows(read(SCOPE, root), ["Тег", "Проект", "Источники"])
    if rows is None:
        return out, [(SCOPE, "нет таблицы «Тег | Проект | Источники»")]
    for n, cells in rows:
        where = f"{SCOPE}:{n}"
        if cells is None or len(cells) != 3:
            errors.append((where, "в строке тегов не 3 ячейки"))
            continue
        tag = cells[0].strip("`")
        if not re.fullmatch(r"[a-z][a-z0-9-]*", tag):
            errors.append((where, f"тег вне схемы: {tag!r}"))
            continue
        if tag in out:
            errors.append((where, f"тег {tag} повторяется"))
        sources = [s.strip() for s in cells[2].split(",") if s.strip()]
        out[tag] = sources
    return out, errors


# ---------------------------------------------------------------- решения

def load_decisions(root=None):
    """{D-NN: {title, status, date, mark, text, line}}, номер «следующий свободный», ошибки."""
    out, errors = {}, []
    if not exists(DECISIONS, root):
        return out, None, [(DECISIONS, "файла нет")]
    text = read(DECISIONS, root)
    m = re.search(r"следующий\s+свободный\s+номер\s+\(сейчас\s+—\s+\*\*(\d+)\*\*\)", text)
    next_free = int(m.group(1)) if m else None
    current = None
    for n, line in enumerate(text.split("\n"), start=1):
        h = re.match(r"^### (D-\d+) — (.+)$", line)
        if h:
            current = h.group(1)
            if current in out:
                errors.append((f"{DECISIONS}:{n}", f"решение {current} повторяется"))
            out[current] = {"title": h.group(2), "status": None, "date": None,
                            "mark": None, "fields": set(), "text": "", "line": f"{DECISIONS}:{n}"}
            continue
        if line.startswith("## ") or line.startswith("# "):
            current = None
            continue
        if current:
            d = out[current]
            d["text"] += line + "\n"
            f = re.match(r"^- \*\*([^*]+?)[:.]\*\*\s*(.*)$", line)
            if f:
                name, value = f.group(1), f.group(2).strip()
                d["fields"].add(name)
                if name == "Статус":
                    d["status"] = value
                elif name == "Дата":
                    d["date"] = value
                elif name == "Метка":
                    d["mark"] = value.strip("`")
    return out, next_free, errors


def accepted(decision):
    return decision.get("status") == "принято"


# ---------------------------------------------------------------- этапы

STAGE_STATE = re.compile(r"^(выполнен \((\d{4}-\d{2}-\d{2})\)|в работе|—)$")
CRITERION = re.compile(r"^- \[( |x)\] (.+?)(?:\s*<!--\s*gate:\s*(.+?)\s*-->)?\s*$")


def load_stages(root=None):
    """[{n, title, state, file, file_state, file_title, criteria:[(line, checked, text, gate)]}], ошибки."""
    stages, errors = [], []
    if not exists(ROADMAP, root):
        return stages, [(ROADMAP, "файла нет")]
    rows = table_rows(read(ROADMAP, root), ["Этап", "Суть", "Состояние"])
    if rows is None:
        return stages, [(ROADMAP, "нет таблицы «Этап | Суть | Состояние»")]
    for n, cells in rows:
        where = f"{ROADMAP}:{n}"
        if cells is None or len(cells) != 3:
            errors.append((where, "в строке плана не 3 ячейки"))
            continue
        num, essence, state = cells
        lm = re.fullmatch(r"\[(.+)\]\((stage-\d+\.md)\)", essence)
        if not num.isdigit() or not lm:
            errors.append((where, "строка плана не «N | [Суть](stage-N.md) | состояние»"))
            continue
        stage = {"n": int(num), "title": lm.group(1), "state": state, "line": where,
                 "file": f"{ROADMAP_DIR}/{lm.group(2)}", "criteria": [],
                 "file_state": None, "file_title": None}
        if not exists(stage["file"], root):
            errors.append((where, f"нет файла этапа {stage['file']}"))
        else:
            for k, line in enumerate(read(stage["file"], root).split("\n"), start=1):
                t = re.match(r"^# Этап (\d+) — (.+)$", line)
                if t:
                    stage["file_title"] = (int(t.group(1)), t.group(2))
                s = re.match(r"^Состояние: (.+)$", line)
                if s:
                    stage["file_state"] = s.group(1).strip()
                c = CRITERION.match(line)
                if c:
                    stage["criteria"].append((f"{stage['file']}:{k}", c.group(1) == "x",
                                              c.group(2), c.group(3)))
        stages.append(stage)
    return stages, errors


def current_stage(stages):
    """Номер этапа «в работе» или None (все выполнены / план сломан)."""
    working = [s["n"] for s in stages if s["state"] == "в работе"]
    return working[0] if len(working) == 1 else None


# ---------------------------------------------------------------- статус книги

STATUS_KEYS = ("book_writing", "steam_release_fact", "permission_decision")


def load_status(root=None):
    """{ключ: значение}, ошибки."""
    out, errors = {}, []
    if not exists(STATUS, root):
        return out, [(STATUS, "файла нет")]
    text = read(STATUS, root)
    m = re.search(r"<!-- book-gate:begin -->\n(.*?)<!-- book-gate:end -->", text, re.S)
    if not m:
        return out, [(STATUS, "нет блока <!-- book-gate:begin --> … <!-- book-gate:end -->")]
    for line in m.group(1).strip().split("\n"):
        kv = re.fullmatch(r"([a-z_]+): (\S+)", line.strip())
        if not kv:
            errors.append((STATUS, f"строка блока book-gate вне схемы: {line!r}"))
            continue
        if kv.group(1) in out:
            errors.append((STATUS, f"поле {kv.group(1)} повторяется"))
        out[kv.group(1)] = kv.group(2)
    for key in STATUS_KEYS:
        if key not in out:
            errors.append((STATUS, f"в блоке book-gate нет поля {key}"))
    for key in out:
        if key not in STATUS_KEYS:
            errors.append((STATUS, f"неизвестное поле блока book-gate: {key}"))
    return out, errors


# ---------------------------------------------------------------- хронология, метод, TODO

def load_timeline(root=None):
    """[(строка, дата, событие, [F-NNNN])], ошибки."""
    out, errors = [], []
    if not exists(TIMELINE, root):
        return out, [(TIMELINE, "файла нет")]
    rows = table_rows(read(TIMELINE, root), ["Дата", "Событие", "Факты"])
    if rows is None:
        return out, [(TIMELINE, "нет таблицы «Дата | Событие | Факты»")]
    for n, cells in rows:
        where = f"{TIMELINE}:{n}"
        if cells is None or len(cells) != 3:
            errors.append((where, "в строке хронологии не 3 ячейки"))
            continue
        refs = [r.strip() for r in cells[2].split(",") if r.strip()]
        out.append((where, cells[0], cells[1], refs))
    return out, errors


def load_method(root=None):
    """[(строка, элемент, где, текст ссылок)], ошибки."""
    out, errors = [], []
    if not exists(METHOD, root):
        return out, [(METHOD, "файла нет")]
    rows = table_rows(read(METHOD, root), ["Элемент процесса", "Где наблюдается", "Факты"])
    if rows is None:
        return out, [(METHOD, "нет таблицы «Элемент процесса | Где наблюдается | Факты»")]
    for n, cells in rows:
        where = f"{METHOD}:{n}"
        if cells is None or len(cells) != 3:
            errors.append((where, "в строке метода не 3 ячейки"))
            continue
        out.append((where, cells[0], cells[1], cells[2]))
    return out, errors


def load_todo(root=None):
    """[(строка, этап, текст)], ошибки."""
    out, errors = [], []
    if not exists(TODO, root):
        return out, [(TODO, "файла нет")]
    for n, line in enumerate(read(TODO, root).split("\n"), start=1):
        if not line.startswith("- "):
            continue
        m = re.match(r"^- \[этап (\d+)\] (\S.*)$", line)
        if not m:
            errors.append((f"{TODO}:{n}", "пункт не «- [этап N] действие» (отмеченные и без этапа запрещены)"))
            continue
        out.append((f"{TODO}:{n}", int(m.group(1)), m.group(2)))
    return out, errors


# ---------------------------------------------------------------- git

def git(args, cwd=None):
    """(код, вывод) команды git; при отсутствии git — (127, '')."""
    try:
        p = subprocess.run(["git"] + args, cwd=cwd or ROOT, capture_output=True, text=True)
    except FileNotFoundError:
        return 127, ""
    return p.returncode, p.stdout


def is_git_repo(root=None):
    code, out = git(["rev-parse", "--is-inside-work-tree"], cwd=root or ROOT)
    if code != 0 or out.strip() != "true":
        return False
    top_code, top = git(["rev-parse", "--show-toplevel"], cwd=root or ROOT)
    return top_code == 0 and os.path.realpath(top.strip()) == os.path.realpath(root or ROOT)


# D-18: DPprofile — компонент SocialMediaImage. До нового переноса —
# отдельная линия с исходной историей DPprofile и изменениями периода DPmetaApp;
# после — коммиты SocialMediaImage с префиксом dpprofile/. Остальные проекты
# не попадают в историю фактов. Опора нужна и самопроверкам.
PRE_MOVE_HEAD = "0e17def1899b6ba76cbbeabb8eeee07f1b103da0"
_history_cache = {}


class History:
    """История DPprofile: каталог для git и отрезки (ревизии для git log, префикс путей).

    Свой репозиторий — один отрезок (HEAD, ""). problem — почему истории нет.
    """

    def __init__(self, where=None, segments=(), problem=None):
        self.where, self.segments, self.problem = where, list(segments), problem

    @property
    def ok(self):
        return self.problem is None

    def _git(self, args):
        return git(args, cwd=self.where)

    def added(self, directory):
        """Пути (от корня DPprofile), когда-либо добавленные в каталог."""
        out = set()
        for revs, prefix in self.segments:
            _, text = self._git(["log", "--format=", "--name-only", "--diff-filter=A", *revs,
                                 "--", prefix + directory])
            out |= {p[len(prefix):] for p in text.split("\n") if p.startswith(prefix + directory + "/")}
        return out

    def first_add(self, rel):
        """(sha, префикс) первого добавления файла — в самом раннем отрезке, где оно есть."""
        for revs, prefix in self.segments:
            _, text = self._git(["log", "--format=%H", "--diff-filter=A", *revs, "--", prefix + rel])
            if text.split():
                return text.split()[-1], prefix
        return None

    def versions(self, rel):
        """[(sha, префикс)] всех коммитов, менявших файл, во всех отрезках."""
        out = []
        for revs, prefix in self.segments:
            _, text = self._git(["log", "--format=%H", *revs, "--", prefix + rel])
            out += [(sha, prefix) for sha in text.split()]
        return out

    def show(self, sha, prefix, rel):
        return self._git(["show", f"{sha}:{prefix}{rel}"])

    def last_change(self, rel):
        """Дата (ГГГГ-ММ-ДД) последнего коммита, менявшего файл, или ""."""
        return self.last_commit(rel)[1]

    def last_commit(self, rel):
        """(коммит, дата ГГГГ-ММ-ДД) последней правки файла или ("", "")."""
        for revs, prefix in reversed(self.segments):
            _, text = self._git(["log", "-1", "--format=%H %cs", *revs, "--", prefix + rel])
            if text.strip():
                sha, _, day = text.strip().partition(" ")
                return sha, day
        return "", ""

    def shallow_boundary(self, sha):
        """Коммит — граница неглубокого клона: у него в клоне нет родителей, и правкой
        файла он выглядит, даже если файл не менялся (git clone --depth)."""
        code, path = self._git(["rev-parse", "--git-path", "shallow"])
        if code != 0 or not sha:
            return False
        where = path.strip()
        if not os.path.isabs(where):
            where = os.path.join(self.where, where)
        try:
            with open(where, encoding="ascii") as f:
                return sha in {line.strip() for line in f}
        except OSError:
            return False

    def locate(self, sha):
        """Префикс путей коммита из истории DPprofile или None — коммит не его."""
        code, kind = self._git(["cat-file", "-t", sha])
        if code != 0 or kind.strip() != "commit":
            return None
        if len(self.segments) == 1:
            return self.segments[0][1]
        (pre, pre_prefix), (post, post_prefix) = self.segments
        if self._git(["merge-base", "--is-ancestor", sha, pre[0]])[0] == 0:
            return pre_prefix
        merge = post[1].lstrip("^")
        if (self._git(["merge-base", "--is-ancestor", merge, sha])[0] == 0
                and self._git(["merge-base", "--is-ancestor", sha, "HEAD"])[0] == 0):
            return post_prefix
        return None


def history(root=None):
    """History DPprofile для каталога root (свой репозиторий или каталог в DPmetaApp)."""
    root = os.path.realpath(root or ROOT)
    onto = os.environ.get("DPPROFILE_PRE_MOVE_HEAD", PRE_MOVE_HEAD)
    _, head = git(["rev-parse", "-q", "--verify", "HEAD"], cwd=root)
    key = (root, onto, head.strip())
    if key not in _history_cache:
        _history_cache[key] = _history(root, onto)
    return _history_cache[key]


def _history(root, onto):
    if is_git_repo(root):
        return History(root, [(["HEAD"], "")])
    code, inside = git(["rev-parse", "--is-inside-work-tree"], cwd=root)
    if code != 0 or inside.strip() != "true":
        return History(problem="не репозиторий git — историю не проверить")
    _, top = git(["rev-parse", "--show-toplevel"], cwd=root)
    _, prefix = git(["rev-parse", "--show-prefix"], cwd=root)
    top = top.strip()
    # Слияние поддерева: коммит, у которого опора — не первый родитель.
    _, merges = git(["rev-list", "--merges", "--parents", "HEAD"], cwd=top)
    merge = next((line.split()[0] for line in merges.split("\n") if onto in line.split()[2:]), None)
    if merge is None:
        return History(problem=f"нет слияния поддерева {prefix.strip()} с опорой {onto[:7]} "
                               "(DPPROFILE_PRE_MOVE_HEAD) — историю не проверить")
    return History(top, [([onto], ""), (["HEAD", "^" + merge], prefix.strip())])

# ---------------------------------------------------------------- условия этапов

class Context:
    """Всё, что нужно условиям критериев; загружается один раз."""

    def __init__(self, root=None):
        self.root = root or ROOT
        # Условия, которые не проверить без полной истории git: «терм: причина».
        self.unknown = []
        self.facts, _, _ = load_facts(self.root)
        self.insights, _, _ = load_insights(self.root)
        self.registry, _ = load_registry(self.root)
        self.notes, _ = load_notes(self.root)
        self.tags, _ = load_scope_tags(self.root)
        self.decisions, _, _ = load_decisions(self.root)
        self.status, _ = load_status(self.root)
        self.timeline, _ = load_timeline(self.root)
        self.method, _ = load_method(self.root)

    def active_facts(self):
        return {k: v for k, v in self.facts.items() if is_active(v[1])}

    def counts(self):
        active_ins = {k: v for k, v in self.insights.items() if is_active(v[1])}
        return {
            "facts": len(self.active_facts()),
            "insights": sum(1 for k in active_ins if k.startswith("I-")),
            "hypotheses": sum(1 for k in active_ins if k.startswith("H-")),
            "sources": len(self.registry),
            "notes": len(self.notes),
            "timeline": len(self.timeline),
            "decisions": sum(1 for d in self.decisions.values() if accepted(d)),
        }


def eval_gate(expr, ctx):
    """(истинно?, [ошибки формата]) для условия «терм & терм …»."""
    errors, result = [], True
    for term in [t.strip() for t in expr.split("&")]:
        ok, err = eval_term(term, ctx)
        if err:
            errors.append(err)
        result = result and ok
    return result, errors


def eval_term(term, ctx):
    kind, _, arg = term.partition(":")
    if kind == "file":
        return exists(arg, ctx.root), None
    if kind == "check":
        script = f"tools/verify/{arg}.py"
        if not exists(script, ctx.root):
            return False, None
        run = read(RUN_SH, ctx.root) if exists(RUN_SH, ctx.root) else ""
        return f"{arg}.py" in run, None
    if kind == "count":
        m = re.fullmatch(r"([a-z]+)>=(\d+)", arg)
        counts = ctx.counts()
        if not m or m.group(1) not in counts:
            return False, f"неизвестный счёт в условии: {term}"
        return counts[m.group(1)] >= int(m.group(2)), None
    if kind == "coverage":
        return coverage(arg, ctx)
    if kind == "stable":
        m = re.fullmatch(r"(.+)>=(\d+)", arg)
        if not m:
            return False, f"условие stable не «путь>=дней»: {term}"
        ok, unknown = stable_check(m.group(1), int(m.group(2)), ctx.root)
        if unknown:
            ctx.unknown.append(f"{term}: {unknown}")
        return ok, None
    if kind == "decision-mark":
        return any(accepted(d) and d.get("mark") == arg for d in ctx.decisions.values()), None
    if kind == "fact-mark":
        return any(arg in (f.get("marks") or []) for _, f, _ in ctx.active_facts().values()), None
    if kind == "status":
        key, _, value = arg.partition("=")
        if key not in STATUS_KEYS or not value:
            return False, f"условие status не «поле=значение»: {term}"
        return ctx.status.get(key) == value, None
    return False, f"неизвестный терм условия: {term}"


def coverage(what, ctx):
    tags = set(ctx.tags)
    if what == "sources":
        return all(any(s in ctx.registry for s in ctx.tags[t]) for t in tags), None
    if what == "facts":
        seen = {p for _, f, _ in ctx.active_facts().values() for p in (f.get("projects") or [])}
        return tags <= seen, None
    if what == "areas":
        seen = {f.get("area") for _, f, _ in ctx.active_facts().values()}
        return {"project", "process", "result"} <= seen, None
    if what == "timeline":
        seen = set()
        for _, _, _, refs in ctx.timeline:
            for r in refs:
                if r in ctx.facts:
                    seen |= set(ctx.facts[r][1].get("projects") or [])
        return tags <= seen, None
    if what == "outline":
        if not exists(OUTLINE, ctx.root):
            return False, None
        items = [l for l in read(OUTLINE, ctx.root).split("\n") if re.match(r"^\s*- ", l)]
        return bool(items) and all(re.search(r"\b[FIH]-\d{4}\b", l) for l in items), None
    if what == "method":
        return bool(ctx.method) and all(re.search(r"\bI-\d{4}\b", refs) for _, _, _, refs in ctx.method), None
    return False, f"неизвестное покрытие: coverage:{what}"


def stable(rel, days, root):
    return stable_check(rel, days, root)[0]


def stable_check(rel, days, root):
    """(истинно?, почему не проверить) для `stable:ПУТЬ>=ДНЕЙ`.

    Без истории (копия без git) и в неглубоком клоне, где граница клона выглядит
    правкой файла, условие не проверить: второе значение — причина, а не ложное
    «условие ложно».
    """
    h = history(root)
    if not h.ok:
        return False, h.problem
    if not exists(rel, root):
        return False, None
    code, dirty = git(["status", "--porcelain", "--", rel], cwd=root)
    if code != 0 or dirty.strip():
        return False, None
    sha, day = h.last_commit(rel)
    if h.shallow_boundary(sha):
        return False, (f"неглубокий клон: граница истории {sha[:7]} выглядит правкой {rel} — "
                       "git fetch --unshallow")
    last = iso(day)
    return last is not None and (today() - last).days >= days, None


# ---------------------------------------------------------------- отчёт

class Report:
    """Сбор ошибок проверки и единый вывод: «✓ имя: итог» или «✗ место: ошибка»."""

    def __init__(self, name):
        self.name = name
        self.errors = []
        self.notes = []

    def err(self, where, message):
        self.errors.append((where, message))

    def extend(self, pairs):
        self.errors.extend(pairs)

    def note(self, message):
        self.notes.append(message)

    def finish(self, summary):
        for message in self.notes:
            print(f"  · {message}")
        if self.errors:
            for where, message in self.errors:
                print(f"✗ {where}: {message}")
            print(f"✗ {self.name}: ошибок — {len(self.errors)}")
            return 1
        print(f"✓ {self.name}: {summary}")
        return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["clones"]:
        registry, errors = load_registry()
        if errors:
            for where, message in errors:
                print(f"✗ {where}: {message}", file=sys.stderr)
            sys.exit(1)
        for sid, s in sorted(registry.items()):
            if s["kind"] == "repo":
                print(f"{s['clone']} https://{s['address']}")
        sys.exit(0)
    print(__doc__)
    sys.exit(2)
