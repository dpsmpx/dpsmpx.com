# Выходы: презентационное изображение (CI-0001)

Что получено и для чего. Хэши, входы, спецификация и её хэш, промпт и
дата каждого файла — `content/items/CI-0001-personal-presentation/provenance.yaml`;
раскладка для проверок — `*.layout.json` рядом с файлом. Каталог —
`content/items/CI-0001-personal-presentation/`.

## Экспорт варианта A — превью для утверждения

Статус `preview`: публиковать нельзя до `APPROVED` (утверждение автора,
ОР-1, права фотографа). После утверждения — `python3 -m tools.cs export
CI-0001 --variant A --format … --final`.

| Файл | Формат | Размер | Язык | Куда |
|---|---|---|---|---|
| `exports/A-ru-master.png`, `exports/A-en-master.png` | `master` | 2560×1440 PNG | RU, EN | мастер-файлы (внутренние) |
| `exports/A-ru-youtube_banner.jpg` | `youtube_banner` | 2560×1440 JPEG, смысл в зоне 1544×423 | RU | шапка канала YouTube |
| `exports/A-ru-telegram_post.jpg` | `telegram_post` | 1280×720 JPEG | RU | закреплённая запись-вход канала-дневника + `variants/telegram.ru.md` |
| `exports/A-ru-vk_post.jpg` | `vk_post` | 1280×720 JPEG (размеры VK не подтверждены) | RU | запись VK + `variants/vk.ru.md` |
| `exports/A-en-github_social.png` | `github_social` | 1280×640 PNG < 1 МБ | EN | баннер README профиля + `variants/github.en.md` |

## Рендеры для критики — все варианты

`renders/<вариант>-<язык>-<формат>`: лента 16:9 (`telegram_post`, RU и
EN), шапка YouTube (RU), 2:1 GitHub (EN) — для A, B, C, D. Рендеры до
ревизии, по которым писалась первая критика, — в истории Git (коммит
`58b31fb`).

| Вариант | Статус | Почему |
|---|---|---|
| A professional | `selected` — выбран сессией для проверки; утверждает автор | `DECISION.md` |
| B technical | `rejected` | fatal B-1: «Android → Windows (Steam)» читается как неверный факт; шапка вне зоны |
| C cinematic | `rejected` | fatal C-1: интерьер заложен в концепцию (Д18) |
| D minimal | `fallback` | без лица — запасной для мест, где лицо не нужно |

## Тексты публикаций

до 04.10.2026 — `copy/`; после миграции v2 — варианты
`variants/telegram.ru.md`, `variants/vk.ru.md`, `variants/github.en.md` (EN,
подпись и строка под баннером), сайт — `variants/website.ru.md`,
`variants/website.en.md`; шапка YouTube — без текста. Канон —
`canonical/v1.md`; кампания — `data/campaigns/CMP-0001.yaml`.
Проверены `tools/check.sh` (`claims`): факты, запреты, числа.

## Версия 2 (05.10.2026): вариант E, утверждён автором

| Файл | Формат | Размер | Язык | Назначение |
|---|---|---|---|---|
| `exports/E-ru-master.png`, `exports/E-en-master.png` | `master` | 2560×1440 PNG | RU, EN | мастер-файлы |
| `exports/E-ru-youtube_banner.jpg` | `youtube_banner` | 2560×1440 JPEG, смысл в зоне 1544×423 | RU | шапка канала YouTube |
| `exports/E-ru-telegram_post.jpg` | `telegram_post` | 1280×720 JPEG | RU | закреплённая запись канала-дневника; «Обо мне» на сайте (RU) |
| `exports/E-ru-vk_post.jpg` | `vk_post` | 1280×720 JPEG (размеры VK не подтверждены) | RU | запись VK |
| `exports/E-en-github_social.png` | `github_social` | 1280×640 PNG | EN | баннер README профиля; «About» (EN) и изображение превью ссылок сайта (`og_default`) |

Тексты площадок — `variants/*.md` из канона v2; одобряет автор
(`python3 -m tools.cs approve CI-0001 <вариант>`). Экспорт A (v1, с портретом)
— история: на сайте и в вариантах больше не используется.
