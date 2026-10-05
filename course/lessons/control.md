# 單元二：流程控制

> **這個單元要解決的問題**：程式不是從上到下跑一遍就結束，它要能「判斷」（如果…就…）、「重複」（做 n 次、做到某個條件為止），還要能「處理意外」（使用者輸入錯誤、檔案不存在）。
> 這些東西大家都會寫，但真正的差距在細節：`if not x` 什麼時候會誤判？`for` 迴圈底下到底發生了什麼？`match` 為什麼有時候會「什麼都匹配」？例外該怎麼抓才不會把 bug 藏起來？

**讀完你會知道：**

1. Python 怎麼判斷「真」和「假」，以及 `and` / `or` 其實回傳什麼
2. `match` 結構化模式比對：不只是 switch，還能「拆解資料」
3. `for` 迴圈背後的「迭代協定」，以及 `enumerate`、`zip` 等工具
4. `break`、`continue`，以及很少人懂的迴圈 `else`
5. 例外處理的完整結構與正確心態

---

## 1. 真值測試：什麼東西算「假」？

### 1.1 不只是 True 和 False

`if` 後面不一定要放 `True` 或 `False`，**任何東西都可以**。Python 會自動判斷它算真還是算假。

以下這些算**假** (falsy)，其他**全部**算真 (truthy)：

| 種類 | 算假的值 |
|---|---|
| 特殊值 | `None`、`False` |
| 數字的零 | `0`、`0.0`、`0j`、`Decimal(0)`、`Fraction(0)` |
| 空的容器 | `""`（空字串）、`[]`、`()`、`{}`、`set()`、`range(0)` |

**白話說：「零」和「空的」都算假，其他都算真。**

```python
for v in [0, 0.0, "", "0", " ", [], [0], {}, None, False, -1]:
    print(f"{v!r:>6} → {bool(v)}")
```

注意這幾個容易搞錯的：

- `"0"` 是**真**：它是一個「有內容」的字串，內容剛好是字元 0。
- `" "` 是**真**：一個空白也是內容。
- `[0]` 是**真**：串列裡有一個元素，雖然那個元素是 0。
- `-1` 是**真**：只有 0 是假，負數不是。

### 1.2 `if not x` 的陷阱

```python
def show_score(score=None):
    if not score:                      # ⚠️ 想判斷「沒有給分數」
        print("沒有分數")
    else:
        print("分數：", score)

show_score()       # 沒有分數 ✓
show_score(85)     # 分數：85 ✓
show_score(0)      # 沒有分數 ✗ 考 0 分也是分數！
```

`not 0` 是 `True`，所以 0 分被誤判成「沒有分數」。正確寫法是明確地問「是不是 None」：

```python
def show_score(score=None):
    if score is None:
        print("沒有分數")
    else:
        print("分數：", score)

show_score()
show_score(0)      # 分數：0 ✓
```

> ✅ **規則**：想問「是不是空的」用 `if not x`；想問「有沒有給值」用 `if x is None`。

---

## 2. 條件運算的細節

### 2.1 鏈式比較

數學上寫 `1 < x < 10`，Python 也可以直接這樣寫：

```python
x = 5
print(1 < x < 10)          # 等同 (1 < x) and (x < 10)
print(0 <= x <= 3)
score = 85
print(80 <= score < 90)    # 是不是 B 等級
```

### 2.2 `and` / `or` 回傳的不是 True/False

這是很多人不知道的：`and` 和 `or` **回傳的是其中一個運算元本身**，不一定是布林值。

| 運算 | 規則（白話） |
|---|---|
| `a or b` | a 是真的就回傳 **a**，否則回傳 **b** |
| `a and b` | a 是假的就回傳 **a**，否則回傳 **b** |

```python
print(0 or "預設值")        # '預設值'：0 是假，所以回傳右邊
print("小明" or "預設值")    # '小明'：左邊是真，直接回傳左邊
print("A" and "B")          # 'B'：左邊是真，回傳右邊
print(0 and "B")            # 0：左邊是假，直接回傳左邊
print([] or {} or "都空")    # 連續 or：回傳第一個真值
```

常見用法：**設定預設值**。

```python
nickname = ""
display_name = nickname or "匿名使用者"
print(display_name)
```

> ⚠️ 但同樣要小心「0 也是假」：`count = user_count or 10`，如果 `user_count` 是 0，就會被換成 10。

### 2.3 短路求值：右邊可能根本不會執行

`and` / `or` 一旦知道答案，就**不會再算右邊**。這叫「短路 (short-circuit)」。

