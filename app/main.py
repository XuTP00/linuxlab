"""LinuxLab — веб-сервис для практического изучения Linux."""
from __future__ import annotations

import asyncio
import base64
import hmac
import json
import os
import shlex
import subprocess
import time
from typing import Any, Optional

from fastapi import FastAPI, Header, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from . import progress as progress_store
from .checker import evaluate
from .config import STATIC_DIR
from .curriculum import MODULES, TASKS, TASK_IDS
from .sessions import manager

app = FastAPI(title="LinuxLab", version="0.01")

# пароль администратора для разблокировки копирования условий заданий
ADMIN_PASSWORD = os.environ.get("LINUXLAB_ADMIN_PASSWORD", "1541685")
UNLOCK_TTL = int(os.environ.get("LINUXLAB_UNLOCK_TTL", str(8 * 3600)))

os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _uid(x_user_id: Optional[str] = Header(default=None), uid: Optional[str] = None) -> str:
    return (x_user_id or uid or "anonymous").strip() or "anonymous"


# ---------------------------------------------------------------- страницы
@app.get("/")
async def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/health")
async def health():
    return {"status": "ok", "tasks": len(TASK_IDS), "time": time.time()}


# ---------------------------------------------------------------- курс
def _task_public(task: dict, module_id: str = "", module_title: str = "") -> dict:
    return {
        "id": task["id"],
        "title": task["title"],
        "module": module_id or task.get("module", ""),
        "module_title": module_title or task.get("module_title", ""),
        "difficulty": task.get("difficulty", 1),
        "points": task.get("points", 10),
    }


@app.get("/api/curriculum")
async def curriculum(x_user_id: Optional[str] = Header(default=None)):
    uid = _uid(x_user_id)
    done = progress_store.get_progress(uid)
    modules = []
    for m in MODULES:
        tasks = []
        for t in m["tasks"]:
            item = _task_public(t, m["id"], m["title"])
            item["done"] = bool(done.get(t["id"], {}).get("done"))
            item["attempts"] = done.get(t["id"], {}).get("attempts", 0)
            tasks.append(item)
        modules.append({
            "id": m["id"],
            "title": m["title"],
            "icon": m.get("icon", ""),
            "summary": m.get("summary", ""),
            "tasks": tasks,
            "done": sum(1 for t in tasks if t["done"]),
            "total": len(tasks),
        })
    total = len(TASK_IDS)
    finished = sum(1 for m in modules for t in m["tasks"] if t["done"])
    return {
        "modules": modules,
        "total": total,
        "done": finished,
        "percent": round(finished * 100 / total, 1) if total else 0,
    }


@app.get("/api/task/{task_id}")
async def get_task(task_id: str, x_user_id: Optional[str] = Header(default=None)):
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(404, "Задание не найдено")
    uid = _uid(x_user_id)
    prog = progress_store.get_progress(uid).get(task_id, {})
    return {
        "id": task["id"],
        "title": task["title"],
        "module": task["module"],
        "module_title": task["module_title"],
        "difficulty": task.get("difficulty", 1),
        "points": task.get("points", 10),
        "task": task.get("task", ""),
        "theory": task.get("theory", ""),
        "goals": task.get("goals", []),
        "hints": task.get("hints", []),
        "checks": [{"title": c.get("title", "Проверка")} for c in task.get("checks", [])],
        "done": bool(prog.get("done")),
        "attempts": prog.get("attempts", 0),
    }


@app.get("/api/solution/{task_id}")
async def get_solution(task_id: str):
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(404, "Задание не найдено")
    return {"id": task_id, "solution": task.get("solution", "")}


# ---------------------------------------------------------------- сессии
@app.post("/api/session")
async def create_session():
    try:
        session = manager.create()
    except Exception as exc:
        raise HTTPException(500, f"Не удалось запустить контейнер: {exc}")
    return {"session_id": session.sid, "container": session.container}


