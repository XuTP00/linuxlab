"""Движок проверки заданий."""
from __future__ import annotations

import fnmatch
import os
import re
import shlex
import time
from typing import Any

from .sessions import ShellSession

MAX_READ = 200_000


class CheckResult:
    __slots__ = ("ok", "message", "title")

    def __init__(self, ok: bool, message: str, title: str = ""):
        self.ok = ok
        self.message = message
        self.title = title

    def as_dict(self) -> dict:
        return {"ok": self.ok, "message": self.message, "title": self.title}


def _read_file(session: ShellSession, path: str, limit: int = MAX_READ) -> str | None:
    if not _exists(session, path):
        return None
    code, out, _ = session.exec_check(f"cat {shlex.quote(path)} 2>/dev/null | head -c {limit}")
    if code != 0:
        return None
    return out


def _exists(session: ShellSession, path: str) -> bool:
    code, _, _ = session.exec_check(f"test -e {shlex.quote(path)} && echo yes")
    return code == 0


def _stat(session: ShellSession, path: str, fmt: str) -> str | None:
    code, out, _ = session.exec_check(f"stat -c {shlex.quote(fmt)} {shlex.quote(path)} 2>/dev/null")
    if code != 0:
        return None
    return out.strip()


def _procs(session: ShellSession, pattern: str) -> list[str]:
    """Список процессов, чья командная строка содержит pattern (без самой проверки)."""
    code, out, _ = session.exec_check(
        f"ps -eo args | grep -F {shlex.quote(pattern)} | grep -v grep | grep -v 'ps -eo'")
    if code != 0:
        return []
    return [line for line in out.splitlines() if line.strip()]


def _session_output(session: ShellSession) -> str:
    """Весь вывод терминала сессии (то, что ученик видел на экране)."""
    try:
        data, _ = session.read_since(0)
        return data
    except Exception:
        return ""


