# Комплект визуализации экосистемы (Д43)

Файлы этого каталога собраны в репозитории DPvisualisation командой
`python3 -m tools.dpvis build --site <каталог>` (DPvisualisation D-15) и
скопированы сюда без правок. Сборка сайта сверяет их sha256 с
`MANIFEST.json`: несовпадение — ошибка сборки, руками файлы не править.

| Файл | Что |
|---|---|
| `dpvis.js` | просмотрщик — склейка модулей `viewer/src/*.js`, без зависимостей |
| `dpvis.css` | стили просмотрщика (всё внутри `.dpvis`) |
| `dpvis-data.json` | публичная выжимка `dpvis-public/1`: модель и срез без закрытых подробностей |
| `MANIFEST.json` | sha256 файлов и даты модели и среза |

Происхождение: DPvisualisation 1.0.0, коммит `3d17055` (ветка
`claude/tender-hypatia-mbrwf9`); 8.11.2026 — `dpvis.js` пересобран в
DPmetaApp из `dpvisualisation/` (DPmetaApp PR #181): тема хозяина `auto`
— настройка системы (SocialMediaImage:Д49); стили и данные — те же.
Срез — 25.10.2026 (10:18 UTC), по полным клонам
репозиториев текущей системы: архива — ранних проектов до репозитория
игры и убранных автором — в схеме нет (DPvisualisation D-20). Схема без
анимаций, связи — прямые, по ширине экрана без прокрутки вбок
(DPvisualisation D-16); управление (DPmetaApp) — отдельным слоем, DPmeta —
слой синхронизации (DPvisualisation D-21); DP_AI_Orcestrator — подсистема
DPmetaApp, отдельного узла нет (DPvisualisation D-22); периферийные
проекты с работой — в схеме (DPvisualisation D-23); история влитого
репозитория до слияния — у его узла, а не в счёте DPmetaApp
(DPvisualisation D-24).

Схема на сайте полустатичная: комплект обновляется при каждой выгрузке
сайта (уточнение Д43, 9 октября 2026); живой режим — в DPmetaApp.

Обновить (сессия или автор):
1. В клоне DPvisualisation: `python3 -m tools.dpvis collect --root <клоны>`.
2. Там же: `python3 -m tools.dpvis build --site dist/site`.
3. Здесь: `python3 -m tools.cs site ecosystem-import <клон DPvisualisation>/dist/site` —
   команда проверяет хэши, копирует четыре файла и проверяет их ещё раз.
4. `tools/check.sh`, затем выгрузка по правилам Д35 и Д36 — и так перед
   каждой выгрузкой сайта.
