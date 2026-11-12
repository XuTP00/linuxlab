"""Модуль 3. Работа с текстом: grep, cut, sort, sed, awk и пайпы."""
from .helpers import dc, fa, fc, fe, fm, fl, fne, hist

LOG_LINES = """2026-01-01 10:00 INFO  service started
2026-01-01 10:05 ERROR connection refused
2026-01-02 10:07 INFO  retrying
2026-01-02 10:09 ERROR timeout
2026-01-02 10:10 INFO  service ok"""

MODULE = {
    "id": "m4",
    "title": "Модуль 4. Текст: grep, sed, awk",
    "icon": "🔤",
    "summary": "Инструменты работы с текстом и потоками: grep, cut, sort, uniq, wc, sed, awk, tee, xargs. Механика пайпов уже знакома из модуля 3.",
    "tasks": [
        {
            "id": "m4-01",
            "title": "Создаём лог-файл",
            "difficulty": 2,
            "points": 10,
            "task": """Создайте каталог `~/logs` и файл `~/logs/app.log` с **ровно** такими пятью строками:

    2026-01-01 10:00 INFO  service started
    2026-01-01 10:05 ERROR connection refused
    2026-01-02 10:07 INFO  retrying
    2026-01-02 10:09 ERROR timeout
    2026-01-02 10:10 INFO  service ok

Проще всего сделать так: сначала `cat > ~/logs/app.log`, затем ввести строки и нажать Ctrl+D.""",
            "goals": ["Создание файла через перенаправление", "Многострочный ввод"],
            "hints": ["mkdir -p ~/logs", "cat > ~/logs/app.log — затем строки и Ctrl+D", "Проверить: wc -l ~/logs/app.log"],
            "solution": "mkdir -p ~/logs && cat > ~/logs/app.log << 'EOF'\n" + LOG_LINES + "\nEOF",
            "checks": [
                fe("/home/student/logs/app.log", "Лог-файл создан"),
                fl("/home/student/logs/app.log", "В файле ровно 5 строк", exact=5),
                fc("/home/student/logs/app.log", "connection refused", "Содержимое совпадает с заданием"),
            ],
        },
        {
            "id": "m4-02",
            "title": "grep: ищем ошибки",
            "difficulty": 2,
            "points": 10,
            "task": """Выведите из `~/logs/app.log` только строки, содержащие слово `ERROR`, и сохраните их в `~/logs/errors.txt`.

В результате должно быть ровно **2 строки**.""",
            "goals": ["Поиск по содержимому", "Перенаправление вывода в файл"],
            "hints": ["grep ERROR ~/logs/app.log", "grep ERROR ~/logs/app.log > ~/logs/errors.txt", "grep -n покажет номера строк"],
            "solution": "grep ERROR ~/logs/app.log > ~/logs/errors.txt",
            "checks": [
                fl("/home/student/logs/errors.txt", "Найдено ровно 2 строки с ERROR", exact=2),
                fc("/home/student/logs/errors.txt", "connection refused", "Первая ошибка попала в файл"),
                fc("/home/student/logs/errors.txt", "timeout", "Вторая ошибка попала в файл"),
            ],
        },
        {
            "id": "m4-03",
            "title": "grep -c: считаем вхождения",
            "difficulty": 2,
            "points": 10,
            "task": """Посчитайте, сколько строк в `~/logs/app.log` содержат `INFO`, и запишите только число в `~/logs/info_count.txt`.

Ответ: 3.""",
            "goals": ["Подсчёт совпадений", "Вывод без лишнего текста"],
            "hints": ["grep -c INFO ~/logs/app.log", "grep -c INFO ~/logs/app.log > ~/logs/info_count.txt"],
            "solution": "grep -c INFO ~/logs/app.log > ~/logs/info_count.txt",
            "checks": [
                fm("/home/student/logs/info_count.txt", r"^3$", "Записано число 3"),
            ],
        },
        {
            "id": "m4-04",
            "title": "grep -v: исключаем лишнее",
            "difficulty": 2,
            "points": 10,
            "task": """Сохраните в `~/logs/no_errors.txt` все строки лога, **не** содержащие `ERROR`.

Таких строк ровно **3**.""",
            "goals": ["Инвертированный поиск"],
            "hints": ["grep -v ERROR ~/logs/app.log", "grep -v ERROR ~/logs/app.log > ~/logs/no_errors.txt"],
            "solution": "grep -v ERROR ~/logs/app.log > ~/logs/no_errors.txt",
            "checks": [
                fl("/home/student/logs/no_errors.txt", "Ровно 3 строки", exact=3),
                {"type": "file_not_contains", "path": "/home/student/logs/no_errors.txt", "text": "ERROR", "title": "ERROR не должно остаться в файле"},
            ],
        },
        {
            "id": "m4-05",
            "title": "cut: вырезаем колонки",
            "difficulty": 3,
            "points": 15,
            "task": """В логе поля разделены пробелами. Вырежите первую колонку (дату) и сохраните **уникальные** даты в `~/logs/dates.txt`.

В файле должно быть 2 строки: `2026-01-01` и `2026-01-02`.""",
            "goals": ["Вырезать поле по разделителю", "Дедупликация через sort -u"],
            "hints": ["cut -d' ' -f1 ~/logs/app.log", "cut -d' ' -f1 ~/logs/app.log | sort -u > ~/logs/dates.txt"],
            "solution": "cut -d' ' -f1 ~/logs/app.log | sort -u > ~/logs/dates.txt",
            "checks": [
                fl("/home/student/logs/dates.txt", "Ровно 2 уникальные даты", exact=2),
                fc("/home/student/logs/dates.txt", "2026-01-01", "Дата 2026-01-01 присутствует"),
                fc("/home/student/logs/dates.txt", "2026-01-02", "Дата 2026-01-02 присутствует"),
            ],
        },
        {
            "id": "m4-06",
            "title": "cut: время",
            "difficulty": 3,
            "points": 10,
            "task": """Вырежите вторую колонку лога (время) в файл `~/logs/times.txt`.

В файле должно быть 5 строк, и среди них — `10:05`.""",
            "goals": ["Нумерация полей", "Работа с cut"],
            "hints": ["cut -d' ' -f2 ~/logs/app.log > ~/logs/times.txt", "cat ~/logs/times.txt"],
            "solution": "cut -d' ' -f2 ~/logs/app.log > ~/logs/times.txt",
            "checks": [
                fl("/home/student/logs/times.txt", "5 строк времени", exact=5),
                fc("/home/student/logs/times.txt", "10:05", "Время 10:05 на месте"),
            ],
        },
        {
            "id": "m4-07",
            "title": "sort: порядок по времени",
            "difficulty": 3,
            "points": 15,
            "task": """Отсортируйте лог по времени (вторая колонка) и сохраните результат в `~/logs/sorted.txt`.

Первой строкой в результате должна оказаться запись `2026-01-01 10:00 INFO  service started`.""",
            "goals": ["Сортировка по ключу", "Стабильность результата"],
            "hints": ["sort -k2 ~/logs/app.log", "sort -k2 ~/logs/app.log > ~/logs/sorted.txt", "Ключ -n — числовая сортировка"],
            "solution": "sort -k2 ~/logs/app.log > ~/logs/sorted.txt",
            "checks": [
                fm("/home/student/logs/sorted.txt", r"^2026-01-01 10:00 INFO  service started", "Первая строка — самая ранняя запись"),
            ],
        },
        {
            "id": "m4-08",
            "title": "uniq -c: считаем повторы",
            "difficulty": 3,
            "points": 15,
            "task": """Посчитайте, сколько раз встречается каждый уровень логирования, и сохраните результат в `~/logs/levels.txt`.

Ожидаемый вид строк: `3 INFO` и `2 ERROR` (с пробелами).""",
            "goals": ["Считать повторы", "Понимать, что uniq требует отсортированный ввод"],
            "hints": ["cut -d' ' -f3 ~/logs/app.log | sort | uniq -c", "cut -d' ' -f3 ~/logs/app.log | sort | uniq -c > ~/logs/levels.txt", "uniq работает только с отсортированным потоком"],
            "solution": "cut -d' ' -f3 ~/logs/app.log | sort | uniq -c > ~/logs/levels.txt",
            "checks": [
                fm("/home/student/logs/levels.txt", r"3\s+INFO", "Найдена строка «3 INFO»"),
                fm("/home/student/logs/levels.txt", r"2\s+ERROR", "Найдена строка «2 ERROR»"),
            ],
        },
        {
            "id": "m4-09",
            "title": "wc -l: считаем строки",
            "difficulty": 2,
            "points": 10,
            "task": """Посчитайте количество строк в `~/logs/app.log` и сохраните вывод `wc -l` в `~/logs/lines.txt`.

В файле должно быть число 5 (вместе с именем файла — это нормально).""",
            "goals": ["Подсчёт строк", "Разница между wc и wc -l"],
            "hints": ["wc -l ~/logs/app.log", "wc -l ~/logs/app.log > ~/logs/lines.txt"],
            "solution": "wc -l ~/logs/app.log > ~/logs/lines.txt",
            "checks": [
                fm("/home/student/logs/lines.txt", r"\b5\b", "Число 5 найдено в выводе wc"),
            ],
        },
        {
            "id": "m4-10",
            "title": "sort -n: числа по порядку",
            "difficulty": 3,
            "points": 15,
            "task": """Создайте файл `~/logs/nums.txt` с числами (каждое с новой строки):

    10
    2
    33
    4

Отсортируйте их **по числовому** значению и сохраните в `~/logs/nums_sorted.txt`.

Первое число в результате — `2` (не `10`!).""",
            "goals": ["Числовая сортировка", "Разница sort и sort -n"],
            "hints": ["printf '10\\n2\\n33\\n4\\n' > ~/logs/nums.txt", "sort -n ~/logs/nums.txt > ~/logs/nums_sorted.txt", "Без -n сортировка идёт как по строкам: 10, 2, 33, 4"],
            "solution": "printf '10\\n2\\n33\\n4\\n' > ~/logs/nums.txt && sort -n ~/logs/nums.txt > ~/logs/nums_sorted.txt",
            "checks": [
                fl("/home/student/logs/nums.txt", "4 числа", exact=4),
                fm("/home/student/logs/nums_sorted.txt", r"^2$", "Первым идёт число 2"),
                fm("/home/student/logs/nums_sorted.txt", r"^33$", "Число 33 не потерялось"),
            ],
        },
        {
            "id": "m4-11",
            "title": "sed: замена текста",
            "difficulty": 3,
            "points": 15,
            "task": """Сделайте копию лога, в которой все `ERROR` заменены на `CRITICAL`, и сохраните её в `~/logs/app_fixed.log`.

Старый оригинал `~/logs/app.log` должен остаться без изменений.""",
            "goals": ["Потоковая замена в sed", "Не трогать оригинал"],
            "hints": ["sed 's/ERROR/CRITICAL/g' ~/logs/app.log > ~/logs/app_fixed.log", "Ключ g заменяет все вхождения в строке"],
            "solution": "sed 's/ERROR/CRITICAL/g' ~/logs/app.log > ~/logs/app_fixed.log",
            "checks": [
                fc("/home/student/logs/app_fixed.log", "CRITICAL", "В копии есть CRITICAL"),
                {"type": "file_not_contains", "path": "/home/student/logs/app_fixed.log", "text": "ERROR", "title": "В копии не осталось ERROR"},
                fc("/home/student/logs/app.log", "ERROR", "Оригинал не изменён"),
            ],
        },
        {
            "id": "m4-12",
            "title": "sed -i: правим файл на месте",
            "difficulty": 4,
            "points": 15,
            "task": """Создайте файл `~/logs/notes.txt` со строкой `status: old`.

Затем измените его **на месте** (`sed -i`), заменив `old` на `new`, и при этом сохраните резервную копию `~/logs/notes.txt.bak` (ключ `-i.bak`).

В `notes.txt` должно быть `status: new`, в `notes.txt.bak` — `status: old`.""",
            "goals": ["Редактирование на месте", "Резервные копии sed"],
            "hints": ["echo 'status: old' > ~/logs/notes.txt", "sed -i.bak 's/old/new/' ~/logs/notes.txt", "ls ~/logs — увидите notes.txt и notes.txt.bak"],
            "solution": "echo 'status: old' > ~/logs/notes.txt && sed -i.bak 's/old/new/' ~/logs/notes.txt",
            "checks": [
                fc("/home/student/logs/notes.txt", "status: new", "Файл изменён на месте"),
                fe("/home/student/logs/notes.txt.bak", "Резервная копия создана"),
                fc("/home/student/logs/notes.txt.bak", "status: old", "В копии — исходное значение"),
            ],
        },
        {
            "id": "m4-13",
            "title": "awk: колонки и условия",
            "difficulty": 4,
            "points": 20,
            "task": """С помощью `awk` выполните два действия:

1. Сохраните в `~/logs/times_awk.txt` вторую колонку лога (время) — 5 строк.
2. Сохраните в `~/logs/info_lines.txt` только строки, где третья колонка равна `INFO` — 3 строки.

Подсказка по синтаксису: `awk '{print $2}'`, `awk '$3==\"INFO\"'`.""",
            "goals": ["Поля awk и автоматические переменные $1, $2, $3", "Условия в awk"],
            "hints": ["awk '{print $2}' ~/logs/app.log > ~/logs/times_awk.txt", "awk '$3==\"INFO\"' ~/logs/app.log > ~/logs/info_lines.txt", "awk -F' ' меняет разделитель полей"],
            "solution": "awk '{print $2}' ~/logs/app.log > ~/logs/times_awk.txt && awk '$3==\"INFO\"' ~/logs/app.log > ~/logs/info_lines.txt",
            "checks": [
                fl("/home/student/logs/times_awk.txt", "5 строк времени", exact=5),
                fl("/home/student/logs/info_lines.txt", "3 строки INFO", exact=3),
            ],
        },
        {
            "id": "m4-14",
            "title": "tee: смотрю и сохраняю",
            "difficulty": 3,
            "points": 15,
            "task": """Выведите на экран только строки лога с `INFO` **и одновременно** сохраните их в `~/logs/info_only.txt` (в файле должно быть 3 строки).

Для этого используйте `tee`.""",
            "goals": ["Дублирование потока", "Понять, что tee пишет в файл и в stdout"],
            "hints": ["grep INFO ~/logs/app.log | tee ~/logs/info_only.txt", "tee без ключа -a перезаписывает файл"],
            "solution": "grep INFO ~/logs/app.log | tee ~/logs/info_only.txt",
            "checks": [
                fl("/home/student/logs/info_only.txt", "3 строки INFO", exact=3),
                hist("tee", "Вы использовали tee"),
            ],
        },
        {
            "id": "m4-15",
            "title": "xargs: применяем команду к списку",
            "difficulty": 4,
            "points": 20,
            "task": """Создайте каталог `~/logs/files` и в нём файлы `a.txt`, `b.txt`, `c.txt`.

Создайте список имён `~/logs/args.txt` (по одному имени на строку: a.txt, b.txt, c.txt).

Используя `xargs`, скопируйте `~/note.txt` в `~/logs/copies/` с добавлением `.bak` к имени:
`a.txt` → `~/logs/copies/a.txt.bak` и так далее.

Справочник: `cat args.txt | xargs -I{} cp ~/note.txt ~/logs/copies/{}.bak`.""",
            "goals": ["Понять, зачем нужен xargs", "Подстановка строки через -I{}"],
            "hints": ["mkdir -p ~/logs/files ~/logs/copies", "printf 'a.txt\\nb.txt\\nc.txt\\n' > ~/logs/args.txt", "cat ~/logs/args.txt | xargs -I{} cp ~/note.txt ~/logs/copies/{}.bak"],
            "solution": "mkdir -p ~/logs/files ~/logs/copies && touch ~/logs/files/{a.txt,b.txt,c.txt} && printf 'a.txt\\nb.txt\\nc.txt\\n' > ~/logs/args.txt && cat ~/logs/args.txt | xargs -I{} cp ~/note.txt ~/logs/copies/{}.bak",
            "checks": [
                dc("/home/student/logs/copies", names=["a.txt.bak", "b.txt.bak", "c.txt.bak"], title="Созданы все три копии"),
                fne("/home/student/logs/copies/a.txt.bak", "Копия не пуста"),
                hist("xargs", "Вы использовали xargs"),
            ],
        },
    ],
}