```python
def expensive():
    print("  ← expensive() 被呼叫了")
    return True

print("1:", False and expensive())   # 左邊已經是假，整個一定是假 → 不呼叫
print("2:", True or expensive())     # 左邊已經是真，整個一定是真 → 不呼叫
print("3:", True and expensive())    # 左邊是真，要看右邊 → 才會呼叫
```

短路最實用的地方是**避免錯誤**：

```python
items = []
# 如果 items 是空的，items[0] 會 IndexError；
# 但因為短路，len(items) > 0 是 False 時，右邊根本不會執行
if len(items) > 0 and items[0] == "apple":
    print("第一個是蘋果")
else:
    print("沒有或不是蘋果")
```

### 2.4 三元運算式與海象運算子

**三元運算式**：一行寫完的 if-else。

```python
n = 7
kind = "偶數" if n % 2 == 0 else "奇數"
print(n, "是", kind)
```

**海象運算子 `:=`**（Python 3.8+）：在運算式中間**同時賦值**。名字由來是 `:=` 側過來看像海象的眼睛和牙齒。

```python
data = [3, 8, 1, 9, 4]
# 沒有海象：len 要算兩次，或多寫一行
if (n := len(data)) > 3:
    print(f"資料太多了：{n} 筆")

import re
text = "訂單編號：A1234，金額 500 元"
if (m := re.search(r"[A-Z]\d+", text)):
    print("找到編號：", m.group())
```

---

## 3. `match`：結構化模式比對（Python 3.10+）

### 3.1 先從最簡單的開始

如果你學過其他語言的 `switch`，`match` 最基本的用法很像：

```python
def http_status(code):
    match code:
        case 200:
            return "成功"
        case 404:
            return "找不到頁面"
        case 500 | 502 | 503:          # | 代表「或」
            return "伺服器錯誤"
        case _:                         # _ 代表「其他所有情況」
            return "未知狀態"

for c in [200, 404, 502, 418]:
    print(c, http_status(c))
```

### 3.2 真正強大的地方：拆解資料

`match` 不只能比對「值」，還能比對「**形狀**」，同時把裡面的東西**拆出來放進變數**。這是它和 switch 最大的差別。

想像你在寫一個文字冒險遊戲，玩家輸入的指令被切成串列：

```python
def run(command):
    match command.split():
        case ["quit"]:
            return "離開遊戲"
        case ["go", direction]:                  # 剛好兩個字，第一個是 go
            return f"往 {direction} 走"
        case ["pick", item]:
            return f"撿起 {item}"
        case ["pick", *items] if items:          # pick 後面有好幾個東西；if 是額外條件（guard）
            return f"撿起 {len(items)} 樣東西：{', '.join(items)}"
        case ["say", *words]:
            return "你說：" + " ".join(words)
        case []:
            return "（沒有輸入）"
        case _:
            return "看不懂這個指令"

for cmd in ["quit", "go north", "pick sword", "pick sword shield potion", "pick", "say hello world", "", "dance"]:
    print(f"{cmd!r:28} → {run(cmd)}")
```

讀 `case ["go", direction]:` 的方式：「如果這是一個**剛好有兩個元素**的序列，**第一個是 "go"**，那就把**第二個元素存進 direction**，然後執行底下的程式。」

### 3.3 各種模式一覽

```python
def describe(x):
    match x:
        case None:
            return "None"
        case bool():                              # 類別模式：型別是 bool（要寫在 int 前面！）
            return f"布林值 {x}"
        case int(n) if n < 0:                     # 型別是 int，且小於 0
            return f"負整數 {n}"
        case int() | float():
            return f"數字 {x}"
        case str() as s if len(s) == 0:           # as：把整個東西綁到 s
            return "空字串"
        case str():
            return f"字串（{len(x)} 個字）"
        case (a, b):                              # 長度為 2 的序列（tuple 或 list）
            return f"一對：{a} 和 {b}"
        case {"name": name, "age": age}:          # 字典模式：只檢查有沒有這些 key
            return f"人物：{name}，{age} 歲"
        case [first, *rest]:
            return f"串列，第一個是 {first}，後面還有 {len(rest)} 個"
        case _:
            return "其他"

for v in [None, True, -5, 3.14, "", "hi", (1, 2), {"name": "小明", "age": 18, "city": "台北"}, [9, 8, 7], {1, 2}]:
    print(f"{v!r:45} → {describe(v)}")
```

幾個重點：

