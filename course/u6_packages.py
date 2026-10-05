from common import T, choice, exercise, lesson, md, qa

LESSON = lesson("packages")

QUIZ = [
    choice("同一個程式中 `import mymod` 執行兩次，`mymod` 的頂層程式碼會執行幾次？", ["0 次", "1 次", "2 次", "看 Python 版本"], 1,
           "第一次 import 後模組物件會存在 `sys.modules`，之後直接取用快取。要重新載入需 `importlib.reload`。"),
    choice("`list(itertools.groupby('aabaa'))` 會分成幾組？", ["2 組", "3 組", "5 組", "1 組"], 1,
           "`groupby` 只合併**相鄰**的相同元素：aa / b / aa。要依值分組請先排序或用 dict。"),
    choice("`np.nan == np.nan` 的結果？", ["`True`", "`False`", "`nan`", "`TypeError`"], 1,
           "IEEE-754 規定 NaN 不等於任何值（包括自己）。判斷缺失用 `pd.isna()` / `np.isnan()`。"),
    choice("Pandas 中 `df.loc` 和 `df.iloc` 的差別？", ["沒有差別", "loc 依標籤/布林，iloc 依整數位置", "loc 只能選列", "iloc 可以用欄名"], 1,
           "`loc` 使用索引標籤（切片含尾），`iloc` 使用 0-based 位置（切片不含尾）。"),
    choice("`df.groupby('dept')['salary'].transform('mean')` 回傳的長度？", ["部門數", "與 df 相同", "1", "欄位數"], 1,
           "`transform` 把每組的結果「廣播」回原本每一列，常用來新增「組內統計」欄位；`agg` 才是每組一列。"),
    choice("`pd.merge(customers, orders, how='left')` 中沒有訂單的顧客會？", ["被刪除", "保留，訂單欄位為 NaN", "引發錯誤", "訂單欄位為 0"], 1,
           "left join 保留左表所有列，右表沒有對應時填入 NaN。"),
    choice("`re.findall(r'<.+>', '<a><b>')` 的結果？", ["`['<a>', '<b>']`", "`['<a><b>']`", "`[]`", "`['a', 'b']`"], 1,
           "`+` 預設貪婪，盡可能匹配最長；加 `?` 變成非貪婪 `<.+?>` 才會得到 `['<a>', '<b>']`。"),
    qa("什麼是「向量化」？為什麼 Pandas/NumPy 的向量化運算比 Python for 迴圈快？",
       "向量化是指對整個陣列/欄位一次下達運算（如 `df['a'] * df['b']`），而不是逐元素寫迴圈。\n\n"
       "快的原因：(1) 迴圈在編譯過的 C 程式中執行，沒有 Python 直譯器逐行解譯、動態型別檢查的開銷；"
       "(2) 資料是同質且連續存放的記憶體，對 CPU 快取友善並能使用 SIMD 指令；(3) 不需要為每個元素建立 Python 物件。"),
    qa("為什麼要使用虛擬環境 (venv)？",
       "不同專案可能需要同一套件的不同版本（例如 A 專案用 pandas 1.x、B 專案用 2.x）。"
       "虛擬環境讓每個專案有獨立的 site-packages，彼此不干擾，也不會污染系統 Python；"
       "搭配 `requirements.txt` / `pyproject.toml` 鎖定版本，能在其他機器重現相同環境。"),
    qa("輸出報表時，為什麼不建議直接 `print(df)`？",
       "DataFrame 的預設顯示會受 Pandas 版本、顯示選項（`display.max_columns`、寬度）、dtype 影響，"
       "可能被截斷（`...`）、科學記號、對齊方式改變。需要穩定輸出時應自己決定格式，"
       "例如逐列 `f\"{row.name} {row.value:.2f}\"`，或 `to_csv` / `to_string(index=False)` 並指定 `float_format`。"),
]

