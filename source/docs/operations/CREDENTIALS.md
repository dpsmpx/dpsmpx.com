# Учётные данные

Решения — Д12 (только у автора), Д25 (граница площадка × окружение);
правила — `docs/SECURITY.md`. В репозитории — только **имя** переменной
(`credential_ref` в `data/platforms/destinations.yaml`), значение — у
автора: переменная окружения в его терминале или локальное хранилище
секретов, из которого она выставляется. Облачным сессиям ИИ рабочие
токены не передаются никогда.

## 1. Где хранить

| Способ | Когда |
|---|---|
| Переменная окружения в терминале автора (`export CS_PROD_TELEGRAM_BOT_TOKEN=…` перед запуском, не в профиле оболочки) | сейчас: просто, ничего не пишется на диск |
| Менеджер паролей / хранилище ОС, из которого переменная выставляется скриптом автора | удобно и безопасно; скрипт — вне репозитория |
| Зашифрованный файл (age/sops) в `local/` (закрыт `.gitignore`) | если нужно хранить на диске |

`local/credentials.yaml` (вне Git) — по желанию: даты смены и срока для
`health`, **без значений**:

```yaml
CS_PROD_TELEGRAM_BOT_TOKEN: {rotated: 2026-10-05, expires: null}
CS_PROD_YOUTUBE_OAUTH: {rotated: 2026-10-05, expires: 2026-10-12}
```

## 2. Подключение площадок

### Telegram (бот в канал) — первая площадка (П4)
1. @BotFather → новый бот (`/newbot`); токен — сразу в хранилище
   секретов, не в чат и не в репозиторий.
2. Создать **закрытый тестовый канал** без подписчиков; добавить бота
   администратором с правом «Публикация сообщений».
3. Узнать числовые id: канала (`-100…`) и бота. Записать в
   `destinations.yaml`: `tg-test.target.id`, `tg-test.account.id`,
   `status: active`.
4. `export CS_STAGING_TELEGRAM_BOT_TOKEN=…`;
   `python3 -m tools.cs health --remote` — сверка бота и канала.
5. `publish … --to tg-devlog --safe` — публикация в тестовый канал.
6. Для дневника: бот — администратор канала-дневника с «Публикацией
   сообщений» (и «Редактированием», если нужна правка); id канала и
   бота → `tg-devlog`, `status: active`; токен рабочий — отдельная
   переменная `CS_PROD_TELEGRAM_BOT_TOKEN` (лучше отдельный бот для
   staging).

### Сайт: Beget (rsync по SSH, Д35, Д36)
Делает автор на своей машине; в репозиторий и в облачные сессии не
попадает ничего, кроме имени переменной.
1. Панель Beget (`cp.beget.com`) → **главная страница** → блок с
   общей / технической информацией об аккаунте: переключатель **SSH**
   (по умолчанию выключен) и **имя сервера** для подключения. Логин и
   пароль — те же, что для панели; порт 22. Проверить: `ssh
   логин@сервер`, затем на сервере `rsync --version`. rsync на сервере
   Beget есть: `site deploy --dry-run` у автора прошёл (05.10.2026);
   пропадёт — сообщить сессии: нужен другой способ выгрузки и новое
   решение по Д35. `kind: command` удалён по Д54: команда из репозитория не выполняется.
   Источник — база знаний Beget, «Как подключиться к серверу по
   SSH» и «Что такое SSH» (04.10.2026). В мобильной версии панели —
   значок ⓘ справа от имени на главной: «Тариф», «Сервер» и
   переключатель «SSH-доступ» (снимок автора, 04.10.2026: SSH включён,
   сервер — вида `<логин>.beget.tech`).
2. Первый вход — вручную: подтвердить отпечаток ключа сервера
   (`known_hosts`). Выгрузка идёт с `BatchMode=yes` и без этого шага
   откажет, а не спросит.
3. Отдельный ключ только для Beget: `ssh-keygen -t ed25519 -f
   ~/.ssh/beget_dpsmpx`, открытую часть (`.pub`) — в
   `~/.ssh/authorized_keys` на сервере (так Beget и описывает вход по
   ключу: статья «Автоматическая SSH-авторизация по ключу»). В
   `~/.ssh/config`: `Host <имя сервера>` → `IdentityFile
   ~/.ssh/beget_dpsmpx`. Пароль панели после этого сессиям ИИ не нужен и
   не передаётся.
