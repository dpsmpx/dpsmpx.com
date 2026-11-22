# Карта мест в источниках

Файлы и теги репозиториев-источников, на которые ссылаются факты и
правила, — с коммитом, на котором место проверено. Здесь только адреса
и назначение, без пересказа содержимого (D-05). Что место есть на
коммите, сверяет `tools/verify/check_refs.py` по клонам; форму —
`tools/verify/check_registry.py`.

Место — путь от корня репозитория или `tag:ИМЯ`; коммит — полный SHA.

| Источник | Место | Коммит | Что там |
|---|---|---|---|
| S-01 | docs/direction/DECISIONS.md | f2ba263fa06265432066aa161129a6b532479bed | журнал архитектурных решений Galdhold (Р0–Р20) и их история |
| S-01 | CLAUDE.md | f2ba263fa06265432066aa161129a6b532479bed | правила агента Galdhold; раздел «README.md» — README не источник истины |
| S-01 | TODO.md | f2ba263fa06265432066aa161129a6b532479bed | список незавершённого Galdhold |
| S-01 | docs/PROCESS.md | f2ba263fa06265432066aa161129a6b532479bed | пояснения к правилам процесса и их происхождение |
| S-01 | docs/PROVENANCE.md | f2ba263fa06265432066aa161129a6b532479bed | происхождение кода и цепочка прав |
| S-01 | ROADMAP/ROADMAP.md | f2ba263fa06265432066aa161129a6b532479bed | план работ Galdhold |
| S-01 | ROADMAP/AAA-ROADMAP.md | f2ba263fa06265432066aa161129a6b532479bed | коммерческая дорожка, задачи К1–К17 |
| S-01 | tools/hostcheck/run.sh | f2ba263fa06265432066aa161129a6b532479bed | вход проверок hostcheck |
| S-01 | tools/hostcheck/check_engine_boundary.py | f2ba263fa06265432066aa161129a6b532479bed | проверка границы движка |
| S-01 | tag:v22.09.26 | 8dc7a988986422530ddc45d64ad7cf7a822122f9 | тег первого релиза GitHub (не предварительного) |
| S-01 | tag:3009261627 | d733cb3797cd5ff4ccb063ae860dd0a740dc9c02 | тег последнего релиза GitHub на 2026-10-04 |
| S-02 | docs/direction/DECISIONS.md | b2cd763575df7dcd6d390ecdf800413bb4e7264a | журнал решений DPlang |
| S-02 | CLAUDE.md | b2cd763575df7dcd6d390ecdf800413bb4e7264a | правила агента DPlang |
| S-02 | tools/check/run.sh | b2cd763575df7dcd6d390ecdf800413bb4e7264a | вход проверок DPlang |
| S-03 | README.md | 3b68ffd61d518b34c7e1650c7d4e143d407ea2e0 | описание DPpass и раздел «Прогресс» |
| S-03 | docs/direction/DECISIONS.md | 3b68ffd61d518b34c7e1650c7d4e143d407ea2e0 | журнал решений DPpass |
| S-03 | docs/direction/ROADMAP/README.md | 3b68ffd61d518b34c7e1650c7d4e143d407ea2e0 | план этапов DPpass |
| S-03 | tools/hostcheck/run.sh | 3b68ffd61d518b34c7e1650c7d4e143d407ea2e0 | вход проверок DPpass |
| S-03 | tools/hostcheck/readme_progress.py | 3b68ffd61d518b34c7e1650c7d4e143d407ea2e0 | построение раздела «Прогресс» README |
| S-04 | README.md | 0b7aad9d6fae8d20ce249dff1fc5112cf80cb15c | README профиля автора |
| S-00 | docs/direction/DECISIONS.md | 396ad75229e65222938fe4cfc2b5ed5162f24ace | журнал решений DPprofile (D-01…D-11) в первой редакции |
