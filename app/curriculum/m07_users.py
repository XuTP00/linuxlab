"""Модуль 6. Пользователи, группы и sudo."""
from .helpers import cok, fc, fe, fm, fl, fne, fowner, ge, hist, ue, uig

MODULE = {
    "id": "m7",
    "title": "Модуль 7. Пользователи, группы, sudo",
    "icon": "👥",
    "summary": "Кто есть в системе, как создавать учётные записи, настраивать группы и права через sudo.",
    "tasks": [
        {
            "id": "m7-01",
            "title": "Кто я?",
            "difficulty": 2,
            "points": 10,
            "task": """Узнайте своё имя пользователя (`whoami` или `id -un`) и сохраните его в `~/user/who.txt`.""",
            "goals": ["Определить текущего пользователя", "Разница между uid и именем"],
            "hints": ["mkdir -p ~/user", "whoami", "id -un > ~/user/who.txt"],
            "solution": "mkdir -p ~/user && whoami > ~/user/who.txt",
            "checks": [
                fm("/home/student/user/who.txt", r"^student\s*$", "Записано имя пользователя student"),
            ],
        },
        {
            "id": "m7-02",
            "title": "Группы пользователя",
            "difficulty": 2,
            "points": 10,
            "task": """Выведите список групп, в которые вы входите (`id -nG`), и сохраните результат в `~/user/groups.txt`.""",
            "goals": ["Понимать группы и членство", "Читать вывод id"],
            "hints": ["id -nG", "id -nG > ~/user/groups.txt", "Основная группа указана первой"],
            "solution": "mkdir -p ~/user && id -nG > ~/user/groups.txt",
            "checks": [
                fc("/home/student/user/groups.txt", "student", "Есть группа student"),
            ],
        },
        {
            "id": "m7-03",
            "title": "sudo: привилегии суперпользователя",
            "difficulty": 3,
            "points": 15,
            "task": """Выполните `sudo id -un` и сохраните результат в `~/user/sudo.txt`.

В лаборатории `sudo` работает без пароля, чтобы вы могли сразу практиковаться.""",
            "goals": ["Использовать sudo", "Понимать, что даёт root"],
            "hints": ["sudo id -un", "sudo id -un > ~/user/sudo.txt", "Почти все команды управления системой требуют root"],
            "solution": "mkdir -p ~/user && sudo id -un > ~/user/sudo.txt",
            "checks": [
                fm("/home/student/user/sudo.txt", r"^root\s*$", "sudo дал права root"),
                hist("sudo", "Вы использовали sudo"),
            ],
        },
        {
            "id": "m7-04",
            "title": "Что мне разрешено? sudo -l",
            "difficulty": 3,
            "points": 15,
            "task": """Посмотрите список своих прав (`sudo -l`) и сохраните вывод в `~/user/sudol.txt`.""",
            "goals": ["Проверять свои привилегии", "Читать правила sudoers"],
            "hints": ["sudo -l", "sudo -l > ~/user/sudol.txt", "Правила хранятся в /etc/sudoers и /etc/sudoers.d"],
            "solution": "mkdir -p ~/user && sudo -l > ~/user/sudol.txt",
            "checks": [
                fne("/home/student/user/sudol.txt", "Вывод непустой"),
                fc("/home/student/user/sudol.txt", "ALL", "Есть упоминание ALL"),
            ],
        },
        {
            "id": "m7-05",
            "title": "Создаём пользователя",
            "difficulty": 4,
            "points": 20,
            "task": """Создайте нового пользователя `developer` с домашним каталогом:

    sudo useradd -m -s /bin/bash developer

Проверьте, что он появился в системе: `id developer`.""",
            "goals": ["Создание учётной записи", "Ключи -m и -s у useradd"],
            "hints": ["sudo useradd -m -s /bin/bash developer", "id developer", "-m создаёт домашний каталог, -s задаёт оболочку"],
            "solution": "sudo useradd -m -s /bin/bash developer",
            "checks": [
                ue("developer", "Пользователь developer создан"),
                cok("getent passwd developer | grep -q '/bin/bash'", "У пользователя оболочка /bin/bash"),
            ],
        },
        {
            "id": "m7-06",
            "title": "Создаём группу",
            "difficulty": 4,
            "points": 15,
            "task": """Создайте группу `devteam`:

    sudo groupadd devteam

Проверьте: `getent group devteam`.""",
            "goals": ["Создание групп", "Связь пользователей и групп"],
            "hints": ["sudo groupadd devteam", "getent group devteam", "cat /etc/group | tail -3"],
            "solution": "sudo groupadd devteam",
            "checks": [
                ge("devteam", "Группа devteam создана"),
            ],
        },
        {
            "id": "m7-07",
            "title": "Добавляем в группу",
            "difficulty": 4,
            "points": 20,
            "task": """Добавьте пользователя `developer` в группу `devteam`:

    sudo usermod -aG devteam developer

Важно: без `-a` (append) группа заменяется, а не дополняется!""",
            "goals": ["Управление членством в группах", "Опасность usermod без -a"],
            "hints": ["sudo usermod -aG devteam developer", "id developer", "Проверить: id -nG developer"],
            "solution": "sudo usermod -aG devteam developer",
            "checks": [
                uig("developer", "devteam", "developer входит в группу devteam"),
            ],
        },
        {
            "id": "m7-08",
            "title": "Смена оболочки пользователя",
            "difficulty": 4,
            "points": 20,
            "task": """Измените оболочку пользователя `developer` на `/bin/bash`:

    sudo usermod -s /bin/bash developer

Проверьте результат через `getent passwd developer` и запишите его в `~/user/passwd.txt`.""",
            "goals": ["Правка учётной записи", "Формат записей в /etc/passwd"],
            "hints": ["sudo usermod -s /bin/bash developer", "getent passwd developer > ~/user/passwd.txt", "Формат: имя:пароль:uid:gid:описание:домашний:оболочка"],
            "solution": "sudo usermod -s /bin/bash developer && getent passwd developer > ~/user/passwd.txt",
            "checks": [
                fc("/home/student/user/passwd.txt", "developer", "Запись о developer сохранена"),
                fc("/home/student/user/passwd.txt", "/bin/bash", "Оболочка /bin/bash на месте"),
            ],
        },
        {
            "id": "m7-09",
            "title": "Меняем владельца файла",
            "difficulty": 4,
            "points": 20,
            "task": """Создайте файл `~/user/owned.txt` и передайте его пользователю `developer`:

    sudo chown developer:devteam ~/user/owned.txt

Проверьте: `ls -l ~/user/owned.txt`.""",
            "goals": ["Смена владельца и группы", "Связь с группами"],
            "hints": ["echo data > ~/user/owned.txt", "sudo chown developer:devteam ~/user/owned.txt", "ls -l ~/user/owned.txt"],
            "solution": "echo data > ~/user/owned.txt && sudo chown developer:devteam ~/user/owned.txt",
            "checks": [
                fowner("/home/student/user/owned.txt", user="developer", group="devteam", title="Владелец developer, группа devteam"),
            ],
        },
        {
            "id": "m7-10",
            "title": "su: заходим под другим пользователем",
            "difficulty": 5,
            "points": 20,
            "task": """Выполните вход под пользователем `developer` через `sudo su - developer -c 'whoami'` и сохраните результат в `~/user/su.txt`.

Флаг `-` означает «логин-окружение»: домашний каталог и переменные меняются как при настоящем входе.""",
            "goals": ["Переключение пользователей", "su vs sudo"],
            "hints": ["sudo su - developer -c 'whoami' > ~/user/su.txt", "su — меняет пользователя, sudo — выполняет одну команду"],
            "solution": "sudo su - developer -c 'whoami' > ~/user/su.txt",
            "checks": [
                fm("/home/student/user/su.txt", r"^developer\s*$", "Вы вошли как developer"),
            ],
        },
        {
            "id": "m7-11",
            "title": "Читаем /etc/passwd",
            "difficulty": 3,
            "points": 15,
            "task": """Вырежите из `/etc/passwd` только имена пользователей (первое поле) и сохраните список в `~/user/users.txt`.

В файле должно быть не меньше 5 строк, и в нём должны быть `root` и `student`.""",
            "goals": ["Структура /etc/passwd", "Работа с cut по разделителю"],
            "hints": ["cut -d: -f1 /etc/passwd > ~/user/users.txt", "wc -l ~/user/users.txt", "Формат: имя:x:uid:gid:gecos:домашний:оболочка"],
            "solution": "cut -d: -f1 /etc/passwd > ~/user/users.txt",
            "checks": [
                fl("/home/student/user/users.txt", "Не меньше 5 пользователей", min=5),
                fc("/home/student/user/users.txt", "root", "Есть root"),
                fc("/home/student/user/users.txt", "student", "Есть student"),
            ],
        },
        {
            "id": "m7-12",
            "title": "Запуск команды от имени другого пользователя",
            "difficulty": 5,
            "points": 20,
            "task": """Выполните команду от имени `developer` и сохраните результат в `~/user/asuser.txt`:

    sudo -u developer whoami

В файле должно быть `developer`.""",
            "goals": ["Ключ -u у sudo", "Права отдельных команд"],
            "hints": ["sudo -u developer whoami > ~/user/asuser.txt", "sudo -u -g можно задать и группу"],
            "solution": "sudo -u developer whoami > ~/user/asuser.txt",
            "checks": [
                fm("/home/student/user/asuser.txt", r"^developer\s*$", "Команда выполнена от имени developer"),
            ],
        },
    ],
}