4. `export CS_PROD_SITE_DEPLOY_TARGET='логин@сервер:dpsmpx.com/public_html/'`
   — в профиле оболочки или в файле, который он подключает (Termux —
   шаг 6 ниже), в одном месте и не в репозитории. Путь обязан кончаться на
   `public_html/` (`guard_suffix`), иначе выгрузка откажет.
5. `python3 -m tools.cs health` — строка «сайт / выгрузка»;
   `python3 -m tools.cs site deploy --dry-run` — что изменится.
6. Выгрузка разрешена (Д34): `production.live: true` в
   `data/website/site.yaml`, `site-production` — `status: active` в
   `destinations.yaml`. Сначала `site deploy --dry-run` — что изменится
   и удалится (`/.well-known/` под защитой), затем `site deploy` или
   `publish … --to site-production --production`.
7. **Выгружают только эти команды** (Д35): источник у них — свежая
   production-сборка, проверки идут до rsync. Свои скрипты и ярлыки
   только вызывают их (шаблон — «Ярлык Termux:Widget» ниже). Прямой
   rsync, scp или sftp в `public_html/` не запускать — даже для
   «починки» и по совету другого помощника: 05.10.2026 так на хостинг
   ушёл весь репозиторий (`docs/audits/2026-10-05-SITE_LEAK_INCIDENT.md`).

`rsync` — Linux, macOS, WSL на Windows, Android (Termux — ниже).
Локальный Claude Code запускает выгрузку только после «да» на запрос
разрешения (`.claude/settings.json`: `ask` на `publish`, `site deploy`,
`rsync`, `ssh`, `scp`, `sftp`; чтение `~/.ssh/**` запрещено). Правила
`ask` спрашивают в любом режиме Claude Code, но сверяют текст команды —
это защита от случайности; ключ на машине доступен локальному агенту
технически (Д36).

#### С телефона: Termux (Android)
Автор работает с телефона в Termux (сообщено 4 октября 2026). Что
отличается от компьютера:
- **Claude Code в Termux официально не поддерживается.** Поддерживаемые
  системы: macOS, Windows, Ubuntu, Debian, Alpine; пакет npm — для
  `linux-arm64` на glibc и musl, а в Android — Bionic
  (code.claude.com/docs/en/setup, 04.10.2026). Для выгрузки он и не
  нужен: по Д36 выгружает автор, а запуск вне сессии ИИ проверка вида
  сессии не останавливает (`session_may_deploy` в
  `tools/cs/site/deploy.py`). Команды ниже автор вводит сам.
- **Рендер изображений** (Playwright, Chromium) на Android не работает;
  `site deploy` его не требует: сборка сайта — чистый Python.
- `rpds-py` (зависимость `jsonschema` ≥ 4.18) собирается из исходников
  компилятором Rust: готовых колёс для Termux нет.

Шаги. `ЛОГИН` и `СЕРВЕР` — из окна ⓘ на главной странице панели; по
Д35 адрес выгрузки в Git не записывается, поэтому здесь — заполнители:
перед запуском их **заменить**. Остальное вводится буквально; где
команда идёт на сервере, а не в Termux, — сказано (после входа меняется
приглашение строки). Команды репозитория — только из его каталога и
только через `python3 -m tools.cs …`: просто `site deploy` оболочка не
знает. Заполнителей в командах проверки сервера нет: адрес они берут из
`CS_PROD_SITE_DEPLOY_TARGET` (шаг 6, «Проверка сервера» ниже).
1. Termux — с F-Droid или из релизов `termux/termux-app` на GitHub,
   не вперемешку с другими источниками. Затем:
   `pkg update && pkg upgrade`,
   `pkg install openssh rsync git gh python python-pip clang rust diffutils`.
   `pip` в Termux не обновлять через `pip` — им управляет `pkg`.
2. Репозиторий — в домашний каталог Termux, не в `/sdcard` (там нет
   прав на исполнение): `gh auth login` (GitHub.com, HTTPS, вход через
   браузер; код вида `XXXX-XXXX` печатает Termux), `gh repo clone
   dpsmpx/DPmetaApp ~/DPmetaApp` — система лежит в
   `~/DPmetaApp/socialmediaimage` (Д45), команды ниже — из этого каталога. В Termux нет хранилища
   ключей: токен `gh` лежит открытым текстом в `~/.config/gh/hosts.yml`
   (`gh` так и предупреждает); потерян телефон — отозвать на GitHub,
   Settings → Applications.