def evaluate(session: ShellSession, spec: dict[str, Any]) -> CheckResult:
    """Выполняет одну проверку. spec — словарь вида {'type': ..., ...}."""
    t = spec.get("type", "")
    title = spec.get("title", "")
    path = spec.get("path", "")

    if t == "file_exists":
        ok = _exists(session, path)
        return CheckResult(ok, f"Файл {path} {'найден' if ok else 'не найден'}", title)

    if t == "file_exists_wait":
        timeout = int(spec.get("timeout", 90))
        deadline = time.time() + timeout
        ok = _exists(session, path)
        while not ok and time.time() < deadline:
            time.sleep(5)
            ok = _exists(session, path)
        return CheckResult(ok, f"Файл {path} {'появился' if ok else 'не появился за отведённое время'}", title)

    if t == "file_absent":
        ok = not _exists(session, path)
        return CheckResult(ok, f"Файл {path} {'отсутствует (верно)' if ok else 'всё ещё существует'}", title)

    if t == "file_contains":
        data = _read_file(session, path)
        if data is None:
            return CheckResult(False, f"Файл {path} не найден", title)
        needle = spec.get("text", "")
        hay = data.lower() if spec.get("ignore_case") else data
        nd = needle.lower() if spec.get("ignore_case") else needle
        ok = nd in hay
        return CheckResult(ok, f"{'Строка найдена' if ok else 'Строка не найдена'}: «{needle}»", title)

    if t == "file_not_contains":
        data = _read_file(session, path)
        if data is None:
            return CheckResult(False, f"Файл {path} не найден", title)
        needle = spec.get("text", "")
        ok = needle not in data
        return CheckResult(ok, f"{'Строки нет (верно)' if ok else 'Найдена лишняя строка'}: «{needle}»", title)

    if t == "file_matches":
        data = _read_file(session, path)
        if data is None:
            return CheckResult(False, f"Файл {path} не найден", title)
        pattern = spec.get("regex", "")
        flags = re.MULTILINE if "m" in spec.get("flags", "m") else 0
        ok = bool(re.search(pattern, data, flags))
        return CheckResult(ok, f"{'Совпадение найдено' if ok else 'Совпадение не найдено'} по /{pattern}/", title)

    if t == "file_lines":
        data = _read_file(session, path)
        if data is None:
            return CheckResult(False, f"Файл {path} не найден", title)
        n = len(data.splitlines())
        lo = spec.get("min")
        hi = spec.get("max")
        ex = spec.get("exact")
        ok = True
        if ex is not None:
            ok = n == ex
        if lo is not None:
            ok = ok and n >= lo
        if hi is not None:
            ok = ok and n <= hi
        expect = []
        if ex is not None:
            expect.append(f"ровно {ex}")
        if lo is not None:
            expect.append(f"не меньше {lo}")
        if hi is not None:
            expect.append(f"не больше {hi}")
        return CheckResult(ok, f"Строк в файле: {n} (ожидалось: {', '.join(expect) or 'любое число'})", title)

    if t == "file_nonempty":
        data = _read_file(session, path)
        ok = data is not None and data.strip() != ""
        return CheckResult(ok, f"Файл {path} {'не пуст (верно)' if ok else 'пуст или отсутствует'}", title)

    if t == "file_empty":
        data = _read_file(session, path)
        ok = data is not None and data.strip() == ""
        return CheckResult(ok, f"Файл {path} {'пуст (верно)' if ok else 'не пуст или отсутствует'}", title)

    if t == "dir_exists":
        code, _, _ = session.exec_check(f"test -d {shlex.quote(path)}")
        ok = code == 0
        return CheckResult(ok, f"Каталог {path} {'существует' if ok else 'не найден'}", title)

    if t == "dir_contains":
        code, out, _ = session.exec_check(f"ls -A {shlex.quote(path)} 2>/dev/null")
        if code != 0:
            return CheckResult(False, f"Каталог {path} не найден", title)
        names = set(out.split())
        need = spec.get("names", [])
        missing = [n for n in need if n not in names]
        ok = not missing and (spec.get("min") is None or len(names) >= spec["min"])
        msg = f"В каталоге {len(names)} элементов" + (f", не хватает: {missing}" if missing else "")
        return CheckResult(ok, msg, title)

    if t == "file_count":
        code, out, _ = session.exec_check(
            f"ls -A {shlex.quote(path)} 2>/dev/null")
        if code != 0:
            return CheckResult(False, f"Каталог {path} не найден", title)
        pattern = spec.get("glob", "*")
        n = len([x for x in out.split() if fnmatch.fnmatch(x, pattern)])
        lo = spec.get("min", 1)
        hi = spec.get("max")
        ok = n >= lo and (hi is None or n <= hi)
        expect = f"не меньше {lo}" + (f", не больше {hi}" if hi is not None else "")
        return CheckResult(ok, f"Подходящих файлов ({pattern}): {n} (ожидалось {expect})", title)

    if t == "file_mode":
        mode = _stat(session, path, "%a")
        if mode is None:
            return CheckResult(False, f"Файл {path} не найден", title)
        want = str(spec.get("mode", ""))
        ok = mode == want.lstrip("0") or mode == want
        return CheckResult(ok, f"Права {path}: {mode} (ожидалось {want})", title)

    if t == "file_owner":
        user = _stat(session, path, "%U")
        group = _stat(session, path, "%G")
        ok = True
        if spec.get("user"):
            ok = ok and user == spec["user"]
        if spec.get("group"):
            ok = ok and group == spec["group"]
        return CheckResult(ok, f"Владелец {path}: {user}:{group} (ожидалось {spec})", title)

    if t == "symlink":
        code, out, _ = session.exec_check(f"readlink -f {shlex.quote(path)} 2>/dev/null")
        target = out.strip()
        want = spec.get("target", "")
        ok = target == want or target == os.path.realpath(want)
        return CheckResult(ok, f"Ссылка {path} → {target or 'нет'} (ожидалось {want})", title)

    if t == "cmd_ok":
        cmd = spec["cmd"]
        code, out, err = session.exec_check(cmd)
        ok = code == 0
        return CheckResult(ok, f"Команда успешно выполнилась" if ok else f"Команда вернула код {code}: {err.strip()[:160]}", title)

    if t == "cmd_fail":
        cmd = spec["cmd"]
        code, _, _ = session.exec_check(cmd)
        ok = code != 0
        return CheckResult(ok, "Команда завершилась с ошибкой (верно)" if ok else "Команда неожиданно успешна", title)

    if t in ("cmd_stdout_contains", "cmd_stdout_not_contains"):
        cmd = spec["cmd"]
        _, out, _ = session.exec_check(cmd)
        needle = spec.get("text", "")
        found = needle.lower() in out.lower() if spec.get("ignore_case") else needle in out
        if t == "cmd_stdout_contains":
            ok = found
            msg = f"{'Найдено' if ok else 'Не найдено'}: «{needle}»"
        else:
            ok = not found
            msg = f"{'Отсутствует (верно)' if ok else 'Присутствует'}: «{needle}»"
        return CheckResult(ok, msg, title)

    if t == "cmd_stdout_matches":
        cmd = spec["cmd"]
        _, out, _ = session.exec_check(cmd)
        ok = bool(re.search(spec.get("regex", ""), out, re.MULTILINE))
        return CheckResult(ok, f"{'Совпадение есть' if ok else 'Совпадения нет'} по /{spec.get('regex')}/", title)

    if t == "cmd_stdout_equals":
        cmd = spec["cmd"]
        _, out, _ = session.exec_check(cmd)
        ok = out.strip() == spec.get("text", "").strip()
        return CheckResult(ok, f"Вывод: «{out.strip()[:80]}» (ожидалось «{spec.get('text','').strip()[:80]}»)", title)

    if t == "user_exists":
        code, _, _ = session.exec_check(f"id {shlex.quote(spec['name'])} >/dev/null 2>&1")
        return CheckResult(code == 0, f"Пользователь {spec['name']} {'существует' if code == 0 else 'не найден'}", title)

    if t == "group_exists":
        code, _, _ = session.exec_check(f"getent group {shlex.quote(spec['name'])} >/dev/null 2>&1")
        return CheckResult(code == 0, f"Группа {spec['name']} {'существует' if code == 0 else 'не найдена'}", title)

    if t == "user_in_group":
        code, _, _ = session.exec_check(
            f"id -nG {shlex.quote(spec['user'])} | tr ' ' '\\n' | grep -qx {shlex.quote(spec['group'])}")
        ok = code == 0
        return CheckResult(ok, f"{spec['user']} {'входит' if ok else 'не входит'} в группу {spec['group']}", title)

    if t == "cron_contains":
        code, out, _ = session.exec_check("crontab -l 2>/dev/null", user="student", cwd="/home/student")
        ok = spec.get("text", "") in out
        return CheckResult(ok, f"{'Задание найдено' if ok else 'Задание не найдено'}: «{spec.get('text','')}»", title)

    if t == "history_contains":
        joined = "\n".join(session.commands)
        needle = spec.get("text", "")
        ok = needle in joined
        return CheckResult(ok, f"{'Команда использована' if ok else 'Команда не использована'}: {needle}", title)

    if t == "output_contains":
        text = spec.get("text", "")
        ok = text in _session_output(session)
        return CheckResult(ok, f"{'Есть в выводе терминала' if ok else 'Не найдено в выводе терминала'}: «{text}»", title)

    if t == "output_not_contains":
        text = spec.get("text", "")
        ok = text not in _session_output(session)
        return CheckResult(ok, f"{'Нет в выводе (верно)' if ok else 'Всё же появилось в выводе'}: «{text}»", title)

    if t == "output_matches":
        text = _session_output(session)
        pattern = spec.get("regex", "")
        ok = bool(re.search(pattern, text, re.MULTILINE))
        return CheckResult(ok, f"{'Совпадение найдено' if ok else 'Совпадение не найдено'} по /{pattern}/", title)

    if t == "file_size_min":
        size = _stat(session, path, "%s")
        if size is None:
            return CheckResult(False, f"Файл {path} не найден", title)
        ok = int(size) >= int(spec.get("bytes", 0))
        return CheckResult(ok, f"Размер {path}: {size} байт (нужно ≥ {spec.get('bytes')})", title)

    if t == "proc_running":
        found = _procs(session, spec["pattern"])
        ok = len(found) > 0
        return CheckResult(ok, f"Процесс {spec['pattern']} {'запущен' if ok else 'не найден'}", title)

    if t == "proc_not_running":
        found = _procs(session, spec["pattern"])
        ok = len(found) == 0
        return CheckResult(ok, f"Процесс {spec['pattern']} {'не запущен (верно)' if ok else 'всё ещё работает'}", title)

    if t == "port_listening":
        code, out, _ = session.exec_check(
            f"ss -tulnH 2>/dev/null | grep -q ':{spec['port']} '")
        ok = code == 0
        return CheckResult(ok, f"Порт {spec['port']} {'слушается' if ok else 'не слушается'}", title)

    if t == "file_exists_in_path":
        code, _, _ = session.exec_check(f"command -v {shlex.quote(spec['name'])} >/dev/null 2>&1")
        return CheckResult(code == 0, f"Программа {spec['name']} {'найдена в PATH' if code == 0 else 'не найдена'}", title)

    return CheckResult(False, f"Неизвестный тип проверки: {t}", title)
