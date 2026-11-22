# Журнал публикаций

Только дописывание, по строке JSON на событие (Д24; `docs/content/PUBLISHING.md`):

- `production.jsonl` — рабочие публикации;
- `staging.jsonl` — безопасный режим (тестовые адресаты);
- окружение development пишет в build/publications (каталог сборки, не в Git).

Файлы не правятся руками: исправление — новым событием
(`publish --reconcile`, `publish --record-manual`). Проверка —
`tools/check.sh publications`.
