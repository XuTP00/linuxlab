"""Перенос теории модуля «Текст, пайпы» из theory_1 в theory_2 (id m3-* -> m4-*)."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent / "app" / "curriculum"
t1 = ROOT / "theory_1.py"
t2 = ROOT / "theory_2.py"

text = t1.read_text(encoding="utf-8")
entries = re.findall(r'    "(m3-\d+)": """(.*?)""",\n', text, re.S)
print("найдено записей m3-*:", len(entries))

# вырезаем их из theory_1
for tid, body in entries:
    text = text.replace(f'    "{tid}": """{body}""",\n', "")

block = "\n".join(f'    "{tid.replace("m3-", "m4-", 1)}": """{body}""",\n' for tid, body in entries)
t2_text = t2.read_text(encoding="utf-8")
t2_text = t2_text.replace('THEORY_2 = {\n', 'THEORY_2 = {\n' + block, 1)
t2.write_text(t2_text, encoding="utf-8")
t1.write_text(text, encoding="utf-8")
print("готово: теория текстового модуля перенесена в theory_2 как m4-*")