3. Зависимости — одним интерпретатором, Python из `pkg`
   (`$PREFIX/bin/python3`): `export ANDROID_API_LEVEL="$(getprop
   ro.build.version.sdk)"` (без неё maturin не соберёт `rpds-py`), затем
   `"$PREFIX/bin/python3" -m pip install -r tools/requirements.txt` —
   несколько минут. У автора в Termux два Python: `~/.local/bin/python`
   (3.14) стоит в `PATH` первым, а `pip` — от Python из `pkg` (04.10.2026,
   `which -a python pip`). Поэтому `python -m tools.cs` падает с
   `ModuleNotFoundError: No module named 'jsonschema'` (04.10 и снова
   05.10.2026), и все команды здесь — через `python3`, как в остальном
   репозитории и в `tools/check.sh`. Проверка — какое имя видит
   `jsonschema`:
   `for p in python python3 "$PREFIX/bin/python3"; do printf '%s: ' "$p"; "$p" -c 'import sys, jsonschema; print(sys.version.split()[0], jsonschema.__version__)' 2>&1 | tail -1; done`.
   Нужно, чтобы работал `python3`. Если работает только
   `$PREFIX/bin/python3` — `python3` в `PATH` перехвачен вторым Python:
   `command -v python3` покажет, где он, и решать, убрать ли его, —
   автору. `rpds-py` собирается под каждую версию Python отдельно —
   повторная сборка в несколько минут нормальна, прерывать её не нужно.
4. Первый вход паролем, шаги 1–2 выше:
   `ssh ЛОГИН@СЕРВЕР`, `yes` на отпечаток, пароль панели
   (на экране не виден). На сервере: `rsync --version | head -1`,
   `ls ~/dpsmpx.com` (ждём `public_html`), `exit`.
5. Ключ (шаг 3 выше):
   `ssh-keygen -t ed25519 -f ~/.ssh/beget_dpsmpx -C "dpsmpx deploy termux"`
   (без пароля на ключ — иначе нужен `ssh-agent`: выгрузка идёт с
   `BatchMode=yes`), затем
   `cat ~/.ssh/beget_dpsmpx.pub | ssh ЛОГИН@СЕРВЕР 'mkdir -p ~/.ssh && chmod 711 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'`
   (пароль панели — последний раз). В `~/.ssh/config` (`chmod 600`):
   ```
   Host СЕРВЕР
     User ЛОГИН
     IdentityFile ~/.ssh/beget_dpsmpx
     IdentitiesOnly yes
     ServerAliveInterval 30
   ```
   Проверка без пароля: `ssh -o BatchMode=yes СЕРВЕР 'echo ok'`.
6. Адрес выгрузки — в отдельный файл вне репозитория:
   `mkdir -p ~/.config/dpsmpx`, в `~/.config/dpsmpx/deploy.env` одна
   строка `export CS_PROD_SITE_DEPLOY_TARGET='ЛОГИН@СЕРВЕР:dpsmpx.com/public_html/'`,
   `chmod 600 ~/.config/dpsmpx/deploy.env`. Его подключают и профиль
   оболочки (`echo $0`: `bash` → `~/.bashrc`, `zsh` → `~/.zshrc`; в
   Termux по умолчанию bash) строкой `. ~/.config/dpsmpx/deploy.env`,
   и ярлык ниже. Ярлык виджета `~/.bashrc` не читает: bash там не
   интерактивный. Других переменных для выгрузки не нужно: прежнюю
   строку `export` из `~/.bashrc` заменить подключением файла;
   `~/.config/dpsmpx/deploy.conf` и прочие самодельные настройки
   выгрузки (`SITE_DIR` и т. п.) — прочитать и удалить, адрес в чат не
   вставлять. Затем — новая вкладка Termux.
   Если переменная уже задана в профиле, файл создаётся из неё: адрес
   не набирать и не выводить на экран (05.10.2026 ярлык отказал: файла
   не было, адрес был только в профиле):
   ```bash
   mkdir -p ~/.config/dpsmpx && chmod 700 ~/.config/dpsmpx
   printf "export CS_PROD_SITE_DEPLOY_TARGET='%s'\n" "$CS_PROD_SITE_DEPLOY_TARGET" > ~/.config/dpsmpx/deploy.env
   chmod 600 ~/.config/dpsmpx/deploy.env
   ( . ~/.config/dpsmpx/deploy.env; case "$CS_PROD_SITE_DEPLOY_TARGET" in *@*:*public_html/) echo "формат верный";; *) echo "формат неверный";; esac )
   grep -l CS_PROD_SITE_DEPLOY_TARGET ~/.zshrc ~/.bashrc ~/.profile ~/.zprofile ~/.config/dpsmpx/* 2>/dev/null
   ```
   Последняя строка — только имена файлов, где ещё записан адрес; в
   профиле строку `export` заменить на `. ~/.config/dpsmpx/deploy.env`.
