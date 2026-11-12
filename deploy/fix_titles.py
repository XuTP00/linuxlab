"""Обновить номера модулей в заголовках после перенумерации."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / "app" / "curriculum"

FIX = [
    ("m04_text.py", 3, 4),
    ("m05_find.py", 4, 5),
    ("m06_processes.py", 5, 6),
    ("m07_users.py", 6, 7),
    ("m08_network.py", 7, 8),
    ("m09_bash.py", 8, 9),
    ("m10_system.py", 9, 10),
    ("m11_advanced.py", 10, 11),
]

for fname, old, new in FIX:
    p = ROOT / fname
    text = p.read_text(encoding="utf-8")
    before = text
    text = text.replace(f'"title": "Модуль {old}.', f'"title": "Модуль {new}.')
    if text != before:
        p.write_text(text, encoding="utf-8")
        print(f"{fname}: Модуль {old} -> Модуль {new}")
    else:
        print(f"{fname}: заголовок не найден")