@app.post("/api/session/{sid}/reset")
async def reset_session(sid: str):
    session = manager.get(sid)
    if not session:
        raise HTTPException(404, "Сессия не найдена")
    try:
        await asyncio.to_thread(session.reset)
    except Exception as exc:
        raise HTTPException(500, f"Не удалось пересоздать контейнер: {exc}")
    return {"ok": True, "session_id": sid}


@app.post("/api/session/{sid}/exec")
async def exec_command(sid: str, request: Request):
    session = manager.get(sid)
    if not session:
        raise HTTPException(404, "Сессия не найдена")
    body = await request.json()
    cmd = body.get("cmd", "")
    if not cmd.strip():
        raise HTTPException(400, "Пустая команда")
    try:
        session.write(cmd)
    except Exception as exc:
        raise HTTPException(500, str(exc))
    return {"ok": True}


@app.get("/api/session/{sid}/output")
async def session_output(sid: str, since: int = 0):
    session = manager.get(sid)
    if not session:
        raise HTTPException(404, "Сессия не найдена")
    data, pos = session.read_since(since)
    return {"data": data, "pos": pos}


@app.websocket("/ws/{sid}")
async def ws_terminal(websocket: WebSocket, sid: str):
    await websocket.accept()
    session = manager.get(sid)
    if not session:
        try:
            session = manager.get_or_create(sid)
        except Exception as exc:
            await websocket.send_text(f"\n[ошибка запуска контейнера: {exc}]\n")
            await websocket.close()
            return
    session.loop = asyncio.get_running_loop()
    session.queue = asyncio.Queue()

    # отдать весь накопленный вывод
    data, pos = session.read_since(0)
    await websocket.send_text(json.dumps({"type": "history", "data": data, "pos": pos}))

    async def reader():
        while True:
            chunk = await session.queue.get()
            await websocket.send_text(json.dumps({"type": "out", "data": chunk}))

    reader_task = asyncio.create_task(reader())
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                msg = {"cmd": raw}
            if msg.get("type") == "cmd":
                cmd = msg.get("cmd", "")
                if cmd:
                    try:
                        session.write(cmd, raw=bool(msg.get("raw")))
                    except Exception as exc:
                        await websocket.send_text(json.dumps({"type": "error", "data": str(exc)}))
            elif msg.get("type") == "input":
                # прямое нажатие клавиш в терминале
                data = msg.get("data", "")
                if data:
                    try:
                        session.write_raw(data)
                    except Exception as exc:
                        await websocket.send_text(json.dumps({"type": "error", "data": str(exc)}))
            elif msg.get("type") == "reset":
                try:
                    await asyncio.to_thread(session.reset)
                    await websocket.send_text(json.dumps({"type": "reset", "data": "Контейнер пересоздан"}))
                except Exception as exc:
                    await websocket.send_text(json.dumps({"type": "error", "data": str(exc)}))
            elif msg.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        reader_task.cancel()


# ---------------------------------------------------------------- предпросмотр сайта
WEB_PORT = int(os.environ.get("LINUXLAB_WEB_PORT", "8080"))

_NO_WEB_PAGE = """<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">
<title>Web</title><style>
body{background:#0b1015;color:#c7d2de;font-family:-apple-system,Segoe UI,Roboto,sans-serif;
     margin:0;padding:40px;line-height:1.6}
h1{font-size:20px;color:#e6edf3;margin:0 0 12px}
code{background:#161e28;border:1px solid #1e2833;border-radius:6px;padding:2px 7px;color:#a5d6ff;
     font-family:Consolas,monospace}
p{color:#8fa0b3;font-size:14px;max-width:640px}
</style></head><body>
<h1>Веб-сервер в контейнере не отвечает</h1>
<p>На порту <code>{port}</code> внутри контейнера пока никто не слушает.<br><br>
Запустите веб-сервер в терминале и откройте эту вкладку снова:<br><br>
<code>sudo angie</code> — веб-сервер Angie на порту 8080,<br>
<code>sudo apache2ctl start</code> — Apache HTTP Server на порту 80.<br><br>
Не забудьте переключить порт в поле «порт» над окном просмотра.</p>
</body></html>"""