7. Ключ водяного знака (Д41) — один раз: `python3 -m tools.cs mark init`
   создаёт `~/.config/dpsmpx/mark.key` (права 600) и печатает его отпечаток.
   Ключ — в свою резервную копию вне Git и вне сессий ИИ: без него
   выпущенные метки не прочитать, а без файла выгрузка отказывает. Для
   изображений на сайте — `pkg install python-numpy python-pillow`; для
   меток OpenTimestamps — тоже: `"$PREFIX/bin/python3" -m pip install
   opentimestamps-client` (Д41 — метки обеих служб; без клиента выгрузка
   ставит только RFC 3161, `.ots` — позже командой `mark stamp`).
   Затем проверки: `tools/check.sh --quick`, `python3 -m tools.cs health`,
   `python3 -m tools.cs site deploy --dry-run` — ничего не выкладывает,
   последняя строка «изменений: N».
8. Выгрузка (разрешена, Д34; только проверенный сайт, Д47): `git pull` в
   `~/DPmetaApp/socialmediaimage`; в `main` должна быть запись проверки
   `data/website/site-check.json` — её пишет сессия полным
   `tools/check.sh --release` и коммитит; после неё система не менялась
   (одобрение автора — тоже правка: после него нужна новая проверка). Снова
   `python3 -m tools.cs site deploy --dry-run` — сверить, что удаляется,
   затем `python3 -m tools.cs site deploy` — или ярлыком ниже. В конце —
   проверка `/`, `/en/`, `/projects/` по `https://dpsmpx.com`: `✓` —
   страница на месте, `?` — адрес не открывается (сеть или
   сертификат), `✗` — 404 или чужая
   страница. После выгрузки — манифест выпуска и метки времени
   (`data/provenance/site-releases/`): `git add data/provenance/site-releases
   && git commit && git push`; метки, не поставленные без сети, —
   `python3 -m tools.cs mark stamp`. Изменений 0 — выгружать нечего: сервер уже совпадает со
   сборкой.

#### Ярлык Termux:Widget
Готовый ярлык — `tools/termux/dpsmpx-site-deploy.sh` (тесты —
`tests/test_termux_shortcut.py`). Он только вызывает систему: rsync,
адресов и путей сервера в нём нет. Нужно приложение Termux:Widget из
того же источника, что и Termux (F-Droid или GitHub), и виджет на
главном экране. Установка — из каталога репозитория:
```bash
mkdir -p ~/.shortcuts && chmod 700 ~/.shortcuts
install -m 700 ~/DPmetaApp/socialmediaimage/tools/termux/dpsmpx-site-deploy.sh ~/.shortcuts/
```
Каталог — `~/.shortcuts/`, а не `~/.shortcuts/tasks/`: оттуда ярлык идёт
без терминала, и подтверждение не спросить. Ярлык — копия: после
изменения файла в репозитории снова выполнить `install`. Ярлык — только
для автора: из сессии Claude Code он отказывает (Д36 — сессия выгружает
`python3 -m tools.cs site deploy` после «да»); без ввода или при
оборванном ответе — тоже отказ.

Что делает нажатие:
1. Отказывает, если нет `~/.config/dpsmpx/deploy.env`, ветка не `main` или
   есть незакоммиченное; затем `git pull --ff-only`. После него — сайт
   проверен (Д47): нет `data/website/site-check.json` или после
   проверенного коммита система менялась (кроме
   `data/provenance/site-releases/` и самой записи) — отказ «нужна новая
   проверка»; иначе — строка «Сайт проверен: <коммит>, <время>».
2. `python3 -m tools.cs site deploy --dry-run` (Python из `pkg`, шаг 3).
   Ошибка — выгрузки нет. «изменений: 0» — «выгружать нечего», конец.
   Есть строки `*deleting` — предупреждает: удаляться должно только
   старое содержимое сайта.
