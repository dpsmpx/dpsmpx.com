# Релизы (RELEASE_DATA)

Структурированные данные о выпусках проектов (PLATFORM_VISION §21–22, Д28):
`data/releases/<проект>.yaml`, схема `schemas/releases.schema.json`.
Тексты ссылаются на них подстановкой `{{release:<проект>.latest.version}}`,
а не переписывают номер версии руками; смена релиза делает зависимые
варианты устаревшими (`python3 -m tools.cs stale`).

Источник — релизы и теги GitHub после проверки человеком (§37: «GitHub
data → normalized project facts → editorial content»). Сырые данные
GitHub в контент не идут. Сейчас релизов нет: Galdhold и DPlang не
выпущены (GH-RELEASE-PLAN, DP-STAGE).