- **字典模式只檢查你列出的 key**，多出來的 key（例如上面的 `city`）不影響比對。
- **字串不會被當成序列來拆**：`"go"` 不會匹配 `[a, b]`，這是刻意的設計，避免意外。
- **順序很重要**：由上往下，第一個符合的就執行，後面的不看了。`bool` 必須寫在 `int` 前面，因為 `True` 也是 `int`。

### 3.4 ⚠️ 最大的陷阱：裸名稱是「捕捉」，不是「比較」

```python
RED = "red"
color = "blue"

match color:
    case RED:                   # ⚠️ 你以為在比較 color == RED
        print("是紅色？？ RED 現在變成了", RED)
```

這段程式會印出「是紅色」，而且 `RED` 被改成了 `"blue"`！因為在 `case` 後面寫一個**普通的名稱**，意思是「**不管是什麼，都把它存進這個名稱**」——這叫捕捉模式，永遠會成功。

正確做法是用「帶點的名稱」（例如列舉 `Color.RED`）或字面值：

```python
from enum import Enum

class Color(Enum):
    RED = "red"
    BLUE = "blue"

color = Color.BLUE
match color:
    case Color.RED:             # 帶點的名稱 → 用 == 比較
        print("紅色")
    case Color.BLUE:
        print("藍色")
```

---

## 4. 迴圈

### 4.1 `for` 迴圈背後發生了什麼？

`for x in 東西:` 看起來很簡單，但背後有一套固定的流程，叫做**迭代協定**：

1. 呼叫 `iter(東西)`，取得一個「**迭代器 (iterator)**」——可以想成一個會記住「目前讀到哪」的書籤。
2. 不斷呼叫 `next(迭代器)` 拿下一個元素，放進 `x`，執行迴圈內容。
3. 當迭代器說「沒有了」（丟出 `StopIteration`），迴圈就結束。

我們可以手動做一次：

```python
fruits = ["蘋果", "香蕉"]
it = iter(fruits)          # 拿到書籤
print(next(it))            # 蘋果
print(next(it))            # 香蕉
try:
    next(it)               # 沒有了
except StopIteration:
    print("StopIteration：迭代結束")
```

**為什麼要知道這個？** 因為這說明了為什麼 `for` 可以走過 list、字串、字典、檔案、range……任何「能給出迭代器」的東西都行。單元四會教你自己做一個。

### 4.2 `range`：產生整數序列

```python
print(list(range(5)))           # [0, 1, 2, 3, 4]：從 0 開始，不包含 5
print(list(range(2, 8)))        # [2, 3, 4, 5, 6, 7]
print(list(range(10, 0, -3)))   # [10, 7, 4, 1]：可以倒著數
print(range(10**18)[-1])        # range 不會真的產生所有數字，所以很大也沒關係
```

### 4.3 好用的迴圈工具

**`enumerate`**：同時拿到「第幾個」和「元素」，不用自己維護計數器。

```python
names = ["小明", "小華", "小美"]

# ❌ 新手寫法
for i in range(len(names)):
    print(i, names[i])

# ✅ Pythonic 寫法
for i, name in enumerate(names, start=1):     # start=1 讓編號從 1 開始
    print(f"第 {i} 位：{name}")
```

**`zip`**：同時走過好幾個序列，像拉鍊一樣一對一對地配起來。

```python
names = ["小明", "小華", "小美"]
scores = [90, 75, 88]
for name, score in zip(names, scores):
    print(name, score)

print(list(zip("abc", [1, 2])))      # 長度不同時，以最短的為準（多的被丟掉！）
try:
    list(zip("abc", [1, 2], strict=True))    # 3.10+：長度不同就報錯，更安全
except ValueError as e:
    print("ValueError:", e)
```

**`sorted` 和 `reversed`**：

```python
scores = {"小明": 90, "小華": 75, "小美": 88}
for name in sorted(scores, key=scores.get, reverse=True):   # 依分數由高到低
    print(name, scores[name])
print(list(reversed([1, 2, 3])))
```

### 4.4 ⚠️ 不要一邊走一邊改

```python
nums = [1, 2, 2, 3, 2]
for x in nums:
    if x == 2:
        nums.remove(x)
print(nums)        # [1, 3, 2] ← 漏刪了一個！
```

**為什麼？** 迭代器內部記著「目前在第幾格」。刪掉第 1 格的 2 之後，後面的元素往前移一格，原本第 2 格的 2 跑到第 1 格，但迭代器下一步已經要看第 2 格了，於是跳過它。

正確做法是**建立一個新串列**：

```python
nums = [1, 2, 2, 3, 2]
nums = [x for x in nums if x != 2]
print(nums)
```

### 4.5 `while` 迴圈

