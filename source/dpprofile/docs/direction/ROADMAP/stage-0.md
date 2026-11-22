# Этап 0 — Каркас, правила и проверки

Состояние: выполнен (2026-10-04)

## Цель

Роли документов, правила работы и проверки, которые ловят нарушения, —
раньше любого содержимого.

## Критерии выхода

- [x] Решения и границы предмета записаны <!-- gate: file:docs/direction/DECISIONS.md & file:docs/direction/SCOPE.md -->
- [x] Правила агента и точка входа есть <!-- gate: file:CLAUDE.md & file:README.md & file:TODO.md -->
- [x] Каталоги ролей созданы со схемами <!-- gate: file:docs/sources/REGISTRY.md & file:docs/sources/CITATION.md & file:docs/facts/README.md & file:docs/insights/README.md & file:docs/timeline/TIMELINE.md & file:docs/method/METHOD.md -->
- [x] Документы книги без прозы <!-- gate: file:docs/book/STATUS.md & file:docs/book/OUTLINE.md & file:docs/book/NON_GOALS.md -->
- [x] Проверки схемы фактов, ссылок выводов, ссылок, запрещённых формулировок, этапов и шлюза книги <!-- gate: check:check_facts & check:check_insights & check:check_links & check:check_forbidden & check:check_stages & check:check_book_gate -->
- [x] Самопроверка: каждая проверка падает на испорченной копии <!-- gate: check:selftest -->
