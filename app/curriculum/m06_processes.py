"""Модуль 5. Процессы, фоновые задачи и окружение."""
from .helpers import cok, fc, fe, fm, fl, fne, hist, no_proc, proc

MODULE = {
    "id": "m6",
    "title": "Модуль 6. Процессы и фоновые задачи",
    "icon": "⚙",
    "summary": "Как Linux запускает, следит и останавливает программы: ps, jobs, nohup, kill, /proc.",
    "tasks": [
        {
            "id": "m6-01",
            "title": "ps: какие процессы идут",
            "difficulty": 3,
            "points": 10,
            "task": """Посмотрите список всех процессов командой `ps aux` и сохраните вывод в `~/proc/aux.txt`.

В файле должны быть строки с `bash` и с `ps`.""",
            "goals": ["Научиться читать вывод ps", "Понять, что такое PID"],
            "hints": ["mkdir -p ~/proc", "ps aux > ~/proc/aux.txt", "Колонки: USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND"],
            "solution": "mkdir -p ~/proc && ps aux > ~/proc/aux.txt",
            "checks": [
                fc("/home/student/proc/aux.txt", "bash", "Виден процесс bash"),
                fc("/home/student/proc/aux.txt", "PID", "Есть заголовок с PID"),
                fne("/home/student/proc/aux.txt", "Файл не пуст"),
            ],
        },
        {
            "id": "m6-02",
            "title": "Запускаем в фоне и находим PID",
            "difficulty": 3,
            "points": 15,
            "task": """Запустите в фоне процесс `sleep 300` и узнайте его PID (например, через `$!` или `pgrep`).

Запишите только номер PID в файл `~/proc/pid.txt`.""",
            "goals": ["Фоновые задачи", "Идентификатор процесса"],
            "hints": ["mkdir -p ~/proc", "sleep 300 &", "echo $! > ~/proc/pid.txt", "pgrep -f 'sleep 300' — другой способ"],
            "solution": "mkdir -p ~/proc; sleep 300 & echo $! > ~/proc/pid.txt",
            "checks": [
                fm("/home/student/proc/pid.txt", r"^\d+$", "Записан номер PID"),
                proc("sleep 300", "Процесс sleep 300 запущен"),
            ],
        },
        {
            "id": "m6-03",
            "title": "pgrep: поиск процесса",
            "difficulty": 3,
            "points": 15,
            "task": """Запустите в фоне `sleep 400` и найдите его PID командой `pgrep -f 'sleep 400'`.

Сохраните результат в `~/proc/pgrep.txt` (только числа).""",
            "goals": ["Поиск процесса по имени", "pgrep vs ps | grep"],
            "hints": ["sleep 400 &", "pgrep -f 'sleep 400' > ~/proc/pgrep.txt", "pgrep сам не выводит заголовок, в отличие от ps aux | grep"],
            "solution": "sleep 400 & pgrep -f 'sleep 400' > ~/proc/pgrep.txt",
            "checks": [
                fm("/home/student/proc/pgrep.txt", r"^\d+", "Найден числовой PID"),
                proc("sleep 400", "Процесс sleep 400 работает"),
            ],
        },
        {
            "id": "m6-04",
            "title": "top: снимок состояния",
            "difficulty": 3,
            "points": 15,
            "task": """Сделайте неинтерактивный снимок `top` (команда `top -b -n 1`) и сохраните вывод в `~/proc/top.txt`.

В выводе должны быть строки с `PID` и `COMMAND`.""",
            "goals": ["Снимать показатели системы", "Ключ -b для пакетного режима"],
            "hints": ["top -b -n 1 > ~/proc/top.txt", "Без -b top ждёт клавиш и в нашей среде зависнет"],
            "solution": "top -b -n 1 > ~/proc/top.txt",
            "checks": [
                fc("/home/student/proc/top.txt", "PID", "Есть колонка PID"),
                fc("/home/student/proc/top.txt", "COMMAND", "Есть колонка COMMAND"),
            ],
        },
        {
            "id": "m6-05",
            "title": "kill: останавливаем процесс",
            "difficulty": 4,
            "points": 20,
            "task": """Запустите в фоне `sleep 500`, запишите его PID, затем завершите процесс командой `kill <PID>`.

Убедитесь, что процесс больше не существует, и запишите результат `pgrep -f 'sleep 500'` в `~/proc/killed.txt` (файл должен быть пустым — процесс не найден).""",
            "goals": ["Сигналы и завершение процессов", "Проверка результата"],
            "hints": ["sleep 500 & pid=$!", "kill $pid", "ps -eo args | grep -F 'sleep 500' | grep -v grep | grep -v 'ps -eo' > ~/proc/killed.txt", "SIGTERM (15) — вежливое завершение, SIGKILL (9) — безусловное"],
            "solution": "sleep 500 & pid=$!; kill $pid; sleep 1; ps -eo args | grep -F 'sleep 500' | grep -v grep | grep -v 'ps -eo' > ~/proc/killed.txt",
            "checks": [
                fe("/home/student/proc/killed.txt", "Файл создан"),
                {"type": "file_empty", "path": "/home/student/proc/killed.txt", "title": "Процесс больше не найден (файл пуст)"},
                no_proc("sleep 500", "Процесс sleep 500 не запущен"),
            ],
        },
        {
            "id": "m6-06",
            "title": "jobs: фоновые задачи шелла",
            "difficulty": 4,
            "points": 15,
            "task": """Запустите фоновую задачу `sleep 600 &` и посмотрите список задач командой `jobs`.

Сохраните вывод в `~/proc/jobs.txt` — в нём должна быть строка вида `[1]+`.""",
            "goals": ["Управление заданиями шелла", "jobs, bg, fg"],
            "hints": ["sleep 600 &", "jobs > ~/proc/jobs.txt", "jobs показывает задания текущего шелла"],
            "solution": "sleep 600 & jobs > ~/proc/jobs.txt",
            "checks": [
                fc("/home/student/proc/jobs.txt", "[1]", "Есть номер задания [1]"),
                fc("/home/student/proc/jobs.txt", "sleep", "Видна команда задания"),
            ],
        },
        {
            "id": "m6-07",
            "title": "nohup: процесс переживает шелл",
            "difficulty": 4,
            "points": 20,
            "task": """Запустите `nohup sleep 700 > /dev/null 2>&1 &` — процесс должен продолжить работать, даже если вы «закроете» терминал.

Убедитесь, что он работает, и запишите вывод `pgrep -f 'sleep 700'` в `~/proc/nohup.txt`.""",
            "goals": ["Запуск фоновых служб", "nohup и перенаправление вывода"],
            "hints": ["nohup sleep 700 > /dev/null 2>&1 &", "pgrep -f 'sleep 700' > ~/proc/nohup.txt"],
            "solution": "nohup sleep 700 > /dev/null 2>&1 & pgrep -f 'sleep 700' > ~/proc/nohup.txt",
            "checks": [
                fm("/home/student/proc/nohup.txt", r"^\d+", "PID записан"),
                proc("sleep 700", "Процесс sleep 700 работает"),
            ],
        },
        {
            "id": "m6-08",
            "title": "/proc: файловая система процессов",
            "difficulty": 4,
            "points": 20,
            "task": """Запустите в фоне `sleep 800`, узнайте его PID и прочитайте его командную строку из `/proc/<PID>/cmdline`.

Сохраните содержимое в `~/proc/cmdline.txt` (в нём будет `sleep` и `800`).""",
            "goals": ["Заглянуть внутрь /proc", "Связь ps и /proc"],
            "hints": ["sleep 800 & pid=$!", "tr '\\0' ' ' < /proc/$pid/cmdline > ~/proc/cmdline.txt", "В /proc для каждого процесса есть каталог с PID"],
            "solution": "sleep 800 & pid=$!; tr '\\0' ' ' < /proc/$pid/cmdline > ~/proc/cmdline.txt",
            "checks": [
                fc("/home/student/proc/cmdline.txt", "sleep", "Прочитана командная строка"),
                fc("/home/student/proc/cmdline.txt", "800", "Виден аргумент 800"),
            ],
        },
        {
            "id": "m6-09",
            "title": "free: память системы",
            "difficulty": 3,
            "points": 10,
            "task": """Посмотрите состояние памяти (`free -h`) и сохраните вывод в `~/proc/mem.txt`.""",
            "goals": ["Оценить использование памяти", "Своп и кэш"],
            "hints": ["free -h > ~/proc/mem.txt", "Обратите внимание на колонки total, used, free, available"],
            "solution": "free -h > ~/proc/mem.txt",
            "checks": [
                fc("/home/student/proc/mem.txt", "Mem:", "Есть раздел Mem:"),
                fc("/home/student/proc/mem.txt", "Swap:", "Есть раздел Swap:"),
            ],
        },
        {
            "id": "m6-10",
            "title": "uptime и нагрузка",
            "difficulty": 3,
            "points": 10,
            "task": """Узнайте время работы системы и среднюю нагрузку (`uptime`), а также подробный вариант (`uptime -p`) — сохраните в `~/proc/uptime.txt`.""",
            "goals": ["Читать нагрузку системы", "load average"],
            "hints": ["uptime > ~/proc/uptime.txt", "uptime -p — «человеческий» формат"],
            "solution": "uptime > ~/proc/uptime.txt",
            "checks": [
                fc("/home/student/proc/uptime.txt", "load average", "Есть load average"),
            ],
        },
        {
            "id": "m6-11",
            "title": "Время выполнения команды",
            "difficulty": 3,
            "points": 15,
            "task": """Замерьте время выполнения команды `sleep 2` встроенной командой `time` и сохраните вывод в `~/proc/time.txt`.

В выводе будет строка `real`.""",
            "goals": ["Измерять время выполнения", "Реальное/user/sys время"],
            "hints": ["{ time sleep 2 ; } > ~/proc/time.txt 2>&1", "Проще: time sleep 2 > ~/proc/time.txt 2>&1", "Время идёт в stderr, поэтому нужен 2>&1"],
            "solution": "{ time sleep 2 ; } > ~/proc/time.txt 2>&1",
            "checks": [
                fc("/home/student/proc/time.txt", "real", "Есть строка real"),
                fc("/home/student/proc/time.txt", "user", "Есть строка user"),
                fc("/home/student/proc/time.txt", "sys", "Есть строка sys"),
            ],
        },
        {
            "id": "m6-12",
            "title": "Переменные окружения",
            "difficulty": 3,
            "points": 15,
            "task": """Создайте переменную окружения `LAB_NAME` со значением `linuxlab` (команда `export`), затем сохраните её значение в `~/proc/env.txt`.

Проверьте, что переменная видна и через `echo $LAB_NAME`, и в общем списке `env`.""",
            "goals": ["Переменные окружения", "export и просмотр env"],
            "hints": ["export LAB_NAME=linuxlab", "echo $LAB_NAME", "echo $LAB_NAME > ~/proc/env.txt", "env | grep LAB_NAME"],
            "solution": "export LAB_NAME=linuxlab && echo $LAB_NAME > ~/proc/env.txt",
            "checks": [
                fm("/home/student/proc/env.txt", r"linuxlab", "Значение переменной сохранено"),
                hist("export", "Вы использовали export"),
            ],
        },
        {
            "id": "m6-13",
            "title": "nice: приоритет процесса",
            "difficulty": 5,
            "points": 20,
            "task": """Запустите процесс с пониженным приоритетом: `nice -n 10 sleep 900 &` и сохраните его PID в `~/proc/nice_pid.txt`.

Затем посмотрите колонку NI у этого процесса через `ps -o pid,ni,cmd -p <PID>` и сохраните вывод в `~/proc/nice.txt`.""",
            "goals": ["Приоритеты процессов", "nice и renice"],
            "hints": ["nice -n 10 sleep 900 & echo $! > ~/proc/nice_pid.txt", "ps -o pid,ni,cmd -p $(cat ~/proc/nice_pid.txt) > ~/proc/nice.txt", "У обычного процесса NI=0, у нашего — 10"],
            "solution": "nice -n 10 sleep 900 & echo $! > ~/proc/nice_pid.txt; ps -o pid,ni,cmd -p $(cat ~/proc/nice_pid.txt) > ~/proc/nice.txt",
            "checks": [
                fm("/home/student/proc/nice_pid.txt", r"^\d+$", "PID записан"),
                fm("/home/student/proc/nice.txt", r"\b10\b", "Приоритет NI=10 отражён в выводе"),
            ],
        },
    ],
}
