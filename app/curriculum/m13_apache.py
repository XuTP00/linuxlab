"""Модуль 13. Установка и настройка Apache HTTP Server.

Apache HTTP Server — популярный свободный веб-сервер с открытым исходным кодом.
Все проверки этого модуля идут через HTTP: сайт должен реально отвечать
(это же видно во вкладке «Web» второй панели).
"""
from .helpers import cok, fc, fe, fm, fne, hist, out, port

MODULE = {
    "id": "m13",
    "title": "Модуль 13. Установка и настройка Apache",
    "icon": "🪶",
    "summary": "Apache HTTP Server: установка, конфигурация, порты, виртуальные хосты, модули, логи и права.",
    "tasks": [
        {
            "id": "m13-01",
            "title": "Устанавливаем Apache",
            "difficulty": 3,
            "points": 15,
            "task": """Apache HTTP Server — один из самых популярных свободных веб-серверов
с открытым исходным кодом. В дистрибутивах Debian/Ubuntu он называется `apache2`.

Установите его:

    sudo apt-get update
    sudo apt-get install -y apache2

Посмотрите версию: `apache2 -v` — она выведет что-то вроде
`Server version: Apache/2.4.65 (Ubuntu)`.""",
            "goals": ["Установить Apache HTTP Server", "Узнать версию сервера"],
            "hints": ["sudo apt-get update && sudo apt-get install -y apache2",
                      "apache2 -v — версия, apache2 -V — подробные параметры сборки",
                      "Конфигурационный каталог: /etc/apache2"],
            "solution": "sudo apt-get update && sudo apt-get install -y apache2 && apache2 -v",
            "checks": [
                cok("command -v apache2 >/dev/null 2>&1", "Программа apache2 установлена"),
                cok("dpkg -s apache2 >/dev/null 2>&1", "Пакет apache2 установлен"),
                out("Apache/2", "В терминале показана версия Apache"),
            ],
        },
        {
            "id": "m13-02",
            "title": "Устройство конфигурации Apache",
            "difficulty": 3,
            "points": 15,
            "task": """Посмотрите, из чего состоит конфигурация Apache:

    ls /etc/apache2/

В ней есть главный файл `apache2.conf`, каталоги `sites-available` и `sites-enabled`
(виртуальные хосты), `mods-available` и `mods-enabled` (модули),
`conf-available`/`conf-enabled` (готовые блоки конфигурации) и `ports.conf` (порты).

Загляните в `sites-available` и `mods-available`:

    ls /etc/apache2/sites-available/ /etc/apache2/mods-available/ | head -20""",
            "goals": ["Разобраться в структуре конфигурации Apache", "Понять разницу available/enabled"],
            "hints": ["ls /etc/apache2/", "cat /etc/apache2/ports.conf — какие порты слушаем",
                      "В available лежат все конфиги, в enabled — только включённые (это симлинки)"],
            "solution": "ls /etc/apache2/ && ls /etc/apache2/sites-available/ && ls /etc/apache2/mods-available/ | head -20",
            "checks": [
                hist("/etc/apache2", "Открыли каталог конфигурации"),
                out("apache2.conf", "Виден главный конфигурационный файл"),
                out("sites-available", "Есть каталог виртуальных хостов"),
            ],
        },
        {
            "id": "m13-03",
            "title": "Первый запуск сервера",
            "difficulty": 3,
            "points": 15,
            "task": """В контейнере нет systemd, поэтому Apache запускают через `apache2ctl`:

    sudo apache2ctl start

Проверьте, что порт 80 слушается: `ss -tuln | grep ':80 '`
и что процесс работает: `pgrep -a apache2`.

При первом запуске появится предупреждение про ServerName — это нормально,
в следующих заданиях мы его устраним.

**Если порт 80 занят** (например, вы не отключили стандартный сайт Angie в прошлом модуле),
Apache не стартует с ошибкой `could not bind to address 0.0.0.0:80`.
Освободите порт:

    sudo ss -tulnp | grep ':80 ' | grep -o 'pid=[0-9]*' | cut -d= -f2 | xargs -r sudo kill

и запустите Apache снова.""",
            "goals": ["Запустить Apache без systemd", "Увидеть процесс и слушающий порт", "Разобраться, почему сервер не может занять порт"],
            "hints": ["sudo apache2ctl start", "pgrep -a apache2 — процессы",
                      "Остановить: sudo apache2ctl stop, перечитать конфиг: sudo apache2ctl graceful",
                      "Порт 80 может держать Angie из предыдущего модуля — проверьте sudo ss -tulnp | grep ':80 '"],
            "solution": "sudo ss -tulnp | grep ':80 ' | grep -o 'pid=[0-9]*' | cut -d= -f2 | xargs -r sudo kill; sleep 1; sudo apache2ctl start && sleep 1 && pgrep -a apache2 && ss -tuln | grep ':80 '",
            "checks": [
                cok("pgrep -x apache2 >/dev/null 2>&1", "Процесс Apache запущен"),
                port(80, "Порт 80 слушается"),
            ],
        },
        {
            "id": "m13-04",
            "title": "Страница по умолчанию",
            "difficulty": 2,
            "points": 10,
            "task": """Откройте сайт, который Apache отдаёт сразу после установки:

    curl http://127.0.0.1/

Должна прийти стандартная страница Ubuntu: «Apache2 Ubuntu Default Page» и «It works!».

Теперь переключитесь во вкладку **«Web»** справа, укажите порт **80**
и путь `/index.html` — вы увидите эту же страницу прямо в интерфейсе.""",
            "goals": ["Обратиться к сайту по HTTP", "Увидеть результат во вкладке Web"],
            "hints": ["curl http://127.0.0.1/", "Во вкладке Web поменяйте порт на 80 и нажмите «Обновить»",
                      "Код ответа: curl -sI http://127.0.0.1/ | head -1"],
            "solution": "curl http://127.0.0.1/ && curl -sI http://127.0.0.1/ | head -1",
            "checks": [
                cok("curl -s http://127.0.0.1/ | grep -qi 'Apache2' ", "Дефолтная страница отдаётся"),
                out("200 OK", "Получен код ответа 200 OK"),
            ],
        },
        {
            "id": "m13-05",
            "title": "Готовим свой каталог сайта",
            "difficulty": 2,
            "points": 15,
            "task": """Создайте каталог сайта `/var/www/mysite` и в нём главную страницу `index.html`
с содержимым:

    <h1>My Apache site</h1>

Проверьте: `sudo cat /var/www/mysite/index.html`.""",
            "goals": ["Создать каталог для сайта", "Подготовить главную страницу"],
            "hints": ["sudo mkdir -p /var/www/mysite",
                      "echo '<h1>My Apache site</h1>' | sudo tee /var/www/mysite/index.html",
                      "Права: каталог 755, файл 644"],
            "solution": "sudo mkdir -p /var/www/mysite && echo '<h1>My Apache site</h1>' | sudo tee /var/www/mysite/index.html",
            "checks": [
                fe("/var/www/mysite/index.html", "Главная страница создана"),
                fc("/var/www/mysite/index.html", "My Apache site", "Содержимое страницы верное"),
            ],
        },
        {
            "id": "m13-06",
            "title": "Виртуальный хост Apache",
            "difficulty": 4,
            "points": 25,
            "task": """Apache хранит сайты в `/etc/apache2/sites-available/`, а включает их
симлинками в `sites-enabled/`. Создайте конфиг `/etc/apache2/sites-available/mysite.conf`:

    <VirtualHost *:8082>
        ServerName mysite.local
        DocumentRoot /var/www/mysite
        <Directory /var/www/mysite>
            Require all granted
        </Directory>
    </VirtualHost>

Затем включите сайт и перечитайте конфигурацию:

    sudo a2ensite mysite
    sudo apache2ctl graceful

Порт 8082 выбран, чтобы не мешать дефолтному сайту на 80 и сайту Angie на 8081.""",
            "goals": ["Написать конфиг виртуального хоста", "Научиться включать и выключать сайты (a2ensite/a2dissite)"],
            "hints": ["Директива DocumentRoot указывает каталог сайта",
                      "Require all granted — блок Directory разрешает доступ (в Apache 2.4 вместо Order/Allow)",
                      "sudo a2ensite mysite — включить, sudo a2dissite mysite — выключить"],
            "solution": "printf '<VirtualHost *:8082>\\n    ServerName mysite.local\\n    DocumentRoot /var/www/mysite\\n    <Directory /var/www/mysite>\\n        Require all granted\\n    </Directory>\\n</VirtualHost>\\n' | sudo tee /etc/apache2/sites-available/mysite.conf && sudo a2ensite mysite && sudo apache2ctl graceful && sleep 1",
            "checks": [
                fe("/etc/apache2/sites-available/mysite.conf", "Конфиг виртуального хоста создан"),
                fc("/etc/apache2/sites-available/mysite.conf", "DocumentRoot /var/www/mysite", "Указан DocumentRoot"),
                fc("/etc/apache2/sites-available/mysite.conf", "8082", "Указан порт 8082"),
                {"type": "cmd_ok", "cmd": "test -L /etc/apache2/sites-enabled/mysite.conf", "title": "Сайт включён через a2ensite"},
            ],
        },
        {
            "id": "m13-07",
            "title": "Apache не слушает порт, пока его не объявили",
            "difficulty": 4,
            "points": 25,
            "task": """Важная особенность Apache: блок `<VirtualHost *:8082>` **не заставляет**
сервер слушать порт 8082. Порты задаются глобально директивой `Listen` в файле
`/etc/apache2/ports.conf`.

Добавьте туда ещё один порт (в начало файла, рядом с другими Listen):

    Listen 8082

Затем перечитайте конфигурацию и проверьте:

    sudo apache2ctl graceful
    ss -tuln | grep ':8082 '

Порт 8082 должен появиться в списке слушающих.""",
            "goals": ["Понять, что порты Apache задаются директивой Listen", "Научиться менять набор слушаемых портов"],
            "hints": ["cat /etc/apache2/ports.conf",
                      "sudo sed -i '1i Listen 8082' /etc/apache2/ports.conf",
                      "После правки: sudo apache2ctl -t && sudo apache2ctl graceful"],
            "solution": "sudo sed -i '1i Listen 8082' /etc/apache2/ports.conf && sudo apache2ctl graceful && sleep 1 && ss -tuln | grep ':8082 '",
            "checks": [
                fc("/etc/apache2/ports.conf", "Listen 8082", "Порт 8082 объявлен в ports.conf"),
                port(8082, "Порт 8082 слушается"),
            ],
        },
        {
            "id": "m13-08",
            "title": "Проверяем сайт через HTTP",
            "difficulty": 3,
            "points": 15,
            "task": """Проверьте, что ваш сайт реально работает:

    curl http://127.0.0.1:8082/

В ответ должна прийти страница «My Apache site».

И посмотрите заголовки: `curl -sI http://127.0.0.1:8082/` — среди них
`Server: Apache/2.4.x (Ubuntu)`.

Веб-вкладка справа: укажите порт **8082** и путь `/index.html`.""",
            "goals": ["Проверить работу сайта по HTTP", "Убедиться, что отвечает именно Apache"],
            "hints": ["curl http://127.0.0.1:8082/", "curl -sI http://127.0.0.1:8082/ | grep Server",
                      "Веб-вкладка: порт 8082, путь /index.html"],
            "solution": "curl http://127.0.0.1:8082/ && curl -sI http://127.0.0.1:8082/ | grep -i server",
            "checks": [
                cok("curl -s http://127.0.0.1:8082/ | grep -q 'My Apache site'", "Сайт отдаёт нашу страницу"),
                cok("curl -sI http://127.0.0.1:8082/ | grep -qi 'Server: Apache'", "Отвечает Apache"),
            ],
        },
        {
            "id": "m13-09",
            "title": "Проверка синтаксиса: apache2ctl -t",
            "difficulty": 3,
            "points": 15,
            "task": """Прежде чем перечитывать конфигурацию, её нужно проверить:

    sudo apache2ctl -t

Ожидаемый ответ — `Syntax OK`. Если есть ошибка, Apache покажет строку и файл,
в котором она найдена.

Аналогично `nginx -t` и `angie -t` — всегда проверяйте конфиг перед применением.""",
            "goals": ["Проверять конфигурацию перед перезагрузкой", "Научиться читать сообщения об ошибках"],
            "hints": ["sudo apache2ctl -t", "Ошибка выглядит так: AH00100: Syntax error on line 5 ...",
                      "После проверки — sudo apache2ctl graceful"],
            "solution": "sudo apache2ctl -t",
            "checks": [
                hist("apache2ctl -t", "Проверили конфигурацию"),
                out("Syntax OK", "Синтаксис корректен"),
            ],
        },
        {
            "id": "m13-10",
            "title": "Управление сайтами: a2dissite",
            "difficulty": 4,
            "points": 20,
            "task": """Сайт включается и выключается без правки конфигов — только симлинками.

1. Выключите наш сайт: `sudo a2dissite mysite && sudo apache2ctl graceful`
2. Убедитесь, что порт 8082 больше не отвечает: `curl -sI http://127.0.0.1:8082/` (будет ошибка соединения)
3. Включите сайт обратно: `sudo a2ensite mysite && sudo apache2ctl graceful`
4. Снова проверьте: `curl http://127.0.0.1:8082/`

После шага 4 сайт снова должен отвечать.""",
            "goals": ["Научиться включать и выключать виртуальные хосты", "Понять механику sites-enabled"],
            "hints": ["sudo a2dissite mysite — снимает симлинк из sites-enabled",
                      "sudo a2ensite mysite — создаёт его снова",
                      "После каждого переключения: sudo apache2ctl graceful"],
            "solution": "sudo a2dissite mysite && sudo apache2ctl graceful && sleep 1; sudo a2ensite mysite && sudo apache2ctl graceful && sleep 1 && curl -s http://127.0.0.1:8082/",
            "checks": [
                {"type": "cmd_ok", "cmd": "test -L /etc/apache2/sites-enabled/mysite.conf", "title": "Сайт снова включён"},
                cok("curl -s http://127.0.0.1:8082/ | grep -q 'My Apache site'", "Сайт отвечает после включения"),
                hist("a2dissite", "Попробовали выключить сайт через a2dissite"),
            ],
        },
        {
            "id": "m13-11",
            "title": "Директива ServerName и глобальный параметр",
            "difficulty": 4,
            "points": 20,
            "task": """При первом запуске Apache ругается: `Could not reliably determine the server's
fully qualified domain name`. Чтобы этого не было, задайте имя сервера глобально.

Создайте файл `/etc/apache2/conf-available/servername.conf`:

    ServerName linuxlab.local

Включите его и перечитайте конфигурацию:

    sudo a2enconf servername
    sudo apache2ctl graceful

Предупреждение должно исчезнуть, а сайт — продолжить работать.""",
            "goals": ["Устранить предупреждение о ServerName", "Научиться подключать готовые блоки конфигурации (a2enconf)"],
            "hints": ["Директива ServerName задаёт основное имя сервера",
                      "a2enconf — аналог a2ensite, но для conf-available",
                      "Проверить: sudo apache2ctl -t"],
            "solution": "echo 'ServerName linuxlab.local' | sudo tee /etc/apache2/conf-available/servername.conf && sudo a2enconf servername && sudo apache2ctl graceful && sleep 1 && sudo apache2ctl -t",
            "checks": [
                fe("/etc/apache2/conf-available/servername.conf", "Файл с ServerName создан"),
                fc("/etc/apache2/conf-available/servername.conf", "ServerName linuxlab.local", "Имя сервера задано"),
                {"type": "cmd_ok", "cmd": "ls /etc/apache2/conf-enabled/ | grep -q servername.conf", "title": "Конфиг включён через a2enconf"},
            ],
        },
        {
            "id": "m13-12",
            "title": "Логи Apache",
            "difficulty": 4,
            "points": 20,
            "task": """Apache пишет два основных журнала:

* `/var/log/apache2/access.log` — все обращения (IP, дата, метод, URL, код, размер);
* `/var/log/apache2/error.log` — ошибки и предупреждения.

Сделайте несколько запросов (`curl http://127.0.0.1:8082/`) и посмотрите журнал:

    sudo tail -3 /var/log/apache2/access.log

В журнале должны появиться строки с `"GET / HTTP/1.1" 200`.""",
            "goals": ["Найти журналы Apache", "Научиться читать формат access.log"],
            "hints": ["ls /var/log/apache2/", "sudo tail -3 /var/log/apache2/access.log",
                      "Формат: IP - - [дата] \"МЕТОД URL\" код размер"],
            "solution": "curl -s http://127.0.0.1:8082/ >/dev/null && sudo tail -3 /var/log/apache2/access.log",
            "checks": [
                fe("/var/log/apache2/access.log", "Журнал доступа существует"),
                fc("/var/log/apache2/access.log", "GET /", "В журнале есть запись о запросе"),
                fc("/var/log/apache2/access.log", "200", "Записан код ответа 200"),
            ],
        },
        {
            "id": "m13-13",
            "title": "Модули Apache: a2enmod",
            "difficulty": 4,
            "points": 20,
            "task": """Apache собран из модулей: rewrite, headers, ssl, php и другие.
Готовые файлы лежат в `/etc/apache2/mods-available/`, включённые — в `mods-enabled/`.

Включите модуль заголовков:

    sudo a2enmod headers
    sudo apache2ctl graceful

Затем добавьте в свой виртуальный хост директиву (внутри блока `<VirtualHost>`):

    Header set X-Lab "linuxlab"

Проверьте, что заголовок появился:

    curl -sI http://127.0.0.1:8082/ | grep -i x-lab""",
            "goals": ["Научиться включать модули Apache", "Добавить свой заголовок в ответ сервера"],
            "hints": ["ls /etc/apache2/mods-available/ — список модулей",
                      "sudo a2enmod headers — включить, sudo a2dismod headers — выключить",
                      "Директива Header работает только с включённым модулем headers"],
            "solution": "sudo a2enmod headers && printf '<VirtualHost *:8082>\\n    ServerName mysite.local\\n    DocumentRoot /var/www/mysite\\n    Header set X-Lab \"linuxlab\"\\n    <Directory /var/www/mysite>\\n        Require all granted\\n    </Directory>\\n</VirtualHost>\\n' | sudo tee /etc/apache2/sites-available/mysite.conf && sudo apache2ctl graceful && sleep 1 && curl -sI http://127.0.0.1:8082/ | grep -i x-lab",
            "checks": [
                {"type": "cmd_ok", "cmd": "ls /etc/apache2/mods-enabled/ | grep -q headers.load", "title": "Модуль headers включён"},
                fc("/etc/apache2/sites-available/mysite.conf", "Header set X-Lab", "В конфиге добавлена директива Header"),
                cok("curl -sI http://127.0.0.1:8082/ | grep -qi 'x-lab: linuxlab'", "Сервер отдаёт свой заголовок X-Lab"),
            ],
        },
        {
            "id": "m13-14",
            "title": "Права на каталог сайта",
            "difficulty": 4,
            "points": 15,
            "task": """Apache работает от пользователя `www-data` и должен иметь права на чтение файлов.

Выставьте права и убедитесь, что сайт работает:

    sudo chmod 755 /var/www/mysite
    sudo chmod 644 /var/www/mysite/index.html
    curl http://127.0.0.1:8082/

Если каталог закрыт (например, 700), Apache не сможет зайти внутрь и ответит
`403 Forbidden` — причина будет в `/var/log/apache2/error.log`.""",
            "goals": ["Настроить права для веб-сервера", "Научиться читать 403 и error.log"],
            "hints": ["ls -ld /var/www/mysite — права на каталог",
                      "На каталоге нужен x (проход), на файле — r (чтение)",
                      "sudo tail -3 /var/log/apache2/error.log — причина отказа"],
            "solution": "sudo chmod 755 /var/www/mysite && sudo chmod 644 /var/www/mysite/index.html && curl http://127.0.0.1:8082/",
            "checks": [
                {"type": "file_mode", "path": "/var/www/mysite", "mode": "755", "title": "Права на каталог — 755"},
                {"type": "file_mode", "path": "/var/www/mysite/index.html", "mode": "644", "title": "Права на файл — 644"},
                cok("curl -s http://127.0.0.1:8082/ | grep -q 'My Apache site'", "Сайт по-прежнему работает"),
            ],
        },
        {
            "id": "m13-15",
            "title": "Коды ответов и страница 404",
            "difficulty": 4,
            "points": 15,
            "task": """Проверьте, как сервер отвечает на несуществующий адрес:

    curl -s -o /dev/null -w '%{http_code}\\n' http://127.0.0.1:8082/nope

Ожидается `404` — страница не найдена. А на существующую главную:

    curl -s -o /dev/null -w '%{http_code}\\n' http://127.0.0.1:8082/

Ожидается `200`.

Проверьте оба кода одной командой и сохраните результат в `~/apache/codes.txt`.""",
            "goals": ["Научиться читать HTTP-коды ответов", "Отличать 200, 403, 404, 500"],
            "hints": ["curl -s -o /dev/null -w '%{http_code}\\n' http://127.0.0.1:8082/nope",
                      "Коды: 200 — ок, 301 — перенаправление, 403 — запрещено, 404 — не найдено, 500 — ошибка сервера",
                      "mkdir -p ~/apache и сохраните вывод в codes.txt"],
            "solution": "mkdir -p ~/apache && { curl -s -o /dev/null -w '%{http_code}\\n' http://127.0.0.1:8082/nope; curl -s -o /dev/null -w '%{http_code}\\n' http://127.0.0.1:8082/; } > ~/apache/codes.txt",
            "checks": [
                fe("/home/student/apache/codes.txt", "Файл с кодами создан"),
                fc("/home/student/apache/codes.txt", "404", "Зафиксирован код 404"),
                fc("/home/student/apache/codes.txt", "200", "Зафиксирован код 200"),
            ],
        },
    ],
}
