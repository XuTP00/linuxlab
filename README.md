# LinuxLab v0.01

Веб-сервис для практического изучения Linux «от нуля до Pro».
Курс построен вокруг практики: каждое задание выполняется в настоящем
docker-контейнере с Ubuntu и проверяется автоматически движком проверок.

* **159 заданий**, 12 модулей, от `help`/`man` до systemd/git.
* Практика — ~100% заданий: каждое требует реальных команд в терминале.
* Терминал — полноценный bash в PTY: печатаете прямо в консоли, работают
  автодополнение по `Tab`, история, `Ctrl+C`, `nano` и `top`.

## Стек

| Слой | Технология |
|------|------------|
| Фронтенд | HTML + CSS + vanilla JS, xterm.js (терминал) |
| Веб-сервер | nginx (reverse proxy + статика) |
| Backend и движок проверок | Python 3.14 + FastAPI + uvicorn |
| Практическая среда | docker (контейнер на пользователя) |
| Автозапуск | systemd unit `linuxlab` |
| Прогресс | SQLite (`/var/lib/linuxlab/progress.db`) |

## Установка на любой Linux-дистрибутив

Скопируйте проект на сервер и запустите установщик — он сам поставит все
зависимости, соберёт образ, настроит systemd и nginx:

```bash
sudo bash install.sh
```

Поддерживаются **Debian/Ubuntu, RHEL/CentOS/Rocky/Alma/Fedora, Arch, openSUSE**
(Alpine — без systemd, сервис запускается вручную).

Что делает установщик:

1. определяет дистрибутив и ставит `docker`, `nginx`, `python3`, `python3-venv`;
2. разворачивает код в `/opt/linuxlab`, создаёт venv и ставит зависимости
   (fastapi, uvicorn);
3. собирает docker-образ лаборатории `linuxlab/lab:latest` (Ubuntu 26.04 + sshd + cron);
4. создаёт systemd-юнит `linuxlab` (env: `LINUXLAB_ADMIN_PASSWORD`, `LINUXLAB_IMAGE`,
   `LINUXLAB_DATA`) и включает автозапуск;
5. настраивает nginx (reverse proxy + WebSocket + статика), убирает дефолтный сайт;
6. проверяет `/api/health` и печатает адрес доступа.

Полезные ключи и переменные:

```bash
sudo bash install.sh --uninstall        # снести сервис (данные и образ останутся)
sudo bash install.sh --skip-packages    # не трогать системные пакеты
APP_DIR=/srv/linuxlab DATA_DIR=/srv/linuxlab-data HTTP_PORT=8080 sudo bash install.sh
```

Обновление (после правки кода) — тот же скрипт:

```bash
cd /opt/linuxlab && sudo bash install.sh
```

Полезные команды на сервере:

```bash
systemctl status linuxlab      # статус сервиса
journalctl -u linuxlab -f       # логи сервиса
systemctl restart linuxlab      # перезапуск
docker ps                       # активные контейнеры-сессии
```

Ручная установка (если скрипт не подходит) — в разделе «Структура»:
`deploy/Dockerfile.lab`, `deploy/nginx.conf`, `deploy/linuxlab.service`.

## Структура

```
install.sh            — установщик для любого Linux-дистрибутива (одна команда)
app/
  main.py            — FastAPI: API, WebSocket терминала, проверки заданий
  sessions.py        — менеджер docker-контейнеров и интерактивных bash-сессий (PTY)
  checker.py         — движок проверок (30+ типов проверок)
  progress.py        — прогресс пользователя (SQLite) и разблокировка копирования
  curriculum/        — учебный контент: 12 модулей, 159 заданий, теория к каждому
  static/            — интерфейс (index.html, css, js, вендорённый xterm.js)
deploy/
  Dockerfile.lab     — образ контейнера-лаборатории
  entrypoint.sh      — sshd + cron внутри контейнера
  linuxlab.service   — systemd unit (шаблон; установщик генерирует свой)
  nginx.conf         — конфигурация nginx (шаблон)
  install.sh         — обёртка на ../install.sh
  validate_course.py — автопрогон эталонных решений всех заданий (тест контента)
```

## Как устроен терминал

* Один docker-контейнер на пользователя (`linuxlab-sess-<id>`).
* Внутри — `bash --rcfile /etc/lab.bashrc -i`, запущенный под PTY (`script`),
  поэтому доступны интерактивные программы и `Ctrl+C`.
* Команды идут по WebSocket `/ws/{sid}`, вывод стримится в xterm.js.
* Проверки выполняются отдельным `docker exec` от root внутри того же контейнера.

