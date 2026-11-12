"""Модуль 9. Пакеты, systemd, cron и системные журналы."""
from .helpers import cok, fc, fe, fm, fne, cron

MODULE = {
    "id": "m10",
    "title": "Модуль 10. Пакеты, systemd, cron, логи",
    "icon": "📦",
    "summary": "Как устроена ОС: пакетный менеджер, юниты systemd, планировщик cron и журналы.",
    "tasks": [
        {
            "id": "m10-01",
            "title": "Список установленных пакетов",
            "difficulty": 3,
            "points": 10,
            "task": """Посмотрите список установленных пакетов (`dpkg -l`) и сохраните его в `~/sys/dpkg.txt`.

В списке должен быть пакет `bash`.""",
            "goals": ["Менеджер пакетов dpkg", "Формат вывода dpkg -l"],
            "hints": ["mkdir -p ~/sys", "dpkg -l > ~/sys/dpkg.txt", "dpkg — низкоуровневый менеджер Debian/Ubuntu"],
            "solution": "mkdir -p ~/sys && dpkg -l > ~/sys/dpkg.txt",
            "checks": [
                fc("/home/student/sys/dpkg.txt", "bash", "Пакет bash в списке"),
                fc("/home/student/sys/dpkg.txt", "coreutils", "Пакет coreutils в списке"),
            ],
        },
        {
            "id": "m10-02",
            "title": "Кто поставил этот файл?",
            "difficulty": 4,
            "points": 15,
            "task": """Узнайте, какому пакету принадлежит файл `/bin/ls` (или `/usr/bin/ls`), и сохраните ответ в `~/sys/pkg.txt`.

Сделайте это командой `dpkg -S`.""",
            "goals": ["Связь файлов и пакетов", "dpkg -S и dpkg -L"],
            "hints": ["dpkg -S /usr/bin/ls", "Обратная операция: dpkg -L bash — какие файлы у пакета"],
            "solution": "dpkg -S /usr/bin/ls > ~/sys/pkg.txt 2>&1",
            "checks": [
                fc("/home/student/sys/pkg.txt", "coreutils", "Файл принадлежит пакету coreutils"),
            ],
        },
        {
            "id": "m10-03",
            "title": "apt: состояние пакетов",
            "difficulty": 4,
            "points": 15,
            "task": """Посмотрите список пакетов через `apt list --installed` и сохраните первые строки в `~/sys/apt.txt`.

В файле должны встречаться `bash` и `coreutils`.""",
            "goals": ["Высокоуровневый apt поверх dpkg", "Фильтрация вывода"],
            "hints": ["apt list --installed | head -30 > ~/sys/apt.txt", "apt list --installed | grep -c '' — сколько всего пакетов"],
            "solution": "apt list --installed | head -40 > ~/sys/apt.txt",
            "checks": [
                fc("/home/student/sys/apt.txt", "bash", "bash в списке apt"),
                fc("/home/student/sys/apt.txt", "coreutils", "coreutils в списке apt"),
            ],
        },
        {
            "id": "m10-04",
            "title": "Установка пакета",
            "difficulty": 4,
            "points": 20,
            "task": """Установите в систему небольшой пакет и убедитесь, что он работает:

    sudo apt-get update
    sudo apt-get install -y htop
    htop --version > ~/sys/htop.txt

В `~/sys/htop.txt` должна быть строка с названием и версией программы (`htop ...`).""",
            "goals": ["Установка пакетов", "Проверка результата установки"],
            "hints": ["sudo apt-get update — обновить индексы репозиториев", "sudo apt-get install -y htop", "htop --version — проверка, что программа установилась"],
            "solution": "sudo apt-get update && sudo apt-get install -y htop && htop --version > ~/sys/htop.txt",
            "checks": [
                fe("/home/student/sys/htop.txt", "Вывод htop --version сохранён"),
                fc("/home/student/sys/htop.txt", "htop", "Версия указана"),
                cok("dpkg -s htop >/dev/null 2>&1", "Пакет htop установлен"),
            ],
        },
        {
            "id": "m10-05",
            "title": "Задание cron",
            "difficulty": 4,
            "points": 15,
            "task": """Добавьте себе задание cron, которое каждую минуту дописывает дату в файл `~/sys/cron.log`:

    * * * * * /bin/date >> /home/student/sys/cron.log

Отредактируйте расписание через `crontab -e` (в редакторе nano: Ctrl+O — сохранить, Ctrl+X — выйти) и проверьте `crontab -l`.""",
            "goals": ["Планировщик cron", "Формат записи: минуты часы дни месяцы дни_недели команда"],
            "hints": ["crontab -e", "Строка должна начинаться с '* * * * *'", "crontab -l — посмотреть свои задания"],
            "solution": "(crontab -l 2>/dev/null; echo '* * * * * /bin/date >> /home/student/sys/cron.log') | crontab -",
            "checks": [
                cron("* * * * *", "Задание с расписанием каждую минуту найдено"),
                cron("/home/student/sys/cron.log", "Задание пишет в нужный файл"),
            ],
        },
        {
            "id": "m10-06",
            "title": "Cron действительно выполняется",
            "difficulty": 5,
            "points": 20,
            "task": """Убедитесь, что задание cron из прошлого шага реально работает: дождитесь выполнения и проверьте, что файл `~/sys/cron.log` появился и содержит дату.

В контейнере демон cron запущен, поэтому задание сработает в течение минуты.""",
            "goals": ["Проверка работы задания по расписанию", "Терпение и наблюдение"],
            "hints": ["ls -l ~/sys/cron.log", "cat ~/sys/cron.log", "Если файла нет — проверьте crontab -l и дайте минуту пройти"],
            "solution": "sleep 70 && cat ~/sys/cron.log",
            "checks": [
                {"type": "file_exists_wait", "path": "/home/student/sys/cron.log", "timeout": 90, "title": "Файл cron.log появился (задание отработало)"},
                fne("/home/student/sys/cron.log", "Файл не пуст"),
            ],
        },
        {
            "id": "m10-07",
            "title": "Пишем unit systemd",
            "difficulty": 5,
            "points": 20,
            "task": """Создайте unit-файл `/etc/systemd/system/lab-demo.service` с таким содержимым:

    [Unit]
    Description=LinuxLab demo service
    After=network.target

    [Service]
    Type=oneshot
    ExecStart=/bin/true

    [Install]
    WantedBy=multi-user.target

Создайте его через `sudo tee`.""",
            "goals": ["Структура unit-файла systemd", "Секции Unit, Service, Install"],
            "hints": ["sudo tee /etc/systemd/system/lab-demo.service << 'EOF' ... EOF", "Файлы сервисов лежат в /etc/systemd/system"],
            "solution": "printf '[Unit]\\nDescription=LinuxLab demo service\\nAfter=network.target\\n\\n[Service]\\nType=oneshot\\nExecStart=/bin/true\\n\\n[Install]\\nWantedBy=multi-user.target\\n' | sudo tee /etc/systemd/system/lab-demo.service",
            "checks": [
                fe("/etc/systemd/system/lab-demo.service", "Unit-файл создан"),
                fc("/etc/systemd/system/lab-demo.service", "[Unit]", "Есть секция [Unit]"),
                fc("/etc/systemd/system/lab-demo.service", "[Service]", "Есть секция [Service]"),
                fc("/etc/systemd/system/lab-demo.service", "ExecStart=", "Задан ExecStart"),
            ],
        },
        {
            "id": "m10-08",
            "title": "Проверяем unit",
            "difficulty": 5,
            "points": 20,
            "task": """Проверьте корректность unit-файла командой `systemd-analyze verify` и сохраните вывод в `~/sys/verify.txt`.

Команда должна завершиться без ошибок.""",
            "goals": ["Диагностика unit-файлов", "systemd-analyze verify"],
            "hints": ["sudo systemd-analyze verify /etc/systemd/system/lab-demo.service", "systemd-analyze verify /etc/systemd/system/lab-demo.service > ~/sys/verify.txt 2>&1; echo $?"],
            "solution": "systemd-analyze verify /etc/systemd/system/lab-demo.service > ~/sys/verify.txt 2>&1",
            "checks": [
                fe("/home/student/sys/verify.txt", "Вывод сохранён"),
                cok("systemd-analyze verify /etc/systemd/system/lab-demo.service >/dev/null 2>&1", "Unit-файл проходит проверку"),
            ],
        },
        {
            "id": "m10-09",
            "title": "Тайна в /etc/shadow",
            "difficulty": 4,
            "points": 15,
            "task": """Посмотрите права и содержимое (структуру) файла `/etc/shadow` — сохраните вывод `sudo ls -l /etc/shadow` в `~/sys/shadow.txt`.

В файле должны быть видны владелец `root`, группа `shadow` и дата изменения.""",
            "goals": ["Почему пароли хранятся отдельно", "Права 640 на shadow"],
            "hints": ["sudo ls -l /etc/shadow > ~/sys/shadow.txt", "Файл читает только root и группа shadow"],
            "solution": "sudo ls -l /etc/shadow > ~/sys/shadow.txt",
            "checks": [
                fc("/home/student/sys/shadow.txt", "root", "Владелец root"),
                fc("/home/student/sys/shadow.txt", "shadow", "Группа shadow"),
            ],
        },
        {
            "id": "m10-10",
            "title": "Настройки DNS-резолвера",
            "difficulty": 4,
            "points": 15,
            "task": """Посмотрите, какие DNS-серверы использует система (`cat /etc/resolv.conf`), и сохраните вывод в `~/sys/resolv.txt`.

В файле должна быть строка `nameserver`.""",
            "goals": ["Где хранится конфигурация DNS", "resolv.conf"],
            "hints": ["cat /etc/resolv.conf > ~/sys/resolv.txt", "Файл может быть символической ссылкой на systemd-resolved"],
            "solution": "cat /etc/resolv.conf > ~/sys/resolv.txt",
            "checks": [
                fc("/home/student/sys/resolv.txt", "nameserver", "Есть строка nameserver"),
            ],
        },
        {
            "id": "m10-11",
            "title": "Время и часовой пояс",
            "difficulty": 3,
            "points": 10,
            "task": """Узнайте текущие дату, время и часовой пояс (`date`, `date +%Z`) и сохраните в `~/sys/date.txt`.""",
            "goals": ["Работа со временем в системе", "Форматы date"],
            "hints": ["date", "date +%Z — только часовой пояс", "date '+%F %T' — 2026-01-01 10:00:00"],
            "solution": "date > ~/sys/date.txt && date +%Z >> ~/sys/date.txt",
            "checks": [
                fne("/home/student/sys/date.txt", "Вывод непустой"),
                fm("/home/student/sys/date.txt", r"\d{4}", "Есть год"),
            ],
        },
        {
            "id": "m10-12",
            "title": "Журналы системы",
            "difficulty": 4,
            "points": 15,
            "task": """Посмотрите, что лежит в `/var/log`, и сохраните список в `~/sys/logs.txt`.

В списке должен быть журнал установки пакетов `dpkg.log`.""",
            "goals": ["Где системные журналы", "Что в /var/log"],
            "hints": ["ls /var/log > ~/sys/logs.txt", "cat /var/log/dpkg.log — что ставилось в системе"],
            "solution": "ls /var/log > ~/sys/logs.txt",
            "checks": [
                fc("/home/student/sys/logs.txt", "dpkg.log", "Журнал dpkg.log найден"),
            ],
        },
    ],
}
