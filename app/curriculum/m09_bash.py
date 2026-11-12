"""Модуль 8. Bash-скрипты."""
from .helpers import cok, fc, fe, fm, fl, fmode, fne

MODULE = {
    "id": "m9",
    "title": "Модуль 9. Скрипты на bash",
    "icon": "📜",
    "summary": "Автоматизация: переменные, аргументы, условия, циклы, функции, коды возврата.",
    "tasks": [
        {
            "id": "m9-01",
            "title": "Первый скрипт",
            "difficulty": 3,
            "points": 10,
            "task": """Создайте скрипт `~/scripts/env.sh`:

    #!/bin/bash
    echo "I am running on $(hostname)" > ~/scripts/env_out.txt

Сделайте его исполняемым и запустите. В `~/scripts/env_out.txt` должно появиться имя хоста.""",
            "goals": ["Shebang", "Подстановка команд $(...)"],
            "hints": ["mkdir -p ~/scripts", "chmod +x ~/scripts/env.sh", "hostname — имя компьютера"],
            "solution": "mkdir -p ~/scripts && printf '#!/bin/bash\\necho \"I am running on $(hostname)\" > ~/scripts/env_out.txt\\n' > ~/scripts/env.sh && chmod +x ~/scripts/env.sh && ~/scripts/env.sh",
            "checks": [
                fmode("/home/student/scripts/env.sh", "755", "Скрипт исполняемый"),
                fe("/home/student/scripts/env_out.txt", "Скрипт отработал"),
                fc("/home/student/scripts/env_out.txt", "I am running on", "Вывод скрипта получен"),
            ],
        },
        {
            "id": "m9-02",
            "title": "Переменные",
            "difficulty": 3,
            "points": 15,
            "task": """Создайте скрипт `~/scripts/vars.sh`, который объявляет переменные и печатает их:

    #!/bin/bash
    NAME="LinuxLab"
    VERSION="0.01"
    echo "Имя: $NAME версия: $VERSION" > ~/scripts/vars_out.txt

Запустите его и проверьте результат.""",
            "goals": ["Объявление и использование переменных", "Кавычки"],
            "hints": ["echo $NAME — подстановка значения", "Переменные без кавычек ломаются на пробелах"],
            "solution": "mkdir -p ~/scripts && printf '#!/bin/bash\\nNAME=\"LinuxLab\"\\nVERSION=\"0.01\"\\necho \"Имя: $NAME версия: $VERSION\" > ~/scripts/vars_out.txt\\n' > ~/scripts/vars.sh && chmod +x ~/scripts/vars.sh && ~/scripts/vars.sh",
            "checks": [
                fc("/home/student/scripts/vars_out.txt", "LinuxLab", "Значение NAME подставлено"),
                fc("/home/student/scripts/vars_out.txt", "0.01", "Значение VERSION подставлено"),
            ],
        },
        {
            "id": "m9-03",
            "title": "Аргументы скрипта",
            "difficulty": 3,
            "points": 15,
            "task": """Создайте скрипт `~/scripts/args.sh`, который принимает имя в аргументе и печатает приветствие:

    #!/bin/bash
    echo "Привет, $1!" > ~/scripts/args_out.txt

Запустите его с аргументом `Мир`: `~/scripts/args.sh Мир`.""",
            "goals": ["Параметры командной строки", "$1, $#, $@"],
            "hints": ["$1 — первый аргумент, $# — их количество", "echo \"Аргументов: $#\""],
            "solution": "mkdir -p ~/scripts && printf '#!/bin/bash\\necho \"Привет, $1!\" > ~/scripts/args_out.txt\\n' > ~/scripts/args.sh && chmod +x ~/scripts/args.sh && ~/scripts/args.sh Мир",
            "checks": [
                fc("/home/student/scripts/args_out.txt", "Привет, Мир!", "Аргумент подставлен"),
            ],
        },
        {
            "id": "m9-04",
            "title": "Условие if",
            "difficulty": 4,
            "points": 20,
            "task": """Создайте скрипт `~/scripts/if.sh`, который принимает число и пишет в stdout `big`, если число больше 10, и `small` иначе.

Запустите его дважды и сохраните результаты:
* `~/scripts/if.sh 20 > ~/scripts/if_big.txt` → должно быть `big`
* `~/scripts/if.sh 5 > ~/scripts/if_small.txt` → должно быть `small`""",
            "goals": ["Конструкция if/else", "Сравнение чисел в bash"],
            "hints": ["if [ $1 -gt 10 ]; then ... else ... fi", "Для строк используйте = , для чисел -eq, -gt, -lt"],
            "solution": "mkdir -p ~/scripts && printf '#!/bin/bash\\nif [ $1 -gt 10 ]; then\\n  echo big\\nelse\\n  echo small\\nfi\\n' > ~/scripts/if.sh && chmod +x ~/scripts/if.sh && ~/scripts/if.sh 20 > ~/scripts/if_big.txt && ~/scripts/if.sh 5 > ~/scripts/if_small.txt",
            "checks": [
                fm("/home/student/scripts/if_big.txt", r"^big$", "Для 20 получено big"),
                fm("/home/student/scripts/if_small.txt", r"^small$", "Для 5 получено small"),
            ],
        },
        {
            "id": "m9-05",
            "title": "Цикл for",
            "difficulty": 4,
            "points": 20,
            "task": """Создайте скрипт `~/scripts/for.sh`, который печатает числа от 1 до 5 (каждое с новой строки) в файл `~/scripts/for_out.txt`.

Подсказка: `for i in 1 2 3 4 5; do echo $i; done`.""",
            "goals": ["Цикл for", "Тело цикла в do ... done"],
            "hints": ["for i in $(seq 1 5); do echo $i; done", "seq генерирует последовательность чисел"],
            "solution": "mkdir -p ~/scripts && printf '#!/bin/bash\\nfor i in 1 2 3 4 5; do\\n  echo $i\\ndone > ~/scripts/for_out.txt\\n' > ~/scripts/for.sh && chmod +x ~/scripts/for.sh && ~/scripts/for.sh",
            "checks": [
                fl("/home/student/scripts/for_out.txt", "5 строк", exact=5),
                fm("/home/student/scripts/for_out.txt", r"^1$", "Есть строка 1"),
                fm("/home/student/scripts/for_out.txt", r"^5$", "Есть строка 5"),
            ],
        },
        {
            "id": "m9-06",
            "title": "Цикл while и счётчик",
            "difficulty": 4,
            "points": 20,
            "task": """Создайте скрипт `~/scripts/while.sh`, который считает от 1 до 3 и печатает итог в `~/scripts/while_out.txt`:

    1
    2
    3

Используйте `while` и счётчик `i`.""",
            "goals": ["Цикл while", "Условие в цикле", "Инкремент"],
            "hints": ["i=0; while [ $i -lt 3 ]; do i=$((i+1)); echo $i; done", "$(( )) — арифметика в bash"],
            "solution": "mkdir -p ~/scripts && printf '#!/bin/bash\\ni=0\\nwhile [ $i -lt 3 ]; do\\n  i=$((i+1))\\n  echo $i\\ndone > ~/scripts/while_out.txt\\n' > ~/scripts/while.sh && chmod +x ~/scripts/while.sh && ~/scripts/while.sh",
            "checks": [
                fl("/home/student/scripts/while_out.txt", "3 строки", exact=3),
                fm("/home/student/scripts/while_out.txt", r"^3$", "Последнее значение 3"),
            ],
        },
        {
            "id": "m9-07",
            "title": "Конструкция case",
            "difficulty": 5,
            "points": 20,
            "task": """Создайте скрипт `~/scripts/case.sh`, который принимает команду `start`, `stop` или `restart` и печатает `OK <команда>`, а для неизвестной команды — `UNKNOWN`.

Проверьте: `~/scripts/case.sh start > ~/scripts/case_out.txt` (в файле должно быть `OK start`).""",
            "goals": ["Конструкция case/case esac", "Шаблоны в bash"],
            "hints": ["case $1 in start) echo 'OK start' ;; stop) ... ;; *) echo UNKNOWN ;; esac", ";; разделяет ветки"],
            "solution": "mkdir -p ~/scripts && printf '#!/bin/bash\\ncase $1 in\\n  start) echo \"OK start\" ;;\\n  stop) echo \"OK stop\" ;;\\n  restart) echo \"OK restart\" ;;\\n  *) echo UNKNOWN ;;\\nesac\\n' > ~/scripts/case.sh && chmod +x ~/scripts/case.sh && ~/scripts/case.sh start > ~/scripts/case_out.txt",
            "checks": [
                fc("/home/student/scripts/case_out.txt", "OK start", "Ветка start отработала"),
            ],
        },
        {
            "id": "m9-08",
            "title": "Функции",
            "difficulty": 5,
            "points": 20,
            "task": """Создайте скрипт `~/scripts/func.sh` с функцией, которая форматирует приветствие, и вызовите её:

    #!/bin/bash
    greet() {
      echo "Hello, $1!"
    }
    greet "$1" > ~/scripts/func_out.txt

Запустите: `~/scripts/func.sh Мир` → в файле будет `Hello, Мир!`.""",
            "goals": ["Объявление функций", "Передача аргументов в функцию"],
            "hints": ["Имя функции пишется без скобок при вызове", "Внутри функции $1 — первый аргумент функции"],
            "solution": "mkdir -p ~/scripts && printf '#!/bin/bash\\ngreet() {\\n  echo \"Hello, $1!\"\\n}\\ngreet \"$1\" > ~/scripts/func_out.txt\\n' > ~/scripts/func.sh && chmod +x ~/scripts/func.sh && ~/scripts/func.sh Мир",
            "checks": [
                fc("/home/student/scripts/func_out.txt", "Hello, Мир!", "Функция отработала"),
            ],
        },
        {
            "id": "m9-09",
            "title": "Коды возврата",
            "difficulty": 5,
            "points": 20,
            "task": """Создайте скрипт `~/scripts/exitcode.sh`, который завершается с кодом 3:

    #!/bin/bash
    exit 3

Запустите его так, чтобы код вернулся в `$?`, и запишите этот код в `~/scripts/code.txt` (в файле должно быть число 3).""",
            "goals": ["Коды возврата", "Как скрипты сообщают об ошибке"],
            "hints": ["~/scripts/exitcode.sh; echo $? > ~/scripts/code.txt", "0 — успех, ненулевое — ошибка"],
            "solution": "mkdir -p ~/scripts && printf '#!/bin/bash\\nexit 3\\n' > ~/scripts/exitcode.sh && chmod +x ~/scripts/exitcode.sh && ~/scripts/exitcode.sh; echo $? > ~/scripts/code.txt",
            "checks": [
                fm("/home/student/scripts/code.txt", r"^3\s*$", "Код возврата 3 записан"),
            ],
        },
        {
            "id": "m9-10",
            "title": "Дописывание в файл (>>)",
            "difficulty": 3,
            "points": 15,
            "task": """Создайте файл `~/scripts/log.txt` с одной строкой `start`, а затем допишите в него ещё две строки (`run`, `stop`) с помощью `>>`.

В итоге в файле должно быть 3 строки: start, run, stop.""",
            "goals": ["Разница > и >>", "Логирование"],
            "hints": ["echo start > ~/scripts/log.txt", "echo run >> ~/scripts/log.txt", "cat -n ~/scripts/log.txt"],
            "solution": "mkdir -p ~/scripts && echo start > ~/scripts/log.txt && echo run >> ~/scripts/log.txt && echo stop >> ~/scripts/log.txt",
            "checks": [
                fl("/home/student/scripts/log.txt", "3 строки", exact=3),
                fc("/home/student/scripts/log.txt", "start", "Первая строка на месте"),
                fc("/home/student/scripts/log.txt", "stop", "Последняя строка на месте"),
            ],
        },
        {
            "id": "m9-11",
            "title": "Строгий режим: set -euo pipefail",
            "difficulty": 5,
            "points": 20,
            "task": """Создайте скрипт `~/scripts/strict.sh`, который начинается со строк

    #!/bin/bash
    set -euo pipefail

и дальше печатает `strict ok` в `~/scripts/strict_out.txt`.

Заключите его в `bash -n` (проверка синтаксиса) и запустите — он должен отработать без ошибок.""",
            "goals": ["Строгий режим bash", "Ошибки прерывают скрипт", "Проверка синтаксиса"],
            "hints": ["bash -n ~/scripts/strict.sh — проверить синтаксис без запуска", "-e — выход при ошибке, -u — ошибка на неопределённой переменной, -o pipefail — ошибки в пайпах"],
            "solution": "mkdir -p ~/scripts && printf '#!/bin/bash\\nset -euo pipefail\\necho \"strict ok\" > ~/scripts/strict_out.txt\\n' > ~/scripts/strict.sh && chmod +x ~/scripts/strict.sh && bash -n ~/scripts/strict.sh && ~/scripts/strict.sh",
            "checks": [
                fc("/home/student/scripts/strict.sh", "set -euo pipefail", "Строгий режим включён"),
                fc("/home/student/scripts/strict_out.txt", "strict ok", "Скрипт отработал"),
            ],
        },
        {
            "id": "m9-12",
            "title": "Чтение файла построчно",
            "difficulty": 5,
            "points": 20,
            "task": """Создайте файл `~/scripts/data.txt` с тремя строками (`alpha`, `beta`, `gamma`).

Создайте скрипт `~/scripts/read.sh`, который читает файл построчно и печатает каждую строку с префиксом `> ` в `~/scripts/read_out.txt`.

В результате должно быть 3 строки, начинающиеся с `> `.""",
            "goals": ["Цикл while read", "Обработка файлов построчно"],
            "hints": ["while IFS= read -r line; do echo \"> $line\"; done < ~/scripts/data.txt > ~/scripts/read_out.txt", "IFS= сохраняет пробелы в строках"],
            "solution": "mkdir -p ~/scripts && printf 'alpha\\nbeta\\ngamma\\n' > ~/scripts/data.txt && printf '#!/bin/bash\\nwhile IFS= read -r line; do\\n  echo \"> $line\"\\ndone < ~/scripts/data.txt\\n' > ~/scripts/read.sh && chmod +x ~/scripts/read.sh && ~/scripts/read.sh > ~/scripts/read_out.txt",
            "checks": [
                fl("/home/student/scripts/read_out.txt", "3 строки", exact=3),
                fc("/home/student/scripts/read_out.txt", "> alpha", "Строки обработаны с префиксом"),
            ],
        },
        {
            "id": "m9-13",
            "title": "Массивы",
            "difficulty": 5,
            "points": 20,
            "task": """Создайте скрипт `~/scripts/array.sh` с массивом из трёх элементов (`red green blue`), который выводит их в файл `~/scripts/array_out.txt` — по одному в строке, начиная со второго элемента (green, blue).""",
            "goals": ["Массивы bash", "Обход массива"],
            "hints": ["arr=(red green blue)", "for item in \"${arr[@]:1}\"; do echo $item; done", "Индексация массивов начинается с 0"],
            "solution": "mkdir -p ~/scripts && printf '#!/bin/bash\\narr=(red green blue)\\nfor item in \"${arr[@]:1}\"; do\\n  echo $item\\ndone > ~/scripts/array_out.txt\\n' > ~/scripts/array.sh && chmod +x ~/scripts/array.sh && ~/scripts/array.sh",
            "checks": [
                fl("/home/student/scripts/array_out.txt", "2 строки", exact=2),
                fc("/home/student/scripts/array_out.txt", "green", "Есть green"),
                fc("/home/student/scripts/array_out.txt", "blue", "Есть blue"),
            ],
        },
        {
            "id": "m9-14",
            "title": "Подключение файла (source)",
            "difficulty": 5,
            "points": 20,
            "task": """Создайте файл настроек `~/scripts/config.sh` с переменной:

    APP_ENV=lab

и скрипт `~/scripts/useconfig.sh`, который подключает его через `source` и печатает значение в `~/scripts/config_out.txt` (должно быть `lab`).""",
            "goals": ["Источник конфигурации", "source vs bash"],
            "hints": ["source ~/scripts/config.sh", "echo $APP_ENV > ~/scripts/config_out.txt", "source выполняет файл в текущем шелле, поэтому переменные видны дальше"],
            "solution": "mkdir -p ~/scripts && echo 'APP_ENV=lab' > ~/scripts/config.sh && printf '#!/bin/bash\\nsource ~/scripts/config.sh\\necho $APP_ENV > ~/scripts/config_out.txt\\n' > ~/scripts/useconfig.sh && chmod +x ~/scripts/useconfig.sh && ~/scripts/useconfig.sh",
            "checks": [
                fc("/home/student/scripts/config.sh", "APP_ENV=lab", "Файл конфигурации создан"),
                fm("/home/student/scripts/config_out.txt", r"^lab\s*$", "Значение подставлено через source"),
            ],
        },
    ],
}
