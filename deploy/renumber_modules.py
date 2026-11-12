"""Перенумерация модулей/заданий после вставки модуля о перенаправлениях.

m03_text -> m04_text, m04_find -> m05_find, ... m10_advanced -> m11_advanced.
Замены выполняются в обратном порядке, чтобы не было каскадных переименований.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent / "app" / "curriculum"

# файл -> (новое имя, старый префикс id, новый префикс id)
MOVE = [
    ("m10_advanced.py", "m11_advanced.py", "m10-", "m11-"),
    ("m09_system.py", "m10_system.py", "m9-", "m10-"),
    ("m08_bash.py", "m09_bash.py", "m8-", "m9-"),
    ("m07_network.py", "m08_network.py", "m7-", "m8-"),
    ("m06_users.py", "m07_users.py", "m6-", "m7-"),
    ("m05_processes.py", "m06_processes.py", "m5-", "m6-"),
    ("m04_find.py", "m05_find.py", "m4-", "m5-"),
    ("m03_text.py", "m04_text.py", "m3-", "m4-"),
]

# обратный порядок, чтобы "m10-" не превратилось в "m11-" дважды
for old_name, new_name, old_pref, new_pref in reversed(MOVE):
    src = ROOT / old_name
    if not src.exists():
        print("нет файла:", old_name)
        continue
    text = src.read_text(encoding="utf-8")
    text = text.replace('"%s' % old_pref, '"%s' % new_pref)
    text = text.replace("'%s" % old_pref, "'%s" % new_pref)
    # id модуля
    text = re.sub(r'"id": "%s"' % old_pref[:-1], '"id": "%s"' % new_pref[:-1], text)
    (ROOT / new_name).write_text(text, encoding="utf-8")
    src.unlink()
    print(f"{old_name} -> {new_name} (ids {old_pref}* -> {new_pref}*)")

# теория: переименовать ключи
for tf, mapping in [
    ("theory_1.py", [("m1-", "m1-"), ("m2-", "m2-"), ("m3-", "m3-")]),
    ("theory_2.py", [("m4-", "m5-"), ("m5-", "m6-"), ("m6-", "m7-")]),
    ("theory_3.py", [("m7-", "m8-"), ("m8-", "m9-"), ("m9-", "m10-"), ("m10-", "m11-")]),
]:
    p = ROOT / tf
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8")
    for old_pref, new_pref in reversed(mapping):
        text = text.replace('"%s' % old_pref, '"%s' % new_pref)
    p.write_text(text, encoding="utf-8")
    print("теория обновлена:", tf)
print("готово")