3. Спрашивает «да». Любой другой ответ — отмена.
4. `python3 -m tools.cs site deploy` и проверка `https://dpsmpx.com/`:
   не 200 — сообщение (500 — Beget не принимает строку `.htaccess`).
Окно не закрывается, пока не нажать Enter: вывод можно прочитать.

#### Проверка сервера (только чтение)
Адрес и путь — из `CS_PROD_SITE_DEPLOY_TARGET` (шаг 6), подставлять в
команды ничего не нужно, и адрес в вывод не попадает. Сначала шаг 8 до
`--dry-run` включительно: он заново собирает `build/site/production`,
с которой сравнивается сервер. Ошибку `ssh` с именем сервера в чат —
только заменив имя на `СЕРВЕР`.
```bash
cd ~/DPmetaApp/socialmediaimage
[ -f ~/.config/dpsmpx/deploy.env ] && . ~/.config/dpsmpx/deploy.env
T="${CS_PROD_SITE_DEPLOY_TARGET:-}"; H="${T%%:*}"; P="${T#*:}"
[ -n "$T" ] && echo "адрес задан" || echo "адрес не задан — шаг 6"
ssh -o BatchMode=yes "$H" "cd '$P' && grep -c '<h1>dpsmpx</h1>' index.html en/index.html"
ssh -o BatchMode=yes "$H" "cd '$P' && find . -mindepth 1 | LC_ALL=C sort" > ~/server-files.txt
(cd build/site/production && find . -mindepth 1 | LC_ALL=C sort) > ~/build-files.txt
diff ~/build-files.txt ~/server-files.txt && echo "списки совпадают: $(wc -l < ~/server-files.txt)"
ssh -o BatchMode=yes "$H" 'cut -d" " -f1,3- ~/.ssh/authorized_keys'
```
Ожидается: `index.html:1` и `en/index.html:1` (сборка без имени, Д37);
«списки совпадают: 39» — без строк `<` и `>` от `diff` (лишнее на
сервере, в том числе `.~tmp~`, видно здесь, а не в `--dry-run`); ключи —
только свои (`ssh-ed25519 … dpsmpx deploy termux`). Разбор адреса —
конструкции POSIX: годится для bash и zsh.

Ключей больше одного — сверить отпечатки (`SHA256:…`) сервера и
телефона; открытые ключи не секрет:
```bash
ssh -o BatchMode=yes "$H" 'cat ~/.ssh/authorized_keys' > ~/server-keys.txt
ssh-keygen -lf ~/server-keys.txt
for f in ~/.ssh/*.pub; do ssh-keygen -lf "$f"; done
ssh -G "$H" | grep -i '^identityfile'
```
Последняя строка — какой ключ берёт выгрузка (ждём `~/.ssh/beget_dpsmpx`).
Строка сервера без пары на телефоне — чужой ключ: удалить её сразу,
сменить пароль панели, сообщить сессии. Своя, но ненужная — удалить её
и закрытый ключ на телефоне.

Предупреждение `ssh` «not using a post-quantum key exchange algorithm» —
о сервере Beget: постквантового обмена ключами у него нет. Исправить
может только Beget. Для выгрузки не опасно: по каналу идут публичные
файлы сайта, а ключ входа из записанного трафика не извлечь.

Ключ на телефоне отзывается удалением его строки из
`~/.ssh/authorized_keys` на сервере (§3 «Ротация и отказ»); потерян
телефон — удалить строку сразу.

#### Если Beget отказывает
Точный текст ошибки и `ssh -v ЛОГИН@СЕРВЕР 2>&1 | tail -25`
показывают причину (пароль в выводе не печатается).

