"""Модуль 7. Сеть, DNS и SSH."""
from .helpers import cok, fc, fe, fm, fne, fnc, hist, port

MODULE = {
    "id": "m8",
    "title": "Модуль 8. Сеть, DNS и SSH",
    "icon": "🌐",
    "summary": "Как Linux общается с сетью: интерфейсы, маршруты, порты, curl/wget, DNS и ключи SSH.",
    "tasks": [
        {
            "id": "m8-01",
            "title": "Сетевые интерфейсы",
            "difficulty": 3,
            "points": 10,
            "task": """Посмотрите список сетевых интерфейсов и их адреса (`ip addr` или `ip a`) и сохраните вывод в `~/net/addr.txt`.

В выводе должны быть интерфейсы `lo` (loopback) и `eth0`.""",
            "goals": ["Интерфейсы и IP-адреса", "ip addr против ifconfig"],
            "hints": ["mkdir -p ~/net", "ip a", "ip a > ~/net/addr.txt", "Современная замена ifconfig и route"],
            "solution": "mkdir -p ~/net && ip a > ~/net/addr.txt",
            "checks": [
                fc("/home/student/net/addr.txt", "lo", "Есть loopback-интерфейс"),
                fc("/home/student/net/addr.txt", "eth0", "Есть основной интерфейс"),
            ],
        },
        {
            "id": "m8-02",
            "title": "Маршруты",
            "difficulty": 3,
            "points": 10,
            "task": """Посмотрите таблицу маршрутизации (`ip route`) и сохраните вывод в `~/net/route.txt`.

В выводе должна быть строка маршрута по умолчанию (`default`).""",
            "goals": ["Куда идёт трафик", "Шлюз по умолчанию"],
            "hints": ["ip route", "ip route > ~/net/route.txt", "default via 172.17.0.1 — шлюз docker"],
            "solution": "mkdir -p ~/net && ip route > ~/net/route.txt",
            "checks": [
                fc("/home/student/net/route.txt", "default", "Есть маршрут по умолчанию"),
            ],
        },
        {
            "id": "m8-03",
            "title": "ping: проверяем доступность",
            "difficulty": 3,
            "points": 15,
            "task": """Проверьте доступность самого себя командой `ping -c 3 127.0.0.1` и сохраните вывод в `~/net/ping.txt`.

В выводе должны быть строки про `3 packets` и `0% packet loss`.""",
            "goals": ["Диагностика сети", "ping и его параметры"],
            "hints": ["ping -c 3 127.0.0.1", "ping -c 3 127.0.0.1 > ~/net/ping.txt", "-c ограничивает число пакетов, Ctrl+C прерывает бесконечный ping"],
            "solution": "mkdir -p ~/net && ping -c 3 127.0.0.1 > ~/net/ping.txt 2>&1",
            "checks": [
                fc("/home/student/net/ping.txt", "3 packets", "Отправлено 3 пакета"),
                fc("/home/student/net/ping.txt", "0% packet loss", "Потерь нет"),
            ],
        },
        {
            "id": "m8-04",
            "title": "Свой веб-сервер",
            "difficulty": 4,
            "points": 20,
            "task": """Поднимите в фоне простейший веб-сервер:

1. Создайте `~/site/index.html` с текстом `Hello from local server`.
2. Запустите в фоне `python3 -m http.server 8080 --directory ~/site`.
3. Скачайте страницу командой `curl http://127.0.0.1:8080` в файл `~/net/local.html`.""",
            "goals": ["Локальный сервер", "Обращение к нему по HTTP", "Работа с портами"],
            "hints": ["mkdir -p ~/site && echo 'Hello from local server' > ~/site/index.html", "python3 -m http.server 8080 --directory ~/site &", "curl -s http://127.0.0.1:8080 > ~/net/local.html"],
            "solution": "mkdir -p ~/site ~/net && echo 'Hello from local server' > ~/site/index.html && (python3 -m http.server 8080 --directory ~/site >/dev/null 2>&1 &) && sleep 1 && curl -s http://127.0.0.1:8080 > ~/net/local.html",
            "checks": [
                fc("/home/student/site/index.html", "Hello from local server", "index.html создан"),
                fc("/home/student/net/local.html", "Hello from local server", "curl получил страницу"),
                port(8080, "Порт 8080 слушается"),
            ],
        },
        {
            "id": "m8-05",
            "title": "Кто слушает порты?",
            "difficulty": 4,
            "points": 15,
            "task": """Посмотрите, какие порты слушаются в системе (`ss -tuln` или `ss -ltnp`), и сохраните вывод в `~/net/ss.txt`.

В выводе должен быть порт `8080` (сервер из прошлого задания всё ещё работает).""",
            "goals": ["Активные сокеты", "netstat vs ss"],
            "hints": ["ss -tuln", "ss -tuln > ~/net/ss.txt", "-t — TCP, -u — UDP, -l — слушающие, -n — числовые порты"],
            "solution": "ss -tuln > ~/net/ss.txt",
            "checks": [
                fc("/home/student/net/ss.txt", "8080", "Порт 8080 виден в списке"),
                fne("/home/student/net/ss.txt", "Вывод непустой"),
            ],
        },
        {
            "id": "m8-06",
            "title": "curl: скачиваем страницу",
            "difficulty": 3,
            "points": 15,
            "task": """Скачайте страницу `http://example.com` утилитой `curl` и сохраните её в `~/net/example.html`.

В файле должно быть слово `Example`.""",
            "goals": ["Работа с HTTP из командной строки", "curl -s и -o"],
            "hints": ["curl -s http://example.com -o ~/net/example.html", "curl -s http://example.com > ~/net/example.html", "Ключ -o сохраняет вывод прямо в файл"],
            "solution": "curl -s http://example.com -o ~/net/example.html",
            "checks": [
                fe("/home/student/net/example.html", "Страница сохранена"),
                fc("/home/student/net/example.html", "Example", "В странице есть слово Example"),
            ],
        },
        {
            "id": "m8-07",
            "title": "wget: альтернатива curl",
            "difficulty": 3,
            "points": 15,
            "task": """Скачайте тот же `http://example.com` утилитой `wget` в файл `~/net/wget.html`.

`wget` умеет качать «как браузер» и создаёт лог загрузки.""",
            "goals": ["wget и его ключи", "Сравнение с curl"],
            "hints": ["wget -q -O ~/net/wget.html http://example.com", "wget -O — имя выходного файла, -q — тихий режим"],
            "solution": "wget -q -O ~/net/wget.html http://example.com",
            "checks": [
                fe("/home/student/net/wget.html", "Файл создан wget"),
                fc("/home/student/net/wget.html", "Example", "Содержимое скачано верно"),
            ],
        },
        {
            "id": "m8-08",
            "title": "DNS: имя → адрес",
            "difficulty": 4,
            "points": 15,
            "task": """Узнайте IP-адрес по имени `example.com` (например, `getent hosts example.com` или `dig example.com`) и сохраните вывод в `~/net/dns.txt`.""",
            "goals": ["Как работает разрешение имён", "getent и dig"],
            "hints": ["getent hosts example.com", "getent hosts example.com > ~/net/dns.txt", "В файле /etc/resolv.conf записаны DNS-серверы"],
            "solution": "getent hosts example.com > ~/net/dns.txt",
            "checks": [
                fc("/home/student/net/dns.txt", "example.com", "Имя разрешено в адрес"),
                fm("/home/student/net/dns.txt", r"\d+\.\d+\.\d+\.\d+", "Найден IP-адрес"),
            ],
        },
        {
            "id": "m8-09",
            "title": "Файл /etc/hosts",
            "difficulty": 4,
            "points": 20,
            "task": """Добавьте в `/etc/hosts` строку, которая сопоставляет имя `lab.local` с адресом `127.0.0.1`.

Используйте `sudo` и допишите строку в конец файла (например, через `sudo tee -a`).""",
            "goals": ["Локальные DNS-записи", "Права на системные файлы"],
            "hints": ["echo '127.0.0.1 lab.local' | sudo tee -a /etc/hosts", "cat /etc/hosts", "После этого ping lab.local будет работать"],
            "solution": "echo '127.0.0.1 lab.local' | sudo tee -a /etc/hosts",
            "checks": [
                fc("/etc/hosts", "lab.local", "Запись добавлена в /etc/hosts"),
                fc("/etc/hosts", "127.0.0.1", "Указан правильный адрес"),
            ],
        },
        {
            "id": "m8-10",
            "title": "SSH-ключи и вход по ssh",
            "difficulty": 5,
            "points": 25,
            "task": """Настройте вход по SSH в этот же компьютер по ключу:

1. Сгенерируйте ключ: `ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519`
2. Добавьте публичный ключ в `~/.ssh/authorized_keys`
3. Подключитесь к себе: `ssh -o StrictHostKeyChecking=no student@localhost 'hostname'`

Сохраните результат подключения в `~/net/ssh.txt` — там должно быть имя хоста (например, `lab`).""",
            "goals": ["Асимметричная криптография", "Авторизация по ключу", "Команда ssh"],
            "hints": ["ssh-keygen -t ed25519 -N '' -f ~/.ssh/id_ed25519", "cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys; chmod 600 ~/.ssh/authorized_keys", "ssh -o StrictHostKeyChecking=no student@localhost hostname > ~/net/ssh.txt"],
            "solution": "mkdir -p ~/.ssh && ssh-keygen -t ed25519 -N '' -f ~/.ssh/id_ed25519 && cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys && ssh -o StrictHostKeyChecking=no student@localhost hostname > ~/net/ssh.txt",
            "checks": [
                fe("/home/student/.ssh/id_ed25519", "Приватный ключ создан"),
                fe("/home/student/.ssh/authorized_keys", "authorized_keys заполнен"),
                fne("/home/student/net/ssh.txt", "SSH-подключение выполнено (вывод непустой)"),
                fnc("/home/student/net/ssh.txt", "Permission denied", "Ошибки доступа нет"),
                fnc("/home/student/net/ssh.txt", "connect to host", "Соединение установлено"),
            ],
        },
        {
            "id": "m8-11",
            "title": "scp: копируем по сети",
            "difficulty": 5,
            "points": 20,
            "task": """Скопируйте файл `~/note.txt` на этот же хост по SSH в `~/net/remote_copy.txt`:

    scp -o StrictHostKeyChecking=no ~/note.txt student@localhost:~/net/remote_copy.txt

Убедитесь, что файл появился и содержит `Hello Linux`.""",
            "goals": ["Копирование файлов по сети", "scp"],
            "hints": ["scp -o StrictHostKeyChecking=no ~/note.txt student@localhost:~/net/remote_copy.txt", "cat ~/net/remote_copy.txt"],
            "solution": "scp -o StrictHostKeyChecking=no ~/note.txt student@localhost:~/net/remote_copy.txt",
            "checks": [
                fe("/home/student/net/remote_copy.txt", "Файл скопирован"),
                fne("/home/student/net/remote_copy.txt", "Скопированный файл не пуст"),
            ],
        },
        {
            "id": "m8-12",
            "title": "nc: проверяем порт",
            "difficulty": 5,
            "points": 20,
            "task": """Проверьте утилитой `netcat`, что порт 8080 открыт, и сохраните вывод в `~/net/nc.txt`.

Запустите проверку так: `nc -zv 127.0.0.1 8080` (сервер из задания про веб-сервер должен ещё работать; если нет — запустите его заново).""",
            "goals": ["Проверка доступности порта", "netcat как диагностика"],
            "hints": ["nc -zv 127.0.0.1 8080", "nc -zv 127.0.0.1 8080 > ~/net/nc.txt 2>&1", "Ключ -z — не передавать данные, -v — подробно"],
            "solution": "nc -zv 127.0.0.1 8080 > ~/net/nc.txt 2>&1",
            "checks": [
                fne("/home/student/net/nc.txt", "Вывод непустой"),
                fc("/home/student/net/nc.txt", "8080", "Упомянут порт 8080"),
            ],
        },
    ],
}
