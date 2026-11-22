# Архитектура

Как устроены репозиторий и инструменты **сейчас**. Почему правила
такие — `docs/PROCESS.md`; что решено — `docs/direction/DECISIONS.md`;
постановка платформы — `docs/direction/PLATFORM_VISION.md`.

## 1. Главная идея

```
Author identity → Canonical knowledge → Canonical content → Owned website → Replaceable adapters → External platforms
(docs/identity)   (data/facts, projects)  (content/items v2)   (tools/cs/site)  (tools/cs/adapters)      (Telegram, VK, …)
                                                                                     │
Analytics ← Publications (журнал) ←──────────────────────────────────────────────────┘
   └→ Knowledge → Strategy (решения автора) → следующий контент
```

Главная собственность автора — канон, медиа, происхождение и история
публикаций в Git; площадки — каналы распространения (§122). Контент
создаётся один раз и показывается многими родными формами (Д22).

## 2. Слои и модули (модульный монолит, Д23)

Один пакет `tools/cs`, одна командная строка `python3 -m tools.cs`.

```
tools/cs/
├── core/            ЯДРО — не знает площадок по имени (тест Boundaries)
│   ├── repo.py          чтение данных с подменяемым корнем (тесты на временном репозитории)
│   ├── textdoc.py       файлы «заголовок YAML + текст» (каноны, варианты)
│   ├── markup.py        разметка канона и рендеры: HTML, HTML Telegram, Markdown, текст
│   ├── inject.py        подстановки {{fact|link|site|release|progress|figure:…}}, отпечатки зависимостей
│   ├── sensitive.py     фильтр чувствительных данных на выходе сайта (Д39)
│   ├── content.py       ContentItem v2: версии канона, варианты, хэш содержимого, одобрение, устаревание
│   ├── validator.py     ContentValidator (§46)
│   ├── ledger.py        журнал публикаций: события, переходы, ключ идемпотентности, целостность
│   ├── engine.py        движок: план → предпроверка → публикация → проверка → запись; повторы; режимы
│   ├── errors.py retry.py credentials.py obs.py   коды ошибок; повторы и частота; учётные данные; логи без секретов
│   ├── campaigns.py     сводка по площадкам, календарь, поиск — виды над моделью
│   ├── analytics.py     нормализованные события метрик (Д29)
│   ├── generation.py    GenerationProvider и кэш генерации (§43–44)
│   ├── events.py        событие проекта → черновик кампании (§36–38)
│   ├── migrate.py       явные миграции схем (Д31)
│   ├── bundle.py health.py   выгрузка базы; здоровье
├── adapters/        ПЛОЩАДКИ — по адаптеру на площадку за PlatformAdapter (§29)
│   ├── base.py          интерфейс: render, validate, identify/check_identity, publish, edit, delete,
│   │                    upload_media, get_status, лимиты из capabilities.yaml, ограничитель частоты, повторы
│   ├── website.py       сайт: сборка с записью + выгрузка (ОР-11)
│   ├── telegram.py      Bot API через транспорт (urllib; в тестах — имитация API)
│   ├── manual.py        VK, YouTube, Discord, GitHub, TikTok — отрисовка и лимиты; публикация — ручной путь (Д33)
│   └── mock.py          имитации всех площадок с внедрением отказов (§102)
├── progress/        ПРОГРЕСС ЭКОСИСТЕМЫ (Д38) — сбор набора из клонов (collect.py), величины и публичная выжимка
│                    (dataset.py), графики SVG (charts.py), фигуры (figures.py), проверка (check.py)
├── mark/            ВОДЯНОЙ ЗНАК (Д41) — ключ (key.py), метка изображений (image.py) и SVG (svg.py), манифест выпуска (release.py), метки времени RFC 3161 и OpenTimestamps (stamp.py), mark verify (verify.py), команды (cli.py)
├── site/            САЙТ — генератор (build.py), фиды и API (feeds.py), подписи (i18n.py), предпросмотр (preview.py), локальный сервер (serve.py), снимки страниц (shots.py), выгрузка на Beget (deploy.py)
├── platform_cli.py  команды платформы;  platform_checks.py  проверки платформы;  capabilities.py  матрица
└── claims.py facts.py validate.py visual.py exports.py provenance.py render.py …   конвейер изображений и гейты (v1)
website/             тема сайта: templates/base.html, static/style.css (цвета — из токенов бренда)
```

