# Реестр источников

Всё, на что факт может сослаться (D-05). Источника нет в реестре — факт
на него не ссылается. Правила ссылок и дат — `docs/sources/CITATION.md`;
места внутри репозиториев — `docs/sources/MAP.md`; наблюдения без
постоянного адреса — `docs/sources/NOTES.md`. Форму проверяет
`tools/verify/check_registry.py`.

- **Вид:** `repo` — репозиторий автора на GitHub (ссылки — коммит, файл,
  релиз); `site` — публичный сайт (ссылки — адрес страницы с датой
  наблюдения); `self` — этот репозиторий.
- **Доступ:** `public` — проверит любой; `private` — только владелец и
  те, кому он дал доступ (на 2026-10-04).
- **Клон:** имя каталога в `build/sources/` для
  `tools/verify/fetch_sources.sh`.
- Номер источника не меняется и не переиспользуется; переименование
  репозитория — уточнение в «Что это», адрес — нынешний.

| Источник | Вид | Адрес | Доступ | Клон | Что это |
|---|---|---|---|---|---|
| S-00 | self | github.com/dpsmpx/DPprofile | private | — | этот репозиторий |
| S-01 | repo | github.com/dpsmpx/Galdhold | private | galdhold | репозиторий VoxelRPG и движка (D-03); до 2026-10-04 — `3D_Voxel_OpenWorld_RPG` (F-0030) |
| S-02 | repo | github.com/dpsmpx/DPlang | private | dplang | репозиторий языка DPlang; рабочее имя языка — «C-» (F-0038) |
| S-03 | repo | github.com/dpsmpx/DPpass | private | dppass | репозиторий DPpass |
| S-04 | repo | github.com/dpsmpx/dpsmpx | public | dpsmpx | репозиторий профиля автора (README на странице профиля GitHub) |
| S-05 | repo | github.com/dpsmpx/Andors-Love | public | andors-love | ранний публичный проект автора |
| S-06 | repo | github.com/dpsmpx/TrueJointTileMaker | public | truejointtilemaker | ранний публичный проект автора |
| S-07 | repo | github.com/dpsmpx/DP_Random_Cells | public | dp_random_cells | ранний публичный проект автора |
| S-08 | repo | github.com/dpsmpx/tanks_blitz_stat_chat | public | tanks_blitz_stat_chat | публичный проект автора |
| S-09 | repo | github.com/dpsmpx/AIM_Trainer_pas | public | aim_trainer_pas | публичный проект автора |
| S-10 | site | github.com/dpsmpx | public | — | аккаунт GitHub автора (данные аккаунта — заметка N-0001) |
| S-11 | site | store.steampowered.com | public | — | магазин Steam: поиск и страницы игр |
| S-12 | repo | github.com/dpsmpx/DP_Ecosystem | public | dp_ecosystem | публичный проект автора (D-13) |
| S-13 | repo | github.com/dpsmpx/DP_Repeated_Tasks | public | dp_repeated_tasks | публичный проект автора (D-13) |
| S-14 | repo | github.com/dpsmpx/PixRogue | public | pixrogue | публичный проект автора (D-13) |
| S-15 | repo | github.com/dpsmpx/DP_TextFile_Sorter | public | dp_textfile_sorter | публичный проект автора (D-13) |
| S-16 | repo | github.com/dpsmpx/dpcalls | public | dpcalls | публичный проект автора (D-13) |
| S-17 | repo | github.com/dpsmpx/DP_Autoclicker | public | dp_autoclicker | публичный проект автора (D-13) |
| S-18 | repo | github.com/dpsmpx/DP_Typing_Master | public | dp_typing_master | публичный проект автора (D-13) |
| S-19 | repo | github.com/dpsmpx/DP_Backup_Tool | public | dp_backup_tool | публичный проект автора (D-13) |
| S-20 | repo | github.com/dpsmpx/DP_Gen_Bots | public | dp_gen_bots | публичный проект автора (D-13) |
| S-21 | repo | github.com/dpsmpx/DP_Graph_Builder | public | dp_graph_builder | публичный проект автора (D-13) |
| S-22 | repo | github.com/dpsmpx/andors-trail-load | public | andors-trail-load | форк чужого репозитория (N-0004); в предмете — только коммиты автора (D-13) |
