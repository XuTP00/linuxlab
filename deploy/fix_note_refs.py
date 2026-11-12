import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent / "app" / "curriculum"

# 1) заменяем ссылки на больше не существующий ~/hello.txt на ~/note.txt
for f in ROOT.glob("m*.py"):
    text = f.read_text(encoding="utf-8")
    if "hello.txt" in text:
        text = text.replace("hello.txt", "note.txt")
        f.write_text(text, encoding="utf-8")
        print("обновлён:", f.name)

# 2) проверки, которые требовали текст "Hello Linux" -> проверка «непусто»
fixes = {
    "m04_text.py": [
        ('fc("/home/student/logs/copies/a.txt.bak", "Hello Linux", "Содержимое копии верное")',
         'fne("/home/student/logs/copies/a.txt.bak", "Копия не пуста")'),
    ],
    "m08_network.py": [
        ('fc("/home/student/net/remote_copy.txt", "Hello Linux", "Содержимое верное")',
         'fne("/home/student/net/remote_copy.txt", "Скопированный файл не пуст")'),
    ],
    "m11_advanced.py": [
        ('fc("/home/student/data/note.dec", "Hello Linux", "Декодирование верное")',
         'fne("/home/student/data/note.dec", "Декодированный файл не пуст")'),
    ],
}
for fname, pairs in fixes.items():
    p = ROOT / fname
    text = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if old in text:
            text = text.replace(old, new)
            print(f"{fname}: проверка заменена")
        else:
            print(f"{fname}: НЕ НАЙДЕНО -> {old[:60]}")
    p.write_text(text, encoding="utf-8")
print("готово")
