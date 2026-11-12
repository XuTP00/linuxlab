"""Модуль 4. Поиск по системе, архивы, ссылки и контрольные суммы."""
from .helpers import cok, dc, de, fa, fc, fe, fm, fl, fsize

MODULE = {
    "id": "m5",
    "title": "Модуль 5. Поиск, архивы и хеши",
    "icon": "🔎",
    "summary": "find, tar, gzip, rsync, sha256sum, diff — инструменты, которыми вы будете пользоваться каждый день.",
    "tasks": [
        {
            "id": "m5-01",
            "title": "find: поиск по имени",
            "difficulty": 3,
            "points": 10,
            "task": """Создайте дерево каталогов:

    ~/tree/a/b/c

и в нём файл `~/tree/a/b/c/deep.txt`.

Найдите его командой `find` (по имени `deep.txt`) и сохраните путь в `~/tree/found.txt`.""",
            "goals": ["Искать файлы по имени на любой глубине"],
            "hints": ["mkdir -p ~/tree/a/b/c && touch ~/tree/a/b/c/deep.txt", "find ~/tree -name 'deep.txt'", "find ~/tree -name 'deep.txt' > ~/tree/found.txt"],
            "solution": "mkdir -p ~/tree/a/b/c && touch ~/tree/a/b/c/deep.txt && find ~/tree -name 'deep.txt' > ~/tree/found.txt",
            "checks": [
                fe("/home/student/tree/a/b/c/deep.txt", "Файл создан"),
                fc("/home/student/tree/found.txt", "deep.txt", "Путь к файлу найден и сохранён"),
            ],
        },
        {
            "id": "m5-02",
            "title": "find: считаем каталоги",
            "difficulty": 3,
            "points": 15,
            "task": """Посчитайте, сколько каталогов в дереве `~/tree` (включая сам `~/tree`), и запишите число в `~/tree/dirs.txt`.

Для дерева из предыдущего задания ответ — 4 (`tree`, `a`, `b`, `c`).""",
            "goals": ["Фильтровать find по типу (-type d)", "Считать строки пайпа"],
            "hints": ["find ~/tree -type d", "find ~/tree -type d | wc -l", "find ~/tree -type d | wc -l > ~/tree/dirs.txt"],
            "solution": "find ~/tree -type d | wc -l > ~/tree/dirs.txt",
            "checks": [
                fm("/home/student/tree/dirs.txt", r"^\s*4\s*$", "Посчитано 4 каталога"),
            ],
        },
        {
            "id": "m5-03",
            "title": "find: фильтр по размеру",
            "difficulty": 4,
            "points": 15,
            "task": """Создайте файл `~/tree/big.bin` размером 2 МБ (`dd if=/dev/zero of=~/tree/big.bin bs=1M count=2`).

Найдите в `~/tree` файлы **больше 100 КБ** и сохраните их список в `~/tree/big_files.txt`.""",
            "goals": ["Фильтрация по размеру (-size)"],
            "hints": ["dd if=/dev/zero of=~/tree/big.bin bs=1M count=2", "find ~/tree -type f -size +100k", "Размер задаётся блоками по 512 байт, но поддерживаются суффиксы k, M, G"],
            "solution": "dd if=/dev/zero of=~/tree/big.bin bs=1M count=2 && find ~/tree -type f -size +100k > ~/tree/big_files.txt",
            "checks": [
                fsize("/home/student/tree/big.bin", 2_000_000, "Файл big.bin создан (2 МБ)"),
                fc("/home/student/tree/big_files.txt", "big.bin", "Большой файл найден"),
            ],
        },
        {
            "id": "m5-04",
            "title": "find -exec: действие для каждого файла",
            "difficulty": 4,
            "points": 20,
            "task": """Создайте несколько `.txt` файлов в `~/tree` (например, `~/tree/one.txt`, `~/tree/two.txt`).

Найдите их и для каждого посчитайте число строк, сохранив результат в `~/tree/counts.txt`.

В файле должны встречаться имена найденных файлов и числа строк.""",
            "goals": ["Выполнять команду для каждого найденного файла", "Связка find -exec и wc"],
            "hints": ["printf 'a\\nb\\nc\\n' > ~/tree/one.txt; printf 'x\\ny\\n' > ~/tree/two.txt", "find ~/tree -name '*.txt' -exec wc -l {} \\;", "Обратите внимание на экранирование ; — это \\;"],
            "solution": "printf 'a\\nb\\nc\\n' > ~/tree/one.txt && printf 'x\\ny\\n' > ~/tree/two.txt && find ~/tree -name '*.txt' -exec wc -l {} \\; > ~/tree/counts.txt",
            "checks": [
                fc("/home/student/tree/counts.txt", "one.txt", "Обработан one.txt"),
                fc("/home/student/tree/counts.txt", "two.txt", "Обработан two.txt"),
            ],
        },
        {
            "id": "m5-05",
            "title": "Массовая очистка через find",
            "difficulty": 4,
            "points": 20,
            "task": """Создайте три файла `~/tree/old1.log`, `~/tree/old2.log`, `~/tree/keep.txt`.

Удалите **все** файлы `*.log` в `~/tree` одной командой `find` с `-delete` (или `find ... -exec rm {} +`).

Файл `keep.txt` должен остаться.""",
            "goals": ["Массовое удаление по шаблону", "Осторожность с -delete"],
            "hints": ["touch ~/tree/{old1.log,old2.log,keep.txt}", "find ~/tree -name '*.log' -delete", "Сначала проверьте, что найдёт команда: find ~/tree -name '*.log'"],
            "solution": "touch ~/tree/{old1.log,old2.log,keep.txt} && find ~/tree -name '*.log' -delete",
            "checks": [
                fa("/home/student/tree/old1.log", "old1.log удалён"),
                fa("/home/student/tree/old2.log", "old2.log удалён"),
                fe("/home/student/tree/keep.txt", "keep.txt остался"),
            ],
        },
        {
            "id": "m5-06",
            "title": "tar: упаковка без сжатия",
            "difficulty": 3,
            "points": 15,
            "task": """Создайте архив `~/tree.tar` (без сжатия) из каталога `~/tree`.

Используйте ключ `-C`, чтобы в архив попали пути относительно домашнего каталога (`tree/...`):

    tar -cf ~/tree.tar -C ~ tree

Проверьте состав архива: `tar -tf ~/tree.tar`.""",
            "goals": ["Создание и просмотр архивов tar"],
            "hints": ["tar -cvf ~/tree.tar -C ~ tree", "tar -tf ~/tree.tar — список файлов", "Ключ -C меняет рабочий каталог для команды"],
            "solution": "tar -cf ~/tree.tar -C ~ tree",
            "checks": [
                fe("/home/student/tree.tar", "Архив создан"),
                cok("tar -tf /home/student/tree.tar | grep -q 'tree/'", "В архиве есть содержимое tree"),
            ],
        },
        {
            "id": "m5-07",
            "title": "gzip: сжатие одного файла",
            "difficulty": 3,
            "points": 15,
            "task": """Создайте большой текстовый файл `~/tree/data.txt` (например, 2000 строк: `for i in $(seq 1 2000); do echo "line $i"; done > ~/tree/data.txt`).

Сожмите его в `~/tree/data.txt.gz` (с сохранением оригинала) и проверьте, что архив меньше исходника.

Результат сравнения сохраните в `~/tree/sizes.txt`.""",
            "goals": ["Сжатие gzip", "Сравнение размеров"],
            "hints": ["gzip -k ~/tree/data.txt", "gzip -k -9 ~/tree/data.txt — максимальное сжатие", "ls -l ~/tree/data.txt*"],
            "solution": "for i in $(seq 1 2000); do echo \"line $i\"; done > ~/tree/data.txt && gzip -k ~/tree/data.txt && ls -l ~/tree/data.txt* > ~/tree/sizes.txt",
            "checks": [
                fe("/home/student/tree/data.txt.gz", "Сжатый файл создан"),
                fe("/home/student/tree/data.txt", "Оригинал сохранён"),
                fc("/home/student/tree/sizes.txt", "data.txt", "Сравнение размеров записано"),
            ],
        },
        {
            "id": "m5-08",
            "title": "Распаковка архива",
            "difficulty": 3,
            "points": 15,
            "task": """Восстановите содержимое каталога `~/tree` из архива `~/tree.tar` в новый каталог `~/restored`.

В `~/restored` должен появиться каталог `tree` с файлами.""",
            "goals": ["Распаковка архива в нужное место", "Ключ -C"],
            "hints": ["mkdir -p ~/restored && tar -xf ~/tree.tar -C ~/restored", "ls -R ~/restored"],
            "solution": "mkdir -p ~/restored && tar -xf ~/tree.tar -C ~/restored",
            "checks": [
                de("/home/student/restored/tree", "Каталог tree восстановлен"),
                cok("test -f /home/student/restored/tree/deep.txt || test -f /home/student/restored/tree/one.txt", "Внутри есть файлы"),
            ],
        },
        {
            "id": "m5-09",
            "title": "Контрольные суммы: sha256sum",
            "difficulty": 3,
            "points": 15,
            "task": """Посчитайте sha256-сумму файла `~/note.txt` и сохраните вывод в `~/tree/sha.txt`.

В файле должна быть 64-символьная hex-строка (хэш).""",
            "goals": ["Проверять целостность файлов", "Понимать, что такое хеш"],
            "hints": ["sha256sum ~/note.txt", "sha256sum ~/note.txt > ~/tree/sha.txt", "Проверка: sha256sum -c"],
            "solution": "sha256sum ~/note.txt > ~/tree/sha.txt",
            "checks": [
                fm("/home/student/tree/sha.txt", r"^[0-9a-f]{64}", "Записан 64-символьный хеш"),
            ],
        },
        {
            "id": "m5-10",
            "title": "rsync: зеркалирование каталога",
            "difficulty": 4,
            "points": 20,
            "task": """Скопируйте каталог `~/tree` в `~/backup` с помощью `rsync -a` (архивный режим).

В `~/backup` должны появиться те же файлы. Затем измените один файл в `~/tree` и повторите rsync — только изменённый файл будет передан.""",
            "goals": ["Инкрементальное копирование", "Разница rsync и cp"],
            "hints": ["rsync -a ~/tree/ ~/backup/", "Обратите внимание на слэш в конце — он важен", "rsync -av ~/tree/ ~/backup/ — покажет, что копируется"],
            "solution": "rsync -a ~/tree/ ~/backup/",
            "checks": [
                de("/home/student/backup", "Каталог backup создан"),
                cok("ls /home/student/backup | grep -q .", "В backup есть файлы"),
                fe("/home/student/backup/one.txt", "one.txt скопирован"),
            ],
        },
        {
            "id": "m5-11",
            "title": "diff: сравнение файлов",
            "difficulty": 4,
            "points": 15,
            "task": """Создайте два файла:

    ~/tree/list1.txt:  apple, banana, cherry
    ~/tree/list2.txt:  apple, banana, melon

Сравните их командой `diff` и сохраните вывод в `~/tree/diff.txt`.

В выводе должны быть символы `<` (только в первом файле) и `>` (только во втором).""",
            "goals": ["Сравнение файлов", "Понимание вывода diff"],
            "hints": ["printf 'apple\\nbanana\\ncherry\\n' > ~/tree/list1.txt", "printf 'apple\\nbanana\\nmelon\\n' > ~/tree/list2.txt", "diff ~/tree/list1.txt ~/tree/list2.txt > ~/tree/diff.txt"],
            "solution": "printf 'apple\\nbanana\\ncherry\\n' > ~/tree/list1.txt && printf 'apple\\nbanana\\nmelon\\n' > ~/tree/list2.txt && diff ~/tree/list1.txt ~/tree/list2.txt > ~/tree/diff.txt",
            "checks": [
                fc("/home/student/tree/diff.txt", "cherry", "Есть строка из первого файла"),
                fc("/home/student/tree/diff.txt", "melon", "Есть строка из второго файла"),
            ],
        },
        {
            "id": "m5-12",
            "title": "find -mtime: файлы по возрасту",
            "difficulty": 5,
            "points": 20,
            "task": """Создайте «старый» файл `~/tree/old_report.txt` (измените дату изменения на 40 дней назад) и «свежий» файл `~/tree/new_report.txt`.

Найдите файлы, изменённые более 30 дней назад (`find -mtime +30`), и сохраните список в `~/tree/old_files.txt`.

В списке должен быть `old_report.txt` и не должно быть `new_report.txt`.""",
            "goals": ["Фильтрация по времени изменения", "Управление временем файла"],
            "hints": ["touch -d '40 days ago' ~/tree/old_report.txt", "find ~/tree -type f -mtime +30", "+30 — строго больше 30 дней"],
            "solution": "touch ~/tree/new_report.txt && touch -d '40 days ago' ~/tree/old_report.txt && find ~/tree -type f -mtime +30 > ~/tree/old_files.txt",
            "checks": [
                fc("/home/student/tree/old_files.txt", "old_report.txt", "Старый файл найден"),
                {"type": "file_not_contains", "path": "/home/student/tree/old_files.txt", "text": "new_report.txt", "title": "Свежий файл не попал в список"},
            ],
        },
    ],
}
