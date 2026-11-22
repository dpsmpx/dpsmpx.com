# Заметки о наблюдениях

Датированные записи о том, что наблюдалось без постоянного адреса
(ответ API, слова автора в сессии), — с происхождением и способом
перепроверки (`docs/sources/CITATION.md`). Заметка не меняется после
коммита; уточнение — новая заметка. Форму проверяет
`tools/verify/check_registry.py`.

Поля: `source` — источник из реестра; `observed` — дата наблюдения;
`origin` — как получено; `content` — что получено, дословно для чисел и
дат; `verify` — как перепроверить.

## Заметки

### N-0001

- source: S-10
- observed: 2026-10-04
- origin: GitHub REST API, данные пользователя dpsmpx; получены инструментом сессии Claude Code (вызов get_me) при создании этого репозитория
- content: login dpsmpx; created_at 2023-03-03T23:22:34Z; public_repos 20
- verify: https://api.github.com/users/dpsmpx — поля created_at и public_repos (public_repos меняется со временем)

### N-0002

- source: S-01
- observed: 2026-10-04
- origin: слова автора в сессии Claude Code 2026-10-04 — ответ в форме вопросов на вопрос «В истории Galdhold один коммит подписан именем автора «Ваше Имя» (F-0031). Это ваш коммит с ненастроенным git user.name?»
- content: «Да, это мой коммит»
- verify: спросить автора; имя «Ваше Имя» в истории Galdhold стоит у коммита 758804f (git log --author='Ваше Имя' в клоне S-01), docs/PROVENANCE.md Galdhold называет его заглушкой git config (F-0049)

### N-0003

- source: S-01
- observed: 2026-10-04
- origin: слова автора в сессии Claude Code 2026-10-04 — ответ в форме вопросов на вопрос о том, где и как создавался код первого коммита VoxelRPG 758804f (234 файла, 30 801 строка; F-0014)
- content: «Его сгенерировал DeepSeek за 16 проходов. Ссылка на сэссию: https://chat.deepseek.com/share/dgshsv2klukia1dwj4»
- verify: открыть https://chat.deepseek.com/share/dgshsv2klukia1dwj4; из среды сессии 2026-10-04 страница не открылась (HTTP 403 от CloudFront), её содержимое с коммитом 758804f не сверено

### N-0004

- source: S-10
- observed: 2026-10-04
- origin: список репозиториев аккаунта dpsmpx, полученный инструментом сессии Claude Code (list_repos) 2026-10-04; здесь — только публичные
- content: публичных 20; не форки — dpsmpx, tanks_blitz_stat_chat, DP_Ecosystem, DP_Repeated_Tasks, PixRogue, Andors-Love, DP_TextFile_Sorter, dpcalls, DP_Autoclicker, TrueJointTileMaker, DP_Typing_Master, DP_Backup_Tool, DP_Gen_Bots, DP_Graph_Builder, AIM_Trainer_pas, DP_Random_Cells; форки — andors-trail-load, gravitydefied, CreepyCodeCollection, pascalabcnet
- verify: https://github.com/dpsmpx?tab=repositories — список публичных репозиториев и пометка «forked from» у форков (меняется со временем)

### N-0005

- source: S-01
- observed: 2026-10-04
- origin: слова автора в сессии Claude Code 2026-10-04 — ответ в форме вопросов на вопрос «В Galdhold влиты PR из ветки с именем chatgpt (№ 97, 98, 99 — 2026-09-24; № 117 — 2026-09-28). Что это за ветка?»
- content: выбран вариант «Работа ChatGPT / Codex»
- verify: спросить автора; слияния из ветки chatgpt — git log --all --merges в клоне S-01 (F-0076)

### N-0006

- source: S-04
- observed: 2026-10-04
- origin: слова автора в сессии Claude Code 2026-10-04 — ответ в форме вопросов на вопрос «Имя dearpixel стоит автором коммитов в Andors-Love (включая первый коммит 2023-04-13), TrueJointTileMaker и DP_Random_Cells; dearVOXEL — имя ветки в Galdhold (PR № 149, 150). Это ваши имена?»
- content: «Как и записано в моём README.md профиля, мои ники также DP и dearpixel.»
- verify: первая строка README.md профиля на коммите 0b7aad9 (F-0089); спросить автора

### N-0007

- source: S-01
- observed: 2026-10-04
- origin: слова автора в сессии Claude Code 2026-10-04 — тот же ответ, что в N-0006, вторая фраза
- content: «dearVoxel - временное название проекта Galdhold, которое я не принял.»
- verify: спросить автора; ветка dearVOXEL — слияния PR № 149 и 150 в клоне S-01 (F-0095)
