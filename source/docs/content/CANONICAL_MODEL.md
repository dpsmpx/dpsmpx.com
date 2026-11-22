# Модель канонического контента

Объект контента v2: **один канон — много форм** (Д22, постановка §1,
§9–12, §21–27, §39–40, §78, §89, §91–93). Объект v1 (`CONTENT_MODEL.md`)
остаётся основой: цель, аудитории, утверждения, гейты, состояния;
v2 добавляет канон, варианты площадок, бренды, цели публикации и
зависимости. Схемы — `schemas/content_item.schema.json` (v2),
`canonical.schema.json`, `variant.schema.json`; проверки — `canonical`,
`claims`, `items` в `tools/check.sh`.

## 1. Сущности и связи

```
Project (data/projects/<id>.yaml) ── Release (data/releases/<id>.yaml)
   │  факты проекта — data/facts/facts.yaml (PROJECT_FACTS, EVIDENCE)
   ▼
ContentItem v2 (content/items/<id>-<slug>/item.yaml)          ContentCampaign (data/campaigns/CMP-NNNN.yaml)
   ├── canonical/v1.md, v2.md …  каноническая версия ◄──────────── items[], schedule[] (когда, куда)
   ├── variants/<площадка>.<язык>.md  вариант площадки (source_version)
   ├── spec/, renders/, exports/  изображения (как в v1)
   └── provenance.yaml             происхождение медиа
   │
   ▼  publish (движок, Д24)
Publication (data/publications/<окружение>.jsonl) ──► Analytics (data/metrics/ → события, Д29)
```

Связь «проект → релиз → новость → статья → посты → видео» (§11)
восстанавливается так: релиз (`data/releases/`) → объект с
`source_projects` и `campaign` → его канон и варианты → записи журнала
по объекту → метрики по `publication_id`. Сводка кампании —
`python3 -m tools.cs campaign status CMP-NNNN`.

## 2. ContentItem v2 — что добавлено

| Поле | Смысл |
|---|---|
| `schema: content_item/v2` | версия схемы (= `content_schema_version`, Д31) |
| `category` | `news`, `devlog`, `article`, `release` — записи ленты `/news/`; `page` — страница сайта |
| `tags` | метки (страницы `/tags/<метка>/`) |
| `brand` | `{mode: PERSONAL | PROJECT | MIXED, brands: [...]}` (Д27) |
| `campaign` | `CMP-NNNN`, если объект — часть кампании |
| `website.path` | адрес страницы (`/about/`); записи — `/news/<slug>/` |
| `canonical` | `{lang, current, versions[{version, file, date, sha256, deps, note}]}` |
| `targets` | цели публикации: `{variant, destination}` или `{variant, na: причина}` (§8 `publication_targets`) |

`NewsItem` (§8) — это объект v2 с `category: news`: id, slug, title,
summary и body (канон), автор (бренд), дата (первая публикация на сайте
в журнале), проекты (`source_projects`), метки, медиа, источники и
утверждения (`claims` + факты из подстановок), состояние и цели.

## 3. Каноническая версия (`canonical/vN.md`)

Заголовок `canonical/v1` (`item`, `version`, `lang`, `date`, `title`,
`summary`, `claims`, `media`, `cta`, `trust`, `generation`,
`change_note`) и текст в **разметке канона** — подмножество Markdown,
которое честно отдаёт любая площадка (`tools/cs/core/markup.py`):
заголовки `##`/`###`, абзацы, списки `- `, **жирный**, *курсив*, `код`,
блоки кода между строками ```` ``` ```` (схемы: отступы сохраняются; Telegram —
`<pre>`, простой текст — как есть), ссылки `[текст](адрес)` и голые
`https://`. Разметки площадок (HTML,
`#метки`, `@упоминания`) в каноне нет — валидатор предупреждает.

**Подстановки** (Д28; §21–22) — числа, версии и адреса не переписываются:

| В тексте | Что подставится |
|---|---|
| `{{fact:GH-LOC}}` | первая допустимая формулировка факта на языке текста |
| `{{fact:GH-CHECKS#1}}` | формулировка с номером |
| `{{link:L-YT-CHANNEL}}` | адрес из `data/identity/links.yaml` (битые — ошибка) |
| `{{site:/projects/galdhold/}}` | адрес на сайте (для площадок — канонический `dpsmpx.com`) |
| `{{release:galdhold.latest.version}}` | поле последнего релиза проекта |

**Версии** (§26–27). `canonical seal` проверяет версию валидатором и
записывает в `item.yaml` её sha256 и зависимости. Зафиксированная
версия **не меняется** — проверка `canonical` красная при правке;
изменение — `canonical new` (копия как `vN+1`, черновик), правка,
`seal`. Разница: `python3 -m tools.cs diff CI-0001 v1 v2`.

## 4. Вариант площадки (`variants/<площадка>[-<суффикс>].<язык>.md`)

