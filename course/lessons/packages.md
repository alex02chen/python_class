# 單元六：套件應用

> **這個單元要解決的問題**：Python 受歡迎的最大原因，是它有非常豐富的「現成工具」：內建的標準函式庫，加上幾十萬個第三方套件。學會「找工具、用工具」，很多問題就不用自己從零開始寫。
> 這個單元先說明 `import` 背後的機制，再介紹最常用的標準函式庫，最後深入資料分析的兩大支柱：**NumPy** 和 **Pandas**。

> 💡 本頁的 NumPy / Pandas 範例第一次執行時，瀏覽器要下載約 10–20 MB 的套件，請稍候幾秒。之後就會很快。

**讀完你會知道：**

1. `import` 到底做了什麼、模組和套件的差別
2. `if __name__ == "__main__":` 的用途
3. 虛擬環境和 pip 是什麼
4. 標準函式庫精選：`itertools`、`functools`、`datetime`、`json`、`re`
5. NumPy：為什麼它比 Python 迴圈快幾十倍
6. Pandas：讀取、篩選、分組、合併、處理缺失值

---

## 1. 模組與套件

### 1.1 名詞解釋

| 名詞 | 是什麼 | 例子 |
|---|---|---|
| **模組 (module)** | 一個 `.py` 檔案 | `math`、`random`、你寫的 `tools.py` |
| **套件 (package)** | 一個資料夾，裡面有很多模組 | `pandas`、`numpy` |
| **標準函式庫** | 安裝 Python 就附帶的模組 | `math`、`json`、`datetime` |
| **第三方套件** | 別人寫好、要另外安裝的 | `pandas`、`requests` |

### 1.2 `import` 背後發生了什麼？

執行 `import math` 時，Python 做了這幾件事：

1. **查快取**：看 `sys.modules` 裡有沒有 `math`，有就直接用（所以**同一個模組只會被載入一次**）
2. **找檔案**：依序在 `sys.path` 列出的資料夾裡找 `math`
3. **執行模組**：把模組裡的程式碼**從頭到尾執行一遍**，建立一個模組物件
4. **綁定名稱**：在目前的程式裡建立名稱 `math`，指向這個模組物件

```python
import sys
import math

print(type(math), math.__name__)
print("math" in sys.modules)          # 已經在快取裡了
print("搜尋路徑的前幾個：", sys.path[:3])
```

### 1.3 各種 import 寫法

```python
import math                         # 匯入整個模組，用 math.xxx 存取
print(math.sqrt(16))

import math as m                    # 取別名（例如 import numpy as np、import pandas as pd）
print(m.pi)

from math import floor, ceil        # 只匯入特定名稱，直接用
print(floor(2.7), ceil(2.1))

from math import factorial as fact  # 匯入並改名
print(fact(5))
```

> ⚠️ **不要寫 `from xxx import *`**：它會把模組裡所有名稱倒進你的程式，可能覆蓋掉你自己的變數，而且讀程式的人看不出某個名稱是從哪來的。

### 1.4 `if __name__ == "__main__":`

每個模組都有一個 `__name__` 變數：

- **直接執行**這個檔案（`python tools.py`）時，`__name__` 是 `"__main__"`
- **被別人 import** 時，`__name__` 是模組名稱 `"tools"`

```python
# 假設這是 tools.py
def add(a, b):
    return a + b

if __name__ == "__main__":
    # 只有直接執行這個檔案時才會跑；被 import 時不會
    print("自我測試：", add(1, 2))

print("目前的 __name__：", __name__)
```

**用途**：讓一個檔案「既可以被 import 當工具使用，又可以直接執行來測試」。沒有這個判斷的話，別人 import 你的模組時，你的測試程式碼也會跟著跑。

### 1.5 套件的資料夾結構

```text
my_project/
├── pyproject.toml           ← 專案設定、相依套件
└── src/
    └── mypkg/               ← 套件（資料夾）
        ├── __init__.py      ← 套件被 import 時執行；決定 `from mypkg import ...` 能拿到什麼
        ├── core.py          ← 模組
        └── utils/
            ├── __init__.py
            └── text.py      ← 在 core.py 中可以寫：from .utils.text import slugify
```