| Сообщение | Вероятная причина | Что делать |
|---|---|---|
| `Permission denied, please try again.` после пароля | неверный логин или пароль; SSH ещё выключен | логин — из «Общей информации», не имя и не почта; пароль — от панели (сброс — в панели); переключатель SSH включён; пароль — вставкой (долгое нажатие → Paste): клавиатура телефона может подменять символы и регистр |
| соединение закрывается сразу после пароля (`Connection closed by … port 22`) | SSH-доступ ещё не применился | выключить и включить SSH в панели, подождать несколько минут, войти снова; не помогает — тикет в поддержку Beget с текстом ошибки |
| `Connection timed out`, `Network is unreachable` | порт 22 закрыт сетью (мобильный оператор, VPN) | другая сеть или без VPN |
| `Could not resolve hostname` | опечатка в имени сервера | имя — из панели |
| `Host key verification failed` | первый вход был с `BatchMode` или отпечаток сменился | первый вход — вручную; сменился — сверить с поддержкой Beget, только потом `ssh-keygen -R СЕРВЕР` |
| `Permission denied (publickey,password)` с `BatchMode=yes` | ключ не принят | `ssh -v`: какой файл ключа предложен; на сервере `chmod 711 ~/.ssh`, `chmod 600 ~/.ssh/authorized_keys`; строка `.pub` целиком, одной строкой |
| `rsync: command not found` на сервере | rsync у Beget нет | сообщить сессии: нужен другой способ выгрузки — новым решением по Д35; самому `lftp`/`scp` не выгружать |

Много неудачных попыток подряд сервер может временно блокировать
адрес — подождать перед новой попыткой (как именно у Beget —
UNKNOWN).

### Сайт: команда выгрузки (Д55)

Вместо rsync выгрузку может делать своя программа автора — только если
автор так настроил: в `data/website/site.yaml` у окружения `deploy:
{kind: command, command_ref: CS_PROD_SITE_DEPLOY_COMMAND}` — имя
переменной, сама команда — только у автора, как адрес выгрузки:

```sh
export CS_PROD_SITE_DEPLOY_COMMAND='["/home/автор/bin/выгрузка-сайта", "--аргумент"]'
```

- Значение — массив JSON строк; первая — абсолютный путь программы (не
  из `PATH`). Иное — отказ до запуска.
- Команда исполняется без оболочки, из корня системы; в выводе вместо
  неё — `<команда выгрузки автора>`. Список `command` в самом
  `site.yaml` не исполняется никогда.
- Правила выпуска те же, что у rsync: `live` (Д34), только автор или
  локальная сессия (Д36), метка сборки (Д41). Пока действует Д52 (сайт на
  паузе), переменная не нужна и сессия её не читает.

### VK, YouTube, Discord, GitHub, TikTok
Сейчас — ручной путь (`docs/platforms/PUBLISHING_CAPABILITY_MATRIX.md`).
Подключение — в своих фазах `ROADMAP/ROADMAP.md` (П5–П8): VK — ключ
пользователя после выдачи права `wall`; YouTube — OAuth-клиент Google
(в режиме «Testing» refresh token живёт 7 дней — перевести приложение в
production или входить заново раз в неделю); Discord — URL вебхука
(это секрет целиком); GitHub — fine-grained token только на нужные
репозитории с `Contents: write`.

## 3. Ротация и отказ (§31)

| Событие | Признак | Что делать |
|---|---|---|
| Истёк срок | `AUTH_EXPIRED`; `health` — «истёк» | обновить у площадки (OAuth — повторный вход), выставить переменную, отметить `rotated` |
| Плановая смена | раз в полгода или при смене машины | выпустить новый, проверить `health --remote`, отозвать старый |
| Отзыв | токен больше не нужен | отозвать у площадки (Telegram — `/revoke` у @BotFather; VK — настройки сообщества; Google — разрешения аккаунта; Discord — удалить вебхук; GitHub — удалить token) |
| Подозрение на утечку | токен попал в чат, лог, Git, чужой компьютер | **сначала отозвать у площадки**, затем выпустить новый; если в Git — `docs/SECURITY.md`, §4 |
| Потеря | токена нет | выпустить новый; старый отозвать |

Потеря или истечение токена одной площадки **не останавливает
остальные** (§31): адресат даёт `MISSING_CREDENTIALS`/`AUTH_EXPIRED`,
публикация остаётся `FAILED` без повторов, остальные площадки и сайт
работают; канон не затронут.

## 4. Что проверяется автоматически

- `secrets` — известные формы токенов (в том числе бота Telegram,
  Discord, GitHub, Google) и файлы секретов в репозитории;
- `destinations` — имя переменной соответствует окружению, одно имя не
  используется в двух окружениях;
- журнал и логи пишутся без токенов (`core/obs.py` вычищает их тем же
  сканером);
- адрес запроса Telegram (с токеном) не попадает в ошибки и логи.

Секреты представлены отдельным типом Secret: str/repr маскируют
значение, reveal вызывается только на границе транспорта.
Не включать reveal в журнал.
