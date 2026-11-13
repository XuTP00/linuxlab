"""Переносим python-http.server с порта 8080 на 8000, чтобы не конфликтовать с Angie (8080)."""
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent / "app" / "curriculum" / "m08_network.py"
text = p.read_text(encoding="utf-8")

# 1) задание «Свой веб-сервер» — порт 8080 → 8000
text = text.replace("python3 -m http.server 8080 --directory ~/site",
                    "python3 -m http.server 8000 --directory ~/site")
text = text.replace("curl http://127.0.0.1:8080", "curl http://127.0.0.1:8000")
text = text.replace("curl -s http://127.0.0.1:8080 > ~/net/local.html",
                    "curl -s http://127.0.0.1:8000 > ~/net/local.html")
text = text.replace('port(8080, "Порт 8080 слушается")',
                    'port(8000, "Порт 8000 слушается")')
# 2) проверка вывода ss
text = text.replace('fc("/home/student/net/ss.txt", "8080", "Порт 8080 виден в списке")',
                    'fc("/home/student/net/ss.txt", "8000", "Порт 8000 виден в списке")')
text = text.replace("""а на каком порту он слушает (в нашем случае `8080`""",
                    """а на каком порту он слушает (в нашем случае `8000`""")
# 3) задание про nc
text = text.replace("nc -zv 127.0.0.1 8080", "nc -zv 127.0.0.1 8000")
text = text.replace('fc("/home/student/net/nc.txt", "8080", "Упомянут порт 8080")',
                    'fc("/home/student/net/nc.txt", "8000", "Упомянут порт 8000")')
text = text.replace("порт 8080 открыт", "порт 8000 открыт")
text = text.replace("`nc -zv 127.0.0.1 8080`", "`nc -zv 127.0.0.1 8000`")

p.write_text(text, encoding="utf-8")
print("обновлено:", p.name)
print("осталось упоминаний 8080:", [l.strip()[:90] for l in text.splitlines() if "8080" in l])