`from .utils.text import ...` 中的 `.` 代表「**同一個套件裡**」，這叫**相對匯入**。

### 1.6 安裝第三方套件：pip 與虛擬環境

**問題**：A 專案需要 pandas 1.5，B 專案需要 pandas 2.2，但電腦上只能裝一個版本，怎麼辦？

**解法：虛擬環境 (virtual environment)**。每個專案有一個獨立的資料夾存放自己的套件，互不干擾。

```text
python -m venv .venv               # 在專案資料夾建立虛擬環境
source .venv/bin/activate          # 啟用（Windows：.venv\Scripts\activate）
pip install pandas                 # 安裝套件（只裝在這個環境裡）
pip install "pandas==2.2.*"        # 指定版本
pip freeze > requirements.txt      # 把目前所有套件和版本記錄下來
pip install -r requirements.txt    # 在別台電腦依照記錄安裝一模一樣的環境
deactivate                         # 離開虛擬環境
```

> 💡 本平台使用 Pyodide（在瀏覽器裡跑的 Python），`import numpy` / `import pandas` 時會自動下載，不需要 pip。

---

## 2. 標準函式庫精選

### 2.1 itertools：迭代工具箱

**排列組合**：

```python
import itertools as it

print(list(it.combinations("ABC", 2)))      # 組合：不在乎順序，AB 和 BA 算同一種
print(list(it.permutations("ABC", 2)))      # 排列：在乎順序
print(list(it.product("ab", repeat=2)))     # 笛卡兒積：每個位置都可以是任何一個

# 實際應用：4 種配料任選 2 種，有幾種組合？
toppings = ["起司", "火腿", "鳳梨", "蘑菇"]
for combo in it.combinations(toppings, 2):
    print(" + ".join(combo))
```

**累積、串接、分組**：

```python
import itertools as it

print(list(it.accumulate([1, 2, 3, 4])))            # 累加：[1, 3, 6, 10]
print(list(it.accumulate([3, 1, 4, 1, 5], max)))    # 累積最大值
print(list(it.chain([1, 2], (3, 4), "ab")))         # 把多個序列接成一個
print(list(it.pairwise([1, 4, 9, 16])))             # 相鄰兩兩配對（3.10+）

# groupby：只合併「相鄰」的相同元素！
print([(k, len(list(g))) for k, g in it.groupby("aaabccaa")])
# 要依值分組，必須先排序
print([(k, len(list(g))) for k, g in it.groupby(sorted("aaabccaa"))])
```

**無限迭代器**（記得搭配 `islice` 或 `break`）：

```python
import itertools as it

print(list(it.islice(it.count(10, 5), 4)))      # 10, 15, 20, 25, …
print(list(it.islice(it.cycle("AB"), 5)))       # A B A B A …
```

### 2.2 functools

```python
from functools import reduce, partial, lru_cache, cmp_to_key

print(reduce(lambda a, b: a * b, range(1, 6)))   # 5! = 120

int_from_binary = partial(int, base=2)            # 固定 base=2
print(int_from_binary("1011"))

# cmp_to_key：用「比較兩個元素」的方式定義排序
# 經典題：把數字排成最大的數
nums = [3, 30, 34, 5, 9]
def compare(a, b):
    return -1 if a + b > b + a else (1 if a + b < b + a else 0)   # 哪個放前面組起來比較大
print("".join(sorted(map(str, nums), key=cmp_to_key(compare))))
```

### 2.3 datetime：日期與時間

