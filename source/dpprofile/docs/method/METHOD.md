# Наблюдаемые элементы процесса

Описание, а не предписание (D-07). Строка — элемент процесса, который
виден в артефактах репозиториев автора, факты, где он виден, и вывод
`I-NNNN` из `docs/insights/`, который обобщает строку в пределах этих
фактов. Обобщения шире выводов («автор всегда …», «метод работает,
потому что …») здесь не делаются.

В столбце «Факты» — сначала факты, затем вывод. Таблицу проверяют
`tools/verify/check_links.py` (номера фактов и выводов),
`tools/verify/check_forbidden.py` (оценки и предписания) и
`tools/verify/check_stages.py` (у каждой строки есть вывод — критерий
этапа 3).

| Элемент процесса | Где наблюдается | Факты |
|---|---|---|
| Журнал решений в репозитории проекта | VoxelRPG, DPlang, DPpass, DPprofile | F-0020, F-0036, F-0044, F-0082, I-0001, I-0002 |
| Файл правил для ИИ-агента `CLAUDE.md` | VoxelRPG, DPlang, DPpass, DPprofile | F-0018, F-0036, F-0044, F-0083, I-0001, I-0002 |
| Список незавершённого `TODO.md` | VoxelRPG, DPlang, DPpass, DPprofile | F-0019, F-0036, F-0044, F-0083, I-0001, I-0002 |
| Скрипт локальных проверок | VoxelRPG, DPlang, DPpass, DPprofile | F-0016, F-0036, F-0044, F-0084, I-0001, I-0002 |
| Решение не использовать GitHub Actions; проверки в сессии | VoxelRPG, DPlang, DPprofile | F-0027, F-0039, F-0087, I-0008 |
| PR № 1 из ветки с префиксом `claude/` | VoxelRPG; prior — DP_Gen_Bots, DP_Graph_Builder, Andors-Love, TrueJointTileMaker, DP_Backup_Tool, DP_Typing_Master, DP_Autoclicker, DP_TextFile_Sorter, PixRogue, DP_Ecosystem, DP_Repeated_Tasks | F-0015, F-0064, F-0066, F-0067, F-0068, F-0069, F-0070, F-0071, F-0072, F-0073, F-0074, F-0075, I-0003 |
| Имя ветки первого PR из `claude/` с review или audit | VoxelRPG; prior — DP_Gen_Bots, DP_Graph_Builder, Andors-Love, TrueJointTileMaker, DP_Backup_Tool, DP_Typing_Master, DP_Repeated_Tasks | F-0015, F-0064, F-0066, F-0067, F-0068, F-0069, F-0070, F-0075, I-0004 |
| PR из веток с префиксом `ccr-` | VoxelRPG, DPlang, DPpass, DPprofile | F-0077, F-0078, F-0079, F-0081, I-0006 |
| Коммиты с именем автора «Claude» в истории | VoxelRPG, DPlang, DPpass, DPprofile | F-0031, F-0041, F-0047, F-0086, I-0005 |
| Коммиты ветки `claude/` с именем автора dpsmpx | prior — DP_Gen_Bots | F-0065, I-0005 |
| Записанный перенос практик из VoxelRPG в новый проект | DPlang | F-0036, F-0037, I-0002 |
| Машинная проверка границы движка в один день с решением Р1 | VoxelRPG | F-0021, F-0022, I-0007 |
| Блок README, который строит скрипт | DPpass, DPprofile | F-0046, F-0085, I-0012 |
| Роль ИИ-агентов в описании автора | профиль | F-0005, I-0005 |
| Код первого коммита из другого ИИ-инструмента | VoxelRPG | F-0051, I-0010 |
