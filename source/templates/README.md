# Шаблоны

Структурные шаблоны: какие поля и в каком порядке. Не тексты на все
случаи — текст пишется под цель объекта (`prompts/text/post.v1.md`).
Числа и утверждения в любом шаблоне — только из `data/facts/facts.yaml`
(id в комментарии `<!-- facts: … -->`), запреты — `forbidden.yaml`.

| Шаблон | Для чего |
|---|---|
| `content_brief.md` | бриф объекта (этап 03) |
| `critique.md` | критика вариантов (этап 06) |
| `telegram_devlog.md` | запись дневника: PROCESS, RESULT, ENGINEERING |
| `telegram_milestone.md` | веха или выпуск в канале |
| `vk_post.md` | короткая запись VK |
| `youtube_description.md` | описание видео |
| `youtube_announcement.md` | анонс видео в других каналах |
| `tiktok_clip.md` | вертикальный клип: описание и обложка |
| `discord_announcement.md` | объявление на сервере (после ОР-6) |

Текст публикации объекта — вариант площадки `content/items/<id>/variants/<площадка>.<язык>.md`
(производная канона, `docs/content/CANONICAL_MODEL.md`; в объектах v1 — `copy/`);
проверка `claims` читает его без служебных комментариев `<!-- … -->`.
