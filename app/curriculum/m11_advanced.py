"""Модуль 10. Git, регулярки и продвинутые приёмы."""
from .helpers import cok, dc, de, fc, fe, fm, fl, fne, fmode

MODULE = {
    "id": "m11",
    "title": "Модуль 11. Git и продвинутые приёмы",
    "icon": "🚀",
    "summary": "Версионирование, awk-агрегация, heredoc, trap, base64, алиасы — то, что делает вас уверенным пользователем.",
    "tasks": [
        {
            "id": "m11-01",
            "title": "Первый репозиторий",
            "difficulty": 3,
            "points": 15,
            "task": """Создайте репозиторий git в `~/git/demo`:

    mkdir -p ~/git/demo && cd ~/git/demo
    git init
    echo "# Demo" > README.md
    git add README.md
    git commit -m "init"

Затем сохраните вывод `git log` в `~/git/log.txt` — в нём должно быть слово `init`.""",
            "goals": ["Инициализация репозитория", "Первый коммит", "git add и git commit"],
            "hints": ["git init — создаёт служебный каталог .git", "git status — что изменилось", "Если git попросит настроить имя: git config --global user.email lab@example.com && git config --global user.name student"],
            "solution": "mkdir -p ~/git/demo && cd ~/git/demo && git init && echo '# Demo' > README.md && git add README.md && git -c user.email=student@lab -c user.name=student commit -m 'init' && git log > ~/git/log.txt",
            "checks": [
                de("/home/student/git/demo/.git", "Репозиторий создан (.git)"),
                fe("/home/student/git/demo/README.md", "README.md создан"),
                fc("/home/student/git/log.txt", "init", "Коммит зафиксирован"),
            ],
        },
        {
            "id": "m11-02",
            "title": "Ветки",
            "difficulty": 4,
            "points": 20,
            "task": """В репозитории `~/git/demo` создайте ветку `feature` и перейдите на неё:

    git checkout -b feature

Сохраните список веток (`git branch`) в `~/git/branches.txt` — в нём должно быть имя `feature`.""",
            "goals": ["Ветвление", "checkout -b"],
            "hints": ["git branch — список веток", "git branch feature && git checkout feature", "git switch -c feature — современный синтаксис"],
            "solution": "cd ~/git/demo && git branch feature && git checkout feature && git branch > ~/git/branches.txt",
            "checks": [
                fc("/home/student/git/branches.txt", "feature", "Ветка feature создана"),
            ],
        },
        {
            "id": "m11-03",
            "title": "Что изменилось? git diff",
            "difficulty": 4,
            "points": 20,
            "task": """В `~/git/demo` измените `README.md` (добавьте строку `changed`), затем посмотрите разницу командой `git diff` и сохраните её в `~/git/diff.txt`.

В выводе должна быть строка, начинающаяся с `+changed`.""",
            "goals": ["Отслеживание изменений", "git diff и git status"],
            "hints": ["echo 'changed' >> README.md", "git diff", "git diff > ~/git/diff.txt", "Строка с + означает добавленную строку"],
            "solution": "cd ~/git/demo && echo 'changed' >> README.md && git diff > ~/git/diff.txt",
            "checks": [
                fm("/home/student/git/diff.txt", r"^\+changed", "Видно добавленную строку"),
            ],
        },
        {
            "id": "m11-04",
            "title": "Хеши коммитов и история",
            "difficulty": 4,
            "points": 20,
            "task": """Сделайте ещё один коммит в `~/git/demo` (например, `git commit -am "second"`) и сохратите историю с хешами (`git log --oneline`) в `~/git/history.txt`.

В файле должно быть 2 строки коммитов.""",
            "goals": ["История изменений", "Оформление вывода git log"],
            "hints": ["git log --oneline", "git log --oneline > ~/git/history.txt", "Хеш коммита — короткий идентификатор"],
            "solution": "cd ~/git/demo && git commit -am 'second' && git log --oneline > ~/git/history.txt",
            "checks": [
                fl("/home/student/git/history.txt", "Два коммита в истории", exact=2),
                fc("/home/student/git/history.txt", "init", "Первый коммит в истории"),
            ],
        },
        {
            "id": "m11-05",
            "title": "awk: считаем сумму",
            "difficulty": 5,
            "points": 20,
            "task": """Создайте файл `~/data/sums.txt` с числами (каждое на строке): 10, 20, 30, 40.

Посчитайте их сумму через `awk` и запишите результат в `~/data/sum.txt`.

Ожидаемый ответ: 100.

Подсказка: `awk '{s+=$1} END {print s}'`.""",
            "goals": ["Агрегация в awk", "Блок END"],
            "hints": ["mkdir -p ~/data && printf '10\\n20\\n30\\n40\\n' > ~/data/sums.txt", "awk '{s+=$1} END {print s}' ~/data/sums.txt > ~/data/sum.txt", "Блок END выполняется после обработки всех строк"],
            "solution": "mkdir -p ~/data && printf '10\\n20\\n30\\n40\\n' > ~/data/sums.txt && awk '{s+=$1} END {print s}' ~/data/sums.txt > ~/data/sum.txt",
            "checks": [
                fm("/home/student/data/sum.txt", r"^100\s*$", "Сумма посчитана верно (100)"),
            ],
        },
        {
            "id": "m11-06",
            "title": "sed и регулярные выражения",
            "difficulty": 5,
            "points": 20,
            "task": """Создайте файл `~/data/phones.txt`:

    +7 900 111-22-33
    +7 900 444-55-66

Замените все цифры на символ `#` (регулярное выражение `[0-9]`) и сохраните результат в `~/data/phones_masked.txt`.""",
            "goals": ["Регулярные выражения в sed", "Классы символов"],
            "hints": ["sed 's/[0-9]/#/g' ~/data/phones.txt > ~/data/phones_masked.txt", "Квадратные скобки задают класс символов"],
            "solution": "mkdir -p ~/data && printf '+7 900 111-22-33\\n+7 900 444-55-66\\n' > ~/data/phones.txt && sed 's/[0-9]/#/g' ~/data/phones.txt > ~/data/phones_masked.txt",
            "checks": [
                fc("/home/student/data/phones_masked.txt", "+# ### ###-##-##", "Цифры заменены на #"),
            ],
        },
        {
            "id": "m11-07",
            "title": "Подстановка процессов",
            "difficulty": 5,
            "points": 20,
            "task": """Используя подстановку процессов `<(...)`, сравните списки файлов двух каталогов и сохраните результат в `~/data/psdiff.txt`.

Пример: `diff <(ls ~/tree) <(ls ~/backup)`.

Файл может оказаться пустым (если каталоги одинаковые) — это нормально, но команда должна выполняться без ошибок.""",
            "goals": ["Подстановка процессов", "Виртуальные файлы /dev/fd"],
            "hints": ["diff <(ls ~/tree) <(ls ~/backup) > ~/data/psdiff.txt", "Работает только в bash, не в sh"],
            "solution": "mkdir -p ~/data && diff <(ls ~/tree) <(ls ~/backup) > ~/data/psdiff.txt 2>&1",
            "checks": [
                fe("/home/student/data/psdiff.txt", "Результат сохранён"),
                cok("bash -c 'diff <(ls /home/student/tree) <(ls /home/student/backup) >/dev/null 2>&1; [ $? -le 1 ]'", "Подстановка процессов работает"),
            ],
        },
        {
            "id": "m11-08",
            "title": "base64: кодирование данных",
            "difficulty": 4,
            "points": 15,
            "task": """Закодируйте файл `~/note.txt` в base64 и сохраните результат в `~/data/note.b64`, затем декодируйте обратно в `~/data/note.dec`.

В декодированном файле должно быть содержимое исходного файла.""",
            "goals": ["Кодирование данных", "base64 и обратное преобразование"],
            "hints": ["base64 ~/note.txt > ~/data/note.b64", "base64 -d ~/data/note.b64 > ~/data/note.dec", "base64 -d (или --decode)"],
            "solution": "mkdir -p ~/data && base64 ~/note.txt > ~/data/note.b64 && base64 -d ~/data/note.b64 > ~/data/note.dec",
            "checks": [
                fe("/home/student/data/note.b64", "Файл закодирован"),
                fne("/home/student/data/note.dec", "Декодированный файл не пуст"),
            ],
        },
        {
            "id": "m11-09",
            "title": "Алиасы в ~/.bashrc",
            "difficulty": 4,
            "points": 15,
            "task": """Добавьте в `~/.bashrc` алиас:

    alias ll='ls -al'

и второй алиас, например:

    alias ..='cd ..'

Сохраните вывод `tail -5 ~/.bashrc` в `~/data/bashrc.txt` — в нём должен быть ваш алиас `ll`.""",
            "goals": ["Настройка интерактивного шелла", "Алиасы"],
            "hints": ["echo \"alias ll='ls -al'\" >> ~/.bashrc", "tail -5 ~/.bashrc > ~/data/bashrc.txt", "Новые алиасы работают только в новом шелле или после source ~/.bashrc"],
            "solution": "mkdir -p ~/data && echo \"alias ll='ls -al'\" >> ~/.bashrc && echo \"alias ..='cd ..'\" >> ~/.bashrc && tail -5 ~/.bashrc > ~/data/bashrc.txt",
            "checks": [
                fc("/home/student/.bashrc", "alias ll", "Алиас добавлен в .bashrc"),
                fc("/home/student/data/bashrc.txt", "alias ll", "Алиас виден в сохранённом выводе"),
            ],
        },
        {
            "id": "m11-10",
            "title": "Heredoc: многострочный ввод",
            "difficulty": 4,
            "points": 15,
            "task": """Создайте файл `~/data/config.ini` с содержимым (используйте heredoc):

    [main]
    host=localhost
    port=8080

Способ: `cat > ~/data/config.ini << 'EOF'` … `EOF`.""",
            "goals": ["Heredoc", "Многострочный ввод без редактора"],
            "hints": ["cat > ~/data/config.ini << 'EOF'", "после первой строки наберите текст и в конце EOF на отдельной строке", "В кавычках 'EOF' подстановки переменных не происходит"],
            "solution": "mkdir -p ~/data && printf '[main]\\nhost=localhost\\nport=8080\\n' > ~/data/config.ini",
            "checks": [
                fe("/home/student/data/config.ini", "Файл создан"),
                fc("/home/student/data/config.ini", "[main]", "Есть секция [main]"),
                fc("/home/student/data/config.ini", "port=8080", "Есть параметр port"),
            ],
        },
        {
            "id": "m11-11",
            "title": "trap: гарантированная уборка",
            "difficulty": 6,
            "points": 25,
            "task": """Создайте скрипт `~/scripts/trap.sh`, который при выходе (даже по ошибке) пишет сообщение `cleanup done` в `~/scripts/trap_out.txt`:

    #!/bin/bash
    trap 'echo "cleanup done" > ~/scripts/trap_out.txt' EXIT
    echo "работаю"

Запустите его и проверьте `~/scripts/trap_out.txt`.""",
            "goals": ["Обработка сигналов", "Блок trap и EXIT"],
            "hints": ["trap 'команда' EXIT — выполняется при завершении скрипта", "mkdir -p ~/scripts", "bash -n ~/scripts/trap.sh — проверка синтаксиса"],
            "solution": "mkdir -p ~/scripts && printf '#!/bin/bash\\ntrap '\"'\"'echo \"cleanup done\" > ~/scripts/trap_out.txt'\"'\"' EXIT\\necho \"работаю\"\\n' > ~/scripts/trap.sh && chmod +x ~/scripts/trap.sh && ~/scripts/trap.sh",
            "checks": [
                fc("/home/student/scripts/trap.sh", "trap", "В скрипте есть trap"),
                fc("/home/student/scripts/trap_out.txt", "cleanup done", "Сообщение записано при выходе"),
            ],
        },
        {
            "id": "m11-12",
            "title": "Права: umask в скрипте и символьные права",
            "difficulty": 5,
            "points": 20,
            "task": """Создайте скрипт `~/scripts/umask.sh`:

    #!/bin/bash
    umask 077
    touch ~/scripts/secret.txt

Запустите его — файл `~/scripts/secret.txt` должен получить права `600`.

Проверьте также, что скопированный вручную файл `~/scripts/public.txt` имеет права `644`.""",
            "goals": ["umask внутри скрипта", "Символьная запись прав (u+x, g-w)"],
            "hints": ["touch ~/scripts/public.txt; chmod 644 ~/scripts/public.txt", "ls -l ~/scripts/", "0666 - 077 = 0600"],
            "solution": "mkdir -p ~/scripts && printf '#!/bin/bash\\numask 077\\ntouch ~/scripts/secret.txt\\n' > ~/scripts/umask.sh && chmod +x ~/scripts/umask.sh && ~/scripts/umask.sh && touch ~/scripts/public.txt && chmod 644 ~/scripts/public.txt",
            "checks": [
                fmode("/home/student/scripts/secret.txt", "600", "secret.txt имеет права 600"),
                fmode("/home/student/scripts/public.txt", "644", "public.txt имеет права 644"),
            ],
        },
    ],
}
