# 單元三：資料結構

> **這個單元要解決的問題**：同樣是「存一堆資料」，選錯容器可能讓程式慢上一千倍。例如「檢查某個值在不在裡面」，用 list 要一個一個比，用 set 幾乎是瞬間完成。
> 這個單元不只教你怎麼用 list、dict、set，更要讓你知道**它們底層長什麼樣子**，這樣你才能判斷什麼情況該用哪個。

**讀完你會知道：**

1. 什麼是「時間複雜度」，以及怎麼用它判斷程式快不快
2. list 的底層是什麼、哪些操作快、哪些操作慢
3. 淺拷貝和深拷貝的差別（二維陣列的經典 bug）
4. tuple 和「解包」的各種技巧
5. dict 和 set 為什麼那麼快：雜湊表的原理
6. `collections`、`heapq`、`bisect` 這些進階工具什麼時候用
7. 排序的 `key` 參數和「穩定排序」

---

## 0. 先備知識：時間複雜度（Big-O）白話版

**時間複雜度**描述的是：「**資料量變大時，執行時間會怎麼成長？**」

| 寫法 | 名稱 | 白話 | 例子 | 資料 10 倍，時間約… |
|---|---|---|---|---|
| O(1) | 常數 | 不管資料多少，一下就好 | 用索引拿 list 的元素 | 不變 |
| O(log n) | 對數 | 每次砍一半 | 在排好序的資料中二分搜尋 | 多一點點 |
| O(n) | 線性 | 每個資料看一次 | 在 list 中找某個值 | 10 倍 |
| O(n log n) | | 好的排序法 | `sorted()` | 約 10 多倍 |
| O(n²) | 平方 | 每兩個資料都比一次 | 兩層迴圈 | **100 倍** |

假設 n = 10 萬：O(n) 大約是 10 萬次運算，瞬間完成；O(n²) 是 100 億次，在瀏覽器裡要跑好幾分鐘。**練習題裡標成「壓力」的測資，就是用來分辨你的寫法是 O(n) 還是 O(n²)。**

---

## 1. list：會自動長大的陣列

### 1.1 底層長什麼樣子？

list 底層是一排**連續的格子**，每一格存一個「指向物件的箭頭」（記得單元一說的：變數是標籤，list 裡存的也是標籤）。

```text
索引:     0      1      2      3
       ┌──────┬──────┬──────┬──────┬ ─ ─ ─ ─ ┐
       │  ●   │  ●   │  ●   │  ●   │ (預留空間)
       └──┼───┴──┼───┴──┼───┴──┼───┴ ─ ─ ─ ─ ┘
          ▼      ▼      ▼      ▼
         10    "hi"   3.14   [1,2]
```

因為格子是連續的，**知道索引就能直接算出位置**，所以 `lst[i]` 是 O(1)，不管 list 多長都一樣快。

list 會**多預留一些空格**。`append` 時如果還有空格，直接放進去就好；空格用完時，才一次搬到一塊更大的空間。所以 `append` 平均起來是 O(1)。

```python
import sys
lst = []
prev = sys.getsizeof(lst)
print(f"空 list 佔 {prev} bytes")
for i in range(30):
    lst.append(i)
    size = sys.getsizeof(lst)
    if size != prev:
        print(f"放進第 {len(lst):2d} 個元素時擴充：{prev} → {size} bytes")
        prev = size
```

可以看到它不是每次都擴充，而是空間不夠時一次多要一些。

### 1.2 哪些操作快、哪些慢？

| 操作 | 複雜度 | 為什麼 |
|---|---|---|
| `lst[i]`、`lst[i] = x`、`len(lst)` | O(1) | 直接算出位置 |
| `lst.append(x)`、`lst.pop()` | O(1) | 只動尾巴 |
| `lst.insert(0, x)`、`lst.pop(0)` | **O(n)** | 開頭插入/刪除，**後面全部要往後/往前挪一格** |
| `x in lst`、`lst.index(x)`、`lst.remove(x)` | **O(n)** | 只能從頭一個一個比 |
| `lst.sort()` | O(n log n) | |
| `lst[a:b]` | O(b−a) | 切片會**複製**出新的 list |

> 💡 **白話說**：list 是「排隊的隊伍」。從隊尾加人、離開很快；但從隊伍最前面插隊或離開，後面每個人都得移動一步。要找「小明在不在隊伍裡」，只能從頭一個一個問。

實際感受一下差異：