```python
from datetime import datetime, date, timedelta

now = datetime(2024, 2, 28, 23, 30)
print(now + timedelta(hours=1))                   # 2024 是閏年 → 2/29
print(now + timedelta(days=2))

d = datetime.strptime("2024-05-01 14:30", "%Y-%m-%d %H:%M")   # 字串 → datetime（parse）
print(d, d.year, d.weekday())                     # weekday：星期一是 0
print(d.strftime("%Y年%m月%d日 %H:%M"))            # datetime → 字串（format）
print(d.isoformat())

print((date(2025, 1, 1) - date(2024, 1, 1)).days, "天")   # 兩個日期相減 → timedelta

try:
    datetime.strptime("2023-02-29", "%Y-%m-%d")   # 2023 不是閏年
except ValueError as e:
    print("ValueError:", e)
```

> 💡 記法：**strptime** 的 p = **p**arse（字串→時間），**strftime** 的 f = **f**ormat（時間→字串）。

### 2.4 json：資料交換格式

JSON 是網路上最常見的資料格式，和 Python 的 dict/list 幾乎一一對應：

| Python | JSON |
|---|---|
| `dict` | object `{}` |
| `list`、`tuple` | array `[]` |
| `str` | string |
| `int`、`float` | number |
| `True` / `False` | `true` / `false` |
| `None` | `null` |

```python
import json

data = {"name": "小明", "scores": [90, 85], "passed": True, "note": None}
text = json.dumps(data, ensure_ascii=False)       # Python → JSON 字串
print(text)
print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))   # 美化輸出

back = json.loads(text)                           # JSON 字串 → Python
print(back["scores"], type(back))
```

> ⚠️ 不加 `ensure_ascii=False` 的話，中文會變成 `小明` 這種跳脫字元。

### 2.5 re：正規表達式

正規表達式 (regular expression) 是描述「文字模式」的小語言，用來搜尋、驗證、擷取文字。

| 符號 | 意思 | 範例 |
|---|---|---|
| `\d` | 一個數字 | `\d\d` 匹配 "42" |
| `\w` | 一個字母、數字或底線 | |
| `\s` | 一個空白字元 | |
| `.` | 任何一個字元（除了換行） | |
| `*` `+` `?` | 0 次以上、1 次以上、0 或 1 次 | `\d+` 匹配一串數字 |
| `{n}` `{m,n}` | 剛好 n 次、m 到 n 次 | `\d{4}` 匹配四位數 |
| `[abc]` `[a-z]` | 其中一個字元 | |
| `^` `$` | 開頭、結尾 | |
| `( )` | 群組（擷取） | |

```python
import re

text = "訂單 A1234 於 2024-05-01 成立，訂單 B5678 於 2024-05-03 取消"
print(re.findall(r"[A-Z]\d{4}", text))                # 找出所有訂單編號
print(re.findall(r"\d{4}-\d{2}-\d{2}", text))         # 找出所有日期

# 具名群組：把配對到的部分分別取出
pattern = re.compile(r"(?P<id>[A-Z]\d+) 於 (?P<date>[\d-]+) (?P<action>成立|取消)")
for m in pattern.finditer(text):
    print(m.group("id"), m["date"], m["action"])

print(re.sub(r"\d", "*", "密碼 1234"))                  # 取代
print(re.split(r"[,;]\s*", "a, b;c,d"))               # 用多種分隔符號切割
print(bool(re.fullmatch(r"09\d{8}", "0912345678")))   # 驗證整個字串符合格式
```

**貪婪 vs 非貪婪**：`+` 和 `*` 預設會「**盡量多吃**」，加上 `?` 變成「**盡量少吃**」：

```python
import re
html = "<b>粗體</b> 和 <i>斜體</i>"
print(re.findall(r"<.+>", html))      # 貪婪：從第一個 < 一路吃到最後一個 >
print(re.findall(r"<.+?>", html))     # 非貪婪：每個標籤分開
```

> 💡 正規表達式字串前面加 `r`（raw string），反斜線才不會被 Python 先處理掉。

---

## 3. NumPy：快速的數值運算

### 3.1 為什麼需要 NumPy？

Python 的 list 很彈性，但做大量數值運算很慢。原因是 list 裡每個數字都是一個獨立的 Python 物件，每次運算 Python 都要檢查型別、建立新物件。

