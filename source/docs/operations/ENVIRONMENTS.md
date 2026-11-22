# Окружения

Решение — Д25. Учётные данные не смешиваются (§55): имя переменной
несёт окружение (`CS_DEV_…`, `CS_STAGING_…`, `CS_PROD_…`), проверка
`destinations` запрещает один токен в двух окружениях.

| | development | staging | production |
|---|---|---|---|
| Площадки | имитации (`tools/cs/adapters/mock.py`) | тестовые адресаты: закрытый тестовый канал Telegram, staging сайта | рабочие адресаты |
| Сайт | — | сборка в build/site/staging, `python3 -m tools.cs site serve` → `http://localhost:8000`; `noindex`, `Disallow: /`, черновики с плашкой | сборка в build/site/production → rsync на Beget (Д35: `site deploy`, `publish --production`); только одобренное и опубликованное; выпуск разрешён (`live: true`, Д34) |
| Журнал | каталог сборки (не в Git) | `data/publications/staging.jsonl` | `data/publications/production.jsonl` |
| Режим запуска | `--dev` | `--safe` | `--production` |
| Одобрение | не нужно | не нужно (проверки — да) | **нужно** (Д12) |
| Кто | сессия ИИ, тесты | автор | автор |
| Учётные данные | не нужны | `CS_STAGING_…` | `CS_PROD_…` |

**По умолчанию — staging** (§105): новая площадка или адаптер сначала
проходит `--safe` на тестовом адресате; рабочий адресат подключается
только после этого. Массового тестового мусора в рабочих каналах не
создаётся (§104).

**Сессия ИИ** работает в `dry-run` и `--dev` (`session_modes` в
`data/policy/publication.yaml`). Облачная сессия не получает рабочих
токенов (`CREDENTIALS.md`).
