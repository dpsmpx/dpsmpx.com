# Промпты

Версионированные инструкции для сессии: как превращать бриф и факты в
спецификации и тексты. Имя — `<тема>/<имя>.v<N>.md`; правка смысла —
новая версия (новый файл), старая остаётся: объекты ссылаются на
версию (`prompt: {id, version}` в `item.yaml`), а записи происхождения —
на файл.

| Промпт | Для чего |
|---|---|
| `prompts/image/presentation-composition.v1.md` | спецификация композиции личной работы (CI-0001) |
| `prompts/critique/visual-critique.v1.md` | отдельный проход критики визуальной работы |
| `prompts/text/post.v1.md` | текст публикации под площадку (вариант `variants/`) |
| `prompts/youtube/description.v1.md` | название и описание видео |
| `prompts/thumbnail/thumbnail.v1.md` | обложка видео |

Общее для всех: факты — только из реестра; запреты — `forbidden.yaml`;
голос — `docs/context/AUTHOR_MASTER_CONTEXT.md`, «Голос».
