"""Полная валидация курса.

Для каждого задания эталонное решение выполняется в контейнере от имени ученика
(неинтерактивно — детерминированно), его вывод добавляется в буфер терминала
сессии, после чего прогоняются все проверки задания.
"""
import subprocess
import sys
import time

sys.path.insert(0, "/opt/linuxlab")
from app.curriculum import MODULES          # noqa: E402
from app.checker import evaluate           # noqa: E402
from app.sessions import ShellSession      # noqa: E402

CONTAINER = "linuxlab-validate"


def main():
    subprocess.run(["docker", "rm", "-f", CONTAINER], capture_output=True)
    subprocess.run(["docker", "run", "-d", "--name", CONTAINER, "--hostname", "lab",
                    "linuxlab/lab:latest"], check=True, capture_output=True)
    time.sleep(3)
    session = ShellSession("validate")
    session.container = CONTAINER

    total = passed = 0
    problems = []
    try:
        for m in MODULES:
            for t in m["tasks"]:
                total += 1
                sol = t.get("solution_auto") or t.get("solution", "")
                session.commands.append(sol)
                try:
                    code, out, err = session.exec_check(
                        sol, timeout=180, user="student", cwd="/home/student")
                except Exception as exc:
                    problems.append((t["id"], f"ошибка запуска: {exc}"))
                    print(f"[FAIL] {t['id']} :: запуск: {exc}", flush=True)
                    continue
                # вывод решения попадает в «терминал», чтобы работали проверки по выводу
                session._push(out + err)
                st = subprocess.run(["docker", "inspect", "-f", "{{.State.Status}} {{.State.ExitCode}}",
                                     CONTAINER], capture_output=True, text=True)
                if "running" not in st.stdout:
                    print(f"[!] контейнер в состоянии {st.stdout.strip()} после {t['id']}", flush=True)
                ok = True
                details = []
                for spec in t["checks"]:
                    try:
                        cr = evaluate(session, spec)
                    except Exception as e:
                        details.append(f"EXC {e}")
                        ok = False
                        continue
                    if not cr.ok:
                        ok = False
                        details.append(f"{spec.get('title') or spec.get('type')}: {cr.message}")
                if ok:
                    passed += 1
                    print(f"[OK]   {t['id']} {t['title']}", flush=True)
                else:
                    problems.append((t["id"], "; ".join(details)))
                    print(f"[FAIL] {t['id']} {t['title']} :: {'; '.join(details)}", flush=True)
    finally:
        subprocess.run(["docker", "rm", "-f", CONTAINER], capture_output=True)

    print("\n==== ИТОГ ====")
    print(f"заданий: {total}, прошли проверки полностью: {passed}, с проблемами: {len(problems)}")
    for pid, why in problems:
        print(f"  {pid}: {why}")


main()
