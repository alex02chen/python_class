from common import T, choice, exercise, lesson, md, qa

LESSON = lesson("basics")

QUIZ = [
    choice("執行 `a = [1]; b = a; b += [2]` 後，`a` 的值是？",
           ["`[1]`", "`[1, 2]`", "`TypeError`", "`[[1], 2]`"], 1,
           "`list` 的 `+=` 呼叫 `__iadd__`，**就地修改**同一個物件，所以 a 也看到變化。"
           "（對比：`b = b + [2]` 會建立新 list，a 不受影響。）"),
    choice("`-7 // 2` 和 `-7 % 2` 分別是？",
           ["`-3` 和 `-1`", "`-4` 和 `1`", "`-3` 和 `1`", "`-4` 和 `-1`"], 1,
           "`//` 是向下取整 (floor)，`%` 的符號跟隨除數，並滿足 `a == (a//b)*b + a%b`。"),
    choice("`round(2.5)` 的結果是？", ["`3`", "`2`", "`2.0`", "`3.0`"], 1,
           "Python 3 的 `round` 採用 round-half-to-even（銀行家捨入），2.5 捨入到最近的偶數 2。"),
    choice("下列哪個**不能**當 `dict` 的 key？",
           ["`(1, 2)`", "`'abc'`", "`[1, 2]`", "`frozenset({1})`"], 2,
           "key 必須可雜湊 (hashable)，list 可變所以不可雜湊。"),
    choice("`'a,,b'.split(',')` 的結果是？",
           ["`['a', 'b']`", "`['a', '', 'b']`", "`['a', ',', 'b']`", "`['a,,b']`"], 1,
           "指定分隔符時，相鄰分隔符之間會產生空字串；不指定分隔符的 `split()` 才會丟掉空字串。"),
    choice("`'Python'[10:]` 的結果是？",
           ["`IndexError`", "`''`", "`'n'`", "`None`"], 1,
           "切片超出範圍會自動截斷，回傳空字串；只有單一索引 `s[10]` 才會 `IndexError`。"),
    choice("`f'{1234.5:>10,.1f}'` 的輸出（以 `|` 表示邊界）是？",
           ["`|   1,234.5|`", "`|1,234.5   |`", "`|1234.5    |`", "`|  1,234.50|`"], 0,
           "`>` 靠右、寬度 10、`,` 千分位、`.1f` 一位小數。"),
    qa("為什麼 `0.1 + 0.2 != 0.3`？實務上應如何比較或計算？",
       "`float` 以二進位儲存，0.1 是無限循環的二進位小數，只能存近似值，誤差累積後兩邊不相等。\n\n"
       "- 比較：`math.isclose(a, b)` 或 `abs(a - b) < eps`\n"
       "- 需要精確十進位（金額）：`Decimal('0.1')`（務必從**字串**建立）\n"
       "- 需要精確分數：`fractions.Fraction(1, 10)`"),
    qa("`is` 和 `==` 差在哪？什麼時候該用 `is`？",
       "`==` 比較值（呼叫 `__eq__`），`is` 比較是否為同一個物件（`id` 相同）。\n\n"
       "應該用 `is` 的情境：與單例比較，如 `x is None`、哨兵物件 (sentinel)。"
       "不要用 `is` 比較數字或字串——小整數快取與字串駐留 (interning) 是 CPython 的實作細節，結果不可靠。"),
    qa("Python 是「強型別」還是「弱型別」？「動態型別」又是什麼意思？",
       "Python 是**強型別**（不做隱式轉型，`'5' + 3` 會 `TypeError`）且**動態型別**"
       "（型別屬於物件而非變數，名稱可在執行期重新綁定到不同型別的物件）。這兩個維度是獨立的。"),
]

