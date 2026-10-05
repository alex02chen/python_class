/* Python 深入教學 — 單頁應用 */
(function () {
  "use strict";

  const COURSE = window.COURSE;
  const UNITS = COURSE.units;
  const EXERCISES = {};
  UNITS.forEach((u) => u.exercises.forEach((ex, i) => (EXERCISES[ex.id] = { ex, unit: u, index: i })));
  const ALL_EX = UNITS.flatMap((u) => u.exercises);

  const RANDOM_CASES = 20;
  const JUDGE_TIMEOUT = 10000;
  const TAG_LABEL = { sample: "範例", normal: "一般", corner: "邊界", stress: "壓力" };
  const TAG_CLASS = { sample: "accent", normal: "", corner: "warn", stress: "bad" };
  const VERDICT_TEXT = { AC: "通過", WA: "答案錯誤", RE: "執行錯誤", TLE: "逾時" };

  /* ---------- 小工具 ---------- */
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  function el(tag, attrs = {}, ...children) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v == null || v === false) continue;
      if (k === "class") node.className = v;
      else if (k === "html") node.innerHTML = v;
      else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
      else node.setAttribute(k, v === true ? "" : v);
    }
    for (const c of children.flat()) if (c != null && c !== false) node.append(c.nodeType ? c : document.createTextNode(c));
    return node;
  }
  const md = (text) => marked.parse(text || "");
  const mdInline = (text) => marked.parseInline(text || "");

  const store = {
    get(key, fallback) {
      try {
        const v = localStorage.getItem("pyclass:" + key);
        return v == null ? fallback : JSON.parse(v);
      } catch (e) {
        return fallback;
      }
    },
    set(key, value) {
      try {
        localStorage.setItem("pyclass:" + key, JSON.stringify(value));
      } catch (e) {
        /* 私密瀏覽或儲存空間已滿時忽略 */
      }
    },
  };
  const isPassed = (id) => !!store.get("passed", {})[id];
  function setPassed(id) {
    const p = store.get("passed", {});
    p[id] = true;
    store.set("passed", p);
  }

  function truncate(text, max = 3000) {
    text = String(text);
    if (text.length <= max) return { text, cut: 0 };
    return { text: text.slice(0, max), cut: text.length };
  }

  function downloadFile(name, content, type = "application/json") {
    const blob = new Blob([content], { type });
    const a = el("a", { href: URL.createObjectURL(blob), download: name });
    document.body.append(a);
    a.click();
    setTimeout(() => {
      URL.revokeObjectURL(a.href);
      a.remove();
    }, 0);
  }

  /* ---------- Python 執行器 ---------- */
  const runner = new PyRunner();
  runner.onStatus((state, text) => {
    const s = $("#pyStatus");
    s.dataset.state = state;
    $(".text", s).textContent = text || { ready: "Python 已就緒", loading: "Python 載入中…", busy: "執行中…" }[state] || "";
  });

  /* ---------- CodeMirror ---------- */
  function makeEditor(parent, value, opts = {}) {
    const cm = CodeMirror(parent, {
      value,
      mode: "python",
      indentUnit: 4,
      tabSize: 4,
      lineNumbers: opts.lineNumbers !== false,
      matchBrackets: true,
      autoCloseBrackets: true,
      viewportMargin: opts.autoHeight ? Infinity : 10,
      extraKeys: {
        Tab: (cm) => (cm.somethingSelected() ? cm.indentSelection("add") : cm.replaceSelection("    ", "end")),
        "Shift-Tab": (cm) => cm.indentSelection("subtract"),
        "Ctrl-/": "toggleComment",
        "Cmd-/": "toggleComment",
        "Ctrl-Enter": () => opts.onRun && opts.onRun(),
        "Cmd-Enter": () => opts.onRun && opts.onRun(),
        "Shift-Ctrl-Enter": () => opts.onSubmit && opts.onSubmit(),
        "Shift-Cmd-Enter": () => opts.onSubmit && opts.onSubmit(),
      },
    });
    return cm;
  }

  function highlightStatic(root) {
    $$("pre > code.language-python", root).forEach((code) => {
      const text = code.textContent;
      code.textContent = "";
      CodeMirror.runMode(text, "python", code);
      code.classList.add("cm-s-default");
    });
  }

  function renderOutput(box, r) {
    box.innerHTML = "";
    if (r.timeout) {
      box.append(el("span", { class: "err" }, r.stderr));
      return;
    }
    if (r.stdout) box.append(r.stdout);
    if (r.stderr) box.append(el("span", { class: "err" }, (r.stdout && !r.stdout.endsWith("\n") ? "\n" : "") + r.stderr));
    if (!r.stdout && !r.stderr) box.append(el("span", { class: "dim" }, "（沒有輸出）"));
    if (r.time_ms != null) box.append(el("span", { class: "dim" }, `\n— 執行時間 ${r.time_ms.toFixed(1)} ms`));
  }

  /* 把課程中的 python 程式碼區塊變成可編輯、可執行的元件 */
  function makeRunnable(pre) {
    const original = pre.textContent.replace(/\n$/, "");
    const wrap = el("div", { class: "runnable" });
    pre.replaceWith(wrap);
    const output = el("pre", { class: "output", hidden: true });
    const run = async () => {
      runBtn.disabled = true;
      output.hidden = false;
      output.innerHTML = '<span class="dim">執行中…</span>';
      const r = await runner.run(cm.getValue(), "", "", 15000);
      renderOutput(output, r);
      runBtn.disabled = false;
    };
    const cm = makeEditor(wrap, original, { lineNumbers: false, autoHeight: true, onRun: run });
    const runBtn = el("button", { class: "btn primary small", onclick: run }, "▶ 執行");
    const resetBtn = el("button", { class: "btn small", onclick: () => cm.setValue(original), title: "還原成原本的範例程式碼" }, "↺ 還原");
    wrap.append(el("div", { class: "runnable-bar" }, runBtn, resetBtn, el("span", { class: "hint" }, "可直接修改 · Ctrl+Enter 執行")), output);
  }

  /* ---------- 側邊欄 ---------- */
  function renderSidebar() {
    const nav = $("#sidebar");
    nav.innerHTML = "";
    nav.append(
      el("a", { class: "nav-link", href: "#/" }, "🏠 首頁"),
      el("a", { class: "nav-link", href: "#/playground" }, "🧪 自由練習場"),
    );
    for (const u of UNITS) {
      const done = u.exercises.filter((e) => isPassed(e.id)).length;
      const sub = el("div", { class: "nav-sub" },
        el("a", { class: "nav-link", href: `#/unit/${u.id}` }, "📖 課程內容"),
        el("a", { class: "nav-link", href: `#/unit/${u.id}/quiz` }, "❓ 重點問答"),
        u.exercises.map((ex) =>
          el("a", { class: "nav-link", href: `#/ex/${ex.id}` }, `✏️ ${ex.title}`, el("span", { class: "nav-ex-status" }, isPassed(ex.id) ? "✅" : "")),
        ),
      );
      nav.append(el("div", { class: "nav-unit" },
        el("div", { class: "nav-unit-title" }, `${u.icon} ${u.num}. ${u.title}`, el("small", {}, `${done}/${u.exercises.length}`)),
        sub));
    }
    markActive();
  }

  function markActive() {
    const hash = location.hash || "#/";
    $$("#sidebar .nav-link").forEach((a) => a.classList.toggle("active", a.getAttribute("href") === hash));
  }

  /* ---------- 首頁 ---------- */
  function renderHome(app) {
    const totalTests = ALL_EX.reduce((n, e) => n + e.tests.length, 0);
    const passed = ALL_EX.filter((e) => isPassed(e.id)).length;
    app.append(
      el("section", { class: "hero" },
        el("h1", {}, "Python 深入教學"),
        el("p", {}, "從物件模型到 Pandas，每個單元都有深入講解、可直接執行的範例、重點問答，以及附帶大量邊界測資的練習題。所有程式都在你的瀏覽器裡執行，不需要安裝任何東西。"),
        el("p", { class: "muted" }, `共 ${UNITS.length} 個單元 · ${ALL_EX.length} 道練習題 · ${totalTests} 組測資 · 已通過 ${passed} 題`),
        el("div", { class: "features" },
          feature("▶ 範例即點即跑", "課程中的每段程式碼都能修改並執行，立刻驗證觀念。"),
          feature("✔ 自動判題", "每題 8~12 組測資：範例、一般、邊界 (corner case)、壓力測試。"),
          feature("🎲 隨機對拍", "用隨機產生器出題，拿你的程式和參考解答比對，找出隱藏 bug。"),
          feature("🧪 自由練習場", "任意 Python 程式 + 自訂輸入，支援 NumPy、Pandas。"),
        ),
      ),
      el("div", { class: "cards" },
        UNITS.map((u) => {
          const done = u.exercises.filter((e) => isPassed(e.id)).length;
          const pct = Math.round((done / u.exercises.length) * 100);
          return el("div", { class: "card" },
            el("div", { class: "num" }, `UNIT ${u.num}`),
            el("h3", {}, `${u.icon} ${u.title}`),
            el("p", {}, u.summary),
            el("div", { class: "progress-label" }, `練習進度 ${done} / ${u.exercises.length}`),
            el("div", { class: "progress" }, el("div", { style: `width:${pct}%` })),
            el("div", { class: "actions" },
              el("a", { class: "btn primary", href: `#/unit/${u.id}` }, "開始學習"),
              el("a", { class: "btn", href: `#/unit/${u.id}/quiz` }, "重點問答"),
              el("a", { class: "btn", href: `#/ex/${u.exercises[0].id}` }, "練習題"),
            ),
          );
        }),
      ),
    );
    function feature(t, d) {
      return el("div", { class: "feature" }, el("b", {}, t), el("span", {}, d));
    }
  }

  /* ---------- 單元頁：教材 + 問答 + 練習列表 ---------- */
  function renderUnit(app, unit, focusQuiz) {
    const prose = el("article", { class: "prose" });
    prose.innerHTML = md(unit.lesson);
    $$("pre > code.language-python", prose).forEach((code) => makeRunnable(code.parentElement));
    app.append(prose);

    prose.append(renderQuiz(unit));

    prose.append(el("h2", { id: "exercises" }, "✏️ 練習題"),
      el("p", { class: "muted" }, "每題都有範例、一般、邊界 (corner)、壓力 (stress) 測資，送出後自動判題。"),
      exerciseList(unit));

    const i = UNITS.indexOf(unit);
    prose.append(el("div", { class: "pager" },
      i > 0 ? el("a", { class: "btn", href: `#/unit/${UNITS[i - 1].id}` }, `← ${UNITS[i - 1].title}`) : el("span"),
      i < UNITS.length - 1 ? el("a", { class: "btn", href: `#/unit/${UNITS[i + 1].id}` }, `${UNITS[i + 1].title} →`) : el("span")));

    if (focusQuiz) requestAnimationFrame(() => $("#quiz").scrollIntoView());
  }

  function exerciseList(unit) {
    return el("div", { class: "ex-list" },
      unit.exercises.map((ex) => {
        const counts = tagCounts(ex);
        return el("a", { class: "ex-row", href: `#/ex/${ex.id}` },
          el("div", {},
            el("div", { class: "title" }, ex.title),
            el("div", { class: "meta" }, `${ex.mode === "func" ? "函式題" : "標準輸入輸出"} · ${ex.tests.length} 組測資（邊界 ${counts.corner || 0}）`)),
          el("div", { class: "right" },
            el("span", { class: "stars", title: `難度 ${ex.difficulty}/3` }, "★".repeat(ex.difficulty) + "☆".repeat(3 - ex.difficulty)),
            isPassed(ex.id) ? el("span", { class: "badge ok" }, "已通過") : el("span", { class: "badge" }, "未完成")));
      }));
  }

  function tagCounts(ex) {
    const c = {};
    ex.tests.forEach((t) => (c[t.tag] = (c[t.tag] || 0) + 1));
    return c;
  }

  function renderQuiz(unit) {
    const key = "quiz:" + unit.id;
    const answers = store.get(key, {});
    const choices = unit.quiz.filter((q) => q.type === "choice");
    const score = el("span", { class: "quiz-score" });
    const updateScore = () => {
      const a = store.get(key, {});
      const right = unit.quiz.filter((q, i) => q.type === "choice" && a[i] === q.answer).length;
      const answered = Object.keys(a).length;
      score.textContent = `選擇題：已作答 ${answered} / ${choices.length}，答對 ${right} 題`;
    };
    const wrap = el("section", { class: "quiz", id: "quiz" },
      el("h2", {}, "❓ 重點問答"),
      el("div", { class: "toolbar" }, score, el("span", { class: "spacer" }),
        el("button", { class: "btn small", onclick: () => { store.set(key, {}); wrap.replaceWith(renderQuiz(unit)); } }, "重新作答")));

    unit.quiz.forEach((q, i) => {
      const item = el("div", { class: "quiz-item" });
      item.append(el("div", { class: "quiz-q", html: `<span class="qn">Q${i + 1}.</span>` + md(q.q) }));
      if (q.type === "choice") {
        const explain = el("div", { class: "quiz-explain", hidden: true });
        const opts = q.options.map((o, j) =>
          el("button", { class: "quiz-opt", html: `${"ABCD"[j]}. ${mdInline(o)}`, onclick: () => choose(j) }));
        const choose = (j) => {
          const a = store.get(key, {});
          a[i] = j;
          store.set(key, a);
          opts.forEach((b, k) => {
            b.classList.toggle("correct", k === q.answer);
            b.classList.toggle("wrong", k === j && j !== q.answer);
          });
          explain.hidden = false;
          explain.innerHTML = (j === q.answer ? "✅ <b>正確！</b> " : `❌ <b>正確答案是 ${"ABCD"[q.answer]}。</b> `) + md(q.explain);
          highlightStatic(explain);
          updateScore();
        };
        item.append(el("div", { class: "quiz-options" }, opts), explain);
        if (answers[i] != null) choose(answers[i]);
      } else {
        const ans = el("div", { class: "quiz-explain", html: md(q.answer) });
        item.append(el("details", { class: "qa-answer" }, el("summary", {}, "先想一想，再點開參考答案"), ans));
        highlightStatic(ans);
      }
      highlightStatic(item);
      wrap.append(item);
    });
    updateScore();
    return wrap;
  }

  /* ---------- 練習題頁 ---------- */
  function renderExercise(app, ex, unit) {
    const codeKey = "code:" + ex.id;
    const isFunc = ex.mode === "func";
    const sample = ex.tests.find((t) => t.tag === "sample") || ex.tests[0];

    // 左欄：題目、提示、測資
    const statement = el("div", { class: "prose ex-statement", html: md(ex.statement) });
    highlightStatic(statement);
    const left = el("div", {},
      el("div", { class: "panel" }, statement),
      ex.hints.length
        ? el("div", { class: "panel" }, el("h2", {}, "💡 提示"),
            ex.hints.map((h, i) => el("details", { class: "qa-answer" }, el("summary", {}, `提示 ${i + 1}`), el("div", { class: "prose", html: md(h) }))))
        : null,
      testPanel());

    // 右欄：編輯器與結果
    const editorWrap = el("div", { class: "editor-wrap" });
    const runBtn = el("button", { class: "btn", onclick: () => runCustom(), title: "Ctrl+Enter" }, "▶ 執行");
    const submitBtn = el("button", { class: "btn primary", onclick: () => submit(), title: "Ctrl+Shift+Enter" }, "✔ 提交判題");
    const randomBtn = ex.gen ? el("button", { class: "btn", onclick: () => randomTest(), title: "用隨機測資和參考解答比對" }, `🎲 隨機對拍 ×${RANDOM_CASES}`) : null;
    const solBtn = el("button", { class: "btn", onclick: () => showSolution() }, "💡 參考解答");
    const resetBtn = el("button", { class: "btn", onclick: () => { if (confirm("確定要清除你的程式碼，回到初始範本嗎？")) cm.setValue(ex.starter); } }, "↺ 重設");
    const customInput = el("textarea", { class: "io", spellcheck: "false" });
    customInput.value = isFunc ? sample.after : sample.stdin;
    const resultBox = el("div", {}, el("div", { class: "muted", html: "按 <b>▶ 執行</b> 用下方自訂輸入測試，或按 <b>✔ 提交判題</b> 跑全部測資。" }));
    const busyButtons = [runBtn, submitBtn, randomBtn].filter(Boolean);

    const right = el("div", { class: "panel editor-panel" },
      editorWrap,
      el("div", { class: "toolbar" }, runBtn, submitBtn, randomBtn, el("span", { class: "spacer" }), solBtn, resetBtn),
      el("label", { class: "field" }, isFunc ? "自訂測試程式（會接在你的程式碼之後、於同一命名空間執行）" : "自訂標準輸入 (stdin)"),
      customInput,
      el("h2", { style: "margin-top:14px" }, "結果"),
      resultBox);

    const counts = tagCounts(ex);
    app.append(el("div", { class: "ex-page" },
      el("div", { class: "crumbs" }, el("a", { href: `#/unit/${unit.id}` }, `${unit.icon} 單元 ${unit.num}：${unit.title}`), " / 練習題"),
      el("div", { class: "ex-head" },
        el("h1", {}, ex.title),
        el("span", { class: "stars" }, "★".repeat(ex.difficulty) + "☆".repeat(3 - ex.difficulty)),
        el("span", { class: "badge accent" }, isFunc ? "函式題" : "標準輸入輸出"),
        el("span", { class: "badge" }, `${ex.tests.length} 組測資`),
        counts.corner ? el("span", { class: "badge warn" }, `邊界 ${counts.corner}`) : null,
        el("span", { id: "passBadge" }, isPassed(ex.id) ? el("span", { class: "badge ok" }, "✅ 已通過") : null)),
      el("div", { class: "ex-grid" }, left, right),
      pager()));

    const cm = makeEditor(editorWrap, store.get(codeKey, ex.starter), { onRun: () => runCustom(), onSubmit: () => submit() });
    let saveTimer;
    cm.on("change", () => {
      clearTimeout(saveTimer);
      saveTimer = setTimeout(() => store.set(codeKey, cm.getValue()), 400);
    });
    requestAnimationFrame(() => cm.refresh());

    function setBusy(b) {
      busyButtons.forEach((btn) => (btn.disabled = b));
    }

    async function runCustom() {
      if (runBtn.disabled) return;
      setBusy(true);
      resultBox.innerHTML = "";
      const out = el("pre", { class: "output", html: '<span class="dim">執行中…</span>' });
      resultBox.append(el("div", { class: "out-box" }, out));
      const r = isFunc ? await runner.run(cm.getValue(), "", customInput.value, JUDGE_TIMEOUT)
                       : await runner.run(cm.getValue(), customInput.value, "", JUDGE_TIMEOUT);
      renderOutput(out, r);
      setBusy(false);
    }

    async function submit() {
      if (submitBtn.disabled) return;
      setBusy(true);
      const code = cm.getValue();
      const summary = el("div", { class: "summary info" }, "判題中…");
      const tbody = el("tbody");
      resultBox.innerHTML = "";
      resultBox.append(summary, el("div", { style: "overflow-x:auto" },
        el("table", { class: "results" },
          el("thead", {}, el("tr", {}, el("th", {}, "#"), el("th", {}, "結果"), el("th", {}, "類型"), el("th", {}, "說明"), el("th", {}, "時間"))),
          tbody)));
      const rows = ex.tests.map((t, i) => {
        const v = el("span", { class: "verdict PENDING" }, "…");
        const time = el("td", { class: "muted" }, "");
        const tr = el("tr", {}, el("td", {}, i + 1), el("td", {}, v), el("td", {}, el("span", { class: `badge ${TAG_CLASS[t.tag]}` }, TAG_LABEL[t.tag])),
          el("td", {}, t.note || ""), time);
        tbody.append(tr);
        return { tr, v, time };
      });
      let ac = 0;
      let firstFail = null;
      for (let i = 0; i < ex.tests.length; i++) {
        const t = ex.tests[i];
        summary.textContent = `判題中… ${i + 1} / ${ex.tests.length}`;
        const r = await runner.judgeOne(code, t, JUDGE_TIMEOUT);
        const row = rows[i];
        row.v.className = `verdict ${r.verdict}`;
        row.v.textContent = r.verdict;
        row.v.title = VERDICT_TEXT[r.verdict];
        row.time.textContent = r.timeout ? "—" : r.time_ms < 1 ? "<1 ms" : `${r.time_ms.toFixed(0)} ms`;
        if (r.verdict === "AC") ac++;
        else if (firstFail == null) firstFail = i;
        attachDetail(row.tr, t, r);
        if (r.fatal) break;
      }
      const all = ac === ex.tests.length;
      summary.className = `summary ${all ? "ok" : "bad"}`;
      summary.innerHTML = all
        ? `🎉 全部通過！${ac} / ${ex.tests.length}`
        : `通過 ${ac} / ${ex.tests.length}　<span style="font-weight:400">點選任一列可查看輸入、期望輸出與你的輸出</span>`;
      if (all) {
        setPassed(ex.id);
        $("#passBadge").replaceChildren(el("span", { class: "badge ok" }, "✅ 已通過"));
        renderSidebar();
      } else if (firstFail != null) {
        rows[firstFail].tr.click();
      }
      setBusy(false);
    }

    function attachDetail(tr, t, r) {
      tr.classList.add("clickable");
      let detail = null;
      tr.onclick = () => {
        if (detail) {
          detail.remove();
          detail = null;
          return;
        }
        detail = el("tr", { class: "detail-row" }, el("td", { colspan: 5 }, compareView(t, r)));
        tr.after(detail);
      };
    }

    function compareView(t, r) {
      const blocks = [];
      if (t.stdin || !isFunc) blocks.push(preBlock("輸入 (stdin)", t.stdin || "（空）"));
      if (t.after) blocks.push(preBlock("測試程式", t.after));
      blocks.push(preBlock("期望輸出", t.expected || "（無輸出）"));
      if (r) {
        blocks.push(preBlock("你的輸出", r.stdout || "（無輸出）", t.expected));
        if (r.stderr) blocks.push(preBlock(r.timeout ? "逾時" : "錯誤訊息", r.stderr));
      }
      return el("div", {},
        el("div", { class: "cmp" }, blocks),
        el("button", { class: "btn small", onclick: () => loadToCustom(t) }, "⤴ 載入到自訂輸入"));
    }

    function preBlock(title, text, expected) {
      const { text: shown, cut } = truncate(text);
      const pre = el("pre");
      if (expected != null) {
        // 標出第一個與期望輸出不同的行
        const a = normalizeOutput(shown).split("\n");
        const b = normalizeOutput(expected).split("\n");
        let marked = false;
        a.forEach((line, i) => {
          if (!marked && line !== b[i]) {
            pre.append(el("span", { class: "diff", title: `第 ${i + 1} 行與期望不同` }, line || " "));
            marked = true;
          } else pre.append(line);
          if (i < a.length - 1) pre.append("\n");
        });
        if (!marked && a.length < b.length) pre.append(el("span", { class: "diff" }, "\n（少了 " + (b.length - a.length) + " 行）"));
      } else {
        pre.textContent = shown;
      }
      if (cut) pre.append(el("div", { class: "trunc" }, `…（共 ${cut.toLocaleString()} 字元，僅顯示前 3000 字）`));
      return el("div", {}, el("h4", {}, title), pre);
    }

    function loadToCustom(t) {
      customInput.value = isFunc ? t.after : t.stdin;
      customInput.scrollIntoView({ block: "center" });
      customInput.focus();
    }

    async function randomTest() {
      if (randomBtn.disabled) return;
      setBusy(true);
      const code = cm.getValue();
      const summary = el("div", { class: "summary info" }, "準備隨機測資…");
      const detail = el("div");
      resultBox.innerHTML = "";
      resultBox.append(summary, detail);
      const base = Math.floor(Math.random() * 1e9);
      let pass = 0;
      for (let i = 0; i < RANDOM_CASES; i++) {
        summary.textContent = `隨機對拍中… ${i + 1} / ${RANDOM_CASES}`;
        const c = await runner.gen(ex.gen, base + i);
        if (c.fatal || c.ok === false) {
          summary.className = "summary bad";
          summary.textContent = "隨機產生器發生錯誤：" + (c.stderr || "");
          setBusy(false);
          return;
        }
        const ref = await runner.run(ex.solution, c.stdin, c.after, JUDGE_TIMEOUT);
        const test = { stdin: c.stdin, after: c.after, expected: ref.stdout, tag: "normal", note: `隨機 seed=${base + i}` };
        const r = await runner.judgeOne(code, test, JUDGE_TIMEOUT);
        if (r.verdict !== "AC") {
          summary.className = "summary bad";
          summary.textContent = `第 ${i + 1} 組隨機測資失敗（${r.verdict} ${VERDICT_TEXT[r.verdict]}），前面通過 ${pass} 組`;
          detail.append(compareView(test, r));
          setBusy(false);
          return;
        }
        pass++;
      }
      summary.className = "summary ok";
      summary.textContent = `🎲 ${RANDOM_CASES} 組隨機測資全部與參考解答一致！`;
      setBusy(false);
    }

    function showSolution() {
      if (!isPassed(ex.id) && !confirm("建議先自己挑戰，真的卡住再看解答。確定要看參考解答嗎？")) return;
      const pre = el("pre", {}, el("code", { class: "language-python" }, ex.solution));
      const body = el("div", { class: "prose", style: "max-width:none" }, pre,
        el("div", { class: "toolbar" },
          el("button", { class: "btn primary", onclick: () => { cm.setValue(ex.solution); closeModal(); } }, "載入到編輯器（覆蓋目前程式碼）")));
      highlightStatic(body);
      openModal(`參考解答：${ex.title}`, body);
    }

    function testPanel() {
      const tbody = el("tbody");
      ex.tests.forEach((t, i) => {
        const tr = el("tr", { class: "clickable" }, el("td", {}, i + 1),
          el("td", {}, el("span", { class: `badge ${TAG_CLASS[t.tag]}` }, TAG_LABEL[t.tag])), el("td", {}, t.note || "—"));
        let detail = null;
        tr.onclick = () => {
          if (detail) { detail.remove(); detail = null; return; }
          detail = el("tr", { class: "detail-row" }, el("td", { colspan: 3 }, compareView(t, null)));
          tr.after(detail);
        };
        tbody.append(tr);
      });
      const c = tagCounts(ex);
      return el("div", { class: "panel" },
        el("h2", {}, "🧪 測資"),
        el("p", { class: "muted", style: "margin:0 0 8px;font-size:.9rem" },
          Object.keys(TAG_LABEL).filter((k) => c[k]).map((k) => `${TAG_LABEL[k]} ${c[k]}`).join(" · ") +
          "。期望輸出由參考解答產生並經過驗證。點選任一列查看內容。"),
        el("div", { style: "overflow-x:auto" },
          el("table", { class: "test-table" }, el("thead", {}, el("tr", {}, el("th", {}, "#"), el("th", {}, "類型"), el("th", {}, "測試重點"))), tbody)),
        el("div", { class: "toolbar" },
          el("button", { class: "btn small", onclick: () => downloadFile(`${ex.id}-tests.json`, JSON.stringify(ex.tests, null, 2)) }, "⬇ 下載全部測資 (JSON)"),
          ex.gen ? el("button", { class: "btn small", onclick: () => showGen() }, "查看隨機產生器") : null));
    }

    function showGen() {
      const body = el("div", { class: "prose", style: "max-width:none" },
        el("p", {}, "這個產生器定義 gen(rng)，回傳一組 stdin（或測試程式）。按「🎲 隨機對拍」時，平台會用它產生資料，分別交給參考解答與你的程式執行並比對輸出。"),
        el("pre", {}, el("code", { class: "language-python" }, ex.gen)));
      highlightStatic(body);
      openModal("隨機測資產生器", body);
    }

    function pager() {
      const idx = ALL_EX.indexOf(ex);
      const prev = ALL_EX[idx - 1];
      const next = ALL_EX[idx + 1];
      return el("div", { class: "pager" },
        prev ? el("a", { class: "btn", href: `#/ex/${prev.id}` }, `← ${prev.title}`) : el("span"),
        next ? el("a", { class: "btn", href: `#/ex/${next.id}` }, `${next.title} →`) : el("span"));
    }
  }

  /* ---------- 自由練習場 ---------- */
  const PLAYGROUND_DEFAULT = `# 自由練習場：任意 Python 程式碼，支援 numpy / pandas（第一次 import 需下載）
name = input("你的名字：")
print(f"哈囉，{name}！")

import sys
nums = [int(x) for x in sys.stdin.read().split()]
print("其餘輸入的總和：", sum(nums))
`;

  function renderPlayground(app) {
    const editorWrap = el("div", { class: "editor-wrap" });
    const stdin = el("textarea", { class: "io", spellcheck: "false" });
    stdin.value = store.get("playground:stdin", "Ada\n1 2 3\n4 5");
    const out = el("pre", { class: "output", html: '<span class="dim">按 ▶ 執行（Ctrl+Enter）</span>' });
    const runBtn = el("button", { class: "btn primary", onclick: () => run() }, "▶ 執行");
    app.append(el("div", { class: "prose", style: "max-width:1100px" },
      el("h1", {}, "🧪 自由練習場"),
      el("p", { class: "muted" }, "寫任何 Python 程式並執行。標準輸入 (input()、sys.stdin) 讀取下方的文字框。程式碼會自動儲存在這個瀏覽器中。"),
      el("div", { class: "panel" }, editorWrap,
        el("div", { class: "toolbar" }, runBtn, el("span", { class: "spacer" }),
          el("button", { class: "btn", onclick: () => cm.setValue(PLAYGROUND_DEFAULT) }, "↺ 範例")),
        el("label", { class: "field" }, "標準輸入 (stdin)"), stdin,
        el("label", { class: "field" }, "輸出"), el("div", { class: "out-box" }, out))));
    const cm = makeEditor(editorWrap, store.get("playground:code", PLAYGROUND_DEFAULT), { onRun: () => run() });
    cm.on("change", () => store.set("playground:code", cm.getValue()));
    stdin.addEventListener("input", () => store.set("playground:stdin", stdin.value));
    requestAnimationFrame(() => cm.refresh());
    async function run() {
      if (runBtn.disabled) return;
      runBtn.disabled = true;
      out.innerHTML = '<span class="dim">執行中…</span>';
      renderOutput(out, await runner.run(cm.getValue(), stdin.value, "", 20000));
      runBtn.disabled = false;
    }
  }

  /* ---------- Modal ---------- */
  function openModal(title, body) {
    $("#modalTitle").textContent = title;
    $("#modalBody").replaceChildren(body);
    $("#modal").hidden = false;
  }
  function closeModal() {
    $("#modal").hidden = true;
  }
  $("#modalClose").onclick = closeModal;
  $("#modal").addEventListener("click", (e) => { if (e.target.id === "modal") closeModal(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeModal(); });

  /* ---------- 路由 ---------- */
  function route() {
    const app = $("#app");
    app.innerHTML = "";
    closeModal();
    document.body.classList.remove("nav-open");
    const parts = (location.hash.replace(/^#\/?/, "") || "").split("/").filter(Boolean);
    let title = "Python 深入教學";
    if (parts[0] === "unit" && UNITS.find((u) => u.id === parts[1])) {
      const unit = UNITS.find((u) => u.id === parts[1]);
      renderUnit(app, unit, parts[2] === "quiz");
      title = `${unit.title} · ${title}`;
    } else if (parts[0] === "ex" && EXERCISES[parts[1]]) {
      const { ex, unit } = EXERCISES[parts[1]];
      renderExercise(app, ex, unit);
      title = `${ex.title} · ${title}`;
    } else if (parts[0] === "playground") {
      renderPlayground(app);
      title = `自由練習場 · ${title}`;
    } else {
      renderHome(app);
    }
    document.title = title;
    markActive();
    if (parts[2] !== "quiz") window.scrollTo(0, 0);
    app.focus({ preventScroll: true });
  }

  /* ---------- 主題與手機選單 ---------- */
  $("#themeBtn").onclick = () => {
    const cur = document.documentElement.dataset.theme ||
      (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("pyclass:theme", next); } catch (e) { /* 忽略 */ }
  };
  $("#menuBtn").onclick = () => document.body.classList.toggle("nav-open");
  $("#scrim").onclick = () => document.body.classList.remove("nav-open");

  marked.setOptions({ gfm: true, breaks: false });
  renderSidebar();
  window.addEventListener("hashchange", route);
  route();
})();
