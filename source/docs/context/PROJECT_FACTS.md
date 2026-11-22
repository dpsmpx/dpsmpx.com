# Факты по проектам

Человекочитаемая сводка по проектам. Сами утверждения, доказательства и
даты — в `data/facts/facts.yaml` (здесь — только id); при расхождении
прав реестр. Проверка ссылок на id — `tools/check.sh` (`facts`).

## Galdhold

| Поле | Значение |
|---|---|
| Name | Galdhold (прежде VoxelRPG; репозиторий `dpsmpx/Galdhold`, прежде `3D_Voxel_OpenWorld_RPG`) — GH-NAME |
| Status | этапы 1–4 закрыты, идёт этап 5 «Коммерческая версия 1 и выпуск» — GH-STAGES |
| Purpose | воксельная action-RPG с открытым процедурным миром — GH-GENRE |
| Technology | C++20, Vulkan 1.1, EnTT, toml++, Android NDK, SDL3 — GH-TECH |
| Platforms | проверялась на Android (2 модели) — GH-ANDROID; Windows готовится — GH-WINDOWS; выпуск — Android + Windows (Steam) — GH-RELEASE-PLAN |
| Verified facts | GH-LOC, GH-CHECKS, GH-ENGINE, GH-ASSETS, GH-PERF-2026-09-30, GH-REPO-START, GH-COMMITS, GH-ROSPATENT, GH-BUSINESS, GH-PRIVATE, GH-AI-TEXTS |
| Current milestone | версия 1: Windows как продукт, страница Steam, трейлер, полировка интерфейса (Galdhold `ROADMAP/Версия 1.md`) |
| Links | дневник `t.me/gh_3D_Voxel_OpenWorld_RPG`, видео `youtu.be/mMDi7HjTBkM` (`data/identity/links.yaml`) |
| Public assets | снимки и видео в дневнике; обложка, аватар и шапка YouTube (рендер игры); своих снимков в этом репозитории пока нет |
| Allowed claims | `allowed_wording` у фактов выше |
| Forbidden claims | «работает на Windows», «на любом Android», «открытый код», «патент», «ни одного чужого ассета», «с нуля за N дней» без оговорки, старые числа (115 000 строк, 100 FPS), «CI», ускорение в N раз — `forbidden.yaml` |

## Движок Galdhold

| Поле | Значение |
|---|---|
| Name | без публичного имени («Engine» в README профиля) |
| Status | этапы 1–2 (движок, полигон) закрыты — GH-STAGES |
| Purpose | нативный движок, не зависящий от игры — GH-ENGINE |
| Technology | как у Galdhold; рендер Vulkan 1.1, планировщик задач, ECS, чанки, звук, платформенный слой |
| Allowed claims | «собственный движок, отделённый от игры; граница проверяется автоматически» |
| Forbidden claims | «универсальный движок», «готов для других игр», «лицензирую движок» |

## DPlang

| Поле | Значение |
|---|---|
| Name | DPlang (прежде «C-») |
| Status | v0.0 пройдена 04.10.2026; v0.1 (компилятор ядра) — в работе — DP-STAGE |
| Purpose | язык для игр, движков и инструментов: надёжность, детерминизм, работа с ИИ — DP-WHAT |
| Technology | компилятор на C++20; первая цель — генерация переносимого C (C-бэкенд) |
| Platforms | план — Android и Windows; сейчас — Linux (v0.1) |
| Verified facts | DP-WHAT, DP-STAGE, DP-EXPERIMENT, DP-INDEPENDENT, DP-PRIVATE |
| Current milestone | v0.1 «ядро-срез» |
| Links | нет открытых (репозиторий закрыт) |
| Public assets | нет |
| Allowed claims | «разрабатываю собственный язык; синтаксис выбран замером» |
| Forbidden claims | «язык готов», «компилятор работает», «ИИ пишет на DPlang лучше, чем на C++», «Galdhold написан на DPlang» |

## Andors-Love

| Поле | Значение |
|---|---|
| Status | открытый репозиторий, последний пуш 09.09.2026 |
| Purpose | пошаговая RPG на C++11, терминал + SDL2 — AL-WHAT |
| Allowed claims | «пошаговая RPG на C++ с двумя интерфейсами над одной логикой» |
| Forbidden claims | материалы и логотип Andor's Trail; «клон» |

## True Joint Tile Maker

| Поле | Значение |
|---|---|
| Status | открытый, GPL-3.0 (TJTM-OPEN); версия 1.6 на 25.10.2026 — перенос на C++ и SDL3 (TJTM-NOW) |
| Purpose | редактор пиксель-графики и карт для Andors-Love — TJTM-WHAT (на 04.10 — PascalABC.NET) |

## DP AIM Trainer

| Поле | Значение |
|---|---|
| Status | закрытый (AIM-PRIVATE); стадия — AIM-STAGE |
| Purpose | замер реакции и разминка перед шутерами — AIM-WHAT |
| Allowed claims | только формулировки фактов; без ссылок на код |

## DP_Clock

| Поле | Значение |
|---|---|
| Status | закрытый (CLK-PRIVATE); стадия — CLK-STAGE |
| Purpose | своё приложение часов для Android — CLK-WHAT |
| Allowed claims | только формулировки фактов; без ссылок на код; «код чужих приложений не копируется» — не как сравнение с ними |

## PixRogue · DP_Ecosystem · утилиты

PIX-WHAT, ECO-WHAT. Только как широта и история пути (Background).
