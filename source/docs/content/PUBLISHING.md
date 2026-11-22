# Публикация

Как одобренный вариант попадает на сайт и площадки (Д12, Д24, Д25,
Д33; постановка §13–19, §47, §51–57, §67, §104–108). Код —
`tools/cs/core/engine.py`, адаптеры — `tools/cs/adapters/`, журнал —
`tools/cs/core/ledger.py`. Кто что решает — `GOVERNANCE.md`; учётные
данные — `docs/operations/CREDENTIALS.md`.

## 1. Производственный конвейер

```
IDEA → RESEARCH → CANONICAL DRAFT → FACT CHECK → EDITORIAL REVIEW → MEDIA GENERATION
     → PLATFORM ADAPTATION → PLATFORM VALIDATION → APPROVAL → SCHEDULE → PUBLISH → VERIFY → MEASURE
```

| Шаг постановки | Здесь |
|---|---|
| IDEA, RESEARCH | объект `IDEA` → `RESEARCHED` (`CONTENT_PIPELINE.md`, 00–02) |
| CANONICAL DRAFT | `canonical/vN.md`, бриф (03), черновик (04) |
| FACT CHECK | подстановки фактов, гейт Factual, `canonical seal` (валидатор) |
| EDITORIAL REVIEW | критика отдельным проходом (06), ревизия (07) |
| MEDIA GENERATION | рендер и экспорт изображений (05, 10) |
| PLATFORM ADAPTATION | `adapt` → правка варианта под площадку |
| PLATFORM VALIDATION | `variant seal`: ContentValidator + лимиты адаптера |
| APPROVAL | `approve` — автор, sha256 содержимого (Д12) |
| SCHEDULE | `publish … --at` или расписание кампании → `SCHEDULED` |
| PUBLISH, VERIFY | движок: `PUBLISHING` → площадка → проверка → `PUBLISHED`/`FAILED`/`UNKNOWN` |
| MEASURE | импорт метрик → события аналитики (Д29) |

## 2. Состояния: контент и публикация — разные (§14)

| Контент (объект, вариант) | Публикация (журнал, по адресату) |
|---|---|
| объект: `IDEA` … `UNDER_REVIEW` ⇄ `REVISED` → `APPROVED` → `EXPORTED` → `PUBLISHED` → `ARCHIVED` | `SCHEDULED` → `PUBLISHING` → `PUBLISHED` / `FAILED` / `UNKNOWN` |
| вариант: `draft` → `ready`; одобрение `none` / `valid` / `invalid` | `FAILED` → `RETRY` → `PUBLISHING`; `UNKNOWN` → сверка |
| | `PUBLISHED` → `SUPERSEDED` (новая версия) → `ARCHIVED`; `DELETED`; `CANCELLED` |

Соответствие постановке: DRAFT = `IDEA`/`draft`, RESEARCHED = `RESEARCHED`,
READY_FOR_REVIEW = `UNDER_REVIEW`/`ready`, APPROVED = одобрение `valid`,
остальное — события журнала. «Одобрено» никогда не означает
«опубликовано».

## 3. Транзакция одной публикации (§15)

```
plan       объект, вариант, адресат (по id), адаптер, текст площадки, ключ
validate   ContentValidator + лимиты площадки + предпроверка (§51):
           аккаунт и адресат — сверка адаптером с явными id; язык; ссылки;
           медиа и хэши; время; версия = одобренная; не устарел; политика
record     PUBLISHING (до вызова площадки)
publish    адаптер → площадка
verify     адаптер: запись существует (где площадка позволяет)
record     PUBLISHED (remote_id, remote_url, verified) | FAILED (код) | UNKNOWN
```

Если площадка не подтвердила — это `FAILED` или `UNKNOWN`, а не успех.

## 4. Идемпотентность (§16)

Ключ = sha256(объект | вариант | sha256 содержимого варианта | адресат |
окружение); `publication_id = PUB-<12 знаков ключа>`. Каждая запись
журнала несёт `publication_id`, объект, площадку, вариант,
`variant_version`, `variant_sha256`, версию канона, ключ.

- Есть `PUBLISHED` по ключу → `already_published`, площадку не трогаем.
- Есть `PUBLISHING`/`UNKNOWN` без исхода → **не повторяем вслепую**:
  адаптер ищет запись на площадке (имитация с поиском, VK `guid`); не
  умеет (Telegram, Discord-вебхук) → `UNKNOWN`, решает человек:
  `publish --reconcile PUB-… --exists yes --url …` или `--exists no`.
- Новая версия варианта уже опубликованного поста → по политике
  `on_update`: `edit` (правка поста, старая публикация `SUPERSEDED`),
  `new` или `manual`.

## 5. Повторы и ошибки (§17–18, §57)

