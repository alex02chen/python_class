"""教材撰寫輔助函式。每個單元檔 (u*.py) 定義一個 UNIT dict。"""

from textwrap import dedent


def md(text):
    return dedent(text).strip("\n") + "\n"


def code(text):
    return dedent(text).strip("\n") + "\n"


def T(stdin="", after="", tag="normal", note="", expect=None):
    """一組測資。

    stdin : 標準輸入
    after : 使用者程式執行完後，在同一命名空間執行的測試碼（用來測函式/類別）
    tag   : sample（範例，題目中公開）、normal（一般）、corner（邊界情況）、stress（大量資料）
    note  : 這組測資在測什麼
    expect: （選填）手寫期望輸出，建置時會與參考解交叉驗證
    """
    # 以換行開頭的三引號字串才做 dedent；單行字串原樣保留（空白本身可能就是要測的 corner case）
    if stdin.startswith("\n") and stdin.strip():
        stdin = dedent(stdin).lstrip("\n")
    t = {"stdin": stdin, "after": code(after) if after else "",
         "tag": tag, "note": note}
    if expect is not None:
        t["expect"] = dedent(expect).strip("\n")
    return t


def choice(q, options, answer, explain):
    return {"type": "choice", "q": md(q), "options": options, "answer": answer, "explain": md(explain)}


def qa(q, answer):
    return {"type": "qa", "q": md(q), "answer": md(answer)}


def exercise(id, title, difficulty, statement, starter, solution, tests, gen=None, hints=(), wrong=(), mode="stdio"):
    return {
        "id": id, "title": title, "difficulty": difficulty, "mode": mode,
        "statement": md(statement), "starter": code(starter), "solution": code(solution),
        "tests": tests, "gen": code(gen) if gen else None, "hints": list(hints),
        "wrong": [code(w) for w in wrong],
    }