Соответствие структуре постановки (§95): `apps/web` → `tools/cs/site`;
`apps/publisher` → `tools/cs/core/engine.py` + `platform_cli.py`;
`apps/tools` → `tools/cs` (проверки, рендер); `core/*` → `tools/cs/core`;
`adapters/*` → `tools/cs/adapters`; `website/` — тема. Причина — правило
«дополнить существующее, а не завести второе» (`CLAUDE.md`) и одна
командная строка; разделение модулей — то же, что в постановке.

## 3. Данные

| Файл | Схема | Что |
|---|---|---|
| `data/facts/facts.yaml` | `facts` | факты с доказательствами (PROJECT_FACTS, EVIDENCE) |
| `data/facts/forbidden.yaml`, `claim_keywords.yaml` | `forbidden`, `claim_keywords` | anti-hype, слова-утверждения |
| `data/identity/links.yaml` | `links` | проверенные ссылки |
| `data/identity/brands.yaml` | `brands` | бренды автора и проектов (Д27) |
| `data/projects/<id>.yaml` | `project` | канонические сущности проектов |
| `data/releases/<проект>.yaml` | `releases` | выпуски (RELEASE_DATA) — пока нет |
| `data/campaigns/CMP-NNNN.yaml` | `campaign` | кампании |
| `data/platforms/capabilities.yaml` | `capabilities` | что позволяют площадки (Д33) |
| `data/platforms/destinations.yaml` | `destinations` | адресаты с явными id и `credential_ref` (Д25) |
| `data/platforms/export_specs.yaml` | `export_specs` | размеры экспорта (Д13) |
| `data/policy/publication.yaml` | `policy` | одобрение, автопубликация (пусто), роли, повторы, отказы, хранение |
| `data/website/site.yaml` | `site` | сайт: адреса окружений, языки, главная |
| `data/website/path.yaml` | `path` | раздел «Путь» (Д44): станции пути и схема конечной цели — ссылки на факты и вехи |
| `data/publications/<окружение>.jsonl` | `publication` | журнал публикаций (только дописывание) |
| `data/provenance/assets.yaml` | `assets` | входные ассеты (MediaAsset) |
| `data/metrics/…`, `data/experiments/…` | `metrics`, `experiment` | метрики (Д15) и эксперименты (Д14) |
| `assets/brand/tokens.json` | `brand_tokens` | токены визуальной системы |
| `content/items/<id>/item.yaml` | `content_item` v1/v2 | объект контента |
| `content/items/<id>/canonical/vN.md` | `canonical` | каноническая версия |
| `content/items/<id>/variants/<площадка>.<язык>.md` | `variant` | вариант площадки |
| `content/items/<id>/spec/*.yaml`, `provenance.yaml` | `composition`, `item_provenance` | изображения и их происхождение |

Модель — `docs/content/CANONICAL_MODEL.md` (v2) и `CONTENT_MODEL.md` (v1).

## 4. Поток публикации

```
canonical/vN.md ──seal──► variants/*.md ──seal──► approve (автор, sha256)
                                                     │
publish: Publisher.plan → validate_variant + preflight (адресат по id, аккаунт, язык, бренд,
         одобрение, устаревание, канон в Git, политика) → Ledger PUBLISHING → Adapter.publish
         → Adapter.get_status (verify) → Ledger PUBLISHED | FAILED | UNKNOWN (+ RETRY с задержкой)
                                                     │
site build (production): только одобренное и опубликованное → фиды, sitemap, /api/v1/
```

Подробно — `docs/content/PUBLISHING.md`. Окружения и учётные данные —
`docs/operations/`.

## 5. Конвейер изображений (v1, без изменений)

