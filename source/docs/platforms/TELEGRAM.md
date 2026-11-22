# Telegram

Площадки: личный профиль `@dpsmpx` (контакт) и канал «Galdhold (dev log)»
`@gh_3D_Voxel_OpenWorld_RPG` (дневник). Состояние на 04.10.2026 —
`docs/audits/2026-10-04-SOCIAL_AUDIT.md`, §3–4.

## Модель

| Поле | Канал-дневник |
|---|---|
| Audience | разработчики (в т. ч. с ИИ), техническая аудитория, ранние игроки; RU |
| Purpose | основной подробный дневник: что сделано, почему, что дальше |
| Primary content | PROCESS, RESULT, RELEASE, ENGINEERING, AI DEVELOPMENT (`CONTENT_STRATEGY.md`, §3) |
| Secondary content | MILESTONE, RESEARCH, EDUCATION, OPINION (помечено как мнение) |
| Length | запись — до ~1 500 знаков; длиннее — Telegraph со своей строкой-выводом в канале; подпись к медиа — до 1 024 знаков (лимит API) |
| Visual format | снимок или клип из настоящей сборки; изображения 16:9, сторона ≤ 1 280 px (сжатие Telegram), HD — до 2 560 px |
| CTA | один на запись: «смотрите видео», «что думаете о …?», ссылка на точку входа |
| Posting rhythm | 1–3 записи в неделю, которые выдерживаются (`CONTENT_STRATEGY.md`, §7) |
| Discoverability | слабая внутри Telegram: каналы растут ссылками извне (YouTube, GitHub, VK) и пересылками |
| Retention mechanism | закреплённая запись-вход; регулярность; серии («Сборка от …») |
| Cross-platform role | источник подробной правды; остальные площадки — короче и ссылаются сюда |

## Правила записи

- Первая строка — суть: что изменилось для игрока или что выяснено.
- Снимок — с подписью «что видно и почему это решение»; пустые снимки —
  нет.
- Ссылка на Telegraph — с одной своей фразой, зачем открывать.
- Не публикуются: оценки ИИ как доказательство (Д7), личное (ОР-8),
  код (Д17), числа не из реестра.
- Шаблоны: `templates/telegram_devlog.md`, `templates/telegram_milestone.md`.

## Публикация через бота

Канал-дневник — площадка с полной автоматизацией через Bot API (Д12,
`docs/platforms/PUBLISHING_CAPABILITY_MATRIX.md`): адаптер
`tools/cs/adapters/telegram.py`, адресат `tg-devlog` (тестовый — `tg-test`).
Публикуется только одобренная автором версия варианта `telegram.ru`;
отложенной публикации в Bot API нет — откладывает планировщик системы;
удалить бот может только посты младше 48 часов; статистика — вручную
(Д15). Подключение — `docs/operations/CREDENTIALS.md`, «Telegram».

## Профиль `@dpsmpx`

Био: ссылки на GitHub и YouTube. Исправить YouTube-ссылку на `@dpsmpx`
(IC-01, ОР-3). Аватар — по решению о знаке (`docs/brand/VISUAL_SYSTEM.md`, §9).

## Официальные источники

- Лимиты текста и подписей — Telegram Bot API (`sendMessage` text 1–4096,
  caption 0–1024): core.telegram.org/bots/api.
- Размеры фото — серверные версии ≤ 800, ≤ 1 280, ≤ 2 560 px:
  core.telegram.org/constructor/photoSize; HD-фото — telegram.org/blog.
- Подробнее — `docs/research/platforms/PLATFORM_GUIDANCE.md`.
