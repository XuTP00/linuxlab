"""LinuxLab — веб-сервис для практического изучения Linux."""
from __future__ import annotations

import asyncio
import hmac
import json
import os
import subprocess
import time
from typing import Any, Optional

from fastapi import FastAPI, Header, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
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