Заголовок `variant/v1`: `platform`, `lang`, `format` (`page`, `post`,
`photo_post`, `album`, `description`, `announcement`, `release_note`,
`clip_caption`, `readme`), `source_version`, `version`, `status`
(`draft`, `ready`, `rejected`, `superseded`), `trust` (`unverified`,
`validated`), `title`, `summary`, `media`, `link` (`canonical` — адрес
объекта на сайте), `cta`, `claims` (факты, написанные словами),
`generation`, `deps`, `approval`.

- Вариант может отличаться длиной, порядком, CTA, глубиной техники и
  форматом медиа (§1) — смысл и факты те же, что в каноне.
- Языковой вариант (`website.en`) — перевод того же канона, а не второй
  источник истины (§78).
- **Содержимое** варианта — площадка, язык, формат, версия канона,
  ссылка, CTA, медиа с хэшами и текст **после подстановки фактов**; его
  sha256 — то, что одобряет автор (`approval.sha256`). Изменилось хоть
  что-то — одобрение недействительно (Д12).
- Отрисовка под площадку — в адаптере (`tools/cs/adapters/`): HTML
  Telegram, Markdown Discord/GitHub, простой текст VK/YouTube, HTML сайта.

Жизненный путь варианта:

```
adapt (заготовка из канона, trust: unverified)
  → правка под площадку (сессия) → variant seal (валидатор, deps, status: ready, trust: validated)
  → approve (автор, sha256) → publish (движок, журнал)
правка после одобрения → approval недействителен → seal (version+1) → approve снова
```

## 5. Зависимости и устаревание (§23–24)

При фиксации записываются отпечатки: факты (из подстановок и
`claims`), ссылки, релизы, версия канона с sha256, медиа с sha256.
Вариант **устарел** (`stale`), если:

- есть новая версия канона (`source_version < current`);
- канон-источник изменён после фиксации;
- изменился факт, ссылка или релиз, на которые он опирается;
- изменился файл медиа.

Устаревший вариант не публикуется в рабочее окружение; опубликованный
устаревший называет `python3 -m tools.cs stale` — решает автор (новая
версия или оставить как историю, `GOVERNANCE.md`, §5).

## 6. Бренды (§91–94, Д27)

`data/identity/brands.yaml`: `author` (PERSONAL), `galdhold`, `dplang`
(PROJECT) — тон, визуальный стиль, разрешённые и запрещённые темы,
CTA, официальные ссылки. Режим объекта:

| Режим | Бренды | Пример |
|---|---|---|
| PERSONAL | `[author]` | «Я создал DPlang» |
| PROJECT | `[dplang]` | «DPlang v0.1 released» |
| MIXED | `[author, dplang]` | «Почему я решил создать собственный язык» |

Адресат (`accepts_brands`) принимает только свои бренды — проверяет
валидатор и движок.

## 7. Проект и релиз (§7, §21–22, §37)

`data/projects/<id>.yaml` — каноническая сущность проекта: имя,
прежние имена, вес (`PROJECT_MAP.md`), бренд, подзаголовок и состояние
(id фактов), строки страницы (`technology`, `platforms`, `status`,
`scale`, `code`, `plan` → id фактов), ссылки с публичными подписями,
репозиторий, загрузка, медиа. Страница проекта на сайте собирается из
этих id — переписанных чисел нет. Все проектные объекты ссылаются на
проект через `source_projects`.

`data/releases/<проект>.yaml` — выпуски (`version`, `date`, `status`,
`platforms`, `url`, `download`, `source`); источник — релизы и теги
GitHub после проверки человеком, не сырые данные (§37).

## 8. Медиа (§39–42)

MediaAsset = запись реестра (`data/provenance/assets.yaml`: id, вид —
в том числе `video` для будущего VideoAsset, источник, размеры, проект,
лицензия, происхождение, производные `variants` по назначению: master,
website, telegram, vk, youtube_thumbnail, discord, github) + выходы
объектов (`provenance.yaml`: рендеры и экспорт с хэшами). Производные не
генерируются заново: экспорт выбранного варианта лежит в `exports/` и
указывается в `media` вариантов площадок. Проверки изображений —
`visual`, `exports`, `provenance` (размеры, формат, читаемость,
контраст, безопасные зоны, бренд, метаданные). Видео-конвейер — позже
(ROADMAP, П11), модель допускает его уже сейчас.

## 9. Кампания (§12, §28, §74, §76)

`data/campaigns/CMP-NNNN.yaml`: цель, объекты, дата запуска, расписание
(`{item, variant, destination, at}` или `na`), эксперименты,
результаты. Сводка по площадкам, календарь и поиск — **производные
виды** (`campaign status`, `calendar`, `search`), а не отдельные данные.
События проектов (релиз, веха, видео…) создают **черновик** кампании
(`events`), не публикацию.

## 10. Миграция v1 → v2 (Д31)

`python3 -m tools.cs migrate CI-NNNN` показывает план, `--apply`
переносит `copy/<площадка>.md` в `variants/` с заголовками (язык — по
`platform_languages`, медиа — экспорт выбранного варианта, формат — по
адаптеру площадки), пустые тексты пропускает и пишет строку в
`history`. Канон после миграции заводится вручную (смысл текстов `copy/`
без разметки площадок) — так сделано с CI-0001.
