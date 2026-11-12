"""Помощники для описания проверок в заданиях."""


def fe(path, title=""):
    return {"type": "file_exists", "path": path, "title": title}


def fa(path, title=""):
    return {"type": "file_absent", "path": path, "title": title}


def fc(path, text, title="", ignore_case=False):
    return {"type": "file_contains", "path": path, "text": text, "title": title, "ignore_case": ignore_case}


def fnc(path, text, title=""):
    return {"type": "file_not_contains", "path": path, "text": text, "title": title}


def fm(path, regex, title="", flags="m"):
    return {"type": "file_matches", "path": path, "regex": regex, "title": title, "flags": flags}


def fl(path, title="", **kw):
    d = {"type": "file_lines", "path": path, "title": title}
    d.update(kw)
    return d


def fne(path, title=""):
    return {"type": "file_nonempty", "path": path, "title": title}


def de(path, title=""):
    return {"type": "dir_exists", "path": path, "title": title}


def dc(path, names=None, title="", **kw):
    d = {"type": "dir_contains", "path": path, "title": title}
    if names:
        d["names"] = names
    d.update(kw)
    return d


def fcount(path, glob="*", title="", **kw):
    d = {"type": "file_count", "path": path, "glob": glob, "title": title}
    d.update(kw)
    return d


def fmode(path, mode, title=""):
    return {"type": "file_mode", "path": path, "mode": mode, "title": title}


def fowner(path, user=None, group=None, title=""):
    d = {"type": "file_owner", "path": path, "title": title}
    if user:
        d["user"] = user
    if group:
        d["group"] = group
    return d


def slink(path, target, title=""):
    return {"type": "symlink", "path": path, "target": target, "title": title}


def cok(cmd, title=""):
    return {"type": "cmd_ok", "cmd": cmd, "title": title}


def cfail(cmd, title=""):
    return {"type": "cmd_fail", "cmd": cmd, "title": title}


def ccontains(cmd, text, title="", ignore_case=False):
    return {"type": "cmd_stdout_contains", "cmd": cmd, "text": text, "title": title, "ignore_case": ignore_case}


def cnot(cmd, text, title=""):
    return {"type": "cmd_stdout_not_contains", "cmd": cmd, "text": text, "title": title}


def cmatch(cmd, regex, title=""):
    return {"type": "cmd_stdout_matches", "cmd": cmd, "regex": regex, "title": title}


def ceq(cmd, text, title=""):
    return {"type": "cmd_stdout_equals", "cmd": cmd, "text": text, "title": title}


def ue(name, title=""):
    return {"type": "user_exists", "name": name, "title": title}


def ge(name, title=""):
    return {"type": "group_exists", "name": name, "title": title}


def uig(user, group, title=""):
    return {"type": "user_in_group", "user": user, "group": group, "title": title}


def cron(text, title=""):
    return {"type": "cron_contains", "text": text, "title": title}


def hist(text, title=""):
    return {"type": "history_contains", "text": text, "title": title}


def out(text, title=""):
    """Текст должен появиться в выводе терминала (ученик видел его на экране)."""
    return {"type": "output_contains", "text": text, "title": title}


def outnot(text, title=""):
    return {"type": "output_not_contains", "text": text, "title": title}


def outmatch(regex, title=""):
    """В выводе терминала должно быть что-то, подходящее под регулярку."""
    return {"type": "output_matches", "regex": regex, "title": title}


def fsize(path, bytes_, title=""):
    return {"type": "file_size_min", "path": path, "bytes": bytes_, "title": title}


def proc(pattern, title=""):
    return {"type": "proc_running", "pattern": pattern, "title": title}


def no_proc(pattern, title=""):
    return {"type": "proc_not_running", "pattern": pattern, "title": title}


def port(p, title=""):
    return {"type": "port_listening", "port": p, "title": title}


def inpath(name, title=""):
    return {"type": "file_exists_in_path", "name": name, "title": title}