```python
import time
from collections import deque

n = 50_000
lst = list(range(n))
t0 = time.perf_counter()
while lst:
    lst.pop(0)              # 每次從開頭拿 → O(n)，總共 O(n²)
t1 = time.perf_counter()

dq = deque(range(n))
while dq:
    dq.popleft()            # deque 從開頭拿 → O(1)
t2 = time.perf_counter()
print(f"list.pop(0)：{(t1 - t0) * 1000:.1f} ms")
print(f"deque.popleft()：{(t2 - t1) * 1000:.1f} ms")
```

### 1.3 淺拷貝 vs 深拷貝：二維陣列的經典 bug

想建立一個 3×3 的格子，很多人會這樣寫：

```python
grid = [[0] * 3] * 3
grid[0][0] = 1
print(grid)       # [[1, 0, 0], [1, 0, 0], [1, 0, 0]] ← 三列一起變了！
```

**為什麼？** `[0] * 3` 做出一個 list `[0, 0, 0]`。外面的 `* 3` 是把「**指向這個 list 的箭頭**」複製三次，所以三列其實是**同一個** list。

```text
grid ──► [ ● , ● , ● ]
           │   │   │
           └───┼───┘
               ▼
          [0, 0, 0]     ← 只有一個！
```

正確寫法是用串列推導式，每一列都**重新做一個**：

```python
grid = [[0] * 3 for _ in range(3)]    # 迴圈跑 3 次，每次都建立一個新的 [0, 0, 0]
grid[0][0] = 1
print(grid)
print(grid[0] is grid[1])             # False：三列是不同的物件
```

> 💡 為什麼內層的 `[0] * 3` 沒問題？因為 0 是整數，不可變。三個格子指向同一個 0 無所謂，你改 `grid[0][0] = 1` 時是把那一格**重新指向** 1，而不是把 0「改成」1。

**拷貝的三種程度**：

```python
import copy
a = [[1, 2], [3, 4]]

b = a                    # 根本沒複製：b 和 a 是同一個
c = a.copy()             # 淺拷貝：外層是新的，裡面的小 list 還是共用（同 a[:]、list(a)）
d = copy.deepcopy(a)     # 深拷貝：一路往下全部複製

a[0].append(99)          # 修改內層
a.append([5])            # 修改外層
print("a:", a)
print("b:", b)           # 全部都跟著變
print("c:", c)           # 外層沒變（沒有 [5]），但內層的 99 跟著變了
print("d:", d)           # 完全獨立
```

| | 外層 | 內層 |
|---|---|---|
| `b = a` | 共用 | 共用 |
| `c = a.copy()`（淺拷貝） | **獨立** | 共用 |
| `d = copy.deepcopy(a)`（深拷貝） | **獨立** | **獨立** |

---

## 2. tuple：不可變的序列

### 2.1 什麼時候用 tuple？

tuple 跟 list 很像，差別在於**建立後不能修改**。適合用在：

- **一組固定的資料**：座標 `(x, y)`、RGB 顏色 `(255, 0, 0)`、資料庫的一筆紀錄
- **當 dict 的 key 或放進 set**：list 不行，tuple 可以
- **函式回傳多個值**：`return a, b` 其實就是回傳一個 tuple

```python
point = 3, 4                  # 其實是「逗號」造出 tuple，括號只是為了清楚
print(type(point), point)
print(type((5)), type((5,)))  # ⚠️ (5) 只是數字 5 加括號；單元素 tuple 必須有逗號

distance = {(0, 0): "原點", (3, 4): "距離 5"}   # tuple 當 key
print(distance[(3, 4)])
```

### 2.2 解包 (unpacking)：一次拆開

```python
x, y = (3, 4)                 # 依序拆給 x 和 y
print(x, y)

a, b = 1, 2
a, b = b, a                   # 交換兩個變數：右邊先打包成 (2, 1)，再拆給 a, b
print(a, b)

first, *middle, last = [1, 2, 3, 4, 5]   # * 收集「剩下的」，而且一定是 list
print(first, middle, last)

head, *tail = "Python"
print(head, tail)

for name, (math, eng) in [("小明", (90, 80)), ("小華", (70, 95))]:   # 巢狀解包
    print(name, "總分", math + eng)
```

### 2.3 tuple 真的「完全不能改」嗎？

tuple 本身不能改（不能換掉裡面的元素），但如果它**裝了一個 list**，那個 list 自己是可以改的：

```python
t = ([1, 2], "abc")
t[0].append(3)           # 沒有換掉 t[0]，而是修改 t[0] 指向的那個 list
print(t)
try:
    t[0] = [9]           # 這才是「換掉」，不允許
except TypeError as e:
    print("TypeError:", e)
```

### 2.4 namedtuple：有名字的 tuple