NumPy 的**陣列 (array)** 則是：

- **所有元素型別相同**（例如全部是 64 位元整數）
- **連續存放在記憶體中**，像 C 語言的陣列
- **運算用 C 語言寫成的迴圈完成**，不經過 Python 直譯器

```python
import numpy as np
import time

n = 1_000_000
py_list = list(range(n))
np_array = np.arange(n)

t0 = time.perf_counter()
result1 = [x * 2 for x in py_list]
t1 = time.perf_counter()
result2 = np_array * 2                    # 一行就對所有元素運算
t2 = time.perf_counter()
print(f"Python list：{(t1 - t0) * 1000:.1f} ms")
print(f"NumPy array：{(t2 - t1) * 1000:.1f} ms")
```

這種「**對整個陣列下指令，而不是寫迴圈**」的寫法叫做**向量化 (vectorization)**。

### 3.2 基本操作

```python
import numpy as np

a = np.array([1, 2, 3, 4])
print(a * 2, a + 10, a ** 2)              # 每個元素都做運算
print(a + np.array([10, 20, 30, 40]))     # 兩個陣列：對應位置相加
print(a.sum(), a.mean(), a.max(), a.std())
print(a.dtype, a.shape)
```

### 3.3 多維陣列

```python
import numpy as np

m = np.arange(12).reshape(3, 4)           # 0~11 排成 3 列 4 行
print(m)
print("形狀：", m.shape)
print("第 1 列第 2 行：", m[1, 2])
print("第 1 行（直的）：", m[:, 1])
print("每一行的總和：", m.sum(axis=0))    # axis=0：沿著「列」的方向壓縮 → 每行一個結果
print("每一列的總和：", m.sum(axis=1))    # axis=1：沿著「行」的方向壓縮 → 每列一個結果
```

> 💡 `axis` 記法：`axis=0` 是「**把這個方向壓扁**」。3×4 的陣列沿 axis=0 壓扁，剩下 4 個數字。

### 3.4 布林遮罩：用條件篩選

```python
import numpy as np

scores = np.array([85, 42, 90, 67, 55, 78])
passed = scores >= 60                     # 每個元素做比較 → 布林陣列
print(passed)
print("及格的分數：", scores[passed])      # 用布林陣列當索引 → 只留下 True 的
print("及格人數：", passed.sum())
print("不及格的補到 60：", np.where(scores < 60, 60, scores))
```

### 3.5 廣播 (broadcasting)

形狀不同的陣列運算時，NumPy 會自動「延伸」較小的那個：

```python
import numpy as np

scores = np.array([[80, 90, 70],          # 3 個學生 × 3 科
                   [60, 75, 85],
                   [90, 95, 100]])
bonus = np.array([5, 0, 10])              # 每科加分
print(scores + bonus)                     # bonus 自動套用到每一列
print(scores - scores.mean(axis=0))       # 每科減去該科平均
```

### 3.6 ⚠️ 固定大小的整數會溢位

Python 的 int 沒有上限，但 NumPy 為了速度用固定大小的整數，**超過範圍會默默溢位**：

```python
import numpy as np
a = np.array([2 ** 62], dtype=np.int64)
print(a * 4)               # 溢位變成錯誤的數字，而且沒有任何警告
print(2 ** 62 * 4)         # Python int 不會
```

---

## 4. Pandas：表格資料處理

### 4.1 兩個核心結構

- **Series**：一欄資料（有標籤的一維陣列）
- **DataFrame**：一張表格（多個 Series 組成，每欄一個名稱）

```python
import pandas as pd

s = pd.Series([90, 75, 88], index=["小明", "小華", "小美"])
print(s)
print(s["小華"], s.mean())

df = pd.DataFrame({
    "name": ["小明", "小華", "小美", "阿強"],
    "dept": ["RD", "Sales", "RD", "HR"],
    "salary": [82000, 56000, 90000, 61000],
})
print(df)
print(df.shape, list(df.columns))
print(df.dtypes)
```

### 4.2 讀取 CSV