## Типы проверок движка

`file_exists`, `file_absent`, `file_contains`, `file_not_contains`, `file_matches`,
`file_lines`, `file_nonempty`, `file_empty`, `file_exists_wait`, `dir_exists`,
`dir_contains`, `file_count`, `file_mode`, `file_owner`, `symlink`, `cmd_ok`,
`cmd_fail`, `cmd_stdout_contains`, `cmd_stdout_not_contains`, `cmd_stdout_matches`,
`cmd_stdout_equals`, `user_exists`, `group_exists`, `user_in_group`, `cron_contains`,
`history_contains`, `file_size_min`, `proc_running`, `proc_not_running`,
`port_listening`, `file_exists_in_path`.

## Интерфейс

* Две панели: задание и терминал. Раскладка переключается кнопкой «⇅ Раскладка»
  (верх-низ ↔ лево-право), границу можно тянуть мышью.
* **Текст задания нельзя скопировать** (мышь, Ctrl+C/X/A, контекстное меню, печать) —
  ученик вводит команды в терминале руками, чтобы набирать практику.
  При попытке копирования показывается подсказка. Терминал при этом работает как обычно.
  Кнопка «🔒 вводите вручную» в шапке панели открывает запрос пароля администратора:
  с правильным паролем (`LINUXLAB_ADMIN_PASSWORD`, по умолчанию `1541685`) копирование
  разрешается на 8 часов (состояние хранится на сервере, у каждого браузера своё),
  с неправильным — остаётся заблокированным. Повторное нажатие снова блокирует.
* Терминал — настоящий bash в PTY: Tab-автодополнение, история, Ctrl+C, nano, top, man/less.
* Сверху — прогресс прохождения курса, слева — дерево модулей с отметками выполненного.

## API

| Метод | Путь | Назначение |
|-------|------|-----------|
| GET | `/api/curriculum` | модули и задания с прогрессом |
| GET | `/api/task/{id}` | текст задания, цели, подсказки, список проверок |
| GET | `/api/solution/{id}` | эталонное решение |
| POST | `/api/check` | проверка задания в контейнере |
| POST | `/api/session` | создать контейнер-сессию |
| POST | `/api/session/{id}/exec` | выполнить команду (REST-фолбэк) |
| POST | `/api/session/{id}/reset` | пересоздать контейнер |
| WS | `/ws/{sid}` | поток вывода терминала |
| GET/POST | `/api/progress` | прогресс и его сброс |

## Программа курса

Курс построен так, чтобы новичок не спотыкался о незнакомые конструкции:
в первых трёх модулях **нет ни одного перенаправления** (`>`, `>>`, `|`) —
только сам терминал и базовые команды. Перенаправления вынесены в отдельную
подробную тему (модуль 3).

0. **Справка: help, --help, man** (8) — как узнать всё о команде и её параметрах
1. **Терминал и навигация** (13) — pwd, ls, cd, mkdir, nano, cp, mv, rm, glob, find
2. **Файлы, каталоги и права** (14) — chmod, umask, chown, ссылки, du/df, tar
3. **Перенаправления и пайпы** (22) — `>`, `>>`, `<`, `|`, `2>`, `2>&1`, /dev/null, tee, heredoc, `$(...)`, xargs, pipefail
4. **Текст: grep, sed, awk** (15) — поиск, замена, поля, инструменты в пайпах
5. **Поиск, архивы и хеши** (12) — find, tar, gzip, rsync, sha256sum, diff
6. **Процессы и фоновые задачи** (13) — ps, top, kill, jobs, nohup, /proc, nice
7. **Пользователи, группы, sudo** (12) — useradd, groupadd, usermod, su, /etc/passwd
8. **Сеть, DNS и SSH** (12) — ip, ping, curl, wget, ss, /etc/hosts, ssh-ключи, scp
9. **Скрипты на bash** (14) — переменные, аргументы, if/for/while/case, функции, trap
10. **Пакеты, systemd, cron, логи** (12) — dpkg, apt, crontab, unit-файлы, /var/log
11. **Git и продвинутые приёмы** (12) — git init/branch/diff, awk-агрегация, heredoc, base64

К каждому заданию добавлен блок «Теория»: что делает команда, какие у неё ключи
и на что обратить внимание.

## Проверка качества контента

```bash
cd /opt/linuxlab && ./venv/bin/python deploy/validate_course.py
```

Скрипт выполняет эталонное решение каждого задания в чистом контейнере
и прогоняет все проверки — итог должен быть «128 из 128».
