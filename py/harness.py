"""判題核心：瀏覽器端 (Pyodide Web Worker) 與 tools/build.py 共用同一份程式碼，
確保「產生期望輸出」與「實際判題」的執行語意完全一致。"""

import io
import linecache
import os
import random
import sys
import time
import traceback

_HIDDEN = {"harness.py"}


def normalize(text):
    """比對前的正規化：統一換行、去除每行行尾空白、去除結尾空行。"""
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def same_output(a, b):
    return normalize(a) == normalize(b)


def _register_source(filename, source):
    # 讓 traceback 能顯示使用者程式碼的原始行
    linecache.cache[filename] = (len(source), None, source.splitlines(True), filename)


def _format_exc():
    exc_type, exc, tb = sys.exc_info()
    te = traceback.TracebackException(exc_type, exc, tb)
    te.stack = traceback.StackSummary.from_list(
        [f for f in te.stack if os.path.basename(f.filename) not in _HIDDEN]
    )
    return "".join(te.format())


def _make_input(stream):
    def _input(prompt=""):
        # 判題時忽略提示字串，避免污染輸出
        line = stream.readline()
        if line == "":
            raise EOFError("EOF when reading a line（沒有更多輸入了）")
        return line[:-1] if line.endswith("\n") else line

    return _input


def run(code, stdin="", after=""):
    """執行使用者程式碼 code（stdin 為標準輸入），接著在同一個命名空間執行測試碼 after。

    回傳 dict：stdout、stderr、ok（是否無未捕捉例外）、time_ms。
    """
    stdin_stream = io.StringIO(stdin)
    out, err = io.StringIO(), io.StringIO()
    ns = {"__name__": "__main__", "input": _make_input(stdin_stream)}
    saved = sys.stdin, sys.stdout, sys.stderr
    sys.stdin, sys.stdout, sys.stderr = stdin_stream, out, err
    ok = True
    t0 = time.perf_counter()
    try:
        _register_source("main.py", code)
        exec(compile(code, "main.py", "exec"), ns)
        if after:
            _register_source("test.py", after)
            exec(compile(after, "test.py", "exec"), ns)
    except SystemExit as e:
        if e.code not in (None, 0):
            ok = False
            err.write(f"SystemExit: {e.code}\n")
    except BaseException:  # noqa: BLE001 — 使用者程式的任何錯誤都要回報
        ok = False
        err.write(_format_exc())
    finally:
        sys.stdin, sys.stdout, sys.stderr = saved
    elapsed = (time.perf_counter() - t0) * 1000
    return {"stdout": out.getvalue(), "stderr": err.getvalue(), "ok": ok, "time_ms": round(elapsed, 2)}


def gen_case(gen_code, seed):
    """執行題目的隨機測資產生器：gen_code 需定義 gen(rng) 回傳 stdin 字串或 {"stdin":..., "after":...}。"""
    ns = {"__name__": "__gen__"}
    exec(compile(gen_code, "gen.py", "exec"), ns)
    case = ns["gen"](random.Random(seed))
    if isinstance(case, str):
        case = {"stdin": case}
    return {"stdin": case.get("stdin", ""), "after": case.get("after", "")}
