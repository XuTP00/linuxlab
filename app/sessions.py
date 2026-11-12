"""Управление docker-контейнерами и интерактивной оболочкой bash."""
from __future__ import annotations

import asyncio
import codecs
import os
import shutil
import subprocess
import threading
import time
import uuid
from typing import Optional

from .config import CONTAINER_PREFIX, DOCKER_IMAGE


def _docker(*args: str, timeout: int = 120, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=check,
    )


class ShellSession:
    """Контейнер + постоянная bash-сессия внутри него."""

    def __init__(self, sid: str):
        self.sid = sid
        self.container = CONTAINER_PREFIX + sid
        self.proc: Optional[subprocess.Popen] = None
        self.buffer = bytearray()
        self.seq = 0
        self.lock = threading.Lock()
        self.created_at = time.time()
        self.last_activity = time.time()
        self.commands: list[str] = []          # история команд пользователя
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.queue: Optional[asyncio.Queue] = None
        self._decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
        self._stopped = False
        self._restarts = 0
        self._line_buffer = ""

    # ---------- жизненный цикл ----------
    def start(self) -> None:
        subprocess.run(["docker", "rm", "-f", self.container],
                       capture_output=True, text=True, timeout=60)
        cmd = ["docker", "run", "-d", "--name", self.container,
               "--hostname", "linuxlab",
               "--hostname", "lab",
               DOCKER_IMAGE]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if res.returncode != 0:
            # упрощённый вариант — без дополнительных capabilities
            cmd = ["docker", "run", "-d", "--name", self.container,
                   "--hostname", "lab", DOCKER_IMAGE]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if res.returncode != 0:
            raise RuntimeError("Не удалось создать контейнер: " + (res.stderr or res.stdout))
        self._spawn_shell()

    def _spawn_shell(self) -> None:
        """Запускает интерактивный bash внутри pty (script) — работают nano, top, vi."""
        self.proc = subprocess.Popen(
            ["docker", "exec", "-i", "-u", "student", "-w", "/home/student",
             self.container, "script", "-qfc",
             "stty rows 40 cols 120; bash --rcfile /etc/lab.bashrc -i", "/dev/null"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,
        )
        self._decoder.reset()
        t = threading.Thread(target=self._reader, daemon=True)
        t.start()

    def reset(self) -> None:
        self.stop()
        self.buffer.clear()
        self.seq = 0
        self.commands.clear()
        self._decoder.reset()
        self.start()

    def stop(self) -> None:
        self._stopped = True
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.stdin.close()
            except Exception:
                pass
            try:
                self.proc.terminate()
            except Exception:
                pass
        subprocess.run(["docker", "rm", "-f", self.container],
                       capture_output=True, text=True, timeout=60)

    # ---------- ввод/вывод ----------
    def _reader(self) -> None:
        """Читает stdout оболочки и складывает в буфер + очередь websocket."""
        proc = self.proc
        while True:
            try:
                chunk = os.read(proc.stdout.fileno(), 65536)
            except Exception:
                chunk = b""
            if not chunk:
                break
            text = self._decoder.decode(chunk)
            if not text:
                continue
            with self.lock:
                self.buffer.extend(text.encode("utf-8", "replace"))
                self.seq += 1
            if self.loop and self.queue:
                try:
                    self.loop.call_soon_threadsafe(self.queue.put_nowait, text)
                except Exception:
                    pass
        # оболочка завершилась (exit) — перезапускаем её
        self._push("\n[ сессия завершена, запускаем новую оболочку ]\n")
        if self._stopped:
            return
        self._restarts = getattr(self, "_restarts", 0) + 1
        if self._restarts > 5:
            self._push("\n[ не удалось перезапустить оболочку. Нажмите «⟳ Контейнер» ]\n")
            return
        try:
            self._spawn_shell()
        except Exception:
            pass

    def _push(self, text: str) -> None:
        with self.lock:
            self.buffer.extend(text.encode("utf-8", "replace"))
            self.seq += 1
        if self.loop and self.queue:
            try:
                self.loop.call_soon_threadsafe(self.queue.put_nowait, text)
            except Exception:
                pass

    def write(self, command: str, raw: bool = False) -> None:
        cmd = command.rstrip("\n") if not raw else command
        if not raw:
            self.commands.append(cmd)
        self.last_activity = time.time()
        if not self.proc or self.proc.poll() is not None:
            self._spawn_shell()
        try:
            payload = cmd if raw else (cmd + "\n")
            self.proc.stdin.write(payload.encode("utf-8"))
            self.proc.stdin.flush()
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("Сессия недоступна: %s" % exc)

    def write_raw(self, data: str) -> None:
        """Прямая передача нажатий клавиш в терминал (как в настоящей консоли)."""
        self.last_activity = time.time()
        if not self.proc or self.proc.poll() is not None:
            self._spawn_shell()
        try:
            self.proc.stdin.write(data.encode("utf-8"))
            self.proc.stdin.flush()
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("Сессия недоступна: %s" % exc)
        # ведём историю команд (для проверок вида «использована команда grep»)
        for ch in data:
            if ch in ("\r", "\n"):
                line = self._line_buffer.strip()
                if line:
                    self.commands.append(line)
                self._line_buffer = ""
            elif ch in ("\x7f", "\b"):
                self._line_buffer = self._line_buffer[:-1]
            elif ch == "\x03":
                self._line_buffer = ""
            elif ord(ch) >= 32:
                self._line_buffer += ch

    def read_since(self, since: int) -> tuple[str, int]:
        """Возвращает (текст, новая_позиция)."""
        with self.lock:
            data = bytes(self.buffer).decode("utf-8", "replace")
            return data[since:], len(data)

    def clear_buffer(self) -> None:
        with self.lock:
            self.buffer.clear()
            self.seq = 0

    # ---------- выполнение команд для проверок ----------
    def exec_check(self, command: str, timeout: int = 30, user: str = "root", cwd: str = "/root") -> tuple[int, str, str]:
        """Однократное выполнение команды в контейнере."""
        try:
            res = subprocess.run(
                ["docker", "exec", "-u", user, "-w", cwd,
                 self.container, "bash", "-lc", command],
                capture_output=True, text=True, timeout=timeout,
            )
            return res.returncode, res.stdout, res.stderr
        except subprocess.TimeoutExpired:
            return 124, "", "timeout"

    def alive(self) -> bool:
        if not self.proc:
            return False
        return self.proc.poll() is None


class SessionManager:
    def __init__(self):
        self.sessions: dict[str, ShellSession] = {}
        self.lock = threading.Lock()

    def get_or_create(self, sid: str) -> ShellSession:
        with self.lock:
            s = self.sessions.get(sid)
            if s is None:
                s = ShellSession(sid)
                s.start()
                self.sessions[sid] = s
            elif not s.alive():
                # оболочка умерла — пересоздаём контейнер
                try:
                    s.reset()
                except Exception:
                    s = ShellSession(sid)
                    s.start()
                    self.sessions[sid] = s
            return s

    def get(self, sid: str) -> Optional[ShellSession]:
        return self.sessions.get(sid)

    def create(self) -> ShellSession:
        sid = uuid.uuid4().hex[:12]
        s = ShellSession(sid)
        s.start()
        with self.lock:
            self.sessions[sid] = s
        return s

    def destroy(self, sid: str) -> None:
        with self.lock:
            s = self.sessions.pop(sid, None)
        if s:
            s.stop()

    def cleanup(self) -> None:
        now = time.time()
        with self.lock:
            victims = [sid for sid, s in self.sessions.items()
                       if now - s.last_activity > self._idle_ttl()]
        for sid in victims:
            self.destroy(sid)

    @staticmethod
    def _idle_ttl() -> int:
        from .config import IDLE_SESSION_TTL
        return IDLE_SESSION_TTL


manager = SessionManager()


def docker_available() -> bool:
    return shutil.which("docker") is not None