`point[0]`、`point[1]` 不好讀，`point.x`、`point.y` 好多了：

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p, p.x, p.y)
print(p[0])                       # 還是可以用索引
x, y = p                          # 還是可以解包
print(p._replace(x=10))           # 不能改，但能做出一個「改了某欄位」的新 tuple
print(p._asdict())
```

---

## 3. dict：用 key 找 value 的雜湊表

### 3.1 為什麼 dict 這麼快？

如果用 list 存「名字 → 電話」，要找某人的電話就得一個一個比對名字，O(n)。dict 平均只要 **O(1)**，不管存了 10 筆還是 1000 萬筆，找一筆的時間差不多。

**原理（白話版）**：想像一個有很多抽屜的櫃子。

1. 要放資料時，先把 key 丟進一個「**雜湊函式**」，它會算出一個數字（雜湊值），例如 `hash("小明") → 8273645…`
2. 用這個數字決定放進**第幾個抽屜**
3. 要找的時候，再算一次雜湊值，**直接打開那個抽屜**，不用一個一個翻

```python
print(hash("小明"), hash("小明"))   # 同一個值，雜湊值一樣
print(hash("小華"))                 # 不同的值，雜湊值（幾乎一定）不同
print(hash(42), hash((1, 2)))
try:
    hash([1, 2])                    # list 不能算雜湊值
except TypeError as e:
    print("TypeError:", e)
```

**為什麼 list 不能當 key？** 如果 key 放進去之後內容被改了，它的雜湊值就變了，下次去找就會開錯抽屜，永遠找不到。所以 Python 規定：**只有不可變的東西才能當 key**。

### 3.2 基本操作

```python
phone = {"小明": "0912", "小華": "0988"}

phone["小美"] = "0955"              # 新增
phone["小明"] = "0911"              # 修改（key 已存在就覆蓋）
print(phone["小華"])                # 讀取
del phone["小華"]                   # 刪除
print(phone, len(phone), "小明" in phone)   # in 檢查的是 key

try:
    phone["阿呆"]                   # 不存在的 key → KeyError
except KeyError as e:
    print("KeyError:", e)
print(phone.get("阿呆"))            # get：不存在回傳 None，不會報錯
print(phone.get("阿呆", "查無此人"))  # 也可以指定預設值
```

### 3.3 走訪 dict

```python
scores = {"小明": 90, "小華": 75, "小美": 88}
for name in scores:                      # 預設走的是 key
    print(name, end=" ")
print()
for name, score in scores.items():       # 同時拿 key 和 value（最常用）
    print(f"{name}: {score}")
print(list(scores.keys()), list(scores.values()))
```

Python 3.7 起，dict **保證保留插入順序**。

### 3.4 實用技巧

```python
# 計數：get 的預設值
text = "banana"
count = {}
for ch in text:
    count[ch] = count.get(ch, 0) + 1
print(count)

# 合併兩個 dict（3.9+）：右邊的優先
default = {"color": "red", "size": "M"}
custom = {"size": "L"}
print(default | custom)

# dict 推導式
squares = {n: n * n for n in range(1, 6)}
print(squares)
inverse = {v: k for k, v in squares.items()}    # 反轉 key 和 value
print(inverse)
```

### 3.5 ⚠️ 兩個陷阱

**陷阱一：走訪時不能刪除 key。**

```python
stock = {"蘋果": 3, "香蕉": 0, "橘子": 0}
try:
    for k in stock:
        if stock[k] == 0:
            del stock[k]
except RuntimeError as e:
    print("RuntimeError:", e)

stock = {"蘋果": 3, "香蕉": 0, "橘子": 0}
stock = {k: v for k, v in stock.items() if v != 0}   # 正確：做一個新的
print(stock)
```

**陷阱二：`1`、`1.0`、`True` 是同一個 key。** 因為它們相等 (`==`) 而且雜湊值相同：

```python
d = {}
d[1] = "整數"
d[1.0] = "浮點數"
d[True] = "布林"
print(d)          # {1: '布林'}：只有一個 key！
```

---

## 4. set：不重複、查找超快的集合

set 就像「**只有 key、沒有 value 的 dict**」，底層一樣是雜湊表。特性：

- 元素**不會重複**
- **沒有順序**（不能用索引）
- `x in s` 是 O(1)

```python
nums = [3, 1, 3, 2, 1, 3]
unique = set(nums)
print(unique, len(unique))      # 去除重複

empty = set()                   # ⚠️ {} 是空的 dict，不是空的 set！
print(type({}), type(empty))
```

### 4.1 集合運算（跟數學一樣）

```python
python_class = {"小明", "小華", "小美", "阿強"}
java_class = {"小華", "阿強", "大雄"}