def _split_http_response(raw: bytes) -> tuple[int, str, bytes]:
    """Разбирает «сырой» HTTP-ответ curl -i на статус, content-type и тело."""
    head, sep, body = raw.partition(b"\r\n\r\n")
    if not sep:
        head, sep, body = raw.partition(b"\n\n")
    lines = head.decode("utf-8", "replace").splitlines()
    status = 200
    ctype = "text/html; charset=utf-8"
    for line in lines[1:]:
        low = line.lower()
        if low.startswith("http/"):
            try:
                status = int(line.split()[1])
            except (ValueError, IndexError):
                pass
        elif low.startswith("content-type:"):
            ctype = line.split(":", 1)[1].strip()
    return status, ctype, body


@app.get("/api/web/{sid}/proxy/{port}")
@app.get("/api/web/{sid}/proxy/{port}/{path:path}")
async def web_proxy(sid: str, port: str, path: str = "index.html"):
    """Отдаёт страницу с веб-сервера внутри контейнера ученика."""
    port = str(port or WEB_PORT)
    session = manager.get(sid)
    if not session:
        return HTMLResponse(_NO_WEB_PAGE.replace("{port}", port), status_code=200)
    url_path = "/" + (path or "index.html")
    code, out, err = session.exec_check(
        f"curl -s -i --max-time 8 http://127.0.0.1:{port}{shlex.quote(url_path)}",
        user="student", cwd="/home/student", binary=True)
    if code != 0 or not (out or b"").strip():
        return HTMLResponse(_NO_WEB_PAGE.replace("{port}", port), status_code=200)
    status, ctype, body = _split_http_response(out)
    if "text/html" in ctype.lower():
        text = body.decode("utf-8", "replace")
        base = f"/api/web/{sid}/proxy/{port}/"
        if "<head>" in text:
            text = text.replace("<head>", f'<head><base href="{base}">', 1)
        elif "<html" in text:
            text = text.replace("<html", f'<html><head><base href="{base}"></head><body', 1)
        return HTMLResponse(text, status_code=status)
    return Response(body, media_type=ctype, status_code=status)


@app.get("/api/web/{sid}/status")
async def web_status(sid: str, port: str = str(WEB_PORT)):
    """Быстрая проверка: отвечает ли веб-сервер в контейнере."""
    session = manager.get(sid)
    if not session:
        return {"ok": False, "code": None, "server": None, "port": port}
    code, out, _ = session.exec_check(
        f"curl -s -o /dev/null -w '%{{http_code}} %{{content_type}}' --max-time 5 "
        f"http://127.0.0.1:{port}/",
        user="student", cwd="/home/student")
    parts = (out or "").split()
    http_code = parts[0] if parts else ""
    server = parts[1] if len(parts) > 1 else ""
    ok = code == 0 and http_code.startswith("2")
    return {"ok": ok, "code": http_code or None, "server": server, "port": port}


# ---------------------------------------------------------------- IDE (редактор файлов)
IDE_ROOT = os.environ.get("LINUXLAB_IDE_ROOT", "/home/student")
IDE_MAX_FILES = 4000
IDE_MAX_SIZE = 400_000

_EXT_LANG = {
    ".py": "python", ".pyw": "python", ".sh": "shell", ".bash": "shell", ".zsh": "shell",
    ".html": "htmlmixed", ".htm": "htmlmixed", ".xml": "xml", ".svg": "xml",
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript", ".json": "javascript",
    ".css": "css", ".scss": "css", ".md": "markdown", ".markdown": "markdown",
    ".sql": "sql", ".php": "php", ".yml": "yaml", ".yaml": "yaml",
    ".c": "clike", ".h": "clike", ".cpp": "clike", ".hpp": "clike", ".java": "clike",
    ".lua": "lua", ".r": "r", ".go": "go", ".rs": "rust",
    ".conf": "nginx", ".nginx": "nginx", ".Dockerfile": "dockerfile",
}


def _ide_lang(path: str) -> str:
    name = os.path.basename(path)
    if name.lower().startswith("dockerfile"):
        return "dockerfile"
    ext = os.path.splitext(name)[1].lower()
    return _EXT_LANG.get(ext, "")


