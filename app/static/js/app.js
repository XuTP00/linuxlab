/* LinuxLab — фронтенд */
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const state = {
    uid: localStorage.getItem("linuxlab.uid") || (() => {
      const u = "u" + Math.random().toString(36).slice(2) + Date.now().toString(36);
      localStorage.setItem("linuxlab.uid", u);
      return u;
    })(),
    curriculum: null,
    flatTasks: [],
    current: null,
    sessionId: null,
    ws: null,
    term: null,
    fit: null,
    history: [],
    histIdx: -1,
    pending: [],
    unlocked: false,
    hintStep: 0,
    layout: localStorage.getItem("linuxlab.layout") || "v",
    ready: false,
  };

  /* ---------------- API ---------------- */
  async function api(path, options = {}) {
    const opts = Object.assign({ headers: {} }, options);
    opts.headers["X-User-Id"] = state.uid;
    if (opts.body) opts.headers["Content-Type"] = "application/json";
    const res = await fetch(path, opts);
    if (!res.ok) {
      let detail = res.statusText;
      try { detail = (await res.json()).error || detail; } catch (e) {}
      throw new Error(detail);
    }
    return res.json();
  }

  /* ---------------- терминал ---------------- */
  function initTerminal() {
    state.term = new Terminal({
      cursorBlink: true,
      fontFamily: '"JetBrains Mono","Fira Code",Consolas,monospace',
      fontSize: 13,
      lineHeight: 1.25,
      scrollback: 5000,
      convertEol: true,
      allowProposedApi: true,
      theme: {
        background: "#0b1015",
        foreground: "#c7d2de",
        cursor: "#3fb950",
        green: "#3fb950",
        blue: "#58a6ff",
        yellow: "#d29922",
        red: "#f85149",
        cyan: "#39c5cf",
        selectionBackground: "#243244",
      },
    });
    state.fit = new FitAddon.FitAddon();
    state.term.loadAddon(state.fit);
    state.term.open($("terminal"));

    // каждое нажатие клавиши уходит в контейнер как в настоящей консоли
    state.term.onData((data) => {
      hideTermHint();
      sendInput(data);
    });

    setTimeout(() => { try { state.fit.fit(); } catch (e) {} }, 50);
    state.term.focus();
    document.addEventListener("click", (ev) => {
      if (ev.target.closest(".term-panel")) state.term.focus();
    });
    window.addEventListener("resize", () => { try { state.fit.fit(); } catch (e) {} });
  }

  function hideTermHint() {
    const h = $("term-hint-line");
    if (h) h.classList.add("hide");
  }

  /* ---------------- сессия / websocket ---------------- */
  async function ensureSession() {
    if (state.sessionId) return state.sessionId;
    const data = await api("/api/session", { method: "POST" });
    state.sessionId = data.session_id;
    connectWs();
    return state.sessionId;
  }

  function connectWs() {
    if (state.ws) { try { state.ws.close(); } catch (e) {} }
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${location.host}/ws/${state.sessionId}`);
    state.ws = ws;
    ws.onopen = () => {
      $("term-dot").classList.add("on");
      $("term-title").textContent = "Терминал · контейнер активен";
      if (state.pending.length) {
        state.pending.forEach((d) => ws.send(JSON.stringify({ type: "input", data: d })));
        state.pending = [];
      }
      state.term.focus();
    };
    ws.onclose = () => {
      $("term-dot").classList.remove("on");
      $("term-title").textContent = "Терминал · переподключение…";
      setTimeout(() => { if (state.sessionId) connectWs(); }, 2000);
    };
    ws.onmessage = (ev) => {
      let msg;
      try { msg = JSON.parse(ev.data); } catch (e) { return; }
      if (msg.type === "history" || msg.type === "out") {
        state.term.write(msg.data.replace(/\r\n/g, "\n"));
      } else if (msg.type === "reset") {
        state.term.clear();
        state.term.write("\n[ " + msg.data + " ]\n\n");
      } else if (msg.type === "error") {
        state.term.write("\n[ ошибка: " + msg.data + " ]\n");
      }
    };
  }

  function sendCommand(cmd, raw) {
    const payload = { type: "cmd", cmd };
    if (raw) payload.raw = true;
    if (state.ws && state.ws.readyState === 1) {
      state.ws.send(JSON.stringify(payload));
    } else {
      api(`/api/session/${state.sessionId}/exec`, { method: "POST", body: JSON.stringify({ cmd }) })
        .catch((e) => state.term.write("\n[ ошибка: " + e.message + " ]\n"));
    }
  }

  /* прямые нажатия клавиш: буферизуем, если сокет ещё не готов */
  function sendInput(data) {
    if (state.ws && state.ws.readyState === 1) {
      state.ws.send(JSON.stringify({ type: "input", data }));
    } else {
      state.pending.push(data);
    }
  }

  /* ---------------- ввод команд ---------------- */
  function initInput() {
    // ввод теперь идёт напрямую в терминал (xterm.onData → WebSocket)
    document.addEventListener("keydown", (ev) => {
      if (ev.target.tagName === "INPUT" || ev.target.tagName === "TEXTAREA") return;
    });
  }

  /* ---------------- курс ---------------- */
  async function loadCurriculum() {
    const data = await api("/api/curriculum");
    state.curriculum = data;
    state.flatTasks = [];
    data.modules.forEach((m) => m.tasks.forEach((t) => state.flatTasks.push(t)));
    renderProgress();
    renderDrawer();
  }

  function renderProgress() {
    const d = state.curriculum;
    $("progress-fill").style.width = d.percent + "%";
    $("progress-percent").textContent = d.percent + "%";
    $("progress-label").textContent = `Пройдено ${d.done} из ${d.total} заданий`;
  }

  function renderDrawer() {
    const body = $("drawer-body");
    body.innerHTML = "";
    state.curriculum.modules.forEach((m, i) => {
      const mod = document.createElement("div");
      mod.className = "mod" + (i === 0 ? " open" : "");
      const head = document.createElement("div");
      head.className = "mod-title";
      head.innerHTML = `<span>${m.icon || ""} ${m.title}</span><span class="count">${m.done}/${m.total}</span>`;
      head.onclick = () => mod.classList.toggle("open");
      const mbody = document.createElement("div");
      mbody.className = "mod-body";
      m.tasks.forEach((t) => {
        const item = document.createElement("div");
        item.className = "task-item" + (t.done ? " done" : "") + (state.current && state.current.id === t.id ? " active" : "");
        item.dataset.id = t.id;
        item.innerHTML = `<span class="mark ok"></span><span>${t.title}</span>`;
        item.onclick = () => { selectTask(t.id); closeDrawer(); };
        mbody.appendChild(item);
      });
      mod.appendChild(head);
      mod.appendChild(mbody);
      body.appendChild(mod);
    });
  }

  function markActive(id) {
    document.querySelectorAll(".task-item").forEach((el) => {
      el.classList.toggle("active", el.dataset.id === id);
    });
  }

  async function selectTask(id) {
    const task = await api("/api/task/" + id);
    state.current = task;
    state.hintStep = 0;
    $("crumbs").textContent = task.module_title;
    $("task-title").textContent = task.title;
    $("task-points").textContent = task.points + " баллов";
    $("task-difficulty").textContent = "●".repeat(task.difficulty) + "○".repeat(Math.max(0, 5 - task.difficulty));
    $("task-text").innerHTML = mdLite(task.task);
    const theory = $("task-theory");
    if (task.theory) {
      $("theory-body").innerHTML = mdLite(task.theory);
      theory.hidden = false;
    } else {
      theory.hidden = true;
    }
    $("task-goals").innerHTML = (task.goals || [])
      .map((g) => `<div class="goal">${escapeHtml(g)}</div>`).join("");
    $("checks").innerHTML = (task.checks || [])
      .map((c, i) => `<div class="check-row" data-idx="${i}"><span class="ic">•</span><span>${escapeHtml(c.title || "Проверка " + (i + 1))}</span></div>`)
      .join("");
    $("checks").classList.remove("show");
    $("hint-box").hidden = true;
    $("solution-box").hidden = true;
    $("hints-list").innerHTML = "";
    const nb = $("btn-next-success");
    if (nb) nb.remove();
    $("check-status").textContent = task.done ? "✓ Уже выполнено" : "";
    markActive(id);
    localStorage.setItem("linuxlab.task", id);
  }

  function mdLite(text) {
    return escapeHtml(text || "")
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
      .replace(/\n\n/g, "<br><br>");
  }
  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  /* ---------------- проверка ---------------- */
  async function runCheck() {
    if (!state.current) return;
    const btn = $("btn-check");
    btn.disabled = true;
    $("check-status").textContent = "Проверяю…";
    try {
      await ensureSession();
      const res = await api("/api/check", {
        method: "POST",
        body: JSON.stringify({ task_id: state.current.id, session_id: state.sessionId }),
      });
      const box = $("checks");
      box.classList.add("show");
      const rows = box.querySelectorAll(".check-row");
      res.results.forEach((r, i) => {
        const row = rows[i];
        if (!row) return;
        row.className = "check-row " + (r.ok ? "ok" : "no");
        row.querySelector(".ic").textContent = r.ok ? "✓" : "✕";
        row.querySelector(".msg")?.remove();
        const msg = document.createElement("span");
        msg.className = "msg";
        msg.textContent = r.message || "";
        row.appendChild(msg);
      });
      $("check-status").textContent = res.all_passed
        ? `✓ Все проверки пройдены (${res.passed}/${res.total})`
        : `Пройдено ${res.passed} из ${res.total}`;
      if (res.all_passed) {
        const t = state.flatTasks.find((x) => x.id === state.current.id);
        if (t) t.done = true;
        await loadCurriculum();
        markActive(state.current.id);
        showNextButton();
      }
    } catch (e) {
      $("check-status").textContent = "Ошибка: " + e.message;
    } finally {
      btn.disabled = false;
    }
  }

  function showNextButton() {
    let btn = $("btn-next-success");
    if (!btn) {
      btn = document.createElement("button");
      btn.id = "btn-next-success";
      btn.className = "btn primary";
      btn.textContent = "Следующее задание →";
      btn.onclick = () => { btn.remove(); step(1); };
      $("btn-next").parentNode.appendChild(btn);
    }
  }

  /* ---------------- подсказки и решение ---------------- */
  async function showHints() {
    if (!state.current) return;
    const task = state.current;
    const box = $("hint-box");
    box.hidden = false;
    const list = $("hints-list");
    const step = Math.min(state.hintStep + 1, (task.hints || []).length);
    state.hintStep = step;
    list.innerHTML = (task.hints || []).slice(0, step).map((h) => `<li>${escapeHtml(h)}</li>`).join("");
  }

  async function showSolution() {
    if (!state.current) return;
    const data = await api("/api/solution/" + state.current.id);
    $("solution-text").textContent = data.solution;
    $("solution-box").hidden = false;
  }

  /* ---------------- навигация ---------------- */
  function step(delta) {
    const idx = state.flatTasks.findIndex((t) => t.id === (state.current && state.current.id));
    const next = state.flatTasks[idx + delta];
    if (next) selectTask(next.id);
  }

  /* ---------------- drawer ---------------- */
  function openDrawer() { $("drawer").classList.add("open"); $("overlay").classList.add("on"); }
  function closeDrawer() { $("drawer").classList.remove("open"); $("overlay").classList.remove("on"); }

  /* ---------------- раскладка ---------------- */
  function applyLayout() {
    $("workbench").className = "workbench layout-" + state.layout;
    localStorage.setItem("linuxlab.layout", state.layout);
    setTimeout(() => { try { state.fit.fit(); } catch (e) {} }, 60);
  }

  function initSplitter() {
    const splitter = $("splitter");
    const wb = $("workbench");
    let dragging = false;
    splitter.addEventListener("mousedown", (ev) => {
      dragging = true;
      ev.preventDefault();
      document.body.style.userSelect = "none";
    });
    window.addEventListener("mousemove", (ev) => {
      if (!dragging) return;
      const rect = wb.getBoundingClientRect();
      const panel = document.querySelector(".task-panel");
      if (state.layout === "v") {
        const pct = ((ev.clientY - rect.top) / rect.height) * 100;
        panel.style.flex = `0 0 ${Math.min(80, Math.max(15, pct))}%`;
      } else {
        const pct = ((ev.clientX - rect.left) / rect.width) * 100;
        panel.style.flex = `0 0 ${Math.min(80, Math.max(15, pct))}%`;
      }
      try { state.fit.fit(); } catch (e) {}
    });
    window.addEventListener("mouseup", () => {
      dragging = false;
      document.body.style.userSelect = "";
    });
  }

  /* ---------------- защита от копирования условий ---------------- */
  function initNoCopy() {
    const panel = document.querySelector(".task-panel");
    if (!panel) return;
    const notice = $("copy-notice");
    const btn = $("btn-unlock");
    let timer = null;

    function showNotice(text) {
      if (!notice) return;
      notice.textContent = text || "Копирование недоступно — введите команды в терминале вручную";
      notice.classList.add("show");
      clearTimeout(timer);
      timer = setTimeout(() => notice.classList.remove("show"), 2600);
    }

    function applyUnlocked(on) {
      state.unlocked = !!on;
      panel.classList.toggle("copy-allowed", state.unlocked);
      if (btn) {
        btn.classList.toggle("unlocked", state.unlocked);
        btn.innerHTML = state.unlocked
          ? "🔓 <b>копирование разрешено</b>"
          : "🔒 <b>вводите вручную</b>";
        btn.title = state.unlocked
          ? "Копирование разрешено. Нажмите, чтобы снова заблокировать"
          : "Команды из задания вводятся вручную. Нажмите, чтобы разрешить копирование (нужен пароль администратора)";
      }
    }
    state.applyUnlocked = applyUnlocked;

    // блокируем копирование, пока не разблокировано
    ["copy", "cut", "dragstart"].forEach((evt) => {
      panel.addEventListener(evt, (e) => {
        if (state.unlocked) return;
        e.preventDefault();
        showNotice();
      });
    });
    panel.addEventListener("contextmenu", (e) => {
      if (state.unlocked) return;
      e.preventDefault();
      showNotice("Контекстное меню отключено — введите команды вручную");
    });
    // Ctrl+A/C/X/Insert — стандартные сочетания копирования (в терминале не мешаем)
    document.addEventListener("keydown", (e) => {
      if (state.unlocked) return;
      if (e.target && e.target.closest && e.target.closest(".term-panel")) return;
      const inTask = e.target && e.target.closest && e.target.closest(".task-panel");
      const focusedInTask = panel.contains(document.activeElement) || inTask;
      if (!focusedInTask && document.activeElement !== document.body) return;
      if ((e.ctrlKey || e.metaKey) && ["c", "x", "i", "a"].includes((e.key || "").toLowerCase())) {
        e.preventDefault();
        showNotice();
      }
    });

    /* --- кнопка и модалка --- */
    const modal = $("unlock-modal");
    const passInput = $("unlock-pass");
    const errBox = $("unlock-error");

    function openModal() {
      modal.hidden = false;
      errBox.hidden = true;
      passInput.value = "";
      setTimeout(() => passInput.focus(), 30);
    }
    function closeModal() {
      modal.hidden = true;
    }
    async function tryUnlock() {
      const pwd = passInput.value;
      try {
        const res = await api("/api/protection/unlock", {
          method: "POST",
          body: JSON.stringify({ password: pwd }),
        });
        if (res && res.ok) {
          applyUnlocked(true);
          closeModal();
          showNotice("Копирование разрешено");
        }
      } catch (e) {
        errBox.hidden = false;
        passInput.value = "";
        passInput.focus();
      }
    }

    btn.addEventListener("click", async () => {
      if (state.unlocked) {
        await api("/api/protection/lock", { method: "POST" }).catch(() => {});
        applyUnlocked(false);
        showNotice("Копирование снова заблокировано");
        return;
      }
      openModal();
    });
    $("unlock-ok").addEventListener("click", tryUnlock);
    $("unlock-cancel").addEventListener("click", closeModal);
    modal.addEventListener("click", (e) => { if (e.target === modal) closeModal(); });
    passInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") { e.preventDefault(); tryUnlock(); }
      if (e.key === "Escape") { closeModal(); }
    });

    // проверяем состояние на сервере (разблокировка живёт 8 часов)
    api("/api/protection").then((r) => applyUnlocked(!!(r && r.unlocked))).catch(() => {});
  }

  /* ---------------- старт ---------------- */
  async function boot() {
    initTerminal();
    initInput();
    initSplitter();
    initNoCopy();
    applyLayout();

    $("btn-tasks").onclick = openDrawer;
    $("btn-close-drawer").onclick = closeDrawer;
    $("overlay").onclick = closeDrawer;
    $("btn-layout").onclick = () => { state.layout = state.layout === "v" ? "h" : "v"; applyLayout(); };
    $("btn-check").onclick = runCheck;
    $("btn-hint").onclick = showHints;
    $("btn-solution").onclick = showSolution;
    $("btn-prev").onclick = () => step(-1);
    $("btn-next").onclick = () => step(1);
    $("btn-clear").onclick = () => {
      sendInput("clear\n");
      state.term.focus();
    };
    $("btn-reset-container").onclick = async () => {
      try {
        await ensureSession();
        if (state.ws && state.ws.readyState === 1) state.ws.send(JSON.stringify({ type: "reset" }));
        else await api(`/api/session/${state.sessionId}/reset`, { method: "POST" });
      } catch (e) { alert(e.message); }
    };
    $("btn-reset-progress").onclick = async () => {
      if (!confirm("Сбросить весь прогресс прохождения?")) return;
      await api("/api/progress/reset", { method: "POST" });
      await loadCurriculum();
      $("check-status").textContent = "Прогресс сброшен";
    };

    try {
      await loadCurriculum();
      const last = localStorage.getItem("linuxlab.task");
      const target = state.flatTasks.find((t) => t.id === last) || state.flatTasks[0];
      if (target) await selectTask(target.id);
    } catch (e) {
      $("task-text").textContent = "Не удалось загрузить курс: " + e.message;
    }

    try {
      await ensureSession();
      state.ready = true;
    } catch (e) {
      state.term.write("\n[ не удалось запустить контейнер: " + e.message + " ]\n");
    }
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