```
spec/*.yaml (composition/v1) → tools/cs/render.py → HTML → tools/render/render.js (Chromium) →
renders/ и exports/: PNG/JPEG + *.layout.json → provenance.yaml (хэши, входы, промпт) → гейты
```

Рендер детерминирован (Д11; `tests/test_render.py`); портрет — только из
`REFERENCE_IMAGE`; каждый формат рендерится под свой размер. Экспорт
выбранного варианта — медиа вариантов площадок (`media` в
`variants/*.md`).

## 6. Проверки (Д3 — без Actions)

`tools/check.sh` — уровни (§99):

| Уровень | Команда | Что |
|---|---|---|
| quick | `tools/check.sh --quick` | схемы, объекты, секреты, ссылки, адресаты — секунды |
| affected | `tools/check.sh --affected` | проверки, затронутые изменёнными файлами (сравнение с `origin/main`) |
| full | `tools/check.sh` | все проверки + все тесты (с рендером) |
| release | `tools/check.sh --release` | full + сборка production-сайта и пробный прогон всех целей кампаний |

| Проверка | Что | Гейт / §99 |
|---|---|---|
| `schemas`, `items` | данные по JSON Schema; состояния, история, гейты | все; malformed content |
| `facts`, `claims` | реестр, утверждения и anti-hype (в том числе тексты `variants/`) | Factual |
| `provenance`, `visual`, `exports` | ассеты и выходы; читаемость, контраст, зоны; файлы экспорта | Provenance, Visual, Platform, Safety, Legal |
| `metrics` | метрики и эксперименты | — |
| `links` | пути в документах | invalid links |
| `secrets` | ключи, токены, cookies, подписанные адреса | secrets, credentials |
| `canonical` | неизменность зафиксированных версий; варианты: валидатор, одобрение, устаревание | content, provenance |
| `publications` | журнал: переходы, время, дубли, одобрение рабочих публикаций | duplicate publication |
| `destinations` | явные id, границы учётных данных, близнецы, бренды | configuration, credentials |
| `campaigns`, `projects` | ссылки на объекты, адресаты, факты страниц | configuration |
| `capabilities` | матрица = данные; данные = адаптеры | adapters |
| `progress` | набор прогресса: ряды и суммы, границы `scope.yaml`, вехи, величины, фигуры на ru и en, публичная выжимка через фильтр Д39 | data, website |
| `site` | сборка staging и production, фиды, JSON, внутренние ссылки; фильтр чувствительных данных по каждому файлу (Д39) | build, website, secrets |
| `siteshots` | страницы staging в Chromium на 390 и 1280 px: прокрутка вбок, край экрана, изображения, CSP, консоль, запросы, шрифт, `h1`, цели касания (`--fast` — пропуск) | website (визуальная регрессия, П2-17) |
| `releases` | манифесты выпусков сайта не изменены после записи; метки времени RFC 3161 и OpenTimestamps на месте (нет — предупреждение и команда `mark stamp`) | website (Д41) |
| тесты | `tests/` — модульные, контрактные, интеграционные, сквозной, свойства, регрессия | tests |

## 7. Тесты (§100–104)

| Вид | Где |
|---|---|
| модульные | `tests/test_platform_units.py` (разметка, подстановки, журнал, повторы, учётные данные), прежние `tests/test_*.py` |
| контрактные (адаптеры) | `tests/test_adapter_contract.py`: Telegram через имитацию Bot API; общий контракт имитаций; ручные адаптеры |
| интеграционные (движок) | `tests/test_publishing.py`: сценарии §56, одобрение, адресаты, бренды, режимы |
| свойства | `tests/test_publishing.py`, `Properties`: случайные сбои — не больше одного поста |
| сквозной | `tests/test_platform_e2e.py`: новость → сайт → Telegram → проверка → аналитика → production-сборка |
| регрессия | рендер (хэши), миграция, неизменность канона, граница модулей; снимки сайта — `tests/test_site_shots.py` (правила ловят поломки, staging фикстуры чистый) |
| прогресс и фильтр | `tests/test_progress.py` (величины, фигуры, границы, валидатор, страница на staging и её отсутствие на production без одобрения), `tests/test_sensitive.py` (каждый вид утечки ловится, чистое и публичное проходит, метаданные изображений) |
| водяной знак | `tests/test_mark.py` (ключ; метка SVG и изображений — повторяемость, заметность, находка после JPEG и уменьшения, чужой ключ; запрос RFC 3161 и своя служба на openssl; выгрузка без ключа — отказ, с ключом — метка один раз, манифест, без сети — метки «позже»; `mark verify`) |
| секреты | `tests/test_secrets.py` (шаблоны ключей и токенов, номер строки; списка личных слов нет — Д40) |

