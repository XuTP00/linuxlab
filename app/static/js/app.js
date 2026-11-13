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
    state.term.open($("term-host"));

    // каждое нажатие клавиши уходит в контейнер как в настоящей консоли
    state.term.onData((data) => {
      hideTermHint();
      sendInput(data);
    });

    setTimeout(() => { try { state.fit.fit(); } catch (e) {} }, 50);
    state.term.focus();
    document.addEventListener("click", (ev) => {
      if (ev.target.closest("#view-ide")) return;   // в IDE фокус принадлежит редактору
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
      const dot = document.querySelector(".term-tab[data-view='term']");
      if (dot) dot.innerHTML = '<span style="color:var(--accent)">●</span> &gt;_ Terminal';
      if (state.pending.length) {
        state.pending.forEach((d) => ws.send(JSON.stringify({ type: "input", data: d })));
        state.pending = [];
      }
      state.term.focus();
    };
    ws.onclose = () => {
      const dot = document.querySelector(".term-tab[data-view='term']");
      if (dot) dot.innerHTML = "&gt;_ Terminal";
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

  /* ---------------- IDE ---------------- */
  const ide = {
    tree: [],
    open: [],          // [{path, name, lang, dirty}]
    editor: null,
    active: null,
    expanded: new Set(),
  };

  function initIde() {
    // CodeMirror
    ide.editor = CodeMirror($("ide-editor"), {
      mode: "text/plain",
      lineNumbers: true,
      indentUnit: 4,
      tabSize: 4,
      indentWithTabs: false,
      lineWrapping: false,
      theme: "dark",
      extraKeys: {
        "Ctrl-S": () => saveActiveFile(),
        "Ctrl-Enter": () => runActiveFile(),
        Tab: (cm) => {
          if (cm.somethingSelected()) cm.indentSelection("add");
          else cm.replaceSelection("    ");
        },
      },
    });
    ide.editor.setValue("");

    $("ide-refresh").onclick = () => loadIdeTree();
    $("ide-new-file").onclick = () => ideCreate("file");
    $("ide-new-folder").onclick = () => ideCreate("folder");
    $("ide-panel-toggle").onclick = () => $("ide-panel").classList.toggle("collapsed");
    $("ide-panel-close").onclick = () => $("ide-panel").classList.add("collapsed");
    $("ide-panel").querySelectorAll(".ide-panel-tab").forEach((t) => {
      t.addEventListener("click", () => {
        $("ide-panel").querySelectorAll(".ide-panel-tab").forEach((x) => x.classList.remove("active"));
        t.classList.add("active");
        if (t.textContent.trim() === "ТЕРМИНАЛ") $("ide-panel").classList.remove("collapsed");
      });
    });
    loadIdeTree();
  }

  async function loadIdeTree() {
    const box = $("ide-tree");
    if (!state.sessionId) { box.innerHTML = '<div class="ide-tree-empty">нет сессии</div>'; return; }
    box.innerHTML = '<div class="ide-tree-empty">загрузка…</div>';
    try {
      const r = await api(`/api/ide/${state.sessionId}/tree`);
      ide.tree = r.items || [];
      renderIdeTree();
    } catch (e) {
      box.innerHTML = `<div class="ide-tree-empty">ошибка: ${e.message}</div>`;
    }
  }

  function renderIdeTree() {
    const box = $("ide-tree");
    box.innerHTML = "";
    if (!ide.tree.length) {
      box.innerHTML = '<div class="ide-tree-empty">папка пуста</div>';
      return;
    }
    const root = "/home/student";
    const rows = [];
    function walk(items, depth) {
      items.forEach((it) => {
        const full = it.path;
        const rel = full.startsWith(root) ? full.slice(root.length) : full;
        const isOpen = ide.expanded.has(full);
        if (it.type === "dir") {
          rows.push({ it, depth, isOpen });
          if (isOpen) {
            const kids = ide.tree.filter((x) => x.path.startsWith(full + "/") && x.path.slice(full.length + 1).indexOf("/") === -1);
            walk(kids, depth + 1);
          }
        } else {
          rows.push({ it, depth, isOpen: false });
        }
      });
    }
    const top = ide.tree.filter((x) => x.path.slice(root.length + 1).indexOf("/") === -1);
    walk(top, 0);
    rows.forEach(({ it, depth, isOpen }) => {
      const row = document.createElement("div");
      row.className = "ide-tree-row" + (ide.active === it.path ? " sel" : "");
      row.style.paddingLeft = 8 + depth * 12 + "px";
      row.title = it.path;
      row.innerHTML = `<span class="ico">${it.type === "dir" ? (isOpen ? "▾" : "▸") : "📄"}</span>` +
        `<span class="nm">${escapeHtml(it.name)}</span>` +
        (it.type === "file" ? `<span class="sz">${it.size}</span>` : "");
      row.onclick = () => {
        if (it.type === "dir") {
          if (ide.expanded.has(it.path)) ide.expanded.delete(it.path);
          else ide.expanded.add(it.path);
          renderIdeTree();
        } else {
          openIdeFile(it.path);
        }
      };
      row.oncontextmenu = (ev) => {
        ev.preventDefault();
        ideFileMenu(it, ev);
      };
      box.appendChild(row);
    });
  }

  async function openIdeFile(path) {
    if (!state.sessionId) return;
    try {
      const f = await api(`/api/ide/${state.sessionId}/file?path=${encodeURIComponent(path)}`);
      const tab = ide.open.find((t) => t.path === path);
      const model = { path: f.path, name: f.name, lang: f.lang, dirty: false };
      if (tab) Object.assign(tab, model);
      else ide.open.push(model);
      ide.active = path;
      $("ide-welcome").style.display = "none";
      const mode = f.lang || "text/plain";
      ide.editor.setOption("mode", mode);
      ide.editor.setValue(f.binary ? "  [двоичный файл — редактирование недоступно]" : f.content);
      ide.editor.clearHistory();
      renderIdeTabs();
      ide.editor.focus();
      $("ide-save-state").textContent = "открыт " + f.name;
    } catch (e) {
      $("ide-save-state").textContent = "ошибка: " + e.message;
    }
  }

  function renderIdeTabs() {
    const box = $("ide-file-tabs");
    box.innerHTML = "";
    ide.open.forEach((t) => {
      const el = document.createElement("div");
      el.className = "ide-file-tab" + (ide.active === t.path ? " active" : "") + (t.dirty ? " dirty" : "");
      el.innerHTML = `<span class="dot-save"></span><span>${escapeHtml(t.name)}</span><span class="x">✕</span>`;
      el.onclick = (ev) => {
        if (ev.target.classList.contains("x")) { closeIdeTab(t.path); return; }
        ide.active = t.path;
        openIdeFile(t.path);
      };
      box.appendChild(el);
    });
  }

  function closeIdeTab(path) {
    const idx = ide.open.findIndex((t) => t.path === path);
    if (idx >= 0) ide.open.splice(idx, 1);
    if (ide.active === path) {
      ide.active = ide.open.length ? ide.open[ide.open.length - 1].path : null;
      if (ide.active) openIdeFile(ide.active);
      else {
        ide.editor.setValue("");
        $("ide-welcome").style.display = "";
        renderIdeTabs();
      }
    } else {
      renderIdeTabs();
    }
  }

  async function saveActiveFile() {
    if (!ide.active || !state.sessionId) return;
    const t = ide.open.find((x) => x.path === ide.active);
    if (!t) return;
    $("ide-save-state").textContent = "сохраняю…";
    try {
      await api(`/api/ide/${state.sessionId}/file`, {
        method: "PUT",
        body: JSON.stringify({ path: t.path, content: ide.editor.getValue() }),
      });
      t.dirty = false;
      renderIdeTabs();
      $("ide-save-state").textContent = "сохранено " + t.name;
      loadIdeTree();
    } catch (e) {
      $("ide-save-state").textContent = "ошибка: " + e.message;
    }
  }

  function runActiveFile() {
    if (!ide.active) return;
    sendCommand("python3 " + ide.active + "\n");
    switchView("term");
  }

  function ideCreate(kind) {
    const name = prompt(kind === "file" ? "Имя нового файла:" : "Имя новой папки:");
    if (!name) return;
    const base = ide.active && ide.active.includes("/")
      ? ide.active.slice(0, ide.active.lastIndexOf("/")) : "/home/student";
    const path = base + "/" + name.trim();
    if (kind === "file") {
      openIdeFile(path).then(async () => {
        await api(`/api/ide/${state.sessionId}/file`, {
          method: "PUT", body: JSON.stringify({ path, content: "" }),
        }).catch(() => {});
        loadIdeTree();
      });
    } else {
      api(`/api/ide/${state.sessionId}/mkdir`, {
        method: "POST", body: JSON.stringify({ path }),
      }).then(() => { ide.expanded.add(path); loadIdeTree(); }).catch((e) => alert(e.message));
    }
  }

  function ideFileMenu(item, ev) {
    const act = prompt(`Действие с «${item.name}»:\n1 — переименовать\n2 — удалить`, "1");
    if (act === "1") {
      const nn = prompt("Новое имя:", item.name);
      if (!nn) return;
      const dir = item.path.slice(0, item.path.lastIndexOf("/"));
      api(`/api/ide/${state.sessionId}/rename`, {
        method: "POST", body: JSON.stringify({ from: item.path, to: dir + "/" + nn }),
      }).then(() => loadIdeTree()).catch((e) => alert(e.message));
    } else if (act === "2") {
      if (!confirm(`Удалить «${item.name}»?`)) return;
      api(`/api/ide/${state.sessionId}/delete`, {
        method: "POST", body: JSON.stringify({ path: item.path }),
      }).then(() => { closeIdeTab(item.path); loadIdeTree(); }).catch((e) => alert(e.message));
    }
  }

  /* ---------------- терминал переезжает между вкладками ---------------- */
  function moveTerminalTo(hostId) {
    const host = $(hostId);
    if (!host || !state.term || !state.term.element) return;
    if (state.term.element.parentNode !== host) {
      host.appendChild(state.term.element);
      setTimeout(() => { try { state.fit.fit(); } catch (e) {} }, 80);
    }
  }

  /* ---------------- вкладки Terminal / Web / IDE ---------------- */
  function initTabs() {
    document.querySelectorAll(".term-tab").forEach((tab) => {
      tab.addEventListener("click", () => switchView(tab.dataset.view));
    });
    $("web-frame").addEventListener("load", () => refreshWebStatus());
    $("web-reload").addEventListener("click", () => loadWeb());
    $("web-path").addEventListener("keydown", (e) => {
      if (e.key === "Enter") { e.preventDefault(); loadWeb(); }
    });
    $("web-port").addEventListener("keydown", (e) => {
      if (e.key === "Enter") { e.preventDefault(); syncWebPort(); loadWeb(); }
    });
    $("web-port").addEventListener("input", syncWebPort);
    $("web-port").addEventListener("change", () => { syncWebPort(); loadWeb(); });
    $("web-auto").addEventListener("change", () => {
      if ($("web-auto").checked) startWebAuto(); else stopWebAuto();
    });
  }

  function webPort() {
    return ($("web-port").value || "8080").trim() || "8080";
  }

  function syncWebPort() {
    $("web-port-label").textContent = webPort();
  }

  function switchView(view) {
    document.querySelectorAll(".term-tab").forEach((t) => {
      t.classList.toggle("active", t.dataset.view === view);
    });
    $("view-term").hidden = view !== "term";
    $("view-web").hidden = view !== "web";
    $("view-ide").hidden = view !== "ide";
    if (view === "web") {
      loadWeb();
      startWebAuto();
    } else {
      stopWebAuto();
    }
    if (view === "ide") {
      moveTerminalTo("ide-term-host");
      $("ide-panel").classList.remove("collapsed");
      loadIdeTree();
    } else {
      moveTerminalTo("term-host");
    }
    setTimeout(() => { try { state.fit.fit(); } catch (e) {} }, 80);
    if (view !== "ide") { try { state.term.focus(); } catch (e) {} }
  }

  let webTimer = null;

  function startWebAuto() {
    stopWebAuto();
    webTimer = setInterval(() => {
      if ($("view-web").hidden) return;
      refreshWebStatus();
      if ($("web-auto").checked) loadWeb(true);
    }, 4000);
  }

  function stopWebAuto() {
    if (webTimer) { clearInterval(webTimer); webTimer = null; }
  }

  async function refreshWebStatus() {
    const st = $("web-status");
    if (!state.sessionId) {
      try { await ensureSession(); } catch (e) { st.textContent = "нет сессии"; st.className = "web-status err"; return; }
    }
    try {
      const r = await api(`/api/web/${state.sessionId}/status?port=${encodeURIComponent(webPort())}`);
      if (r.ok) {
        st.textContent = `${r.code || "200"} OK${r.server ? " · " + r.server : ""}`;
        st.className = "web-status ok";
      } else {
        st.textContent = "сервер не отвечает";
        st.className = "web-status err";
      }
    } catch (e) {
      st.textContent = "ошибка проверки";
      st.className = "web-status err";
    }
  }

  function loadWeb(quiet) {
    if (!state.sessionId) {
      ensureSession().then(() => loadWeb(quiet)).catch(() => {});
      return;
    }
    const port = webPort();
    const raw = ($("web-path").value || "/index.html").trim();
    const p = raw.replace(/^\/+/, "");
    const url = `/api/web/${state.sessionId}/proxy/${port}/${p}`;
    const frame = $("web-frame");
    if (!quiet) $("web-status").textContent = "загрузка…";
    frame.src = url;
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
    // 1) сначала критичные обработчики — даже если что-то сломается, интерфейс жив
    bindUi();
    initTerminal();
    initInput();
    initSplitter();
    initNoCopy();
    initTabs();
    applyLayout();

    // 2) необязательные подсистемы — падение одной не ломает остальные
    try { initIde(); } catch (e) { console.error("IDE:", e); }

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

  function bindUi() {
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
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