實務上資料通常來自檔案。練習題會從標準輸入給你 CSV 文字，可以用 `io.StringIO` 把字串包裝成「假檔案」：

```python
import io
import pandas as pd

csv_text = """name,dept,salary,joined
Ann,RD,82000,2019-03-01
Bob,Sales,56000,2020-07-15
Cy,RD,,2021-01-10
Dee,HR,61000,2018-11-30
"""
df = pd.read_csv(io.StringIO(csv_text), parse_dates=["joined"])
print(df)
print(df.dtypes)          # salary 有空值，所以變成 float64；joined 變成日期型別
```

> ⚠️ `read_csv` 會**自動猜型別**，有時候猜錯：`"001"` 會被當成數字 1；字串 `"NA"`、`"null"` 會被當成缺失值。需要時用 `dtype={"欄位": str}`、`keep_default_na=False` 控制。

### 4.3 選取資料

```python
import pandas as pd
df = pd.DataFrame({"name": ["小明", "小華", "小美"], "age": [28, 35, 42], "city": ["台北", "高雄", "台北"]})

print(df["name"].tolist())                  # 選一欄 → Series
print(df[["name", "age"]])                  # 選多欄（注意兩層中括號）→ DataFrame
print(df[df["age"] > 30])                   # 用條件篩選列
print(df[(df["city"] == "台北") & (df["age"] < 40)])   # 多條件：用 & |，每個條件要加括號
print(df.loc[df["age"] > 30, "name"].tolist())   # loc：依「標籤 / 條件」選列和欄
print(df.iloc[0], df.iloc[-1, 1])                # iloc：依「位置數字」選
```

| | `loc` | `iloc` |
|---|---|---|
| 依據 | 標籤（索引名稱、欄名）或布林條件 | 位置（0, 1, 2…） |
| 切片 `a:b` | **包含** b | **不包含** b |

> ⚠️ 多個條件要用 `&`（且）、`|`（或），**不能用 `and` / `or`**，而且每個條件要用括號包起來。

### 4.4 新增欄位與排序

```python
import pandas as pd
df = pd.DataFrame({"item": ["咖啡", "蛋糕", "三明治"], "price": [120, 80, 95], "qty": [3, 10, 4]})

df["total"] = df["price"] * df["qty"]                         # 向量化：整欄一起算
df["level"] = df["total"].apply(lambda t: "高" if t > 400 else "低")   # apply：逐一呼叫函式（較慢）
print(df.sort_values("total", ascending=False))
print(df.sort_values(["level", "total"], ascending=[True, False]))   # 多欄排序
```

> 💡 **能向量化就不要用 `apply`**。`apply` 本質上就是一個 Python 迴圈，資料量大時會慢很多。上面的 `level` 可以改寫成 `np.where(df["total"] > 400, "高", "低")`。

### 4.5 處理缺失值

真實資料常常有空缺。Pandas 用 `NaN`（Not a Number）表示缺失：

```python
import pandas as pd
import numpy as np

s = pd.Series([1.0, np.nan, 3.0, np.nan, np.nan, 6.0])
print("缺幾個：", s.isna().sum())
print("平均（自動略過 NaN）：", s.mean())
print("補 0：", s.fillna(0).tolist())
print("用前一個值補：", s.ffill().tolist())
print("線性內插：", s.interpolate().tolist())
print("直接刪掉：", s.dropna().tolist())
print(np.nan == np.nan)           # False！NaN 不等於任何東西，包括自己
```

> ⚠️ 判斷缺失一定要用 `isna()`，不能用 `== np.nan`。

### 4.6 groupby：分組統計

`groupby` 的概念是「**拆開 → 各自計算 → 合併**」(split-apply-combine)：

```text
原始資料           拆開 (split)        計算 (apply)     合併 (combine)
dept  salary
RD    82000   →   RD: 82000, 90000  →  平均 86000  ┐
Sales 56000   →   Sales: 56000      →  平均 56000  ├→  dept   平均
RD    90000   →   HR: 61000         →  平均 61000  ┘    HR     61000
HR    61000                                              RD     86000
                                                         Sales  56000
```