print("兩堂都修：", python_class & java_class)    # 交集
print("至少修一堂：", python_class | java_class)  # 聯集
print("只修 Python：", python_class - java_class) # 差集
print("只修其中一堂：", python_class ^ java_class) # 對稱差
print({"小明"} <= python_class)                   # 子集合
```

### 4.2 為什麼「查有沒有」要用 set？

```python
import time
n = 100_000
data_list = list(range(n))
data_set = set(data_list)
queries = range(n - 1000, n)

t0 = time.perf_counter()
hits = sum(q in data_list for q in queries)
t1 = time.perf_counter()
hits = sum(q in data_set for q in queries)
t2 = time.perf_counter()
print(f"list 查 1000 次：{(t1 - t0) * 1000:.1f} ms")
print(f"set  查 1000 次：{(t2 - t1) * 1000:.3f} ms")
```

> 💡 **去重又想保留順序？** set 不保證順序，用 `list(dict.fromkeys(lst))`。

```python
print(list(dict.fromkeys(["b", "a", "b", "c", "a"])))
```

---

## 5. 推導式：一行建立容器

**串列推導式**是「用一個迴圈建立 list」的簡寫：

```python
# 一般寫法
squares = []
for x in range(10):
    if x % 2 == 0:
        squares.append(x * x)
print(squares)

# 推導式：[ 要放什麼   for 變數 in 來源   if 條件 ]
squares = [x * x for x in range(10) if x % 2 == 0]
print(squares)
```

讀推導式的順序：**先看 `for`，再看 `if`，最後看最前面放什麼**。

```python
matrix = [[1, 2, 3], [4, 5, 6]]
flat = [v for row in matrix for v in row]          # 兩層：外層迴圈寫在前面
print(flat)
transposed = [list(col) for col in zip(*matrix)]   # 轉置：zip(*m) 把每一列拆開再一對一配
print(transposed)
words = ["apple", "Bob", "cat"]
print({w: len(w) for w in words})                  # dict 推導式
print({w[0].lower() for w in words})               # set 推導式
```

**產生器運算式**：把中括號改成小括號，就**不會真的建立 list**，而是需要時才一個一個產生。資料量大時很省記憶體：

```python
total = sum(x * x for x in range(1_000_000))   # 不會建立一個 100 萬個元素的 list
print(total)
```

> ⚠️ 推導式好用，但**不要寫得太複雜**。超過兩層迴圈或條件很複雜時，寫成一般迴圈比較好讀。

---

## 6. collections：標準庫的進階容器

### 6.1 Counter：計數器

```python
from collections import Counter

c = Counter("mississippi")
print(c)
print(c["s"], c["z"])               # 不存在的回傳 0，不會 KeyError
print(c.most_common(2))             # 出現最多的前 2 名

words = "the cat and the hat and the bat".split()
print(Counter(words).most_common(3))
print(Counter("aab") + Counter("bcc"))   # 可以相加
```

> ⚠️ `most_common()` 在次數相同時，**不保證字典序**（它依照第一次出現的順序）。如果題目要求「同次數依字母排序」，要自己用 `sorted` 處理。

### 6.2 defaultdict：自動建立預設值

```python
from collections import defaultdict

# 依開頭字母分組
groups = defaultdict(list)          # 存取不存在的 key 時，自動建立一個空 list
for word in ["apple", "avocado", "banana", "blueberry", "cherry"]:
    groups[word[0]].append(word)    # 不用先檢查 key 存不存在
print(dict(groups))

count = defaultdict(int)            # int() 會回傳 0，適合計數
for ch in "hello":
    count[ch] += 1
print(dict(count))
```

### 6.3 deque：兩頭都快的佇列

deque（唸作 "deck"）是 double-ended queue，**兩端加入、移除都是 O(1)**，適合做佇列（先進先出）和滑動視窗。

```python
from collections import deque

q = deque([1, 2, 3])
q.append(4)          # 右邊加
q.appendleft(0)      # 左邊加
print(q)
print(q.popleft(), q.pop(), q)   # 左邊拿、右邊拿

recent = deque(maxlen=3)          # 最多只保留 3 個，超過時自動從另一頭擠掉
for page in ["首頁", "商品", "購物車", "結帳"]:
    recent.append(page)
print("最近瀏覽：", list(recent))
```

---

## 7. heapq（優先佇列）與 bisect（二分搜尋）

### 7.1 heapq：一直拿最小的

**情境**：你有一堆工作，每次都要先做「優先度最高（數字最小）」的那個，而且工作會不斷加進來。如果每次都 `sort`，太慢了。

**堆積 (heap)** 是一種特殊的排列方式，保證**最小的永遠在第 0 個**，而且加入、取出都只要 O(log n)。

```python
import heapq