`for` 適合「走過一堆東西」，`while` 適合「重複做直到某個條件不成立」，不知道要做幾次的情況：

```python
# 一個數字一直除以 2，幾次會變成 1 以下？
n = 1000
count = 0
while n > 1:
    n //= 2
    count += 1
print("除了", count, "次")
```

> ⚠️ `while` 最常見的 bug 是**忘記更新條件**，造成無窮迴圈。在本平台上，程式跑超過 10 秒會被自動中止。

### 4.6 `break`、`continue` 和迴圈的 `else`

- `break`：**立刻跳出**整個迴圈。
- `continue`：**跳過這一輪**剩下的部分，直接進下一輪。

```python
for n in range(1, 11):
    if n % 2 == 0:
        continue        # 偶數跳過
    if n > 7:
        break           # 超過 7 就結束
    print(n, end=" ")
print()
```

**迴圈的 `else`** 是 Python 特有的、很多人沒看過的語法。它的意思是：「**如果迴圈是正常跑完的（沒有被 break），就執行 else**」。

> 💡 **白話說**：把 `else` 讀成「**沒有 break 的話**」就對了。

它最適合用在「搜尋」：找到就 break，找不到就會進 else。

```python
def check_prime(n):
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            print(f"{n} 不是質數，可以被 {d} 整除")
            break
    else:
        print(f"{n} 是質數")      # 試完所有可能都沒 break → 沒有因數

check_prime(91)
check_prime(97)
```

如果沒有 `for-else`，你得額外設一個 `found = False` 的旗標變數，比較囉唆。

### 4.7 跳出多層迴圈

Python 沒有 `break 2` 這種語法。最乾淨的做法是：**把迴圈包進函式，用 `return` 直接離開**。

```python
def find(matrix, target):
    for r, row in enumerate(matrix):
        for c, value in enumerate(row):
            if value == target:
                return r, c          # 一次跳出兩層
    return None

grid = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(find(grid, 6), find(grid, 10))
```

---

## 5. 例外處理

### 5.1 例外是什麼？

程式執行時發生「沒辦法繼續」的狀況，例如除以零、把 `"abc"` 轉成整數、讀取不存在的檔案，Python 就會**丟出 (raise) 一個例外**。如果沒有人**接住 (catch)** 它，程式就會停下來並印出錯誤訊息。

```python
try:
    print(10 / 0)
except ZeroDivisionError as e:
    print("錯誤類型：", type(e).__name__)
    print("錯誤訊息：", e)
```

**讀錯誤訊息的技巧**：最後一行最重要（錯誤類型 + 原因），往上看是「怎麼走到這裡的」呼叫路徑，最下面那一層通常就是出錯的那一行。

### 5.2 完整結構：try / except / else / finally

```python
def parse_age(text):
    try:
        age = int(text)                      # 可能出錯的程式碼
    except ValueError:                       # 出錯時做什麼
        print(f"  {text!r} 不是數字")
        return None
    else:                                    # 沒出錯時才做（成功之後的事）
        print(f"  成功讀到 {age}")
        return age
    finally:                                 # 不管怎樣最後都做（通常用來清理資源）
        print("  （finally：檢查結束）")

parse_age("18")
parse_age("十八")
```

| 區塊 | 什麼時候執行 | 白話 |
|---|---|---|
| `try` | 一定先執行 | 「試試看」 |
| `except` | `try` 裡出了**符合類型**的錯 | 「如果出這種錯，就這樣處理」 |
| `else` | `try` **完全沒出錯** | 「成功的話，接著做這個」 |
| `finally` | **不管有沒有出錯、有沒有 return** | 「最後一定要收拾」 |

**為什麼需要 `else`？直接寫在 try 裡不行嗎？** 可以，但不好。`try` 區塊應該**只包住你預期可能出錯的那幾行**。如果把後續的程式碼也放進 `try`，那些程式碼出的錯也會被你的 `except` 接住，你可能就誤會了錯誤的來源。

### 5.3 例外的家族樹

例外是有「繼承關係」的。`except` 一個父類別，會連子類別一起接住：

```text
BaseException
 ├── SystemExit、KeyboardInterrupt  ← 程式要結束、使用者按 Ctrl+C（通常不該接！）
 └── Exception                      ← 一般錯誤都在這底下
      ├── ArithmeticError
      │    └── ZeroDivisionError, OverflowError
      ├── LookupError
      │    └── IndexError（串列索引超出）, KeyError（字典沒有這個 key）
      ├── ValueError（值不對，例如 int("abc")）
      ├── TypeError（型別不對，例如 "a" + 1）
      ├── AttributeError, NameError
      └── OSError
           └── FileNotFoundError ...
```

