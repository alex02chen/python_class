from common import T, choice, exercise, lesson, md, qa

LESSON = lesson("control")

QUIZ = [
    choice("`print(0 or [] or 'x' or 5)` 輸出？", ["`True`", "`'x'`", "`x`", "`5`"], 2,
           "`or` 回傳第一個真值運算元：`0`、`[]` 為假，`'x'` 為真 → 回傳 `'x'`，print 印出 `x`。"),
    choice("下列程式輸出？\n```python\nfor i in range(3):\n    if i == 5:\n        break\nelse:\n    print('done')\n```",
           ["什麼都不印", "`done`", "`SyntaxError`", "印三次 `done`"], 1,
           "迴圈正常結束（沒有 break），所以執行 `else`。"),
    choice("`match ['go', 'north']:` 搭配 `case [x]:` 會？", ["匹配，x='go'", "匹配，x=['go','north']", "不匹配", "SyntaxError"], 2,
           "序列模式長度必須一致（除非使用 `*rest`），長度 2 不符合長度 1 的模式。"),
    choice("以下何者正確描述 `try/except/else/finally` 的 `else`？",
           ["發生例外時執行", "try 沒有例外時執行", "永遠執行", "except 執行後才執行"], 1,
           "`else` 只在 try 區塊沒有拋出例外時執行；把「成功後才做的事」放這裡，避免意外捕捉到它的例外。"),
    choice("`list(zip('abc', [1, 2]))` 的結果？", ["`ValueError`", "`[('a',1),('b',2)]`", "`[('a',1),('b',2),('c',None)]`", "`[]`"], 1,
           "`zip` 以最短的為準。要求等長請用 `strict=True`；要補值請用 `itertools.zip_longest`。"),
    choice("`1 < 3 > 2` 的值？", ["`True`", "`False`", "`TypeError`", "`2`"], 0, "等同 `1 < 3 and 3 > 2`。"),
    choice("下列函式回傳什麼？\n```python\ndef f():\n    try:\n        return 1\n    finally:\n        return 2\n```",
           ["`1`", "`2`", "`None`", "`SyntaxError`"], 1,
           "`finally` 中的 `return` 會覆蓋 try 中的回傳值（甚至會吞掉例外），3.14 起還會給出 SyntaxWarning。"),
    qa("為什麼不建議寫 `except:` 或 `except Exception: pass`？",
       "裸 `except:` 會捕捉 `BaseException`，連 `KeyboardInterrupt`（Ctrl+C）和 `SystemExit` 都吞掉，程式會無法中斷。"
       "`except Exception: pass` 則讓所有錯誤無聲消失，bug 會在很遠的地方才以奇怪的形式出現。"
       "應只捕捉預期且能處理的特定例外，並至少記錄 (log) 下來。"),
    qa("說明 `match` 的捕捉模式陷阱：`case RED:` 和 `case Color.RED:` 有何不同？",
       "`case RED:` 中的裸名稱是**捕捉模式**：永遠匹配，並把主體值綁定給 `RED`（還會蓋掉原本的常數）。"
       "`case Color.RED:` 是**值模式**（點分名稱），會用 `==` 比較。比對常數請使用點分名稱、字面值，或 guard (`case x if x == RED`)。"),
    qa("EAFP 與 LBYL 是什麼？各舉一例。",
       "- **LBYL**（Look Before You Leap）：先檢查再操作，如 `if key in d: v = d[key]`。\n"
       "- **EAFP**（Easier to Ask Forgiveness than Permission）：直接操作，失敗再處理，如 `try: v = d[key] except KeyError: ...`。\n\n"
       "Python 社群偏好 EAFP：程式碼主線較清楚，且避免「檢查後、使用前」狀態被改變的競態條件（例如檔案在檢查後被刪除）。"),
]

