"""Модуль 2. Файлы, каталоги и права доступа.

Заметьте: здесь по-прежнему нет перенаправлений (>, >>, |) — все результаты
смотрятся на экране. Запись вывода в файл — отдельная тема (модуль 3).
"""
from .helpers import cok, dc, de, fa, fc, fe, fl, fmode, fowner, fsize, hist, out, slink

MODULE = {
    "id": "m2",
    "title": "Модуль 2. Файлы, каталоги и права",
    "icon": "🔐",
    "summary": "Права доступа, владельцы, ссылки, размеры и диски — то, без чего нельзя понять Linux.",
    "tasks": [
        {
            "id": "m2-01",
            "title": "Права 644",
            "difficulty": 2,
            "points": 10,
            "task": """Создайте файл `~/perm/report.txt` (`mkdir -p ~/perm`, затем `touch`) и выставьте на него права `644`.

`644` читается так: владелец — `rw`, группа — `r`, остальные — `r`.
Проверьте результат командой `ls -l ~/perm/report.txt`.""",
            "goals": ["Назначать права числом", "Проверять результат через ls -l"],
            "hints": ["mkdir -p ~/perm && touch ~/perm/report.txt", "chmod 644 ~/perm/report.txt", "ls -l ~/perm/report.txt"],
            "solution": "mkdir -p ~/perm && touch ~/perm/report.txt && chmod 644 ~/perm/report.txt",
            "checks": [
                fe("/home/student/perm/report.txt", "Файл создан"),
                fmode("/home/student/perm/report.txt", "644", "Права равны 644"),
            ],
        },
        {
            "id": "m2-02",
            "title": "Исполняемый скрипт",
            "difficulty": 2,
            "points": 15,
            "task": """Создайте скрипт `~/scripts/hello.sh` в редакторе nano:

    #!/bin/bash
    echo "hi from script"

Сделайте его исполняемым (`chmod +x`) и **запустите**: `./scripts/hello.sh`

Вывод скрипта появится прямо в терминале — это и есть результат его работы.""",
            "goals": ["Право на исполнение", "Запуск скрипта из домашнего каталога"],
            "hints": ["mkdir -p ~/scripts && nano ~/scripts/hello.sh", "chmod +x ~/scripts/hello.sh", "Запуск по относительному пути: ./scripts/hello.sh"],
            "solution": "nano ~/scripts/hello.sh && chmod +x ~/scripts/hello.sh && ./scripts/hello.sh",
            "solution_auto": "mkdir -p ~/scripts && printf '#!/bin/bash\\necho \"hi from script\"\\n' > ~/scripts/hello.sh && chmod +x ~/scripts/hello.sh && ~/scripts/hello.sh",
            "checks": [
                fmode("/home/student/scripts/hello.sh", "755", "Скрипт исполняемый"),
                hist("hello.sh", "Скрипт запущен"),
                out("hi from script", "Вывод скрипта появился в терминале"),
            ],
        },
        {
            "id": "m2-03",
            "title": "Рекурсивный chmod",
            "difficulty": 2,
            "points": 15,
            "task": """Создайте каталог `~/perm/box` и внутри него файлы `one.txt` и `two.txt`.

Затем выставьте права `755` сразу на каталог **и** на все файлы внутри него одной командой с ключом `-R`.""",
            "goals": ["Рекурсивное изменение прав", "Права каталогов: rwx = проход и листинг"],
            "hints": ["mkdir -p ~/perm/box && touch ~/perm/box/{one.txt,two.txt}", "chmod -R 755 ~/perm/box", "Без -r chmod работает только с одним уровнем"],
            "solution": "mkdir -p ~/perm/box && touch ~/perm/box/{one.txt,two.txt} && chmod -R 755 ~/perm/box",
            "checks": [
                fmode("/home/student/perm/box", "755", "Права каталога 755"),
                fmode("/home/student/perm/box/one.txt", "755", "Права one.txt 755"),
                fmode("/home/student/perm/box/two.txt", "755", "Права two.txt 755"),
            ],
        },
        {
            "id": "m2-04",
            "title": "Маска umask",
            "difficulty": 3,
            "points": 15,
            "task": """Узнайте текущую маску `umask` (в нашей лаборатории она равна `0022` — это 644 для файлов и 755 для каталогов).

Создайте файл `~/perm/plain.txt` и посмотрите на его права через `ls -l`.

Правило простое: из базовых прав (666 для файла) вычитается маска.""",
            "goals": ["Понять, что маска вычитается из базовых прав", "Предсказать права нового файла"],
            "hints": ["umask", "touch ~/perm/plain.txt && ls -l ~/perm/plain.txt", "666 - 022 = 644"],
            "solution": "umask && touch ~/perm/plain.txt && ls -l ~/perm/plain.txt",
            "checks": [
                hist("umask", "Узнали маску командой umask"),
                out("0022", "Маска 0022 показана на экране"),
                fmode("/home/student/perm/plain.txt", "644", "У нового файла права 644"),
            ],
        },
        {
            "id": "m2-05",
            "title": "Смена владельца",
            "difficulty": 3,
            "points": 15,
            "task": """Создайте файл `~/perm/owner.txt` и смените его владельца на `root` командой `sudo chown root:root`.

Затем верните владельца `student` (в группе `student`).

В контейнере у вас есть `sudo` без пароля — это упрощает учебные задачи.""",
            "goals": ["Менять владельца и группу файла", "Понимать разницу между пользователем и группой"],
            "hints": ["touch ~/perm/owner.txt", "sudo chown root:root ~/perm/owner.txt", "sudo chown student:student ~/perm/owner.txt"],
            "solution": "touch ~/perm/owner.txt && sudo chown root:root ~/perm/owner.txt && sudo chown student:student ~/perm/owner.txt",
            "checks": [
                fe("/home/student/perm/owner.txt", "Файл существует"),
                fowner("/home/student/perm/owner.txt", user="student", group="student", title="Владелец снова student:student"),
            ],
        },
        {
            "id": "m2-06",
            "title": "Читаем вывод ls -l",
            "difficulty": 2,
            "points": 15,
            "task": """Создайте три файла с разными правами в `~/perm`:

    private.txt  →  600
    shared.txt   →  644
    public.sh    →  755

Затем выполните `ls -l ~/perm` и найдите в выводе строки с наборами
`-rw-------`, `-rw-r--r--` и `-rwxr-xr-x` — они соответствуют 600, 644 и 755.""",
            "goals": ["Различать 9 символов прав", "Связать числовую маску с символьной записью"],
            "hints": ["touch ~/perm/{private.txt,shared.txt,public.sh}", "chmod 600 ~/perm/private.txt; chmod 644 ~/perm/shared.txt; chmod 755 ~/perm/public.sh", "ls -l ~/perm"],
            "solution": "touch ~/perm/{private.txt,shared.txt,public.sh} && chmod 600 ~/perm/private.txt && chmod 644 ~/perm/shared.txt && chmod 755 ~/perm/public.sh && ls -l ~/perm",
            "checks": [
                fmode("/home/student/perm/private.txt", "600", "private.txt — 600"),
                fmode("/home/student/perm/shared.txt", "644", "shared.txt — 644"),
                fmode("/home/student/perm/public.sh", "755", "public.sh — 755"),
                out("-rwxr-xr-x", "В выводе ls -l есть набор -rwxr-xr-x"),
            ],
        },
        {
            "id": "m2-07",
            "title": "stat: полная информация о файле",
            "difficulty": 3,
            "points": 15,
            "task": """Выполните `stat ~/perm/data.txt` (создайте файл заранее) и найдите в выводе строки:
`Size:`, `Uid:`, `Gid:` и `Inode:`.

Inode — это номер файла в файловой системе; именно он связывает имя с данными.""",
            "goals": ["Получить метаданные файла", "Понять, что такое inode"],
            "hints": ["echo hello > ~/perm/data.txt", "stat ~/perm/data.txt", "Короткий формат: stat -c '%s %U %i' ~/perm/data.txt"],
            "solution": "echo hello > ~/perm/data.txt && stat ~/perm/data.txt",
            "checks": [
                hist("stat", "Использована команда stat"),
                out("Size:", "Есть строка Size:"),
                out("Inode:", "Есть строка Inode:"),
            ],
        },
        {
            "id": "m2-08",
            "title": "Тип файла: file",
            "difficulty": 3,
            "points": 15,
            "task": """Создайте два файла:

* `~/perm/script.sh` — текст со строкой `#!/bin/bash`
* `~/perm/blob.bin` — бинарные данные (`head -c 64 /dev/urandom > ~/perm/blob.bin`)

Определите тип каждого командой `file`. Для текстового файла вы увидите `ASCII text`,
для бинарного — `data`.

Обратите внимание: тип определяется по содержимому, а не по расширению.""",
            "goals": ["Определять тип содержимого", "Отличать текст от бинарных данных"],
            "hints": ["echo '#!/bin/bash' > ~/perm/script.sh", "file ~/perm/script.sh ~/perm/blob.bin", "Переименуйте blob.bin в blob.txt — тип не изменится"],
            "solution": "echo '#!/bin/bash' > ~/perm/script.sh && head -c 64 /dev/urandom > ~/perm/blob.bin && file ~/perm/script.sh ~/perm/blob.bin",
            "checks": [
                hist("file", "Использована команда file"),
                out("text", "Текстовый тип определён"),
                out("data", "Бинарный тип определён"),
            ],
        },
        {
            "id": "m2-09",
            "title": "Символическая ссылка",
            "difficulty": 3,
            "points": 15,
            "task": """Создайте символическую ссылку `~/passwd_link` на `/etc/passwd`:

    ln -s /etc/passwd ~/passwd_link

Проверьте цель ссылки командой `readlink -f ~/passwd_link` и посмотрите на ссылку через `ls -l`.""",
            "goals": ["Отличать символическую ссылку от копии", "Уметь проверять цель ссылки"],
            "hints": ["ln -s /etc/passwd ~/passwd_link", "ls -l покажет стрелку -> /etc/passwd", "readlink -f покажет абсолютный путь цели"],
            "solution": "ln -s /etc/passwd ~/passwd_link",
            "checks": [
                slink("/home/student/passwd_link", "/etc/passwd", "Ссылка указывает на /etc/passwd"),
                hist("ln -s", "Использована команда ln -s"),
            ],
        },
        {
            "id": "m2-10",
            "title": "Жёсткая ссылка",
            "difficulty": 4,
            "points": 15,
            "task": """Создайте файл `~/perm/original.txt`, затем сделайте **жёсткую** ссылку
`~/perm/hardlink.txt` на него (команда `ln` без ключа `-s`).

У жёсткой ссылки тот же inode, что и у оригинала. Проверьте это:

    stat -c '%i' ~/perm/original.txt
    stat -c '%i' ~/perm/hardlink.txt

Номера должны совпасть.""",
            "goals": ["Жёсткие и символические ссылки", "Понять, что такое inode"],
            "hints": ["touch ~/perm/original.txt && ln ~/perm/original.txt ~/perm/hardlink.txt", "stat -c '%i' файл — показывает inode", "Проверка одной командой: test $(stat -c %i a) = $(stat -c %i b)"],
            "solution": "touch ~/perm/original.txt && ln ~/perm/original.txt ~/perm/hardlink.txt",
            "checks": [
                fe("/home/student/perm/hardlink.txt", "Жёсткая ссылка создана"),
                cok("test $(stat -c %i /home/student/perm/original.txt) = $(stat -c %i /home/student/perm/hardlink.txt)", "inode у оригинала и ссылки совпадают"),
            ],
        },
        {
            "id": "m2-11",
            "title": "Сколько весит? du и dd",
            "difficulty": 3,
            "points": 15,
            "task": """Создайте файл `~/perm/big.bin` размером 5 МБ:

    dd if=/dev/zero of=~/perm/big.bin bs=1M count=5

Посчитайте, сколько он занимает: `du -sh ~/perm/big.bin`.""",
            "goals": ["Создать файл заданного размера", "Считать размер файлов"],
            "hints": ["dd if=/dev/zero of=~/perm/big.bin bs=1M count=5", "du -sh файл — краткий вывод в человекочитаемом виде", "ls -lh ~/perm/big.bin — тоже покажет размер"],
            "solution": "dd if=/dev/zero of=~/perm/big.bin bs=1M count=5 && du -sh ~/perm/big.bin",
            "checks": [
                fsize("/home/student/perm/big.bin", 5_000_000, "Файл не меньше 5 МБ"),
                hist("du", "Использована команда du"),
            ],
        },
        {
            "id": "m2-12",
            "title": "Место на дисках: df",
            "difficulty": 3,
            "points": 10,
            "task": """Посмотрите, сколько свободного места осталось на смонтированных файловых
системах: `df -h`.

Важно различать: `du` считает размер данных в каталоге, а `df` — свободное место на разделе.""",
            "goals": ["Отличать du от df", "Читать таблицу разделов"],
            "hints": ["df -h", "Ключи: -h — человекочитаемый вывод, -T — тип ФС, -i — свободные иноды"],
            "solution": "df -h",
            "checks": [
                hist("df", "Использована команда df"),
                out("Filesystem", "Есть заголовок Filesystem"),
                out("Use%", "Есть колонка Use%"),
            ],
        },
        {
            "id": "m2-13",
            "title": "Архивирование: tar",
            "difficulty": 3,
            "points": 15,
            "task": """Создайте архив `~/backup.tar.gz` из каталога `~/projects/demo`:

    tar -czf ~/backup.tar.gz -C ~ projects/demo

Посмотрите, что внутри, не распаковывая: `tar -tzf ~/backup.tar.gz`.

Ключи: `c` — создать, `z` — сжатие gzip, `f` — имя файла, `t` — показать список, `x` — распаковать.""",
            "goals": ["Упаковать каталог в архив", "Просмотреть содержимое архива без распаковки"],
            "hints": ["tar -czf ~/backup.tar.gz -C ~ projects/demo", "tar -tzf ~/backup.tar.gz — список файлов", "Ключ -C меняет рабочий каталог для команды"],
            "solution": "tar -czf ~/backup.tar.gz -C ~ projects/demo",
            "checks": [
                fe("/home/student/backup.tar.gz", "Архив создан"),
                cok("tar -tzf /home/student/backup.tar.gz | grep -q 'demo'", "В архиве есть файлы каталога demo"),
                hist("tar", "Использована команда tar"),
            ],
        },
        {
            "id": "m2-14",
            "title": "Найдите нужное в выводе",
            "difficulty": 3,
            "points": 10,
            "task": """Выполните `ls -l ~/perm` и найдите в выводе файл с правами `-rw-------`
(то есть 600) — это `private.txt` из предыдущего задания.

Понаблюдайте, как легко пропустить нужную строку в длинном выводе: именно для этого
позже появятся grep и фильтры.""",
            "goals": ["Научиться читать большие объёмы вывода", "Подготовиться к инструментам поиска"],
            "hints": ["ls -l ~/perm", "Ищите строку, начинающуюся с -rw-------", "Пока нет grep — смотрите глазами; в следующих модулях будет удобнее"],
            "solution": "ls -l ~/perm",
            "checks": [
                hist("ls -l", "Использован подробный вывод ls -l"),
                out("-rw-------", "В выводе найдена строка с правами 600"),
            ],
        },
    ],
}
