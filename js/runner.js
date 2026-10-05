/* 主執行緒端的 Python 執行器：一次只跑一個工作，逾時就砍掉 worker 並重建。 */
(function () {
  const DEFAULT_TIMEOUT = 10000;

  function normalize(text) {
    const lines = String(text).replace(/\r\n/g, "\n").split("\n").map((l) => l.replace(/\s+$/, ""));
    while (lines.length && lines[lines.length - 1] === "") lines.pop();
    return lines.join("\n");
  }

  class PyRunner {
    constructor() {
      this.listeners = new Set();
      this.queue = Promise.resolve();
      this.seq = 0;
      this.state = "idle"; // idle | loading | ready | busy
      this._spawn();
    }

    onStatus(fn) {
      this.listeners.add(fn);
      fn(this.state, this.statusText || "");
    }

    _emit(state, text) {
      this.state = state;
      if (text !== undefined) this.statusText = text;
      this.listeners.forEach((fn) => fn(state, this.statusText));
    }

    _spawn() {
      this.worker = new Worker("js/worker.js");
      this.pending = null;
      this._emit("loading", "正在啟動 Python…");
      this.worker.onmessage = (e) => {
        const msg = e.data;
        if (msg.type === "status") {
          this._emit(this.pending ? "busy" : msg.text === "Python 已就緒" ? "ready" : "loading", msg.text);
          return;
        }
        const p = this.pending;
        if (!p || msg.id !== p.id) return;
        if (msg.type === "started") {
          // 套件下載完成、真正開始執行時才開始計時
          p.timer = setTimeout(() => {
            this.worker.terminate();
            this.pending = null;
            p.resolve({ ok: false, timeout: true, stdout: "", stderr: `執行超過 ${p.timeout / 1000} 秒，已強制中止（可能是無窮迴圈或效率太低）。` });
            this._spawn();
          }, p.timeout);
        } else if (msg.type === "result") {
          clearTimeout(p.timer);
          this.pending = null;
          this._emit("ready", "Python 已就緒");
          p.resolve(msg.result);
        }
      };
      this.worker.onerror = (e) => {
        this._emit("error", "Python 載入失敗：" + (e.message || "請確認網路連線（需要連到 cdn.jsdelivr.net）"));
        const p = this.pending;
        if (p) {
          clearTimeout(p.timer);
          this.pending = null;
          p.resolve({ ok: false, stdout: "", stderr: "Python 執行環境載入失敗，請重新整理頁面。", fatal: true });
        }
      };
      this.worker.postMessage({ id: 0, cmd: "ping", args: {} });
    }

    _call(cmd, args, timeout) {
      const job = () =>
        new Promise((resolve) => {
          const id = ++this.seq;
          this.pending = { id, resolve, timeout: timeout || DEFAULT_TIMEOUT, timer: null };
          this._emit("busy", "執行中…");
          this.worker.postMessage({ id, cmd, args });
        });
      const p = this.queue.then(job, job);
      this.queue = p.catch(() => {});
      return p;
    }

    run(code, stdin = "", after = "", timeout) {
      return this._call("run", { code, stdin, after }, timeout);
    }

    gen(gen, seed) {
      return this._call("gen", { gen, seed }, 5000);
    }

    /** 回傳 verdict：AC / WA / RE / TLE */
    async judgeOne(code, test, timeout) {
      const r = await this.run(code, test.stdin, test.after, timeout);
      let verdict = "AC";
      if (r.timeout) verdict = "TLE";
      else if (!r.ok) verdict = "RE";
      else if (normalize(r.stdout) !== normalize(test.expected)) verdict = "WA";
      return { verdict, ...r };
    }
  }

  window.PyRunner = PyRunner;
  window.normalizeOutput = normalize;
})();
