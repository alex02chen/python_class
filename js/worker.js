/* Pyodide Web Worker：在背景執行 Python，主執行緒可隨時 terminate() 以中止無窮迴圈。 */
const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.27.7/full/";

importScripts(PYODIDE_URL + "pyodide.js");

const status = (text) => self.postMessage({ type: "status", text });

const ready = (async () => {
  status("正在下載 Python 執行環境（第一次約需數秒）…");
  const py = await loadPyodide({ indexURL: PYODIDE_URL });
  const src = await (await fetch(new URL("../py/harness.py", self.location))).text();
  py.FS.writeFile("/home/pyodide/harness.py", src);
  py.runPython("import sys; sys.path.insert(0, '/home/pyodide'); import harness");
  status("Python 已就緒");
  return { py, harness: py.pyimport("harness") };
})();

function toJs(proxy) {
  const obj = proxy.toJs({ dict_converter: Object.fromEntries });
  proxy.destroy();
  return obj;
}

async function loadPackages(py, codes) {
  for (const code of codes) {
    if (!code) continue;
    await py.loadPackagesFromImports(code, {
      messageCallback: (msg) => status(msg.replace(/^Loading/, "下載套件").replace(/^Loaded/, "已載入")),
      errorCallback: (msg) => status(msg),
    });
  }
}

self.onmessage = async (e) => {
  const { id, cmd, args } = e.data;
  try {
    const { py, harness } = await ready;
    if (cmd === "run") {
      await loadPackages(py, [args.code, args.after]);
      self.postMessage({ type: "started", id });
      const res = toJs(harness.run(args.code, args.stdin || "", args.after || ""));
      self.postMessage({ type: "result", id, result: res });
    } else if (cmd === "gen") {
      self.postMessage({ type: "started", id });
      const res = toJs(harness.gen_case(args.gen, args.seed));
      self.postMessage({ type: "result", id, result: res });
    } else if (cmd === "ping") {
      self.postMessage({ type: "result", id, result: { ok: true } });
    }
  } catch (err) {
    self.postMessage({ type: "result", id, result: { ok: false, stdout: "", stderr: String(err), fatal: true } });
  }
};