Реальные площадки в тестах не используются; рабочая проверка —
безопасный режим на тестовом канале автора (§104).

## 8. Команды

```sh
tools/check.sh [--quick|--affected|--release|--fast] [проверка …]
python3 -m tools.cs status | render | export | new | metrics import          # конвейер изображений (v1)
python3 -m tools.cs migrate | canonical new|seal | adapt | variant seal | validate | diff
python3 -m tools.cs preview <объект|кампания> | approve <объект> <вариант>
python3 -m tools.cs publish <объект> <вариант> --to <адресат> [--dev|--safe|--production] [--at ISO]
python3 -m tools.cs publish --due | --record-manual | --reconcile | --cancel | --delete
python3 -m tools.cs campaign status|list | calendar | search | stale
python3 -m tools.cs site build|serve|shots|scan [каталог]|deploy | health | bundle | capabilities [--write] | events
python3 -m tools.cs progress collect --start … --end … [--cutoff …] | progress show --id <набор>
python3 -m tools.cs mark init | mark verify <файл|адрес> [--no-key] | mark stamp [выпуск …] [--tsa URL]   # Д41
```

## 9. Окружение

- Python 3.10+ с PyYAML и jsonschema (`tools/requirements.txt`); метка
  изображений и перцептивный хэш (Д41) — ещё numpy и Pillow (там же); метки
  OpenTimestamps — клиент `ots`; проверка `.tsr` — openssl.
- Рендер изображений: Node.js и Playwright с Chromium (как раньше;
  `CS_CHROMIUM=<путь>`).
- `CS_TODAY` — дата для тестов сроков; `CS_SKIP_RENDER=1` — без тестов
  рендера (`--fast`).
- Учётные данные — переменные `CS_<DEV|STAGING|PROD>_…` у автора
  (`docs/operations/CREDENTIALS.md`).
- Хук начала сессии `.claude/hooks/session-start.sh` — зависимости,
  указатель на HANDOFF, ветки с невлитой работой.

## 10. Как расширять

- **Площадка:** класс в `tools/cs/adapters/` (наследник `PlatformAdapter`),
  строка в `REGISTRY`, запись в `capabilities.yaml` (+ `--write`
  матрицы), адресаты в `destinations.yaml`, контрактный тест. Модель,
  кампании, сайт не меняются (§69).
- **Проверка:** функция `check() -> Report`, строка в `CHECKS`
  (`__main__.py`), тест.
- **Поле модели:** схема + миграция (`core/migrate.py`, Д31).
- **Поставщик генерации:** класс с `name` и `generate()` (`core/generation.py`).
- **Формат площадки:** `export_specs.yaml` с источником (Д13).

## 11. Ограничения

- Контраст в `visual` — по 95-му перцентилю яркости фона; тонкие детали
  может пропустить — смотреть глазами.
- Проверка чисел различает числа и даты по шаблонам; числа меньше 10 не
  проверяются.
- `secrets` знает известные формы ключей — не заменяет осторожности.
- Telegram не позволяет сверить исход по ключу — после обрыва решает
  человек (`--reconcile`).
- Предпросмотр площадок — точный текст и разметка, вид карточки —
  приближение; сайт — настоящая сборка.
- Защита «не из сессии ИИ» — по переменным окружения Claude Code; это
  защита от случайности, граница безопасности — отсутствие токенов.