| Код | Повтор | Что делать |
|---|---|---|
| `RATE_LIMITED` | да, не раньше `retry_after` | — |
| `PLATFORM_UNAVAILABLE` | да | запрос не дошёл; канон цел, публикация ждёт (§67) |
| `OUTCOME_UNKNOWN` | **нет** | сверка (§4) |
| `AUTH_EXPIRED`, `MISSING_CREDENTIALS` | нет | обновить учётные данные (`CREDENTIALS.md`) |
| `PERMISSION_DENIED`, `INVALID_DESTINATION` | нет | права бота, id адресата |
| `INVALID_CONTENT`, `MEDIA_REJECTED` | нет | правка варианта → новая версия → одобрение |
| `MANUAL_REQUIRED`, `UNSUPPORTED` | нет | ручной путь (§7) |
| `UNKNOWN_PLATFORM_ERROR` | нет | разбор; в журнале — код и сообщение без сырого ответа |

Повторы: до `max_attempts` за запуск и `max_total_attempts` на ключ за
всё время (`data/policy/publication.yaml`), задержка экспоненциальная с
дрожанием; каждая попытка — `PUBLISHING`, каждая неудача — `FAILED`,
ожидание — `RETRY`. Упавшая повторяемая публикация ждёт `publish --due`.
Частота — ограничитель **в адаптере** (Telegram — ~1/с в чат).

## 6. Режимы и окружения (§53–55, §105, Д25)

| Режим | Окружение | Что делает | Кто запускает |
|---|---|---|---|
| `dry-run` (по умолчанию) | — | всё готовит и проверяет, печатает адресат, текст, медиа, ключ; ничего не пишет и не отправляет | кто угодно |
| `--dev` | development | имитации площадок (`adapters/mock.py`), журнал в каталоге сборки | сессия ИИ, тесты |
| `--safe` | staging | только staging-близнец адресата (`staging_twin`): тестовый канал, staging сайта | автор |
| `--production` | production | рабочий адресат, нужно одобрение, канон закоммичен | **только автор**; сайт — ещё локальная сессия Claude Code после «да» автора (Д36) |

Учётные данные staging и production разные (`CS_STAGING_…`/`CS_PROD_…`,
проверка `destinations`). Разработка идёт в staging (§105).

## 7. Ручной путь (Д33)

Площадки без API или без допуска (VK до права `wall`, YouTube-загрузка,
TikTok, личный профиль Telegram, Discord до ОР-6): `preview` даёт текст в
разметке площадки и медиа; автор публикует сам и записывает:

```sh
python3 -m tools.cs publish CI-0001 vk.ru --to vk-author --record-manual --url https://vk.com/wall-…_…
```

Ручная запись требует действующего одобрения так же, как автоматическая.

## 8. Команды — вертикальный срез (§72)

```sh
python3 -m tools.cs canonical seal CI-0101                    # канон проверен и зафиксирован
python3 -m tools.cs adapt CI-0101 --platform telegram --lang ru   # заготовка варианта
python3 -m tools.cs variant seal CI-0101 telegram.ru          # валидатор, зависимости, ready
python3 -m tools.cs preview CI-0101 --serve                   # http://localhost:8001/_preview/
python3 -m tools.cs approve CI-0101 telegram.ru               # автор, в своём терминале
python3 -m tools.cs publish CI-0101 website.ru --to site-production --production   # сборка → rsync на Beget → проверка по HTTP (Д35)
python3 -m tools.cs site deploy --dry-run                     # тема и код сайта: что изменится на хостинге
python3 -m tools.cs publish CI-0101 telegram.ru --to tg-devlog            # пробный прогон
python3 -m tools.cs publish CI-0101 telegram.ru --to tg-devlog --safe     # тестовый канал
python3 -m tools.cs publish CI-0101 telegram.ru --to tg-devlog --production
python3 -m tools.cs campaign status CMP-0001                  # сводка по площадкам (§28)
python3 -m tools.cs publish --due --production                # запланированные и повторы
```

Сквозной путь на имитациях проверяет `tests/test_platform_e2e.py`
(§103), сценарии §56 — `tests/test_publishing.py`.

## 9. Политика при отказах (§67, §108)

- Площадка недоступна → публикация `FAILED (retryable)`/`SCHEDULED`;
  канон и варианты не трогаются.
- Провайдер ИИ недоступен → объект остаётся черновиком; публикации это
  не касается (ядро офлайн-первым).
- Сайт недоступен → публикация в соцсети допускается, только если канон
  сохранён в Git (`outage.require_canonical_in_git: true`); после запуска
  рабочего сайта — ещё и «сначала сайт»
  (`require_website_published_before_social`, сейчас `false` — штатной
  выгрузки ещё не было, HTTPS у домена нет; домен зарегистрирован,
  ОР-11 закрыт).

## 10. Наблюдаемость (§106–107)

Каждая попытка пишет строку JSON в каталог сборки (build/logs, не в
Git): id публикации и кампании, площадка, попытка, задержка, код ошибки,
метаданные ответа — после вычистки секретов (`core/obs.py`). Проверка
здоровья — `python3 -m tools.cs health` (`--remote` — сверка аккаунтов
staging-адресатов).
