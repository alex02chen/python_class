"""把 course/*.py 的教材、問答與練習題打包成 data/course.js。

對每一題：
  1. 用參考解答執行所有測資，產生期望輸出 (expected)。
  2. 若參考解在任何測資上丟出未捕捉的例外 → 建置失敗（避免錯誤測資上線）。
  3. 執行隨機測資產生器 N 次，確認參考解能處理所有隨機資料。
  4. 若題目提供 wrong 解（常見錯誤寫法），確認它至少在一組測資上失敗——證明測資真的抓得到該錯誤。

用法：python tools/build.py [--random 30]
"""

import argparse
import importlib.util
import json
import multiprocessing as mp
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "py"))
sys.path.insert(0, str(ROOT / "course"))
import harness  # noqa: E402

TIMEOUT = 10  # 秒，單組測資在本機的上限


def _worker(conn, fn, args):
    try:
        conn.send(getattr(harness, fn)(*args))
    except BaseException as e:  # noqa: BLE001
        conn.send({"error": repr(e)})


def call(fn, *args):
    """在子行程執行 harness 函式，避免無窮迴圈或狀態污染建置程式。"""
    parent, child = mp.Pipe()
    p = mp.Process(target=_worker, args=(child, fn, args))
    p.start()
    if parent.poll(TIMEOUT):
        res = parent.recv()
        p.join()
        return res
    p.kill()
    return {"error": f"timeout > {TIMEOUT}s"}


def load_units():
    units = []
    for path in sorted((ROOT / "course").glob("u*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        units.append(mod.UNIT)
    return units


def build_exercise(ex, n_random, errors):
    tag = f"[{ex['id']}]"
    for i, t in enumerate(ex["tests"], 1):
        res = call("run", ex["solution"], t["stdin"], t["after"])
        if "error" in res or not res["ok"]:
            errors.append(f"{tag} 測資 #{i} 參考解失敗：{res.get('error') or res['stderr']}")
            continue
        t["expected"] = harness.normalize(res["stdout"])
        if "expect" in t:  # 題目作者手寫的期望輸出，用來交叉驗證參考解
            if not harness.same_output(t.pop("expect"), t["expected"]):
                errors.append(f"{tag} 測資 #{i} 參考解輸出與手寫期望不符：\n{t['expected']}")

    if ex.get("gen"):
        for seed in range(n_random):
            case = call("gen_case", ex["gen"], seed)
            if "error" in case:
                errors.append(f"{tag} 產生器 seed={seed} 失敗：{case['error']}")
                break
            res = call("run", ex["solution"], case["stdin"], case["after"])
            if "error" in res or not res["ok"]:
                errors.append(f"{tag} 隨機 seed={seed} 參考解失敗：{res.get('error') or res['stderr']}")
                break

    for wrong in ex.pop("wrong", []):
        caught = False
        for t in ex["tests"]:
            res = call("run", wrong, t["stdin"], t["after"])
            if "error" in res or not res["ok"] or not harness.same_output(res["stdout"], t.get("expected", "")):
                caught = True
                break
        if not caught:
            errors.append(f"{tag} 測資沒有抓到錯誤解：\n{wrong}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--random", type=int, default=30, help="每題用參考解驗證的隨機測資數")
    args = ap.parse_args()

    units = load_units()
    errors = []
    n_ex = n_tests = 0
    for u in units:
        for ex in u["exercises"]:
            build_exercise(ex, args.random, errors)
            n_ex += 1
            n_tests += len(ex["tests"])
            print(f"  ✓ {ex['id']:<20} {len(ex['tests']):>3} 組測資")
    if errors:
        print("\n建置失敗：", file=sys.stderr)
        for e in errors:
            print(" -", e, file=sys.stderr)
        sys.exit(1)

    out = ROOT / "data" / "course.js"
    payload = json.dumps({"units": units}, ensure_ascii=False, indent=1)
    out.write_text("// 由 tools/build.py 自動產生，請勿手動修改。\nwindow.COURSE = " + payload + ";\n", encoding="utf-8")
    print(f"\n完成：{len(units)} 個單元、{n_ex} 題、{n_tests} 組測資 → {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
