# Промпты: презентационное изображение (CI-0001)

Какие версионированные инструкции применены и к чему. Генеративной
модели нет: изображение собирается программно из спецификации (Д11).

| Этап | Промпт | Результат |
|---|---|---|
| 04_draft → 05_generation | `prompts/image/presentation-composition.v1.md` | спецификации `spec/variant-{a,b,c,d}.yaml` (`composition/v1`) → рендер `tools/cs/render.py` |
| 06_critique | `prompts/critique/visual-critique.v1.md` | `CRITIQUE.md` — отдельный проход агента только для чтения |
| тексты публикаций | `prompts/text/post.v1.md` + шаблоны `templates/telegram_devlog.md`, `templates/vk_post.md` | `copy/telegram.md`, `copy/vk.md`, `copy/github.md`, `copy/youtube.md` |

В `item.yaml` — `prompt: {id: image/presentation-composition, version: 1}`;
в каждой записи `provenance.yaml` — путь промпта, по которому собран
файл. Новая версия промпта — новый файл и перерендер с записью в
истории объекта.

## Вход генерации

- Бриф `BRIEF.md`, направление `CREATIVE_DIRECTION.md`.
- Факты — id в `claims` спецификаций и объекта (`data/facts/facts.yaml`).
- Портрет — A-001 (`REFERENCE_IMAGE`), шрифты — A-002, токены — A-003.