EXERCISES = [
    exercise(
        "c1-fizzbuzz", "可設定規則的 FizzBuzz", 1,
        r'''
        第一行有兩個整數 `n`、`k`（0 ≤ n ≤ 10⁵，0 ≤ k ≤ 10）。接下來 `k` 行，每行是一條規則：正整數 `d` 與一個單字 `w`。

        對 `i = 1..n` 各輸出一行：把 **i 能整除的所有規則的單字**，依「規則輸入順序」串接起來；若沒有任何規則符合，輸出 `i` 本身。

        ### 輸入範例
        ```text
        6 2
        2 Fizz
        3 Buzz
        ```
        ### 輸出範例
        ```text
        1
        Fizz
        Buzz
        Fizz
        5
        FizzBuzz
        ```
        ''',
        r'''
        n, k = map(int, input().split())
        ''',
        r'''
        import sys
        n, k = map(int, input().split())
        rules = []
        for _ in range(k):
            d, w = input().split()
            rules.append((int(d), w))
        out = []
        for i in range(1, n + 1):
            s = "".join(w for d, w in rules if i % d == 0)
            out.append(s or str(i))
        sys.stdout.write("\n".join(out) + ("\n" if out else ""))
        ''',
        [
            T("""
              6 2
              2 Fizz
              3 Buzz
              """, tag="sample", expect="1\nFizz\nBuzz\nFizz\n5\nFizzBuzz"),
            T("15 2\n3 Fizz\n5 Buzz\n", note="經典版"),
            T("0 1\n3 Fizz\n", tag="corner", note="n = 0：沒有任何輸出", expect=""),
            T("5 0\n", tag="corner", note="沒有規則：原樣輸出數字", expect="1\n2\n3\n4\n5"),
            T("4 1\n1 X\n", tag="corner", note="d = 1：每個數都符合", expect="X\nX\nX\nX"),
            T("6 2\n3 Buzz\n2 Fizz\n", tag="corner", note="規則順序決定串接順序：BuzzFizz"),
            T("4 2\n2 A\n2 B\n", tag="corner", note="重複的除數", expect="1\nAB\n3\nAB"),
            T("3 1\n100 Big\n", tag="corner", note="除數大於 n", expect="1\n2\n3"),
            T("30 3\n2 a\n3 b\n5 c\n", note="三條規則"),
            T("100000 2\n3 Fizz\n5 Buzz\n", tag="stress", note="n = 10^5（記得用 join 一次輸出）"),
        ],
        gen=r'''
        def gen(rng):
            k = rng.randint(0, 4)
            rules = [f"{rng.randint(1, 7)} {rng.choice(['Fizz','Buzz','Bang','X'])}" for _ in range(k)]
            return f"{rng.randint(0, 40)} {k}\n" + "".join(r + "\n" for r in rules)
        ''',
        hints=["先把規則存成 list of tuple，保留輸入順序。", "`''.join(...) or str(i)`：空字串為假。",
               "大量輸出時，先收集再 `print('\\n'.join(out))` 比逐行 print 快。"],
        wrong=[r'''
        n, k = map(int, input().split())
        rules = dict()
        for _ in range(k):
            d, w = input().split()
            rules[int(d)] = w
        for i in range(1, n + 1):
            s = "".join(w for d, w in sorted(rules.items()) if i % d == 0)
            print(s or i)
        '''],
    ),
    exercise(
        "c2-prime", "質數判斷（含負數與大數）", 2,
        r'''
        第一行為整數 `T`（1 ≤ T ≤ 50），接下來 `T` 行各有一個整數 `x`（−10¹² ≤ x ≤ 10¹²）。

        對每個 `x`，若為質數輸出 `prime`，否則輸出 `not prime`。（負數、0、1 都不是質數。）

        ### 輸入範例
        ```text
        4
        2
        1
        97
        91
        ```
        ### 輸出範例
        ```text
        prime
        not prime
        prime
        not prime
        ```

        > 時間限制：每組測資 10 秒（瀏覽器中的 Python 比本機慢數倍）。若對 10¹² 等級的數從 2 一路試除到 x，會逾時。
        ''',
        r'''
        def is_prime(x):
            ...

        t = int(input())
        for _ in range(t):
            x = int(input())
        ''',
        r'''
        def is_prime(x):
            if x < 2:
                return False
            if x < 4:
                return True
            if x % 2 == 0 or x % 3 == 0:
                return False
            d = 5
            while d * d <= x:
                if x % d == 0 or x % (d + 2) == 0:
                    return False
                d += 6
            return True

        t = int(input())
        for _ in range(t):
            print("prime" if is_prime(int(input())) else "not prime")
        ''',
        [
            T("4\n2\n1\n97\n91\n", tag="sample", expect="prime\nnot prime\nprime\nnot prime"),
            T("3\n0\n-7\n-1\n", tag="corner", note="0 與負數", expect="not prime\nnot prime\nnot prime"),
            T("3\n2\n3\n4\n", tag="corner", note="最小的幾個數", expect="prime\nprime\nnot prime"),
            T("4\n25\n49\n121\n169\n", tag="corner", note="質數的平方：迴圈條件要 <=", expect="not prime\nnot prime\nnot prime\nnot prime"),
            T("3\n561\n1105\n1729\n", tag="corner", note="Carmichael 數", expect="not prime\nnot prime\nnot prime"),
            T("2\n999999999989\n1000000000000\n", tag="corner", note="10^12 附近最大的質數", expect="prime\nnot prime"),
            T("1\n999998000001\n", tag="corner", note="999999^2，平方數", expect="not prime"),
            T("1\n999983000037\n", tag="corner", note="兩個大質數 999983 × 1000039 的乘積", expect="not prime"),
            T("5\n2147483647\n1000000007\n998244353\n4294967297\n10000000019\n", note="常見的大數"),
            T("10\n" + "999999999989\n" * 10, tag="stress", note="10 個大質數"),
        ],
        gen=r'''
        def gen(rng):
            nums = [rng.randint(-20, 10 ** rng.randint(1, 9)) for _ in range(rng.randint(1, 10))]
            return f"{len(nums)}\n" + "".join(f"{x}\n" for x in nums)
        ''',
        hints=["只需試除到 √x。", "排除 2、3 的倍數後，只需檢查 6k±1。", "用 `d * d <= x` 避免浮點誤差。"],
        wrong=[r'''
        t = int(input())
        for _ in range(t):
            x = int(input())
            ok = x > 1
            for d in range(2, int(x ** 0.5)):
                if x % d == 0:
                    ok = False
                    break
            print("prime" if ok else "not prime")
        '''],
    ),
    exercise(
        "c3-interpreter", "成績簿指令解譯器（match + 例外）", 3,
        r'''
        實作一個以 `match` 撰寫的指令解譯器。輸入有若干行指令（單字之間以一個或多個空白分隔），逐行處理：

        | 指令 | 行為 | 輸出 |
        |---|---|---|
        | `add 名字 分數` | 新增或覆蓋學生分數（分數須為 0~100 的整數） | 成功不輸出；分數不合法輸出 `INVALID` |
        | `del 名字` | 刪除學生 | 不存在輸出 `NOT FOUND` |
        | `query 名字` | 查詢 | 輸出 `名字 分數`；不存在輸出 `NOT FOUND` |
        | `avg` | 全班平均 | 輸出兩位小數；沒有學生輸出 `N/A` |
        | `top` | 最高分 | 輸出 `名字 分數`，同分取**名字字典序最小**；沒有學生輸出 `N/A` |
        | `end` | 結束 | 立刻停止，**忽略之後所有行** |
        | 空白行 | 忽略 | — |
        | 其他（未知指令或參數個數錯誤） | — | 輸出 `UNKNOWN` |

        輸入也可能在沒有 `end` 的情況下直接結束 (EOF)。

        ### 輸入範例
        ```text
        add amy 90
        add bob 85
        query amy
        avg
        add cat abc
        hello
        end
        avg
        ```
        ### 輸出範例
        ```text
        amy 90
        87.50
        INVALID
        UNKNOWN
        ```
        ''',
        r'''
        book = {}
        while True:
            try:
                line = input()
            except EOFError:
                break
            match line.split():
                case ["end"]:
                    break
                # 在這裡加上其他 case
        ''',
        r'''
        book = {}
        while True:
            try:
                line = input()
            except EOFError:
                break
            match line.split():
                case []:
                    continue
                case ["end"]:
                    break
                case ["add", name, score]:
                    try:
                        s = int(score)
                    except ValueError:
                        print("INVALID")
                        continue
                    if 0 <= s <= 100:
                        book[name] = s
                    else:
                        print("INVALID")
                case ["del", name]:
                    if book.pop(name, None) is None:
                        print("NOT FOUND")
                case ["query", name]:
                    print(f"{name} {book[name]}" if name in book else "NOT FOUND")
                case ["avg"]:
                    print(f"{sum(book.values()) / len(book):.2f}" if book else "N/A")
                case ["top"]:
                    if book:
                        name, s = min(book.items(), key=lambda kv: (-kv[1], kv[0]))
                        print(name, s)
                    else:
                        print("N/A")
                case _:
                    print("UNKNOWN")
        ''',
        [
            T("""
              add amy 90
              add bob 85
              query amy
              avg
              add cat abc
              hello
              end
              avg
              """, tag="sample", expect="amy 90\n87.50\nINVALID\nUNKNOWN"),
            T("", tag="corner", note="完全沒有輸入", expect=""),
            T("avg\ntop\nquery x\ndel x\n", tag="corner", note="空成績簿的各種查詢", expect="N/A\nN/A\nNOT FOUND\nNOT FOUND"),
            T("add a 100\nadd b 0\nadd c 101\nadd d -1\nadd e 3.5\navg\n", tag="corner", note="分數邊界 0、100、101、-1、小數",
              expect="INVALID\nINVALID\nINVALID\n50.00"),
            T("add a 50\nadd a 70\nquery a\ndel a\ndel a\nquery a\n", tag="corner", note="覆蓋、重複刪除",
              expect="a 70\nNOT FOUND\nNOT FOUND"),
            T("add zed 90\nadd amy 90\nadd bob 80\ntop\n", tag="corner", note="同分取字典序最小", expect="amy 90"),
            T("   add   x   10   \n\n\nquery    x\n", tag="corner", note="多重空白與空白行", expect="x 10"),
            T("add a\nadd a 1 2\nquery\navg now\nADD a 1\nend extra\n", tag="corner", note="參數個數錯誤、大小寫敏感",
              expect="UNKNOWN\nUNKNOWN\nUNKNOWN\nUNKNOWN\nUNKNOWN\nUNKNOWN"),
            T("add a 1\nadd b 2\nadd c 2\navg\n", tag="corner", note="平均 1.666… 四捨五入", expect="1.67"),
            T("add a 10\nend\nquery a\n", tag="corner", note="end 之後全部忽略", expect=""),
            T("add a +5\nadd b ０7\nquery a\nquery b\n", tag="corner", note="int() 接受正號與全形數字", expect="a 5\nb 7"),
        ],
        gen=r'''
        def gen(rng):
            names = ["amy", "bob", "cy"]
            lines = []
            for _ in range(rng.randint(0, 12)):
                c = rng.choice(["add", "add", "del", "query", "avg", "top", "bad", ""])
                if c == "add":
                    lines.append(f"add {rng.choice(names)} {rng.choice([rng.randint(-5, 105), 'x'])}")
                elif c in ("del", "query"):
                    lines.append(f"{c} {rng.choice(names)}")
                else:
                    lines.append(c)
            if rng.random() < 0.3:
                lines.insert(rng.randint(0, len(lines)), "end")
            return "".join(l + "\n" for l in lines)
        ''',
        hints=["`match line.split():` 搭配 `case ['add', name, score]:`。", "`case []:` 可以處理空白行。",
               "`min(items, key=lambda kv: (-kv[1], kv[0]))` 一次處理「分數高、名字小」。"],
        wrong=[r'''
        book = {}
        while True:
            try:
                line = input()
            except EOFError:
                break
            match line.split():
                case []:
                    continue
                case ["end"]:
                    break
                case ["add", name, score]:
                    book[name] = int(score) if score.isdigit() and int(score) <= 100 else print("INVALID")
                case ["del", name]:
                    if book.pop(name, None) is None:
                        print("NOT FOUND")
                case ["query", name]:
                    print(f"{name} {book[name]}" if name in book else "NOT FOUND")
                case ["avg"]:
                    print(f"{sum(book.values()) / len(book):.2f}" if book else "N/A")
                case ["top"]:
                    print(*max(book.items(), key=lambda kv: kv[1])) if book else print("N/A")
                case _:
                    print("UNKNOWN")
        '''],
    ),
    exercise(
        "c4-collatz", "Collatz 步數與最高點", 2,
        r'''
        Collatz 規則：若 `n` 為偶數則 `n ← n / 2`，否則 `n ← 3n + 1`，直到 `n = 1`。

        第一行為 `T`，接下來 `T` 行各有一個整數 `n`（可能 ≤ 0，絕對值 ≤ 10¹⁸）。

        對每個 `n`：
        - 若 `n ≤ 0`，輸出 `invalid`
        - 否則輸出兩個數：到達 1 所需的步數、過程中出現過的最大值（包含 `n` 本身）

        ### 輸入範例
        ```text
        3
        6
        1
        0
        ```
        ### 輸出範例
        ```text
        8 16
        0 1
        invalid
        ```
        （6 → 3 → 10 → 5 → 16 → 8 → 4 → 2 → 1，共 8 步，最高 16）
        ''',
        r'''
        t = int(input())
        ''',
        r'''
        t = int(input())
        for _ in range(t):
            n = int(input())
            if n <= 0:
                print("invalid")
                continue
            steps, peak = 0, n
            while n != 1:
                n = n // 2 if n % 2 == 0 else 3 * n + 1
                peak = max(peak, n)
                steps += 1
            print(steps, peak)
        ''',
        [
            T("3\n6\n1\n0\n", tag="sample", expect="8 16\n0 1\ninvalid"),
            T("1\n1\n", tag="corner", note="已經是 1：0 步", expect="0 1"),
            T("2\n-5\n-1000000000000000000\n", tag="corner", note="負數", expect="invalid\ninvalid"),
            T("1\n2\n", tag="corner", expect="1 2"),
            T("1\n27\n", note="27 需要 111 步，最高到 9232", expect="111 9232"),
            T("1\n1024\n", tag="corner", note="2 的次方：一路除 2", expect="10 1024"),
            T("1\n837799\n", note="一百萬以內步數最多的起點", expect="524 2974984576"),
            T("1\n1000000000000000000\n", tag="corner", note="10^18（用 / 會變 float 而失準！）"),
            T("1\n1152921504606846978\n", tag="corner", note="2^60+2：n / 2 的 float 結果會失準"),
            T("1\n989345275647\n", tag="stress", note="步數很長的大數"),
        ],
        gen=r'''
        def gen(rng):
            nums = [rng.randint(-3, 10 ** rng.randint(1, 15)) for _ in range(rng.randint(1, 6))]
            return f"{len(nums)}\n" + "".join(f"{x}\n" for x in nums)
        ''',
        hints=["用 `//` 而不是 `/`：`/` 會產生 float，超過 2^53 就失去精度。", "`continue` 可以提早處理 invalid。"],
        wrong=[r'''
        t = int(input())
        for _ in range(t):
            n = int(input())
            if n <= 0:
                print("invalid")
                continue
            steps, peak = 0, n
            while n != 1:
                n = int(n / 2) if n % 2 == 0 else 3 * n + 1
                peak = max(peak, n)
                steps += 1
            print(steps, peak)
        '''],
    ),
    exercise(
        "c5-spiral", "螺旋矩陣", 3,
        r'''
        讀入 `n m`（1 ≤ n, m ≤ 60），輸出 `n` 列 `m` 行的螺旋矩陣：從左上角開始，順時針向內填入 `1, 2, …, n·m`。

        每個數字**靠右對齊**，寬度為 `n·m` 的位數，數字之間以一個空白分隔（行尾不要有多餘空白——判題會忽略行尾空白，但好習慣很重要）。

        ### 輸入範例
        ```text
        3 4
        ```
        ### 輸出範例
        ```text
         1  2  3  4
        10 11 12  5
         9  8  7  6
        ```
        ''',
        r'''
        n, m = map(int, input().split())
        ''',
        r'''
        n, m = map(int, input().split())
        grid = [[0] * m for _ in range(n)]
        dr, dc = [0, 1, 0, -1], [1, 0, -1, 0]
        r = c = d = 0
        for k in range(1, n * m + 1):
            grid[r][c] = k
            nr, nc = r + dr[d], c + dc[d]
            if not (0 <= nr < n and 0 <= nc < m and grid[nr][nc] == 0):
                d = (d + 1) % 4
                nr, nc = r + dr[d], c + dc[d]
            r, c = nr, nc
        w = len(str(n * m))
        for row in grid:
            print(" ".join(f"{v:>{w}}" for v in row))
        ''',
        [
            T("3 4\n", tag="sample", expect=" 1  2  3  4\n10 11 12  5\n 9  8  7  6"),
            T("1 1\n", tag="corner", note="最小", expect="1"),
            T("1 5\n", tag="corner", note="單列", expect="1 2 3 4 5"),
            T("5 1\n", tag="corner", note="單行", expect="1\n2\n3\n4\n5"),
            T("2 2\n", tag="corner", expect="1 2\n4 3"),
            T("3 3\n", tag="corner", note="奇數方陣，最後落在正中央", expect="1 2 3\n8 9 4\n7 6 5"),
            T("4 4\n", note="偶數方陣"),
            T("3 1\n", tag="corner", note="寬度 1"),
            T("2 5\n", tag="corner", note="寬度變 2 位數的邊界：10"),
            T("4 3\n", note="直的長方形"),
            T("60 60\n", tag="stress", note="最大，寬度 4"),
        ],
        gen=r'''
        def gen(rng):
            return f"{rng.randint(1, 12)} {rng.randint(1, 12)}\n"
        ''',
        hints=["用方向陣列 (右、下、左、上)，撞牆或撞到已填格子就轉向。",
               "`f'{v:>{w}}'`：格式規格裡也能放變數。", "一個 `[[0]*m]*n` 會讓每列共用同一個 list！"],
        wrong=[r'''
        n, m = map(int, input().split())
        grid = [[0] * m] * n
        dr, dc = [0, 1, 0, -1], [1, 0, -1, 0]
        r = c = d = 0
        for k in range(1, n * m + 1):
            grid[r][c] = k
            nr, nc = r + dr[d], c + dc[d]
            if not (0 <= nr < n and 0 <= nc < m and grid[nr][nc] == 0):
                d = (d + 1) % 4
                nr, nc = r + dr[d], c + dc[d]
            r, c = nr, nc
        w = len(str(n * m))
        for row in grid:
            print(" ".join(f"{v:>{w}}" for v in row))
        '''],
    ),
]

UNIT = {
    "id": "control", "num": 2, "title": "流程控制", "icon": "🔀",
    "summary": "真值、短路求值、match 模式比對、迭代協定、for-else、例外處理",
    "lesson": LESSON, "quiz": QUIZ, "exercises": EXERCISES,
}