EXERCISES = [
    exercise(
        "b1-temperature", "溫度轉換（含 -0.0 陷阱）", 1,
        r'''
        讀入一行溫度，格式為「數值 + 單位」，單位為 `C` 或 `F`（**大小寫皆可**），數值與單位間、前後**可能有空白**。

        - 若為攝氏，轉成華氏輸出：`F = C × 9 / 5 + 32`
        - 若為華氏，轉成攝氏輸出：`C = (F − 32) × 5 / 9`

        輸出轉換後的數值（**四捨五入到小數點後一位**，用 `f"{x:.1f}"` 即可）緊接目標單位（大寫）。

        **注意**：若格式化後是 `-0.0`，必須輸出 `0.0`。

        ### 輸入範例
        ```text
        100C
        ```
        ### 輸出範例
        ```text
        212.0F
        ```
        ''',
        r'''
        s = input()
        # 在這裡寫你的程式
        ''',
        r'''
        s = input().strip()
        value, unit = float(s[:-1]), s[-1].upper()
        if unit == "C":
            result, target = value * 9 / 5 + 32, "F"
        else:
            result, target = (value - 32) * 5 / 9, "C"
        text = f"{result:.1f}"
        if text == "-0.0":
            text = "0.0"
        print(text + target)
        ''',
        [
            T("100C\n", tag="sample", note="沸點", expect="212.0F"),
            T("32F\n", tag="sample", note="冰點", expect="0.0C"),
            T("37.5c\n", note="小寫單位"),
            T("98.6F\n", note="體溫"),
            T("-40C\n", tag="corner", note="-40 度攝氏 = 華氏", expect="-40.0F"),
            T("-40f\n", tag="corner", note="反向也是 -40"),
            T("  25 C  \n", tag="corner", note="數值、單位前後都有空白"),
            T("31.95F\n", tag="corner", note="結果約 -0.03，格式化會變成 -0.0", expect="0.0C"),
            T("-0C\n", tag="corner", note="負零"),
            T("0F\n", tag="corner", note="華氏 0 度"),
            T("1e3C\n", tag="corner", note="科學記號也是合法 float"),
            T("-459.67F\n", tag="corner", note="絕對零度"),
        ],
        gen=r'''
        def gen(rng):
            v = round(rng.uniform(-500, 500), rng.randint(0, 3))
            unit = rng.choice("CcFf")
            pad = lambda: " " * rng.randint(0, 2)
            return f"{pad()}{v}{pad()}{unit}{pad()}\n"
        ''',
        hints=["`s.strip()` 去頭尾空白後，最後一個字元就是單位。", "`float(' 25 ')` 允許前後空白。",
               "`f'{-0.04:.1f}'` 會得到 `'-0.0'`。"],
        wrong=[r'''
        s = input().strip()
        v, u = float(s[:-1]), s[-1]
        print(f"{v*9/5+32:.1f}F" if u == "C" else f"{(v-32)*5/9:.1f}C")
        '''],
    ),
    exercise(
        "b2-palindrome", "Unicode 回文判斷", 1,
        r'''
        讀入一行字串（**可能是空字串**）。忽略所有「非字母數字」的字元（以 `str.isalnum()` 判斷，所以中文字也算），
        並忽略英文大小寫，判斷它是否為回文。是則輸出 `Yes`，否則輸出 `No`。

        > 過濾後若為空字串，視為回文。

        ### 輸入範例
        ```text
        A man, a plan, a canal: Panama
        ```
        ### 輸出範例
        ```text
        Yes
        ```
        ''',
        r'''
        s = input()
        ''',
        r'''
        s = input()
        t = [ch.lower() for ch in s if ch.isalnum()]
        print("Yes" if t == t[::-1] else "No")
        ''',
        [
            T("A man, a plan, a canal: Panama\n", tag="sample", expect="Yes"),
            T("race a car\n", tag="sample", expect="No"),
            T("\n", tag="corner", note="空字串", expect="Yes"),
            T("!!! ,,, ???\n", tag="corner", note="只有標點，過濾後為空", expect="Yes"),
            T("a\n", tag="corner", note="單一字元"),
            T("ab\n", tag="corner", note="兩個不同字元"),
            T("上海自來水來自海上\n", tag="corner", note="中文回文"),
            T("No 'x' in Nixon\n", note="大小寫混合"),
            T("0P\n", tag="corner", note="數字與字母：p 和 0 不同", expect="No"),
            T("12321\n", note="純數字"),
            T("Was it a car or a cat I saw?\n", note="經典句子"),
            T(("ab" * 50000) + "a\n", tag="stress", note="十萬字元"),
        ],
        gen=r'''
        def gen(rng):
            half = "".join(rng.choice("aAbB1 ,.") for _ in range(rng.randint(0, 8)))
            s = half + rng.choice(["", "x", "!"]) + half[::-1]
            if rng.random() < 0.4:
                s += rng.choice("abc")
            return s + "\n"
        ''',
        hints=["先用 list comprehension 過濾並轉小寫。", "`seq == seq[::-1]` 就是回文檢查。"],
        wrong=[r'''
        s = input().lower().replace(" ", "")
        print("Yes" if s == s[::-1] else "No")
        '''],
    ),
    exercise(
        "b3-bigdigits", "超大整數的位數與位數和", 2,
        r'''
        讀入一個整數（前後可能有空白，可能帶 `+` 或 `-` 號，可能有前導 0，**最長可達 10 萬位**）。

        輸出兩個數，以空白分隔：
        1. 這個整數的「值」以十進位表示時有幾位數（不含正負號，`0` 算 1 位；前導 0 不算）
        2. 各位數字的和

        ### 輸入範例
        ```text
        -00123
        ```
        ### 輸出範例
        ```text
        3 6
        ```

        > 💡 想想看：為什麼直接 `int(input())` 會在某些測資失敗？
        ''',
        r'''
        s = input()
        ''',
        r'''
        s = input().strip().lstrip("+-").lstrip("0") or "0"
        print(len(s), sum(int(ch) for ch in s))
        ''',
        [
            T("-00123\n", tag="sample", expect="3 6"),
            T("98765\n", tag="sample", expect="5 35"),
            T("0\n", tag="corner", note="零是 1 位數", expect="1 0"),
            T("-0\n", tag="corner", note="負零", expect="1 0"),
            T("0000\n", tag="corner", note="全部是前導 0", expect="1 0"),
            T("+7\n", tag="corner", note="帶正號"),
            T("   42   \n", tag="corner", note="前後空白"),
            T("1" + "0" * 100 + "\n", note="10 的 100 次方"),
            T("9" * 4300 + "\n", tag="corner", note="剛好 4300 位，int() 還可以"),
            T("9" * 4301 + "\n", tag="corner", note="4301 位：int() 會 ValueError！"),
            T("-" + "123456789" * 11112 + "\n", tag="stress", note="約 10 萬位的負數"),
        ],
        gen=r'''
        def gen(rng):
            sign = rng.choice(["", "", "-", "+"])
            zeros = "0" * rng.randint(0, 3)
            body = "".join(rng.choice("0123456789") for _ in range(rng.randint(0, 30)))
            return f"{sign}{zeros}{body or '0'}\n"
        ''',
        hints=["Python 3.11+ 的 `int(str)` 有 4300 位上限。", "直接處理字串：去掉符號與前導 0。",
               "前導 0 全去掉後可能變空字串，記得補回 `'0'`。"],
        wrong=[r'''
        n = abs(int(input()))
        print(len(str(n)), sum(map(int, str(n))))
        '''],
    ),
    exercise(
        "b4-rounding", "正確的四捨五入", 2,
        r'''
        第一行為整數 `T`（0 ≤ T ≤ 1000），接下來 `T` 行，每行有一個十進位小數 `x`（一般小數表示法，可能為負）與整數 `n`（0 ≤ n ≤ 10）。

        請把 `x` **四捨五入**（遇到 5 一律遠離 0，即 `ROUND_HALF_UP`）到小數點後 `n` 位，並剛好輸出 `n` 位小數（`n = 0` 時不輸出小數點）。
        結果為零時一律輸出不帶負號的形式（例如 `0`、`0.00`）。

        ### 輸入範例
        ```text
        3
        2.675 2
        2.5 0
        -1.005 2
        ```
        ### 輸出範例
        ```text
        2.68
        3
        -1.01
        ```

        > `round()` 與 `float` 在這題會給錯答案，想想為什麼。
        ''',
        r'''
        t = int(input())
        for _ in range(t):
            x, n = input().split()
        ''',
        r'''
        from decimal import Decimal, ROUND_HALF_UP

        t = int(input())
        for _ in range(t):
            x, n = input().split()
            q = Decimal(x).quantize(Decimal(1).scaleb(-int(n)), rounding=ROUND_HALF_UP)
            if q == 0:
                q = abs(q)
            print(f"{q:f}")
        ''',
        [
            T("""
              3
              2.675 2
              2.5 0
              -1.005 2
              """, tag="sample", expect="2.68\n3\n-1.01"),
            T("0\n", tag="corner", note="T = 0，什麼都不印", expect=""),
            T("""
              4
              0.5 0
              1.5 0
              2.5 0
              3.5 0
              """, tag="corner", note="銀行家捨入會給 0 2 2 4", expect="1\n2\n3\n4"),
            T("""
              3
              -0.4 0
              -0.001 2
              0.0 3
              """, tag="corner", note="結果為 -0 要輸出 0", expect="0\n0.00\n0.000"),
            T("""
              2
              7 3
              -12 1
              """, tag="corner", note="整數輸入要補小數位", expect="7.000\n-12.0"),
            T("""
              2
              1.0000000005 9
              0.9999999999 10
              """, tag="corner", note="精度高到 float 失真"),
            T("""
              2
              123456789012345678.5 0
              99.995 2
              """, tag="corner", note="超出 float 精確範圍、進位到百位", expect="123456789012345679\n100.00"),
            T("""
              3
              1.45 1
              -2.5 0
              0.045 2
              """, note="一般"),
        ],
        gen=r'''
        def gen(rng):
            lines = []
            for _ in range(rng.randint(1, 8)):
                ip = rng.randint(-1000, 1000)
                frac = "".join(rng.choice("0123456789") for _ in range(rng.randint(0, 6)))
                x = f"{ip}.{frac}" if frac else str(ip)
                lines.append(f"{x} {rng.randint(0, 5)}")
            return f"{len(lines)}\n" + "\n".join(lines) + "\n"
        ''',
        hints=["`decimal.Decimal` 從字串建立才精確。", "`Decimal('2.675').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)`",
               "`Decimal(1).scaleb(-n)` 會得到 `1E-n`。"],
        wrong=[r'''
        t = int(input())
        for _ in range(t):
            x, n = input().split()
            n = int(n)
            print(f"{round(float(x), n):.{n}f}")
        '''],
    ),
    exercise(
        "b5-duration", "秒數轉時分秒（負數取整陷阱）", 2,
        r'''
        讀入一個整數 `s`（−10¹⁸ ≤ s ≤ 10¹⁸），代表秒數。輸出 `H:MM:SS` 格式：

        - 小時 `H` 不補零、不設上限（可以超過 24）
        - 分、秒固定兩位數
        - 若 `s` 為負，在最前面加 `-`，其餘部分與 `|s|` 相同

        ### 輸入範例
        ```text
        3725
        ```
        ### 輸出範例
        ```text
        1:02:05
        ```
        ''',
        r'''
        s = int(input())
        ''',
        r'''
        s = int(input())
        sign = "-" if s < 0 else ""
        m, sec = divmod(abs(s), 60)
        h, m = divmod(m, 60)
        print(f"{sign}{h}:{m:02d}:{sec:02d}")
        ''',
        [
            T("3725\n", tag="sample", expect="1:02:05"),
            T("0\n", tag="corner", note="零秒", expect="0:00:00"),
            T("59\n", tag="corner", note="分鐘進位前一刻", expect="0:00:59"),
            T("60\n", tag="corner", note="剛好一分鐘", expect="0:01:00"),
            T("3599\n", tag="corner", expect="0:59:59"),
            T("3600\n", tag="corner", expect="1:00:00"),
            T("86400\n", note="一天：小時不換成天", expect="24:00:00"),
            T("-1\n", tag="corner", note="負數：divmod(-1, 60) == (-1, 59)！", expect="-0:00:01"),
            T("-3725\n", tag="corner", expect="-1:02:05"),
            T("1000000000000000000\n", tag="corner", note="10^18 秒"),
            T("-1000000000000000000\n", tag="corner", note="-10^18 秒"),
        ],
        gen=r'''
        def gen(rng):
            return f"{rng.choice([1, -1]) * rng.randint(0, 10 ** rng.randint(1, 18))}\n"
        ''',
        hints=["`divmod(a, b)` 一次拿到商和餘數。", "負數先取絕對值再算，最後補負號。"],
        wrong=[r'''
        s = int(input())
        h, r = divmod(s, 3600)
        m, sec = divmod(r, 60)
        print(f"{h}:{m:02d}:{sec:02d}")
        '''],
    ),
]

UNIT = {
    "id": "basics", "num": 1, "title": "基礎語法", "icon": "🔤",
    "summary": "物件模型、可變性、數值與浮點陷阱、字串切片與格式化",
    "lesson": LESSON, "quiz": QUIZ, "exercises": EXERCISES,
}