tasks = []
heapq.heappush(tasks, (2, "寫報告"))
heapq.heappush(tasks, (1, "修 bug"))
heapq.heappush(tasks, (3, "喝咖啡"))
heapq.heappush(tasks, (1, "回信"))
print("最急的：", tasks[0])
while tasks:
    priority, name = heapq.heappop(tasks)   # tuple 會先比第一個元素，相同再比第二個
    print(priority, name)

nums = [5, 1, 8, 3, 9, 2]
print(heapq.nlargest(3, nums), heapq.nsmallest(2, nums))
```

> 💡 heapq 只有「最小堆積」。要「每次拿最大的」，可以存負數：`heappush(h, -x)`，拿出來時再加負號。

### 7.2 bisect：在排好序的資料中找位置

```python
import bisect

# 分數 → 等第：60 以下 F、60~69 D、70~79 C、80~89 B、90 以上 A
cutoffs = [60, 70, 80, 90]
grades = "FDCBA"
for score in [55, 60, 75, 89, 90, 100]:
    print(score, grades[bisect.bisect_right(cutoffs, score)])

sorted_list = [1, 3, 5, 7]
bisect.insort(sorted_list, 4)     # 插入並保持排序
print(sorted_list)
print(bisect.bisect_left(sorted_list, 5))   # 5 應該放在第幾個位置
```

---

## 8. 排序：`key` 參數與穩定性

### 8.1 `sorted()` vs `.sort()`

```python
nums = [3, 1, 2]
new = sorted(nums)          # 回傳新的 list，原本的不變
print(nums, new)
nums.sort()                 # 就地排序，回傳 None
print(nums)

x = [3, 1, 2]
x = x.sort()                # ⚠️ 常見錯誤：x 變成 None 了
print(x)
```

### 8.2 `key`：告訴 Python「依照什麼排序」

`key` 是一個函式，Python 會對每個元素呼叫它，**依照回傳值排序**：

```python
words = ["banana", "Apple", "cherry", "date"]
print(sorted(words))                    # 預設：大寫字母排在小寫前面
print(sorted(words, key=str.lower))     # 不分大小寫
print(sorted(words, key=len))           # 依長度

students = [("小明", 85), ("小華", 92), ("小美", 85), ("阿強", 70)]
print(sorted(students, key=lambda s: s[1], reverse=True))   # 依分數由高到低
```

**多個條件排序**：讓 `key` 回傳一個 tuple，Python 會先比第一個，相同再比第二個。數字要「由大到小」可以加負號：

```python
students = [("小明", 85), ("小華", 92), ("小美", 85), ("阿強", 70)]
# 分數由高到低，同分時依名字排序
print(sorted(students, key=lambda s: (-s[1], s[0])))
```

### 8.3 穩定排序

Python 的排序是**穩定的 (stable)**：如果兩個元素的 key 一樣，它們會**保持原本的前後順序**。

```python
students = [("小明", 85), ("小華", 92), ("小美", 85), ("阿強", 70)]
by_score = sorted(students, key=lambda s: s[1])
print(by_score)       # 小明和小美都是 85，小明原本在前面，排完還是在前面
```

---

## 9. 該選哪一個？決策表

| 我想要… | 用這個 |
|---|---|
| 一串有順序的資料，會用索引存取 | `list` |
| 一組固定的資料、要當 dict 的 key | `tuple` / `namedtuple` |
| 用名字（key）查資料 | `dict` |
| 查 key 時不想處理「不存在」的情況 | `defaultdict` 或 `dict.get` |
| 去除重複、快速檢查「有沒有」 | `set` |
| 計算每個東西出現幾次 | `Counter` |
| 從兩頭加入/取出（佇列、滑動視窗） | `deque` |
| 一直需要拿最小（或最大）的 | `heapq` |
| 在排好序的資料中找位置 | `bisect` |

## 10. 本章小結

### 常見錯誤速查

1. `[[0] * 3] * 3` 三列共用同一個 list。
2. `list.pop(0)`、`insert(0, x)` 是 O(n)，大量使用請改用 `deque`。
3. 在大 list 中反覆 `x in lst` 是 O(n)，改用 `set`。
4. `{}` 是空 dict，空 set 要寫 `set()`。
5. `lst = lst.sort()` 會讓 lst 變成 None。
6. 走訪 dict 時刪除 key 會 RuntimeError。
7. `Counter.most_common()` 同次數時不依字母排序。
