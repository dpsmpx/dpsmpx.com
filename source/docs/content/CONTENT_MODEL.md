# Модель контента

Формальная модель объекта контента (Д1). **Версия 2** (канон, варианты
площадок, бренды, цели публикации, зависимости) — `CANONICAL_MODEL.md`;
здесь — основа, общая для v1 и v2. Машиночитаемая схема —
`schemas/content_item.schema.json`; проверка — `tools/cs/validate.py`
(в составе `tools/check.sh`). Конвейер — `CONTENT_PIPELINE.md`; гейты и
оценки — `QUALITY_MODEL.md`.

## 1. ContentItem

Каталог объекта: `content/items/<id>-<slug>/`.

```
content/items/CI-0001-personal-presentation/
├── item.yaml          объект: цель, аудитория, утверждения, состояние, гейты, история
├── spec/              спецификации композиции и текстов вариантов (вход генерации)
├── renders/           результаты генерации по вариантам (в т. ч. отклонённые)
├── exports/           экспорт выбранного варианта под форматы площадок
├── canonical/         v2: каноническая версия (CANONICAL_MODEL.md)
├── variants/          v2: варианты площадок (в v1 — copy/)
└── provenance.yaml    происхождение входов и выходов (хэши, метод, инструмент)
```

Документы продукта (бриф, направление, критика, решение) — рядом с
документацией: `docs/content/products/<product>/`. `item.yaml` ссылается
на них.

```
ContentItem
├── id                 CI-NNNN, не переиспользуется
├── slug, title
├── type               image | presentation_card | post | devlog | thumbnail | video_meta |
│                      short_video | presentation | release_announcement | article | campaign
├── pillar             PERSON | PROJECT | ENGINEERING | AI_DEVELOPMENT | RESULT | PROCESS |
│                      RESEARCH | EDUCATION | MILESTONE | RELEASE | OPINION | COMMUNITY
├── topic
├── objective          одна фраза: что должен понять/сделать зритель
├── audiences          из CONTENT_STRATEGY §2
├── platforms          github | telegram | youtube | vk | discord | tiktok
├── languages          ru | en
├── tone
├── claims[]           ссылки на факты реестра: {fact: <id>}
├── source_projects[]  galdhold | dplang | …
├── brief              путь к брифу
├── visual_direction   путь к творческому направлению
├── prompt             {id, version} из prompts/
├── inputs[]           id входных ассетов из provenance (например, A-001)
├── variants[]         {id, label, spec, renders[], status, rejection_reason}
├── selected_variant
├── review             {file, scores{variant: {ось: 0–5}}, issues{fatal, major, minor}}
├── gates              {factual, brand, visual, platform, safety, legal, provenance}
├── approval           {by: author, date, note} — только автор
├── exports[]          {format, file, lang, sha256}
├── publication[]      {platform, state, url, published_at}
├── experiments[]      id экспериментов (data/experiments/)
├── metrics[]          файлы метрик (data/metrics/)
├── provenance         путь к provenance.yaml
├── state              состояние (§2)
└── history[]          {date, state, note} — путь по состояниям
```

## 2. Состояния

```
IDEA → RESEARCHED → BRIEFED → GENERATED → UNDER_REVIEW ⇄ REVISED
                                              │
                                              ▼
                                          APPROVED → EXPORTED → PUBLISHED → ARCHIVED
любое (кроме PUBLISHED, ARCHIVED) → REJECTED
```

| Состояние | Что должно быть (проверяется) |
|---|---|
| IDEA | id, type, pillar, objective |
| RESEARCHED | + audiences, platforms; claims существуют в реестре (или `claims: []` с `claims_none_reason`) |
| BRIEFED | + файл брифа существует |
| GENERATED | + хотя бы один вариант со спецификацией и существующими рендерами |
| UNDER_REVIEW | + файл критики; оценки по шести осям у каждого варианта |
| REVISED | + запись истории с тем, что изменено |
| APPROVED | + выбран вариант; все гейты `pass` или `n/a`; нет открытых fatal и major; `approval.by: author` |
| EXPORTED | + экспорт выбранного варианта; файлы есть, хэши совпадают, размеры — по `export_specs.yaml` |
| PUBLISHED | + `publication` с адресом и датой хотя бы для одной площадки |
| ARCHIVED | конечное; объект не меняется |
| REJECTED | конечное; причина — в истории |

**Нельзя публиковать объект не в `EXPORTED`/`PUBLISHED`** — а туда нельзя
попасть, минуя `APPROVED`. История должна быть допустимым путём по
стрелкам; перескок (`GENERATED → APPROVED`) — ошибка проверки.

## 3. Варианты и эксперименты

- **Вариант** (`variants[]`) — альтернатива для выбора внутри объекта
  (A — professional, B — technical, C — cinematic, D — minimal или
  другие, если цель требует). Выбор — по цели (`QUALITY_MODEL.md`, §5).
- **Эксперимент** — отдельная сущность (`EXPERIMENTS_AND_ANALYTICS.md`):
  гипотеза, варианты, аудитория, площадка, метрика, результат, решение.
  Вариант становится частью эксперимента только по записи эксперимента.

## 4. Связи

```
facts.yaml ──(claims)──▶ ContentItem ◀──(inputs)── provenance (assets)
                            │
             variants ──▶ renders ──(selected)──▶ exports ──▶ publication ──▶ metrics
                                                                  ▲
                                                     experiments ─┘
```

## 5. Как завести объект

```sh
python3 -m tools.cs new --type post --pillar RESULT --slug first-clip \
    --objective "Показать новый бой одним клипом"
```

Создаёт каталог, `item.yaml` в состоянии `IDEA` и пустой
`provenance.yaml`. Дальше — по `CONTENT_PIPELINE.md`.