EXERCISES = [
    exercise(
        "p1-groupby", "Pandas：部門薪資統計", 2, r'''
        從標準輸入讀入一份 CSV（第一行為標題 `name,dept,salary`）。`salary` **可能空白**（缺失）。欄位可能以雙引號包住（例如部門名稱含逗號）。

        對每個部門計算：**有薪資資料的人數**、平均薪資、最高薪資（缺失的列不納入任何統計；若某部門全部缺失，該部門不輸出）。

        每個部門輸出一行 `部門,人數,平均(兩位小數),最高(整數)`，排序：**平均薪資遞減**，相同時依**部門名稱**遞增。

        > 提示：`pd.read_csv(io.StringIO(sys.stdin.read()))`。輸出請自己格式化，不要直接 print DataFrame。
        > 若部門名稱含逗號，輸出時原樣輸出即可（不需加引號）。

        ### 輸入範例
        ```text
        name,dept,salary
        Ann,RD,80000
        Bob,Sales,50000
        Cy,RD,
        Dee,RD,70000
        ```
        ### 輸出範例
        ```text
        RD,2,75000.00,80000
        Sales,1,50000.00,50000
        ```
        ''',
        r'''
        import io
        import sys
        import pandas as pd

        df = pd.read_csv(io.StringIO(sys.stdin.read()))
        ''',
        r'''
        import io
        import sys
        import pandas as pd

        df = pd.read_csv(io.StringIO(sys.stdin.read()), dtype={"dept": str, "name": str})
        df = df.dropna(subset=["salary"])
        stats = df.groupby("dept")["salary"].agg(["count", "mean", "max"]).reset_index()
        rows = sorted(stats.itertuples(index=False), key=lambda r: (-r.mean, r.dept))
        for r in rows:
            print(f"{r.dept},{r.count},{r.mean:.2f},{int(r.max)}")
        ''',
        [
            T("name,dept,salary\nAnn,RD,80000\nBob,Sales,50000\nCy,RD,\nDee,RD,70000\n", tag="sample",
              expect="RD,2,75000.00,80000\nSales,1,50000.00,50000"),
            T("name,dept,salary\n", tag="corner", note="只有標題，沒有資料", expect=""),
            T("name,dept,salary\nA,X,\nB,X,\nC,Y,100\n", tag="corner", note="X 部門全部缺失 → 不輸出", expect="Y,1,100.00,100"),
            T("name,dept,salary\nA,B,100\nC,A,100\nD,C,100\n", tag="corner", note="平均相同 → 依名稱", expect="A,1,100.00,100\nB,1,100.00,100\nC,1,100.00,100"),
            T('name,dept,salary\nA,"R&D, Taipei",90000\nB,"R&D, Taipei",60000\nC,HR,70000\n', tag="corner", note="引號包住含逗號的欄位",
              expect="R&D, Taipei,2,75000.00,90000\nHR,1,70000.00,70000"),
            T("name,dept,salary\n甲,研發,1\n乙,研發,2\n丙,業務,2\n", tag="corner", note="中文、平均 1.5", expect="業務,1,2.00,2\n研發,2,1.50,2"),
            T("name,dept,salary\nA,X,1\nB,X,2\nC,X,2\n", tag="corner", note="平均 1.666… → 1.67", expect="X,3,1.67,2"),
            T("name,dept,salary\nA,X,9999999999\nB,X,1\n", tag="corner", note="大數"),
            T("name,dept,salary\nA,001,5\nB,1,7\n", tag="corner", note="部門代碼 001 和 1 是不同部門（要指定 dtype=str）", expect="1,1,7.00,7\n001,1,5.00,5"),
            T("name,dept,salary\n" + "".join(f"p{i},D{i % 37},{(i * 7919) % 100000}\n" for i in range(50000)), tag="stress", note="5 萬列"),
        ],
        gen=r'''
        def gen(rng):
            rows = []
            for i in range(rng.randint(0, 10)):
                sal = "" if rng.random() < 0.2 else str(rng.randint(1, 100) * 1000)
                rows.append(f"p{i},{rng.choice(['RD', 'HR', 'Ops', 'Sales'])},{sal}")
            return "name,dept,salary\n" + "".join(r + "\n" for r in rows)
        ''',
        hints=["`dropna(subset=['salary'])` 先排除缺失。", "`groupby('dept')['salary'].agg(['count', 'mean', 'max'])`",
               "讀檔時 `dtype={'dept': str}`，否則 `001` 會被當成數字 1。"],
        wrong=[r'''
        import io, sys
        import pandas as pd
        df = pd.read_csv(io.StringIO(sys.stdin.read()))
        df["salary"] = df["salary"].fillna(0)
        s = df.groupby("dept")["salary"].agg(["count", "mean", "max"]).sort_values("mean", ascending=False)
        for dept, r in s.iterrows():
            print(f"{dept},{int(r['count'])},{r['mean']:.2f},{int(r['max'])}")
        '''],
    ),
    exercise(
        "p2-interpolate", "Pandas：時間序列缺值補齊", 3, r'''
        讀入 CSV（標題 `date,temp`），`date` 格式為 `YYYY-MM-DD`，`temp` 可能空白。資料**可能未排序**、**同一天可能出現多次**。

        處理步驟：
        1. 依日期排序；同一天出現多次時，只保留**輸入中最後出現**的那一筆
        2. 缺值以**相鄰有效值的線性內插**補齊（依「列的位置」內插，不考慮日期間隔）
        3. 開頭的缺值用第一個有效值補、結尾的缺值用最後一個有效值補
        4. 若全部都是缺值（或沒有任何資料列），只輸出 `no data`

        輸出每天一行：`日期 溫度`（溫度一位小數）。

        ### 輸入範例
        ```text
        date,temp
        2024-01-03,
        2024-01-01,10
        2024-01-04,16
        2024-01-02,
        ```
        ### 輸出範例
        ```text
        2024-01-01 10.0
        2024-01-02 12.0
        2024-01-03 14.0
        2024-01-04 16.0
        ```
        ''',
        r'''
        import io
        import sys
        import pandas as pd

        df = pd.read_csv(io.StringIO(sys.stdin.read()))
        ''',
        r'''
        import io
        import sys
        import pandas as pd

        df = pd.read_csv(io.StringIO(sys.stdin.read()), dtype={"date": str})
        df["temp"] = pd.to_numeric(df["temp"], errors="coerce").astype(float)
        df = df.drop_duplicates(subset="date", keep="last").sort_values("date", kind="stable")
        if df["temp"].notna().sum() == 0:
            print("no data")
        else:
            temps = df["temp"].interpolate().bfill().ffill()
            for d, t in zip(df["date"], temps):
                print(f"{d} {t:.1f}")
        ''',
        [
            T("date,temp\n2024-01-03,\n2024-01-01,10\n2024-01-04,16\n2024-01-02,\n", tag="sample",
              expect="2024-01-01 10.0\n2024-01-02 12.0\n2024-01-03 14.0\n2024-01-04 16.0"),
            T("date,temp\n", tag="corner", note="沒有資料列", expect="no data"),
            T("date,temp\n2024-01-01,\n2024-01-02,\n", tag="corner", note="全部缺值", expect="no data"),
            T("date,temp\n2024-01-01,\n2024-01-02,\n2024-01-03,5\n2024-01-04,\n", tag="corner", note="開頭與結尾缺值",
              expect="2024-01-01 5.0\n2024-01-02 5.0\n2024-01-03 5.0\n2024-01-04 5.0"),
            T("date,temp\n2024-01-01,1\n2024-01-01,9\n2024-01-02,3\n", tag="corner", note="重複日期保留最後一筆",
              expect="2024-01-01 9.0\n2024-01-02 3.0"),
            T("date,temp\n2024-01-01,5\n2024-01-01,\n", tag="corner", note="最後一筆是缺值：仍以它為準（變成全缺）", expect="no data"),
            T("date,temp\n2024-03-01,-3.5\n", tag="corner", note="只有一筆、負數", expect="2024-03-01 -3.5"),
            T("date,temp\n2024-01-01,0\n2024-01-10,\n2024-01-20,1\n", tag="corner", note="依位置內插，不看日期間隔",
              expect="2024-01-01 0.0\n2024-01-10 0.5\n2024-01-20 1.0"),
            T("date,temp\n2024-02-28,1\n2024-03-01,\n2024-02-29,\n2024-03-02,4\n", tag="corner", note="閏年 2/29 的排序",
              expect="2024-02-28 1.0\n2024-02-29 2.0\n2024-03-01 3.0\n2024-03-02 4.0"),
            T("date,temp\n2024-01-01,1\n2024-01-02,\n2024-01-03,\n2024-01-04,\n2024-01-05,2\n", note="長段缺值",
              expect="2024-01-01 1.0\n2024-01-02 1.2\n2024-01-03 1.5\n2024-01-04 1.8\n2024-01-05 2.0"),
            T("date,temp\n2023-12-31,1.25\n2024-01-01,1.35\n", tag="corner", note="四捨五入：1.25 → 1.2（浮點/銀行家）", expect="2023-12-31 1.2\n2024-01-01 1.4"),
        ],
        gen=r'''
        def gen(rng):
            days = [f"2024-01-{d:02d}" for d in range(1, 13)]
            rows = []
            for _ in range(rng.randint(0, 10)):
                t = "" if rng.random() < 0.4 else str(rng.randint(-50, 50) / 2)
                rows.append(f"{rng.choice(days)},{t}")
            return "date,temp\n" + "".join(r + "\n" for r in rows)
        ''',
        hints=["`drop_duplicates(subset='date', keep='last')` 要在排序**前**做（才是「輸入中」最後一筆）。",
               "`interpolate()` 不會補開頭的缺值，所以再接 `.bfill().ffill()`。",
               "`YYYY-MM-DD` 字串的字典序就是日期順序。"],
        wrong=[r'''
        import io, sys
        import pandas as pd
        df = pd.read_csv(io.StringIO(sys.stdin.read()))
        df = df.sort_values("date").drop_duplicates(subset="date", keep="last")
        if df["temp"].isna().all():
            print("no data")
        else:
            df["temp"] = df["temp"].interpolate().ffill().fillna(0)
            for d, t in zip(df["date"], df["temp"]):
                print(f"{d} {t:.1f}")
        '''],
    ),
    exercise(
        "p3-merge", "Pandas：訂單與顧客合併", 3, r'''
        輸入包含兩份 CSV，以一行 `---` 分隔：

        1. 訂單：標題 `order_id,customer_id,amount`
        2. 顧客：標題 `customer_id,name`

        對**每位顧客**（包含沒有訂單的）輸出一行：`customer_id,name,訂單數,總金額(兩位小數)`，
        排序：總金額遞減，相同時依 `customer_id` 遞增（數值比較）。

        若有訂單的 `customer_id` 不在顧客表中，把這些訂單彙總成**最後一行** `?,UNKNOWN,訂單數,總金額`（沒有這種訂單就不輸出此行）。

        ### 輸入範例
        ```text
        order_id,customer_id,amount
        1,10,100
        2,20,250.5
        3,10,50
        4,99,70
        ---
        customer_id,name
        10,Ann
        20,Bob
        30,Cy
        ```
        ### 輸出範例
        ```text
        20,Bob,1,250.50
        10,Ann,2,150.00
        30,Cy,0,0.00
        ?,UNKNOWN,1,70.00
        ```
        ''',
        r'''
        import io
        import sys
        import pandas as pd

        orders_text, customers_text = sys.stdin.read().split("---\n")
        ''',
        r'''
        import io
        import sys
        import pandas as pd

        orders_text, customers_text = sys.stdin.read().split("---\n")
        orders = pd.read_csv(io.StringIO(orders_text))
        customers = pd.read_csv(io.StringIO(customers_text), dtype={"name": str}, keep_default_na=False)

        per = orders.groupby("customer_id")["amount"].agg(["count", "sum"])
        merged = customers.merge(per, left_on="customer_id", right_index=True, how="left")
        merged["count"] = merged["count"].fillna(0).astype(int)
        merged["sum"] = merged["sum"].fillna(0.0)
        for r in sorted(merged.itertuples(index=False), key=lambda r: (-r.sum, r.customer_id)):
            print(f"{r.customer_id},{r.name},{r.count},{r.sum:.2f}")

        unknown = orders[~orders["customer_id"].isin(customers["customer_id"])]
        if len(unknown):
            print(f"?,UNKNOWN,{len(unknown)},{unknown['amount'].sum():.2f}")
        ''',
        [
            T("order_id,customer_id,amount\n1,10,100\n2,20,250.5\n3,10,50\n4,99,70\n---\ncustomer_id,name\n10,Ann\n20,Bob\n30,Cy\n",
              tag="sample", expect="20,Bob,1,250.50\n10,Ann,2,150.00\n30,Cy,0,0.00\n?,UNKNOWN,1,70.00"),
            T("order_id,customer_id,amount\n---\ncustomer_id,name\n1,A\n2,B\n", tag="corner", note="沒有任何訂單", expect="1,A,0,0.00\n2,B,0,0.00"),
            T("order_id,customer_id,amount\n1,5,10\n---\ncustomer_id,name\n", tag="corner", note="沒有任何顧客", expect="?,UNKNOWN,1,10.00"),
            T("order_id,customer_id,amount\n---\ncustomer_id,name\n", tag="corner", note="兩邊都空", expect=""),
            T("order_id,customer_id,amount\n1,2,5\n2,10,5\n---\ncustomer_id,name\n10,X\n2,Y\n", tag="corner", note="同金額依 id 數值排序（2 < 10）",
              expect="2,Y,1,5.00\n10,X,1,5.00"),
            T("order_id,customer_id,amount\n1,1,-30\n2,1,10\n3,2,0\n---\ncustomer_id,name\n1,Neg\n2,Zero\n3,None\n", tag="corner", note="負數金額（退款）",
              expect="2,Zero,1,0.00\n3,None,0,0.00\n1,Neg,2,-20.00"),
            T("order_id,customer_id,amount\n1,1,0.1\n2,1,0.2\n---\ncustomer_id,name\n1,F\n", tag="corner", note="浮點加總 0.30000000000000004", expect="1,F,2,0.30"),
            T("order_id,customer_id,amount\n1,7,1\n2,8,2\n3,7,3\n---\ncustomer_id,name\n1,A\n", tag="corner", note="多筆未知顧客彙總",
              expect="1,A,0,0.00\n?,UNKNOWN,3,6.00"),
            T("order_id,customer_id,amount\n1,1,5\n---\ncustomer_id,name\n1,NA\n2,null\n", tag="corner", note="名字是 NA/null 字串（read_csv 預設會當成缺值！）",
              expect="1,NA,1,5.00\n2,null,0,0.00"),
            T("order_id,customer_id,amount\n" + "".join(f"{i},{i % 1000},{i % 97}.5\n" for i in range(30000)) + "---\ncustomer_id,name\n"
              + "".join(f"{i},c{i}\n" for i in range(0, 1200, 2)), tag="stress", note="3 萬筆訂單"),
        ],
        gen=r'''
        def gen(rng):
            ids = list(range(1, 6))
            orders = [f"{i},{rng.choice(ids + [9])},{rng.randint(-5, 50)}" for i in range(rng.randint(0, 8))]
            custs = [f"{c},n{c}" for c in rng.sample(ids, rng.randint(0, 5))]
            return ("order_id,customer_id,amount\n" + "".join(o + "\n" for o in orders) + "---\n"
                    + "customer_id,name\n" + "".join(c + "\n" for c in custs))
        ''',
        hints=["先對訂單 groupby 再和顧客 left merge，就能保留沒有訂單的顧客。",
               "`orders['customer_id'].isin(customers['customer_id'])` 找出已知顧客的訂單。",
               "`read_csv` 會把字串 `NA`、`null` 當成缺值：用 `keep_default_na=False` 或對 name 欄另外處理。"],
        wrong=[r'''
        import io, sys
        import pandas as pd
        a, b = sys.stdin.read().split("---\n")
        orders, customers = pd.read_csv(io.StringIO(a)), pd.read_csv(io.StringIO(b))
        m = orders.merge(customers, on="customer_id", how="inner")
        g = m.groupby(["customer_id", "name"])["amount"].agg(["count", "sum"]).reset_index()
        for r in g.sort_values("sum", ascending=False).itertuples():
            print(f"{r.customer_id},{r.name},{r.count},{r.sum:.2f}")
        '''],
    ),
    exercise(
        "p4-combos", "itertools：所有和為目標的組合", 2, r'''
        第一行為整數 `target`，第二行為 `n` 個整數（0 ≤ n ≤ 15，**可能有重複、負數、0**；第二行可能是空行）。

        找出所有「從中挑選 **至少一個** 元素、總和等於 `target`」的組合。視為多重集合：**值相同的組合只輸出一次**。

        每個組合以**遞增**順序輸出一行（數字以空白分隔），所有行依「數值 tuple 的字典序」排序。沒有任何組合時輸出 `none`。

        ### 輸入範例
        ```text
        5
        1 2 3 2 4
        ```
        ### 輸出範例
        ```text
        1 2 2
        1 4
        2 3
        ```
        ''',
        r'''
        from itertools import combinations

        target = int(input())
        nums = list(map(int, input().split()))
        ''',
        r'''
        from itertools import combinations

        target = int(input())
        nums = sorted(map(int, input().split()))
        found = {c for r in range(1, len(nums) + 1) for c in combinations(nums, r) if sum(c) == target}
        if found:
            for c in sorted(found):
                print(*c)
        else:
            print("none")
        ''',
        [
            T("5\n1 2 3 2 4\n", tag="sample", expect="1 2 2\n1 4\n2 3"),
            T("3\n\n", tag="corner", note="空集合", expect="none"),
            T("0\n\n", tag="corner", note="target 0 但沒有元素（不能選空組合）", expect="none"),
            T("0\n0 0\n", tag="corner", note="0 本身", expect="0\n0 0"),
            T("0\n-1 1 2 -2\n", tag="corner", note="負數相消", expect="-2 -1 1 2\n-2 2\n-1 1"),
            T("4\n2 2 2 2\n", tag="corner", note="大量重複只輸出一次", expect="2 2"),
            T("7\n7\n", tag="corner", note="單一元素", expect="7"),
            T("100\n1 2 3\n", note="無解", expect="none"),
            T("3\n3 1 2 0\n", tag="corner", note="0 可加可不加", expect="0 1 2\n0 3\n1 2\n3"),
            T("-3\n-1 -2 -3 1\n", tag="corner", note="負目標", expect="-3\n-3 -1 1\n-2 -1"),
            T("10\n" + " ".join(["1", "2", "3", "4", "5", "1", "2", "3", "4", "5", "-1", "0", "6", "7", "8"]) + "\n", tag="stress", note="n = 15"),
        ],
        gen=r'''
        def gen(rng):
            nums = [rng.randint(-3, 6) for _ in range(rng.randint(0, 8))]
            return f"{rng.randint(-3, 10)}\n" + " ".join(map(str, nums)) + "\n"
        ''',
        hints=["先排序，`combinations` 產生的每個 tuple 就自然是遞增的。", "放進 `set` 去重，最後 `sorted`。",
               "注意排序字典序：`(-3,)` 會排在 `(-2, -1)` 前面。"],
        wrong=[r'''
        from itertools import combinations
        target = int(input())
        nums = sorted(map(int, input().split()))
        out = [c for r in range(1, len(nums) + 1) for c in combinations(nums, r) if sum(c) == target]
        for c in out:
            print(*c)
        if not out:
            print("none")
        '''],
    ),
    exercise(
        "p5-logs", "標準庫綜合：日誌分析 (re + datetime + json)", 3, r'''
        從標準輸入讀入若干行日誌，合法格式為：

        ```text
        YYYY-MM-DD HH:MM:SS LEVEL 訊息
        ```

        - `LEVEL` 必須是 `DEBUG`、`INFO`、`WARNING`、`ERROR` 之一（**不分大小寫**，統計時轉大寫）
        - 日期時間必須是**真實存在**的時間（`2023-02-29` 不合法）
        - 訊息可以為空，但 LEVEL 後面必須有空白或直接行尾
        - 空白行完全忽略（不算 total 也不算 invalid）；其他不合法的行計入 `invalid`

        輸出一行 JSON（`json.dumps(結果, sort_keys=True, ensure_ascii=False)`）：

        | key | 說明 |
        |---|---|
        | `total` | 合法行數 |
        | `invalid` | 不合法行數 |
        | `levels` | 各 LEVEL 的次數（只列出有出現的） |
        | `first` / `last` | 最早 / 最晚的時間（ISO 格式 `YYYY-MM-DDTHH:MM:SS`），沒有合法行時為 `null` |
        | `span_seconds` | `last − first` 的秒數（整數），沒有合法行時為 0 |
        | `top_error` | ERROR 訊息中出現最多次的訊息（去除前後空白後比較；同次數取字典序最小），沒有 ERROR 時為 `null` |

        ### 輸入範例
        ```text
        2024-05-01 10:00:00 INFO server start
        2024-05-01 10:05:00 error db timeout
        oops
        2024-05-01 09:59:00 ERROR db timeout
        ```
        ### 輸出範例
        ```text
        {"first": "2024-05-01T09:59:00", "invalid": 1, "last": "2024-05-01T10:05:00", "levels": {"ERROR": 2, "INFO": 1}, "span_seconds": 360, "top_error": "db timeout", "total": 3}
        ```
        ''',
        r'''
        import json
        import re
        import sys
        from datetime import datetime

        for line in sys.stdin.read().splitlines():
            pass
        ''',
        r'''
        import json
        import re
        import sys
        from collections import Counter
        from datetime import datetime

        PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (DEBUG|INFO|WARNING|ERROR)(?: (.*))?", re.IGNORECASE)

        total = invalid = 0
        levels, errors, times = Counter(), Counter(), []
        for line in sys.stdin.read().splitlines():
            if not line.strip():
                continue
            m = PATTERN.fullmatch(line)
            try:
                if not m:
                    raise ValueError
                ts = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                invalid += 1
                continue
            total += 1
            level = m.group(2).upper()
            levels[level] += 1
            times.append(ts)
            if level == "ERROR":
                errors[(m.group(3) or "").strip()] += 1

        first, last = (min(times), max(times)) if times else (None, None)
        top_error = min(errors.items(), key=lambda kv: (-kv[1], kv[0]))[0] if errors else None
        print(json.dumps({
            "total": total,
            "invalid": invalid,
            "levels": dict(levels),
            "first": first.isoformat() if first else None,
            "last": last.isoformat() if last else None,
            "span_seconds": int((last - first).total_seconds()) if times else 0,
            "top_error": top_error,
        }, sort_keys=True, ensure_ascii=False))
        ''',
        [
            T("2024-05-01 10:00:00 INFO server start\n2024-05-01 10:05:00 error db timeout\noops\n2024-05-01 09:59:00 ERROR db timeout\n",
              tag="sample",
              expect='{"first": "2024-05-01T09:59:00", "invalid": 1, "last": "2024-05-01T10:05:00", "levels": {"ERROR": 2, "INFO": 1}, "span_seconds": 360, "top_error": "db timeout", "total": 3}'),
            T("", tag="corner", note="完全沒有輸入",
              expect='{"first": null, "invalid": 0, "last": null, "levels": {}, "span_seconds": 0, "top_error": null, "total": 0}'),
            T("\n   \n\n", tag="corner", note="只有空白行",
              expect='{"first": null, "invalid": 0, "last": null, "levels": {}, "span_seconds": 0, "top_error": null, "total": 0}'),
            T("2023-02-29 00:00:00 INFO x\n2024-02-29 00:00:00 INFO leap\n2024-13-01 00:00:00 INFO x\n2024-01-01 24:00:00 INFO x\n", tag="corner",
              note="不存在的日期時間（2023 非閏年、13 月、24 點）",
              expect='{"first": "2024-02-29T00:00:00", "invalid": 3, "last": "2024-02-29T00:00:00", "levels": {"INFO": 1}, "span_seconds": 0, "top_error": null, "total": 1}'),
            T("2024-01-01 00:00:00 FATAL boom\n2024-01-01 00:00:00 INFOx\n2024-01-01 00:00:00 warning\n2024-1-01 00:00:00 INFO a\n", tag="corner",
              note="未知 LEVEL、LEVEL 後沒空白、沒有訊息、日期沒補零",
              expect='{"first": "2024-01-01T00:00:00", "invalid": 3, "last": "2024-01-01T00:00:00", "levels": {"WARNING": 1}, "span_seconds": 0, "top_error": null, "total": 1}'),
            T("2024-01-01 00:00:00 ERROR b\n2024-01-01 00:00:01 ERROR a\n2024-01-01 00:00:02 ERROR  b \n2024-01-01 00:00:03 ERROR a\n", tag="corner",
              note="ERROR 訊息同次數取字典序最小、去除前後空白",
              expect='{"first": "2024-01-01T00:00:00", "invalid": 0, "last": "2024-01-01T00:00:03", "levels": {"ERROR": 4}, "span_seconds": 3, "top_error": "a", "total": 4}'),
            T("2024-01-01 00:00:00 ERROR\n", tag="corner", note="ERROR 但訊息為空",
              expect='{"first": "2024-01-01T00:00:00", "invalid": 0, "last": "2024-01-01T00:00:00", "levels": {"ERROR": 1}, "span_seconds": 0, "top_error": "", "total": 1}'),
            T("2023-12-31 23:59:59 info 跨年\n2024-01-01 00:00:00 Debug 新年快樂\n", tag="corner", note="跨年、中文、大小寫混合",
              expect='{"first": "2023-12-31T23:59:59", "invalid": 0, "last": "2024-01-01T00:00:00", "levels": {"DEBUG": 1, "INFO": 1}, "span_seconds": 1, "top_error": null, "total": 2}'),
            T(" 2024-01-01 00:00:00 INFO leading space\n2024-01-01 00:00:00 INFO trailing  \n", tag="corner", note="行首有空白不合法",
              expect='{"first": "2024-01-01T00:00:00", "invalid": 1, "last": "2024-01-01T00:00:00", "levels": {"INFO": 1}, "span_seconds": 0, "top_error": null, "total": 1}'),
            T("2020-01-01 00:00:00 INFO a\n2024-01-01 00:00:00 INFO b\n", note="跨多年的秒數",
              expect='{"first": "2020-01-01T00:00:00", "invalid": 0, "last": "2024-01-01T00:00:00", "levels": {"INFO": 2}, "span_seconds": 126230400, "top_error": null, "total": 2}'),
            T("".join(f"2024-03-{1 + i % 28:02d} {i % 24:02d}:{i % 60:02d}:00 {['INFO', 'ERROR', 'debug', 'bad'][i % 4]} msg{i % 5}\n" for i in range(20000)),
              tag="stress", note="2 萬行"),
        ],
        gen=r'''
        def gen(rng):
            lines = []
            for _ in range(rng.randint(0, 8)):
                d = f"{rng.choice([2023, 2024])}-{rng.randint(1, 13):02d}-{rng.randint(1, 31):02d}"
                t = f"{rng.randint(0, 24):02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d}"
                lv = rng.choice(["INFO", "error", "Debug", "WARNING", "TRACE"])
                msg = rng.choice(["", " a", " b", " a ", " 中文"])
                lines.append(rng.choice([f"{d} {t} {lv}{msg}", "", "garbage"]))
            return "".join(l + "\n" for l in lines)
        ''',
        hints=["用 `re.fullmatch` 確保整行都符合格式。", "`datetime.strptime` 遇到不存在的日期會拋 `ValueError`。",
               "`(?: (.*))?` 表示「可選的：空白 + 訊息」。", "`json.dumps` 會把 None 轉成 null。"],
        wrong=[r'''
        import json, sys
        from collections import Counter
        from datetime import datetime
        total = invalid = 0
        levels, errors, times = Counter(), Counter(), []
        for line in sys.stdin.read().splitlines():
            if not line.strip():
                continue
            parts = line.split(" ", 3)
            if len(parts) < 3 or parts[2].upper() not in ("DEBUG", "INFO", "WARNING", "ERROR"):
                invalid += 1
                continue
            total += 1
            ts = datetime.fromisoformat(parts[0] + " " + parts[1])
            levels[parts[2].upper()] += 1
            times.append(ts)
            if parts[2].upper() == "ERROR":
                errors[parts[3].strip() if len(parts) > 3 else ""] += 1
        print(json.dumps({"total": total, "invalid": invalid, "levels": dict(levels),
            "first": min(times).isoformat() if times else None, "last": max(times).isoformat() if times else None,
            "span_seconds": int((max(times) - min(times)).total_seconds()) if times else 0,
            "top_error": errors.most_common(1)[0][0] if errors else None}, sort_keys=True, ensure_ascii=False))
        '''],
    ),
]

UNIT = {
    "id": "packages", "num": 6, "title": "套件應用", "icon": "📦",
    "summary": "import 機制、標準庫精選、NumPy 向量化、Pandas 資料分析",
    "lesson": LESSON, "quiz": QUIZ, "exercises": EXERCISES,
}
