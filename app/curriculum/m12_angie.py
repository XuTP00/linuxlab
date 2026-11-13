"""Модуль 12. Установка и настройка Angie — веб-сервер внутри контейнера.

Результат работы каждого задания видно во вкладке «Web 8080» второй панели.
"""
from .helpers import cok, fc, fe, fm, fl, fmode, fne, hist, out, port

MODULE = {
    "id": "m12",
    "title": "Модуль 12. Установка и настройка Angie",
    "icon": "🌐",
    "summary": "Свободный веб-сервер Angie (форк nginx): репозиторий, установка, конфигурация, виртуальные хосты и логи.",
    "tasks": [
        {
            "id": "m12-01",
            "title": "Подключаем репозиторий Angie",
            "difficulty": 4,
            "points": 20,
            "task": """Angie — свободный веб-сервер с открытым исходным кодом, созданный как форк nginx
и полностью с ним совместимый по синтаксису конфигурации.

Чтобы его установить, нужно подключить репозиторий Angie. Сделайте два шага:

1. Скачайте ключ подписи репозитория:

       sudo curl -o /etc/apt/trusted.gpg.d/angie-signing.gpg https://angie.software/keys/angie-signing.gpg

2. Добавьте источник пакетов (имя дистрибутива и кодовое имя берутся из /etc/os-release):

       echo "deb https://download.angie.software/angie/$(. /etc/os-release && echo "$ID/$VERSION_ID $VERSION_CODENAME") main" \
         | sudo tee /etc/apt/sources.list.d/angie.list

В файле `/etc/apt/sources.list.d/angie.list` должна быть строка с `download.angie.software`.""",
            "goals": ["Понять, как устроены репозитории apt", "Подключить сторонний репозиторий вместе с ключом"],
            "hints": ["Ключ кладём в /etc/apt/trusted.gpg.d/, источник — в /etc/apt/sources.list.d/",
                      "Имя дистрибутива: . /etc/os-release && echo $ID $VERSION_ID $VERSION_CODENAME",
                      "После этого обязательно: sudo apt-get update"],
            "solution": "sudo curl -o /etc/apt/trusted.gpg.d/angie-signing.gpg https://angie.software/keys/angie-signing.gpg && echo \"deb https://download.angie.software/angie/$(. /etc/os-release && echo \"$ID/$VERSION_ID $VERSION_CODENAME\") main\" | sudo tee /etc/apt/sources.list.d/angie.list",
            "checks": [
                fe("/etc/apt/trusted.gpg.d/angie-signing.gpg", "Ключ подписи скачан"),
                fe("/etc/apt/sources.list.d/angie.list", "Файл источника создан"),
                fc("/etc/apt/sources.list.d/angie.list", "download.angie.software", "В источнике указан репозиторий Angie"),
            ],
        },
        {
            "id": "m12-02",
            "title": "Обновляем индексы и ставим Angie",
            "difficulty": 3,
            "points": 15,
            "task": """Теперь пакет доступен в системе. Установите веб-сервер:

    sudo apt-get update
    sudo apt-get install -y angie

Затем посмотрите версию: `angie -v` (команда называется так же, как пакет).

В терминале должно появиться что-то вроде `Angie version: Angie/1.12.4`.""",
            "goals": ["Установить пакет из подключённого репозитория", "Узнать версию установленного сервера"],
            "hints": ["sudo apt-get update — обновить индексы, без этого пакет не найдётся",
                      "sudo apt-get install -y angie",
                      "Бинарник лежит в /usr/sbin/angie"],
            "solution": "sudo apt-get update && sudo apt-get install -y angie && angie -v",
            "checks": [
                cok("command -v angie >/dev/null 2>&1", "Программа angie установлена"),
                cok("dpkg -s angie >/dev/null 2>&1", "Пакет angie установлен через apt"),
                out("Angie version", "В терминале показана версия Angie"),
            ],
        },
        {
            "id": "m12-03",
            "title": "Смотрим, как устроен конфиг",
            "difficulty": 3,
            "points": 15,
            "task": """Посмотрите основной конфигурационный файл Angie:

    cat /etc/angie/angie.conf

В нём есть блоки `user`, `worker_processes`, `events`, `http` и строка
`include /etc/angie/http.d/*.conf;` — все файлы из каталога `/etc/angie/http.d/`
подключаются автоматически.

Также посмотрите готовый виртуальный хост: `cat /etc/angie/http.d/default.conf`.""",
            "goals": ["Понять структуру конфигурации Angie", "Узнать, где лежат виртуальные хосты"],
            "hints": ["cat /etc/angie/angie.conf", "ls /etc/angie/http.d/",
                      "Конфигурация Angie синтаксически совместима с nginx"],
            "solution": "cat /etc/angie/angie.conf && ls /etc/angie/http.d/",
            "checks": [
                hist("/etc/angie/angie.conf", "Открыли основной конфиг"),
                out("worker_processes", "Виден блок worker_processes"),
                out("http.d", "Виден путь подключения виртуальных хостов"),
            ],
        },
        {
            "id": "m12-04",
            "title": "Готовим каталог сайта",
            "difficulty": 2,
            "points": 15,
            "task": """Создайте каталог сайта `/var/www/site` и в нём главную страницу `index.html`
с одной строкой:

    <h1>Hello from Angie</h1>

Каталог `/var/www` — стандартное место для сайтов. Файл `index.html` — стандартное
имя главной страницы: сервер отдаёт её автоматически при запросе `/`.""",
            "goals": ["Создать структуру сайта", "Понять роль index.html и каталога /var/www"],
            "hints": ["sudo mkdir -p /var/www/site",
                      "echo '<h1>Hello from Angie</h1>' | sudo tee /var/www/site/index.html",
                      "Права: каталог 755, файл 644 — чтобы сервер мог их читать"],
            "solution": "sudo mkdir -p /var/www/site && echo '<h1>Hello from Angie</h1>' | sudo tee /var/www/site/index.html",
            "checks": [
                fe("/var/www/site/index.html", "Главная страница создана"),
                fc("/var/www/site/index.html", "Hello from Angie", "Содержимое страницы верное"),
                cok("test -d /var/www/site", "Каталог сайта существует"),
            ],
        },
        {
            "id": "m12-05",
            "title": "Пишем свой виртуальный хост",
            "difficulty": 4,
            "points": 20,
            "task": """Опишите сайт в отдельном файле `/etc/angie/http.d/site.conf`:

    server {
        listen 8080;
        server_name lab.local;
        root /var/www/site;
        index index.html;
    }

Смысл директив:
* `listen 8080` — какой порт слушаем (8080 — чтобы не конфликтовать с другим сайтом);
* `server_name` — доменное имя, по которому приходят запросы;
* `root` — каталог с файлами сайта;
* `index` — имя файла главной страницы.

Создайте файл через `sudo tee`.""",
            "goals": ["Написать первый server-блок", "Понять директивы listen, server_name, root, index"],
            "hints": ["sudo tee /etc/angie/http.d/site.conf — вводите блок и завершайте Ctrl+D",
                      "Проверить, что файл подхватится: sudo angie -t",
                      "Директива root указывает на каталог, а не на файл"],
            "solution": "printf 'server {\\n    listen 8080;\\n    server_name lab.local;\\n    root /var/www/site;\\n    index index.html;\\n}\\n' | sudo tee /etc/angie/http.d/site.conf",
            "checks": [
                fe("/etc/angie/http.d/site.conf", "Файл виртуального хоста создан"),
                fc("/etc/angie/http.d/site.conf", "listen 8080", "Указан порт 8080"),
                fc("/etc/angie/http.d/site.conf", "root /var/www/site", "Указан каталог сайта"),
            ],
        },
        {
            "id": "m12-06",
            "title": "Проверяем конфигурацию",
            "difficulty": 3,
            "points": 15,
            "task": """Прежде чем перезапускать сервер, конфигурацию нужно проверить — это спасёт от падения:

    sudo angie -t

Ожидаемый ответ:

    angie: the configuration file /etc/angie/angie.conf syntax is ok
    angie: configuration file /etc/angie/angie.conf test is successful

Ключ `-t` (test) только проверяет конфиг и ничего не запускает.""",
            "goals": ["Проверять конфигурацию перед применением", "Понять, зачем нужен ключ -t"],
            "hints": ["sudo angie -t", "Если ошибка — покажет строку с проблемой",
                      "Аналог в nginx: nginx -t"],
            "solution": "sudo angie -t",
            "checks": [
                hist("angie -t", "Проверили конфигурацию"),
                out("syntax is ok", "Синтаксис корректен"),
                out("test is successful", "Тест конфигурации пройден"),
            ],
        },
        {
            "id": "m12-07",
            "title": "Запускаем Angie",
            "difficulty": 3,
            "points": 15,
            "task": """В контейнере нет systemd, поэтому запускаем сервер вручную — в фоне:

    sudo angie

После запуска появятся главный процесс и рабочие процессы. Проверьте: `pgrep -a angie`.

Сервер должен слушать порт 8080: `ss -tuln | grep 8080`.

**Важно:** вместе с пакетом Angie ставится стандартный сайт, который слушает порт 80
(`/etc/angie/http.d/default.conf`). Мы его не используем — отключим, чтобы порт 80
остался свободным для других серверов:

    sudo rm /etc/angie/http.d/default.conf

**Если Angie не стартует** с ошибкой `bind() to 0.0.0.0:8080 failed (98: Address already in use)`,
найдите процесс и освободите порт:

    ss -tulnp | grep ':8080 ' | grep -o 'pid=[0-9]*' | cut -d= -f2 | xargs -r sudo kill

и запустите Angie снова.""",
            "goals": ["Запустить веб-сервер вручную", "Увидеть процессы мастера и воркеров", "Отключить стандартный сайт, освободив порт 80"],
            "hints": ["sudo angie — запустить демоном (по умолчанию он уходит в фон)",
                      "pgrep -a angie — список процессов",
                      "Кто занял порт: ss -tulnp | grep 8080, освободить: ss -tulnp | grep ':8080 ' | grep -o 'pid=[0-9]*' | cut -d= -f2 | xargs -r sudo kill",
                      "Остановить сервер: sudo angie -s stop"],
            "solution": "sudo rm -f /etc/angie/http.d/default.conf; ss -tulnp | grep ':8080 ' | grep -o 'pid=[0-9]*' | cut -d= -f2 | xargs -r sudo kill; sleep 1; sudo angie && sleep 1 && pgrep -a angie && ss -tuln | grep 8080",
            "checks": [
                cok("pgrep -x angie >/dev/null 2>&1", "Процесс Angie запущен"),
                port(8080, "Порт 8080 слушается"),
                cok("! ss -tuln | grep -q ':80 '", "Порт 80 свободен (стандартный сайт отключён)"),
            ],
        },
        {
            "id": "m12-08",
            "title": "Сайт отвечает",
            "difficulty": 3,
            "points": 15,
            "task": """Проверьте сайт из консоли:

    curl http://127.0.0.1:8080

В ответ должен прийти HTML нашей страницы: `<h1>Hello from Angie</h1>`.

Посмотрите и заголовки ответа: `curl -I http://127.0.0.1:8080` — среди них будет
`Server: Angie/1.12.4`.""",
            "goals": ["Обратиться к сайту по HTTP", "Научиться читать заголовки ответа"],
            "hints": ["curl http://127.0.0.1:8080", "curl -I — только заголовки ответа",
                      "Тот же адрес откройте во вкладке «Web 8080» справа"],
            "solution": "curl http://127.0.0.1:8080 && curl -I http://127.0.0.1:8080",
            "checks": [
                cok("curl -s http://127.0.0.1:8080 | grep -q 'Hello from Angie'", "Сайт отдаёт нужную страницу"),
                out("Server: Angie", "В заголовках ответа указан сервер Angie"),
            ],
        },
        {
            "id": "m12-09",
            "title": "Смотрим результат во вкладке «Web 8080»",
            "difficulty": 2,
            "points": 10,
            "task": """Справа, в панели с терминалом, есть вкладки. Переключитесь на вкладку
**«Web 8080»** — там встроенный браузер показывает сайт, который отдаёт ваш Angie
из контейнера.

Убедитесь, что на странице виден ваш заголовок «Hello from Angie».

После этого проверьте код ответа в консоли:

    curl -sI http://127.0.0.1:8080 | head -1

Ожидается строка `HTTP/1.1 200 OK`.""",
            "goals": ["Понять, как сайт из контейнера показывается в интерфейсе", "Проверить код ответа"],
            "hints": ["Вкладка «Web 8080» — это предпросмотр сайта из вашего контейнера",
                      "Если страница пустая — нажмите «Обновить» на вкладке",
                      "Код ответа: curl -sI http://127.0.0.1:8080 | head -1"],
            "solution": "curl -sI http://127.0.0.1:8080 | head -1",
            "checks": [
                out("200 OK", "Получен код ответа 200 OK"),
                hist("127.0.0.1:8080", "Обратились к сайту в контейнере"),
            ],
        },
        {
            "id": "m12-10",
            "title": "Логи доступа",
            "difficulty": 4,
            "points": 20,
            "task": """Добавьте в свой конфиг `/etc/angie/http.d/site.conf` логи:

    access_log /var/log/angie/access.log;
    error_log  /var/log/angie/error.log;

(внутри блока `server { ... }`).

Затем перезапустите сервер, сделайте несколько запросов (`curl http://127.0.0.1:8080`)
и посмотрите журнал:

    sudo tail -5 /var/log/angie/access.log

В журнале будут строки вида `127.0.0.1 - - [дата] "GET / HTTP/1.1" 200 ...`.""",
            "goals": ["Настроить журналы доступа и ошибок", "Понять формат записи в access.log"],
            "hints": ["Директивы access_log и error_log размещаются внутри блока server",
                      "Каталог /var/log/angie/ создаётся пакетом автоматически",
                      "После правки конфига: sudo angie -s reload"],
            "solution": "printf 'server {\\n    listen 8080;\\n    server_name lab.local;\\n    root /var/www/site;\\n    index index.html;\\n    access_log /var/log/angie/access.log;\\n    error_log /var/log/angie/error.log;\\n}\\n' | sudo tee /etc/angie/http.d/site.conf && sudo angie -s reload && sleep 1 && curl -s http://127.0.0.1:8080 >/dev/null && sudo tail -3 /var/log/angie/access.log",
            "checks": [
                fc("/etc/angie/http.d/site.conf", "access_log", "Включён access_log"),
                fe("/var/log/angie/access.log", "Журнал доступа создан"),
                fc("/var/log/angie/access.log", "GET /", "В журнале есть запись о запросе"),
            ],
        },
        {
            "id": "m12-11",
            "title": "Статика: стили и картинки",
            "difficulty": 4,
            "points": 20,
            "task": """Добавьте на сайт файл стилей `/var/www/site/style.css` с любым правилом
(например, `body { color: #2b6cb0; }`) и подключите его в `index.html`
(добавьте в начало файла строку `<link rel="stylesheet" href="/style.css">`).

Проверьте, что сервер отдаёт CSS:

    curl http://127.0.0.1:8080/style.css

Ссылка в HTML начинается с `/`, поэтому работает как «путь от корня сайта» — именно
для этого в конфиге указан `root`.""",
            "goals": ["Подключить статические ресурсы к странице", "Понять разницу между абсолютным и относительным путём"],
            "hints": ["Путь в ссылке начинается с / — это корень сайта (каталог root)",
                      "Проверить: curl -s http://127.0.0.1:8080/style.css",
                      "Файлы .css отдаются сервером как статика (Content-Type: text/css)"],
            "solution": "echo 'body { color: #2b6cb0; }' | sudo tee /var/www/site/style.css && sudo sed -i '1i <link rel=\"stylesheet\" href=\"/style.css\">' /var/www/site/index.html && curl -s http://127.0.0.1:8080/style.css",
            "checks": [
                fe("/var/www/site/style.css", "Файл стилей создан"),
                fc("/var/www/site/index.html", "style.css", "Стили подключены в страницу"),
                cok("curl -s http://127.0.0.1:8080/style.css | grep -q 'body'", "Сервер отдаёт CSS-файл"),
            ],
        },
        {
            "id": "m12-12",
            "title": "Второй виртуальный хост",
            "difficulty": 5,
            "points": 20,
            "task": """На одном сервере может работать много сайтов. Добавьте второй:

1. Создайте каталог `/var/www/site2` с `index.html`, содержащим строку `Second site`.
2. Создайте `/etc/angie/http.d/site2.conf`:

       server {
           listen 8081;
           server_name lab.local;
           root /var/www/site2;
           index index.html;
       }

3. Перезагрузите сервер: `sudo angie -s reload`
4. Проверьте: `curl http://127.0.0.1:8081`""",
            "goals": ["Настроить несколько виртуальных хостов на разных портах", "Понять, что каждому server-блоку соответствует свой root"],
            "hints": ["Каждый server-блок — отдельный сайт",
                      "Не забудьте sudo angie -s reload после правки конфига",
                      "Проверка: curl http://127.0.0.1:8081"],
            "solution": "sudo mkdir -p /var/www/site2 && echo 'Second site' | sudo tee /var/www/site2/index.html && printf 'server {\\n    listen 8081;\\n    server_name lab.local;\\n    root /var/www/site2;\\n    index index.html;\\n}\\n' | sudo tee /etc/angie/http.d/site2.conf && sudo angie -s reload && sleep 1 && curl -s http://127.0.0.1:8081",
            "checks": [
                fe("/etc/angie/http.d/site2.conf", "Конфиг второго хоста создан"),
                fc("/etc/angie/http.d/site2.conf", "listen 8081", "Второй сайт слушает 8081"),
                cok("curl -s http://127.0.0.1:8081 | grep -q 'Second site'", "Второй сайт отвечает"),
            ],        },
        {
            "id": "m12-13",
            "title": "Горячая перезагрузка",
            "difficulty": 4,
            "points": 20,
            "task": """Сервер можно перечитать конфигурацию, не останавливая его:

    sudo angie -s reload

Сделайте так, чтобы правка была видна сразу:

1. Добавьте в `/var/www/site/index.html` строку с маркером `version-2`
   (например, `<p>version-2</p>`).
2. Выполните `sudo angie -s reload`.
3. Убедитесь, что изменения видны: `curl http://127.0.0.1:8080`.

Вкладка «Web 8080» справа тоже покажет обновлённую страницу (нажмите «Обновить»).""",
            "goals": ["Научиться применять конфигурацию без остановки сервера", "Понять разницу между reload и restart"],
            "hints": ["sudo angie -s reload — перечитать конфигурацию, старые соединения не рвутся",
                      "sudo angie -s stop — полностью остановить сервер",
                      "Проверка: curl http://127.0.0.1:8080 | grep version-2"],
            "solution": "echo '<p>version-2</p>' | sudo tee -a /var/www/site/index.html && sudo angie -s reload && sleep 1 && curl -s http://127.0.0.1:8080",
            "checks": [
                fc("/var/www/site/index.html", "version-2", "Маркер добавлен в страницу"),
                cok("curl -s http://127.0.0.1:8080 | grep -q 'version-2'", "Сервер отдаёт обновлённую страницу"),
                hist("angie -s reload", "Конфигурация перечитана без остановки сервера"),
            ],
        },
        {
            "id": "m12-14",
            "title": "Права доступа к сайту",
            "difficulty": 4,
            "points": 15,
            "task": """Сервер работает от отдельного пользователя (в пакете Angie — `www-data`)
и должен иметь права на чтение файлов сайта.

Проверьте и выставьте правильные права:

    sudo chmod 755 /var/www/site
    sudo chmod 644 /var/www/site/index.html

Убедитесь, что сайт всё ещё отвечает: `curl http://127.0.0.1:8080`.

Если бы права были закрыты, в журнале ошибок появилась бы запись `Permission denied`.""",
            "goals": ["Понять, почему серверу нужны права на файлы сайта", "Настроить корректные права"],
            "hints": ["Каталог — 755 (можно зайти и прочитать), файл — 644 (можно прочитать)",
                      "Проверить: ls -l /var/www/site",
                      "Ошибки доступа смотрите в /var/log/angie/error.log"],
            "solution": "sudo chmod 755 /var/www/site && sudo chmod 644 /var/www/site/index.html && curl -s http://127.0.0.1:8080",
            "checks": [
                fmode("/var/www/site", "755", "Права на каталог сайта — 755"),
                fmode("/var/www/site/index.html", "644", "Права на файл — 644"),
                cok("curl -s http://127.0.0.1:8080 | grep -q 'Hello from Angie'", "Сайт по-прежнему отвечает"),
            ],
        },
    ],
}