def _ide_session(sid: str):
    session = manager.get(sid)
    if not session:
        raise HTTPException(404, "Сессия не найдена — перезагрузите страницу")
    return session


def _ide_run(session, cmd: str, timeout: int = 30):
    return session.exec_check(cmd, timeout=timeout, user="student", cwd=IDE_ROOT)


@app.get("/api/ide/{sid}/tree")
async def ide_tree(sid: str, path: str = ""):
    """Дерево файлов домашнего каталога ученика (скрытые и служебные папки скрыты)."""
    session = _ide_session(sid)
    base = path or IDE_ROOT
    cmd = (
        f"cd {shlex.quote(base)} 2>/dev/null && "
        "find . -mindepth 1 -maxdepth 5 "
        "\\( -name '.*' -prune \\) -o "
        "\\( -name node_modules -prune \\) -o "
        "\\( -name __pycache__ -prune \\) -o "
        f"-printf '%y|%s|%p\\n' | head -n {IDE_MAX_FILES}"
    )
    code, out, err = _ide_run(session, cmd)
    if code != 0:
        return {"root": base, "items": [], "error": err.strip()[:200] or "не удалось прочитать каталог"}
    items = []
    for line in out.splitlines():
        parts = line.split("|", 2)
        if len(parts) != 3:
            continue
        kind, size, p = parts
        if kind == "l":
            continue
        items.append({
            "type": "dir" if kind == "d" else "file",
            "name": os.path.basename(p) or p,
            "path": os.path.normpath(os.path.join(base, p)),
            "size": int(size) if size.isdigit() else 0,
        })
    items.sort(key=lambda x: (x["type"] != "dir", x["name"].lower()))
    return {"root": base, "items": items}


@app.get("/api/ide/{sid}/file")
async def ide_file(sid: str, path: str):
    """Содержимое файла (для редактора)."""
    session = _ide_session(sid)
    code, out, err = _ide_run(
        session, f"cat {shlex.quote(path)} 2>/dev/null | head -c {IDE_MAX_SIZE}")
    raw = out
    code2, real, _ = _ide_run(
        session, f"wc -c < {shlex.quote(path)} 2>/dev/null")
    size = int(real.strip()) if real.strip().isdigit() else len(raw)
    binary = "\x00" in raw
    return {
        "path": path,
        "name": os.path.basename(path),
        "lang": _ide_lang(path),
        "size": size,
        "binary": binary,
        "content": "" if binary else raw,
        "truncated": size > IDE_MAX_SIZE,
    }


@app.put("/api/ide/{sid}/file")
async def ide_save(sid: str, request: Request):
    """Сохраняет файл в контейнере ученика."""
    session = _ide_session(sid)
    body = await request.json()
    path = body.get("path", "")
    content = body.get("content", "")
    if not path:
        raise HTTPException(400, "не указан путь")
    data = base64.b64encode(content.encode("utf-8")).decode("ascii")
    cmd = (f"printf '%s' '{data}' | base64 -d > {shlex.quote(path)} && "
           f"wc -c < {shlex.quote(path)}")
    code, out, err = _ide_run(session, cmd, timeout=60)
    if code != 0:
        raise HTTPException(500, err.strip()[:300] or "не удалось сохранить файл")
    return {"ok": True, "path": path, "size": int(out.strip() or 0)}


@app.post("/api/ide/{sid}/mkdir")
async def ide_mkdir(sid: str, request: Request):
    session = _ide_session(sid)
    body = await request.json()
    path = body.get("path", "")
    if not path:
        raise HTTPException(400, "не указан путь")
    code, out, err = _ide_run(session, f"mkdir -p {shlex.quote(path)}")
    if code != 0:
        raise HTTPException(500, err.strip()[:300] or "не удалось создать каталог")
    return {"ok": True, "path": path}


@app.post("/api/ide/{sid}/delete")
async def ide_delete(sid: str, request: Request):
    session = _ide_session(sid)
    body = await request.json()
    path = body.get("path", "")
    if not path:
        raise HTTPException(400, "не указан путь")
    code, out, err = _ide_run(session, f"rm -rf {shlex.quote(path)}")
    if code != 0:
        raise HTTPException(500, err.strip()[:300] or "не удалось удалить")
    return {"ok": True, "path": path}


