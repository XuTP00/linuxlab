"""Модуль 1. Терминал и навигация — базовые команды, без перенаправлений.

Ученик учится ориентироваться в консоли: где я, что вокруг, как создавать,
перемещать и удалять. Запись текста в файлы через > появится позже,
в отдельном модуле про перенаправления.
"""
from .helpers import dc, de, fa, fc, fe, fne, hist, out

MODULE = {
    "id": "m1",
    "title": "Модуль 1. Терминал и навигация",
    "icon": "⌨",
    "summary": "Первые шаги в консоли: где я, что вокруг, как создавать, перемещать и удалять файлы.",
    "tasks": [
        {
            "id": "m1-01",
            "title": "Где я? pwd",
            "difficulty": 1,
            "points": 10,
            "task": """Выполните `pwd` (print working directory) — команда покажет полный путь
текущего каталога.

В приглашении шелла виден путь `~`, но `pwd` всегда печатает абсолютный путь.""",
            "goals": ["Узнать свой текущий каталог", "Понять разницу между ~ и абсолютным путём"],
            "hints": ["Наберите pwd и нажмите Enter", "Домашний каталог ученика — /home/student"],
            "solution": "pwd",
            "checks": [
                hist("pwd", "Команда pwd выполнена"),
                out("/home/student", "На экране показан путь домашнего каталога"),
            ],
        },
        {
            "id": "m1-02",
            "title": "Что вокруг? ls -la",
            "difficulty": 1,
            "points": 10,
            "task": """Выполните `ls -la` — так выглядит «подробный» список файлов, включая скрытые.

В выводе вы увидите: права (`drwxr-xr-x`), число ссылок, владельца, группу, размер, дату и имя.
Точка в начале имени означает, что файл скрытый — например `.bashrc`.""",
            "goals": ["Научиться смотреть содержимое каталога", "Увидеть скрытые файлы"],
            "hints": ["ls -la", "Без ключа -a скрытые файлы не показываются", "Ключ -l включает подробный формат"],
            "solution": "ls -la",
            "checks": [
                hist("ls", "Выполнен ls"),
                out(".bashrc", "В списке виден скрытый файл .bashrc"),
                out("total", "Виден подробный формат с колонкой total"),
            ],
        },
        {
            "id": "m1-03",
            "title": "cd: переходим между каталогами",
            "difficulty": 1,
            "points": 10,
            "task": """Создайте каталог `~/projects` и перейдите в него:

    mkdir ~/projects
    cd ~/projects

Проверьте, где вы теперь, командой `pwd`.

Обратите внимание: приглашение шелла показывает текущий каталог — теперь это `~/projects`.""",
            "goals": ["Создавать каталоги", "Переходить между каталогами", "Следить за приглашением шелла"],
            "hints": ["mkdir ~/projects", "cd ~/projects", "Вернуться назад: cd .., в домашний каталог: cd ~ или cd"],
            "solution": "mkdir ~/projects && cd ~/projects && pwd",
            "checks": [
                de("/home/student/projects", "Каталог ~/projects создан"),
                hist("cd", "Использована команда cd"),
                out("/home/student/projects", "В выводе pwd виден новый каталог"),
            ],
        },
        {
            "id": "m1-04",
            "title": "Каркас проекта: mkdir -p",
            "difficulty": 1,
            "points": 10,
            "task": """Создайте «каркас проекта» одной командой:

    mkdir -p ~/projects/demo/src ~/projects/demo/docs ~/projects/demo/tests

Ключ `-p` (parents) создаёт все промежуточные каталоги и не ругается,
если каталог уже существует.

Проверьте результат: `ls -R ~/projects/demo`.""",
            "goals": ["Однократно создать несколько каталогов", "Понять ключ -p"],
            "hints": ["mkdir -p ~/projects/demo/{src,docs,tests} — фигурные скобки раскрывает сам шелл", "ls -R показывает дерево каталогов"],
            "solution": "mkdir -p ~/projects/demo/src ~/projects/demo/docs ~/projects/demo/tests",
            "checks": [
                de("/home/student/projects/demo/src", "Каталог src создан"),
                de("/home/student/projects/demo/docs", "Каталог docs создан"),
                de("/home/student/projects/demo/tests", "Каталог tests создан"),
            ],
        },
        {
            "id": "m1-05",
            "title": "Создаём файл в редакторе nano",
            "difficulty": 2,
            "points": 15,
            "task": """Создайте файл `~/note.txt` с любым текстом (например, строкой `Привет, Linux!`).

Способ 1 — скопировать готовый системный файл:

    cp /etc/os-release ~/note.txt

Способ 2 — создать пустой файл и набрать текст в редакторе **nano**:

    touch ~/note.txt
    nano ~/note.txt

В nano: **Ctrl+O** — сохранить, **Enter** — подтвердить имя, **Ctrl+X** — выйти.

Проверьте результат: `cat ~/note.txt`.""",
            "goals": ["Научиться создавать файлы разными способами", "Освоить nano: сохранение и выход"],
            "hints": ["nano ~/note.txt", "Внизу nano есть подсказка с клавишами", "Если случайно нажали Ctrl+X — спросит сохранять ли: выберите Y"],
            "solution": "cp /etc/os-release ~/note.txt",
            "checks": [
                fe("/home/student/note.txt", "Файл note.txt создан"),
                fne("/home/student/note.txt", "Файл не пуст"),
            ],
        },
        {
            "id": "m1-06",
            "title": "Пустые файлы: touch",
            "difficulty": 1,
            "points": 10,
            "task": """Создайте в каталоге `~/projects/demo/src` три пустых файла:

    a.txt
    b.txt
    c.txt

Команда `touch` создаёт пустой файл (а если файл уже есть — обновляет время его изменения).""",
            "goals": ["Массово создавать пустые файлы", "Проверять содержимое каталога"],
            "hints": ["cd ~/projects/demo/src", "touch a.txt b.txt c.txt", "ls -l покажет размер 0 байт"],
            "solution": "cd ~/projects/demo/src && touch a.txt b.txt c.txt",
            "checks": [
                dc("/home/student/projects/demo/src", names=["a.txt", "b.txt", "c.txt"], title="В каталоге src три файла"),
                {"type": "file_size_min", "path": "/home/student/projects/demo/src/a.txt", "bytes": 0, "title": "Файл a.txt существует"},
            ],
        },
        {
            "id": "m1-07",
            "title": "Копирование: cp",
            "difficulty": 1,
            "points": 10,
            "task": """Скопируйте файл `~/note.txt` в `~/projects/demo/docs/note-copy.txt`.

Проверьте, что копия создана и содержит то же самое: `cat ~/projects/demo/docs/note-copy.txt`.""",
            "goals": ["Использовать cp", "Понять разницу между источником и назначением"],
            "hints": ["cp ~/note.txt ~/projects/demo/docs/note-copy.txt", "Если каталога docs нет — mkdir -p", "Ключ -i спросит подтверждение перезаписи"],
            "solution": "cp ~/note.txt ~/projects/demo/docs/note-copy.txt",
            "checks": [
                fe("/home/student/projects/demo/docs/note-copy.txt", "Копия создана"),
                fne("/home/student/projects/demo/docs/note-copy.txt", "Копия не пуста"),
            ],
        },
        {
            "id": "m1-08",
            "title": "Переименование: mv",
            "difficulty": 1,
            "points": 10,
            "task": """Переименуйте `~/projects/demo/docs/note-copy.txt` в `greeting.txt`.

Тот же инструмент `mv` умеет и перемещать файлы между каталогами.""",
            "goals": ["Использовать mv", "Различать переименование и перемещение"],
            "hints": ["mv ~/projects/demo/docs/note-copy.txt ~/projects/demo/docs/greeting.txt", "ls ~/projects/demo/docs — проверьте результат"],
            "solution": "mv ~/projects/demo/docs/note-copy.txt ~/projects/demo/docs/greeting.txt",
            "checks": [
                fe("/home/student/projects/demo/docs/greeting.txt", "Файл greeting.txt существует"),
                fa("/home/student/projects/demo/docs/note-copy.txt", "Старое имя больше не используется"),
            ],
        },
        {
            "id": "m1-09",
            "title": "Удаление: rm -r",
            "difficulty": 2,
            "points": 10,
            "task": """Создайте каталог `~/projects/demo/tmp` с файлом `garbage.txt` внутри
(`mkdir -p` + `touch`), затем **удалите каталог вместе со всем содержимым**.

Для каталогов `rm` требует ключа `-r` (рекурсивно).""",
            "goals": ["Рекурсивное удаление", "Понимать опасность rm -rf"],
            "hints": ["mkdir -p ~/projects/demo/tmp && touch ~/projects/demo/tmp/garbage.txt", "rm -r ~/projects/demo/tmp", "rm спросит подтверждение: y — да, n — нет"],
            "solution": "mkdir -p ~/projects/demo/tmp && touch ~/projects/demo/tmp/garbage.txt && rm -rf ~/projects/demo/tmp",
            "checks": [
                fa("/home/student/projects/demo/tmp", "Каталог tmp удалён"),
                hist("rm", "Использована команда rm"),
            ],
        },
        {
            "id": "m1-10",
            "title": "Скрытые файлы и ls -a",
            "difficulty": 2,
            "points": 10,
            "task": """Создайте свой скрытый файл `~/.myconfig` (имя начинается с точки)
и посмотрите на него через `ls -a` — в выводе он должен появиться.

Проверьте и обычный `ls` — там вашего файла не будет.""",
            "goals": ["Понять, что файлы с точкой — скрытые", "Использовать ls -a"],
            "hints": ["touch ~/.myconfig", "ls -a", "Без ключа -a скрытые файлы не видны"],
            "solution": "touch ~/.myconfig && ls -a",
            "checks": [
                fe("/home/student/.myconfig", "Скрытый файл создан"),
                hist("ls -a", "Использован ls -a"),
                out(".myconfig", "Файл виден в выводе ls -a"),
            ],
        },
        {
            "id": "m1-11",
            "title": "Шаблоны (glob)",
            "difficulty": 2,
            "points": 10,
            "task": """Создайте каталог `~/projects/demo/logs` и в нём три файла:

    log1.log
    log2.log
    log3.log

Затем посмотрите на них с помощью маски: выполните `ls ~/projects/demo/logs/*.log`.

Маску раскрывает сам шелл: вместо `*.log` в команду подставляются подходящие имена.""",
            "goals": ["Использовать маски при работе с файлами", "Понять, что маску раскрывает шелл"],
            "hints": ["mkdir -p ~/projects/demo/logs && cd ~/projects/demo/logs && touch log1.log log2.log log3.log", "ls *.log", "Если под маску ничего не подходит, вы получите ошибку «No such file»"],
            "solution": "mkdir -p ~/projects/demo/logs && cd ~/projects/demo/logs && touch log1.log log2.log log3.log && ls *.log",
            "checks": [
                dc("/home/student/projects/demo/logs", names=["log1.log", "log2.log", "log3.log"], title="Созданы три .log файла"),
                hist("*.log", "Использована маска *.log"),
                out("log1.log", "В выводе виден log1.log"),
            ],
        },
        {
            "id": "m1-12",
            "title": "find: ищем по дереву каталогов",
            "difficulty": 2,
            "points": 15,
            "task": """Создайте файлы в `~/projects/demo/src`:

    main.c
    utils.c
    readme.md

Затем найдите все файлы с расширением `.c` командой `find`:

    find ~/projects/demo/src -name '*.c'

В выводе должны быть `main.c` и `utils.c`, но не `readme.md`.""",
            "goals": ["Использовать find с фильтром по имени", "Понять структуру аргументов find"],
            "hints": ["touch ~/projects/demo/src/{main.c,utils.c,readme.md}", "find путь -name 'шаблон' — путь всегда первый", "Другие фильтры: -type f, -size +1M, -mtime +30"],
            "solution": "touch ~/projects/demo/src/{main.c,utils.c,readme.md} && find ~/projects/demo/src -name '*.c'",
            "checks": [
                fe("/home/student/projects/demo/src/main.c", "Файлы созданы"),
                hist("find", "Использована команда find"),
                out("main.c", "В выводе find есть main.c"),
                out("utils.c", "В выводе find есть utils.c"),
            ],
        },
        {
            "id": "m1-13",
            "title": "Какая программа это делает? command -v",
            "difficulty": 3,
            "points": 10,
            "task": """Узнайте, какой именно файл выполняется при вызове `ls`, и посмотрите на экран.

Поможет `command -v ls` (путь к программе) или `type ls` (путь + пояснение, что это).

Полезно знать: шелл ищет программы по списку каталогов в переменной `PATH`.""",
            "goals": ["Понять, как шелл находит программы", "Узнать абсолютный путь к команде"],
            "hints": ["command -v ls", "type -a ls — покажет все совпадения в PATH", "echo $PATH — сам список каталогов поиска"],
            "solution": "command -v ls",
            "checks": [
                hist("command -v", "Использована команда command -v"),
                out("/usr/bin/ls", "Показан абсолютный путь к программе ls"),
            ],
        },
    ],
}