```python
import pandas as pd
df = pd.DataFrame({
    "dept": ["RD", "Sales", "RD", "HR", "Sales", "RD"],
    "salary": [82000, 56000, 90000, 61000, 73000, 75000],
    "years": [5, 2, 8, 6, 1, 3],
})

print(df.groupby("dept")["salary"].mean())

summary = df.groupby("dept").agg(
    人數=("salary", "size"),
    平均薪資=("salary", "mean"),
    最高年資=("years", "max"),
)
print(summary.sort_values("平均薪資", ascending=False))

# transform：結果和原表一樣長，適合新增「組內統計」欄位
df["部門平均"] = df.groupby("dept")["salary"].transform("mean")
df["高於部門平均"] = df["salary"] > df["部門平均"]
print(df)
```

### 4.7 merge：合併兩張表

就像 SQL 的 JOIN，用共同的欄位把兩張表接起來：

```python
import pandas as pd
orders = pd.DataFrame({"order_id": [1, 2, 3, 4], "cust_id": [10, 20, 10, 99], "amount": [100, 250, 50, 70]})
customers = pd.DataFrame({"cust_id": [10, 20, 30], "name": ["Ann", "Bob", "Cy"]})

print("inner（兩邊都有的才留）：")
print(pd.merge(orders, customers, on="cust_id", how="inner"))
print("left（左邊全留，右邊沒有的補 NaN）：")
print(pd.merge(customers, orders, on="cust_id", how="left"))
print("outer（全部都留）：")
print(pd.merge(orders, customers, on="cust_id", how="outer", indicator=True))
```

| `how=` | 保留哪些列 |
|---|---|
| `"inner"` | 兩邊都有對應的 |
| `"left"` | 左表全部 |
| `"right"` | 右表全部 |
| `"outer"` | 兩邊全部 |

### 4.8 樞紐分析表

```python
import pandas as pd
sales = pd.DataFrame({
    "month": ["1月", "1月", "2月", "2月", "2月", "3月"],
    "region": ["北區", "南區", "北區", "北區", "南區", "南區"],
    "revenue": [100, 80, 120, 30, 90, 60],
})
print(sales.pivot_table(index="month", columns="region", values="revenue", aggfunc="sum", fill_value=0))
```

---

## 5. 實務心法

1. **能向量化就不要寫迴圈**。`apply` 和 `iterrows` 都是迴圈，資料量大時很慢。
2. **讀檔時就指定型別**：`dtype={"id": str}` 避免 `"00123"` 變成 123；`parse_dates=[...]` 讓日期欄位變成日期型別。
3. **修改篩選後的資料用 `loc`**：寫 `df.loc[條件, "欄位"] = 值`，不要寫 `df[條件]["欄位"] = 值`（後者可能改到副本，原表沒變）。
4. **輸出報表時自己控制格式**：`print(df)` 的樣子會因版本、欄寬而不同，需要穩定輸出就用 `f"{x:.2f}"` 自己格式化。練習題都是這樣要求的。
5. **NaN 不等於 NaN**；整數欄位一旦出現 NaN 就會被轉成 float。

## 6. 本章小結

| 觀念 | 一句話記住 |
|---|---|
| import | 找檔案 → 執行一次 → 快取在 `sys.modules` |
| `__name__ == "__main__"` | 直接執行才跑，被 import 時不跑 |
| 虛擬環境 | 每個專案一套獨立的套件 |
| itertools | 排列組合、累積、串接；`groupby` 只合併相鄰的 |
| datetime | strptime 解析、strftime 格式化 |
| json | `ensure_ascii=False` 才能正常顯示中文 |
| re | `r"..."` 寫法；`+?` 非貪婪 |
| NumPy | 同型別、連續記憶體、向量化運算 |
| Pandas | `loc`/`iloc` 選取、`groupby` 分組、`merge` 合併、`isna` 判斷缺失 |