```python
data = {"a": 1}
for key in ["a", "b"]:
    try:
        print(data[key])
    except LookupError as e:            # KeyError 是 LookupError 的子類別，所以接得到
        print("找不到：", type(e).__name__, e)
```

**多個 except 時，子類別要寫在前面**，否則永遠輪不到它：

```python
try:
    [1, 2][5]
except IndexError:          # 比較具體的先寫
    print("索引超出範圍")
except LookupError:
    print("其他查找錯誤")
```

### 5.4 ⚠️ 不要這樣抓例外

```python
# ❌ 裸 except：連 Ctrl+C 都接住了，程式會變得關不掉
try:
    pass
except:
    pass

# ❌ 抓了什麼都不做：錯誤被默默吞掉，bug 會在很遠的地方用奇怪的形式出現
try:
    pass
except Exception:
    pass
```

> ✅ **原則**：只抓你**預期會發生**、而且**知道怎麼處理**的例外。不知道怎麼處理的，就讓它往上丟。

### 5.5 自己丟出例外

當你的函式收到不合理的輸入，**主動丟出例外**比默默回傳一個奇怪的值好得多：

```python
class InsufficientFunds(Exception):     # 自訂例外：繼承 Exception 就好
    pass

def withdraw(balance, amount):
    if amount <= 0:
        raise ValueError(f"金額必須為正數，收到 {amount}")
    if amount > balance:
        raise InsufficientFunds(f"餘額 {balance} 不足以提領 {amount}")
    return balance - amount

for amt in [30, 500, -1]:
    try:
        print("提領後餘額：", withdraw(100, amt))
    except (ValueError, InsufficientFunds) as e:   # 用 tuple 一次接多種
        print(f"{type(e).__name__}：{e}")
```

在 `except` 裡面再丟出另一個例外時，用 `raise ... from e` 保留原本的原因，除錯時才看得到完整脈絡：

```python
def load_config(d):
    try:
        return d["port"]
    except KeyError as e:
        raise RuntimeError("設定檔缺少 port 欄位") from e

try:
    load_config({})
except RuntimeError as e:
    print(e, "← 原因：", repr(e.__cause__))
```

### 5.6 EAFP vs LBYL：兩種寫程式的心態

| | LBYL（Look Before You Leap） | EAFP（Easier to Ask Forgiveness than Permission） |
|---|---|---|
| 意思 | 先檢查，再做 | 直接做，出錯再處理 |
| 白話 | 先確認有沒有，再拿 | 直接拿，拿不到再說 |
| 範例 | `if key in d: v = d[key]` | `try: v = d[key] except KeyError: ...` |

```python
stock = {"蘋果": 5}

# LBYL
if "香蕉" in stock:
    print(stock["香蕉"])
else:
    print("沒有香蕉（LBYL）")

# EAFP
try:
    print(stock["香蕉"])
except KeyError:
    print("沒有香蕉（EAFP）")

# 這個情境其實有更簡單的寫法：
print(stock.get("香蕉", 0))
```

Python 社群偏好 EAFP，原因有二：
1. 主要邏輯比較清楚，不會被一堆 `if` 打斷。
2. 避免「**檢查和使用之間情況改變了**」的問題。例如你檢查檔案存在，下一刻被別的程式刪掉了，你去開檔還是會失敗。

---

## 6. 本章小結

| 觀念 | 一句話記住 |
|---|---|
| 真值 | 「零」和「空的」是假，其他都是真 |
| `if not x` vs `is None` | 0 和空字串也會被 `not` 當成假 |
| `and` / `or` | 回傳的是運算元本身，而且會短路 |
| `match` | 能比對「形狀」並拆出資料；裸名稱是捕捉不是比較 |
| `for` | 背後是 `iter()` + `next()`；不要一邊走一邊改 |
| `enumerate` / `zip` | 取代 `range(len(...))`；`zip` 以最短的為準 |
| 迴圈 `else` | 讀成「沒有 break 的話」 |
| 例外 | 只抓預期且能處理的；`try` 只包會出錯的那幾行 |

### 常見錯誤速查

1. `if not score` 把 0 分當成沒有分數。
2. `case RED:` 永遠匹配，而且會蓋掉 `RED`。
3. 迭代串列時 `remove` 元素，會跳過下一個。
4. 裸 `except:` 讓程式關不掉，`except Exception: pass` 把 bug 藏起來。
5. `finally` 裡寫 `return`，會蓋掉 try 的回傳值，甚至吞掉例外。