@app.post("/api/ide/{sid}/rename")
async def ide_rename(sid: str, request: Request):
    session = _ide_session(sid)
    body = await request.json()
    src = body.get("from", "")
    dst = body.get("to", "")
    if not src or not dst:
        raise HTTPException(400, "не указаны пути")
    code, out, err = _ide_run(session, f"mv {shlex.quote(src)} {shlex.quote(dst)}")
    if code != 0:
        raise HTTPException(500, err.strip()[:300] or "не удалось переименовать")
    return {"ok": True, "path": dst}


# ---------------------------------------------------------------- проверки
@app.post("/api/check")
async def check_task(request: Request, x_user_id: Optional[str] = Header(default=None)):
    body = await request.json()
    task_id = body.get("task_id", "")
    sid = body.get("session_id", "")
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(404, "Задание не найдено")
    session = manager.get(sid)
    if not session:
        raise HTTPException(404, "Сессия не найдена — перезагрузите страницу")
    uid = _uid(x_user_id)
    results = []
    passed = 0
    for spec in task.get("checks", []):
        res = await asyncio.to_thread(evaluate, session, spec)
        results.append(res.as_dict())
        if res.ok:
            passed += 1
    all_ok = passed == len(results) and len(results) > 0
    progress_store.mark(uid, task_id, all_ok)
    return {
        "task_id": task_id,
        "passed": passed,
        "total": len(results),
        "all_passed": all_ok,
        "results": results,
        "progress": progress_store.summary(uid, TASK_IDS),
    }


# ---------------------------------------------------------------- защита копирования
@app.get("/api/protection")
async def protection_state(x_user_id: Optional[str] = Header(default=None)):
    uid = _uid(x_user_id)
    return {"unlocked": progress_store.is_unlocked(uid)}


@app.post("/api/protection/unlock")
async def protection_unlock(request: Request, x_user_id: Optional[str] = Header(default=None)):
    body = await request.json()
    pwd = str(body.get("password", ""))
    uid = _uid(x_user_id)
    if not hmac.compare_digest(pwd, ADMIN_PASSWORD):
        raise HTTPException(401, "Неверный пароль")
    progress_store.set_unlock(uid, time.time() + UNLOCK_TTL)
    return {"ok": True, "expires_in": UNLOCK_TTL}


@app.post("/api/protection/lock")
async def protection_lock(x_user_id: Optional[str] = Header(default=None)):
    uid = _uid(x_user_id)
    progress_store.clear_unlock(uid)
    return {"ok": True, "unlocked": False}


# ---------------------------------------------------------------- прогресс
@app.get("/api/progress")
async def progress(x_user_id: Optional[str] = Header(default=None)):
    uid = _uid(x_user_id)
    return progress_store.summary(uid, TASK_IDS)


@app.post("/api/progress/reset")
async def progress_reset(x_user_id: Optional[str] = Header(default=None)):
    uid = _uid(x_user_id)
    progress_store.reset(uid)
    return {"ok": True}


# ---------------------------------------------------------------- фоновая уборка
@app.on_event("startup")
async def startup():
    # после перезапуска сервиса старые контейнеры-сессии осиротели — убираем их
    def cleanup_orphan_containers():
        try:
            res = subprocess.run(
                ["docker", "ps", "-aq", "--filter", "name=linuxlab-sess-"],
                capture_output=True, text=True, timeout=60)
            ids = [x for x in res.stdout.split() if x]
            if ids:
                subprocess.run(["docker", "rm", "-f", *ids],
                               capture_output=True, text=True, timeout=120)
        except Exception:
            pass
    await asyncio.to_thread(cleanup_orphan_containers)

    async def cleaner():
        while True:
            await asyncio.sleep(120)
            try:
                await asyncio.to_thread(manager.cleanup)
            except Exception:
                pass
    asyncio.create_task(cleaner())


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)
