from common import T, choice, exercise, md, qa

LESSON = md(r'''
# 單元三：資料結構

> 目標：知道每個內建容器「底層是什麼」、各操作的時間複雜度，以及何時該換用 `collections` / `heapq` / `bisect`。

## 1. list：動態陣列

`list` 底層是**連續的指標陣列**，空間不夠時以約 1.125 倍成長（攤銷 O(1) append）。

| 操作 | 複雜度 | 說明 |
|---|---|---|
| `lst[i]`、`lst[i] = x`、`len(lst)` | O(1) | |
| `append(x)`、`pop()` | 攤銷 O(1) | 尾端操作 |
| `insert(0, x)`、`pop(0)` | **O(n)** | 要搬移所有元素 → 改用 `deque` |
| `x in lst`、`lst.index(x)`、`remove(x)` | **O(n)** | 線性搜尋 → 改用 `set`/`dict` |
| `lst.sort()` | O(n log n) | Timsort，**穩定** |
| `lst[a:b]` | O(b−a) | 切片會複製 |

```python
import sys
lst = []
prev = sys.getsizeof(lst)
for i in range(20):
    lst.append(i)
    size = sys.getsizeof(lst)
    if size != prev:
        print(f"len={len(lst):2d} 容量擴充，記憶體 {prev} → {size} bytes")
        prev = size
```

### 1.1 淺拷貝 vs 深拷貝

```python
import copy
grid = [[0] * 3] * 3          # ⚠️ 三列是「同一個」list
grid[0][0] = 1
print(grid)

grid = [[0] * 3 for _ in range(3)]   # ✅ 每列獨立
grid[0][0] = 1
print(grid)

a = [[1, 2], [3, 4]]
b = a.copy()                  # 淺拷貝：外層新、內層共用（同 a[:]、list(a)）
c = copy.deepcopy(a)          # 深拷貝：遞迴複製
a[0].append(99)
print(b, c)
```

## 2. tuple：不可變序列與解包

```python
point = 3, 4                  # 逗號才是 tuple 的關鍵，括號只是分組
single = (5,)                 # 單元素 tuple 要有逗號
print(type(point), type((5)), type(single))

x, y = point                  # 解包
first, *middle, last = [1, 2, 3, 4, 5]
print(first, middle, last)
a, b = 1, 2
a, b = b, a                   # 交換：右邊先打包成 tuple 再解包
print(a, b)

for name, (lo, hi) in [("A", (1, 5)), ("B", (2, 8))]:   # 巢狀解包
    print(name, hi - lo)

# tuple 本身不可變，但它「裝的東西」可能可變
t = ([1], 2)
t[0].append(3)
print(t)
```

`namedtuple` / `typing.NamedTuple` 讓 tuple 有欄位名稱，可讀性好又省記憶體：

```python
from collections import namedtuple
Point = namedtuple("Point", "x y")
p = Point(1, 2)
print(p, p.x, p._replace(x=9), p._asdict())
```

## 3. dict：雜湊表

- 平均 O(1) 的查詢、插入、刪除；key 必須**可雜湊**。
- Python 3.7+ 保證**保留插入順序**。

```python
d = {"apple": 3, "banana": 5}
print(d.get("cherry"), d.get("cherry", 0))        # 不存在時不會 KeyError
d.setdefault("cherry", 0)                          # 不存在才設定
d["apple"] += 1
print(d)
print(list(d.keys()), list(d.values()), list(d.items()))

merged = d | {"apple": 100, "durian": 1}           # 3.9+ 合併，右邊優先
print(merged)

inverse = {v: k for k, v in d.items()}             # dict comprehension
print(inverse)

# 迭代時不能改變大小
try:
    for k in d:
        if d[k] == 0:
            del d[k]
except RuntimeError as e:
    print("RuntimeError:", e)
d = {k: v for k, v in d.items() if v != 0}         # 正確作法：建新 dict
print(d)
```

### 3.1 什麼可以當 key？

可雜湊 = 有 `__hash__` 且在生命週期內不變，並且 `a == b` 時 `hash(a) == hash(b)`。

```python
print(hash(1) == hash(1.0) == hash(True))   # True
d = {1: "int"}
d[1.0] = "float"
d[True] = "bool"
print(d)          # {1: 'bool'}  ← 三者相等，所以是同一個 key！
```

## 4. set：無序、不重複、O(1) 成員測試

```python
a, b = {1, 2, 3, 4}, {3, 4, 5}
print(a | b, a & b, a - b, a ^ b)
print({1, 2} <= a, a.isdisjoint({9}))
empty = set()             # 注意：{} 是空 dict！
print(type({}), type(empty))

words = ["b", "a", "b", "c", "a"]
print(list(dict.fromkeys(words)))   # 去重且保留順序（set 不保序）
```

成員測試效能比較：

```python
import time
n = 200_000
lst, st = list(range(n)), set(range(n))
t0 = time.perf_counter(); _ = [x in lst for x in range(n - 200, n)]; t1 = time.perf_counter()
_ = [x in st for x in range(n - 200, n)]; t2 = time.perf_counter()
print(f"list: {(t1 - t0) * 1000:.2f} ms, set: {(t2 - t1) * 1000:.3f} ms")
```

## 5. 推導式與產生器運算式

```python
squares = [x * x for x in range(10) if x % 2 == 0]
matrix = [[r * 3 + c for c in range(3)] for r in range(3)]
flat = [v for row in matrix for v in row]          # 巢狀：外層迴圈寫在前面
transposed = [list(col) for col in zip(*matrix)]
print(squares, matrix, flat, transposed, sep="\n")

total = sum(x * x for x in range(10**6))           # 產生器運算式：不建立中間 list
print(total)
```

## 6. collections 工具箱

```python
from collections import Counter, defaultdict, deque, OrderedDict

c = Counter("mississippi")
print(c.most_common(2), c["s"], c["z"])            # 不存在的 key 回傳 0
print(Counter("aab") + Counter("bc"), Counter("aab") - Counter("a"))

groups = defaultdict(list)                          # 不存在的 key 自動建立 list()
for word in ["apple", "avocado", "banana", "blueberry", "cherry"]:
    groups[word[0]].append(word)
print(dict(groups))

dq = deque([1, 2, 3], maxlen=5)                     # 雙端佇列：兩端 O(1)
dq.appendleft(0); dq.append(4); dq.append(5)        # 超過 maxlen 會從另一端擠掉
print(dq, dq.popleft())
dq.rotate(2)
print(dq)

od = OrderedDict.fromkeys("abc")
od.move_to_end("a")                                 # LRU 快取常用
print(list(od))
```

## 7. heapq（優先佇列）與 bisect（二分搜尋）

```python
import heapq
nums = [5, 1, 8, 3, 9, 2]
heapq.heapify(nums)                    # O(n) 建立最小堆積
print(heapq.heappop(nums), heapq.heappop(nums))
heapq.heappush(nums, 0)
print(nums[0])                         # 最小值永遠在 [0]
print(heapq.nlargest(3, [5, 1, 8, 3, 9, 2]), heapq.nsmallest(2, "python"))

tasks = []
heapq.heappush(tasks, (2, "寫報告"))
heapq.heappush(tasks, (1, "修 bug"))
heapq.heappush(tasks, (3, "喝咖啡"))
while tasks:
    print(heapq.heappop(tasks))        # tuple 依序比較：先比優先度

import bisect
scores = [60, 70, 80, 90]
grades = "FDCBA"
for s in [55, 60, 75, 90, 100]:
    print(s, grades[bisect.bisect_right(scores, s)])
sorted_list = [1, 3, 5]
bisect.insort(sorted_list, 4)
print(sorted_list, bisect.bisect_left(sorted_list, 3))
```

## 8. 排序的精髓：key 與穩定性

```python
from operator import itemgetter
people = [("Ann", 25), ("Bob", 30), ("Cy", 25), ("Dee", 30)]
print(sorted(people, key=itemgetter(1)))                 # 穩定：同齡保留原順序
print(sorted(people, key=lambda p: (-p[1], p[0])))       # 年齡遞減、名字遞增
print(sorted(["b", "A", "c"]), sorted(["b", "A", "c"], key=str.lower))

# 多鍵排序的另一招：利用穩定性，從「次要鍵」排到「主要鍵」
data = sorted(people, key=itemgetter(0), reverse=True)
data.sort(key=itemgetter(1))
print(data)
```

> `sorted()` 回傳新 list；`list.sort()` 就地排序並回傳 `None`。寫 `lst = lst.sort()` 會讓 lst 變成 None！

## 9. 選擇容器的決策表

| 需求 | 選擇 |
|---|---|
| 有序、可重複、依索引存取 | `list` |
| 固定內容、可當 key | `tuple` / `namedtuple` |
| 依 key 查值 | `dict`（預設值用 `defaultdict`） |
| 去重、成員測試 | `set` |
| 計數 | `Counter` |
| 兩端進出（佇列、滑動視窗） | `deque` |
| 一直取最小/最大 | `heapq` |
| 在有序序列中找位置 | `bisect` |
''')

QUIZ = [
    choice("`[[0]*2]*2` 執行 `g[0][0] = 1` 後，`g` 是？", ["`[[1,0],[0,0]]`", "`[[1,0],[1,0]]`", "`[[1,1],[0,0]]`", "`TypeError`"], 1,
           "外層 `*2` 複製的是「指向同一個內層 list 的參考」，兩列其實是同一個物件。"),
    choice("`{1: 'a', 1.0: 'b', True: 'c'}` 的結果是？", ["三個 key", "`{1: 'c'}`", "`{True: 'c'}`", "`TypeError`"], 1,
           "`1 == 1.0 == True` 且雜湊值相同，所以是同一個 key；key 保留第一次插入的物件 `1`，值被後來的覆蓋為 `'c'`。"),
    choice("從 list 開頭反覆 `pop(0)` 處理 n 個元素的總複雜度？", ["O(n)", "O(n log n)", "O(n²)", "O(1)"], 2,
           "每次 `pop(0)` 都要搬移剩餘元素，O(n) × n 次 = O(n²)。改用 `deque.popleft()` 是 O(1)。"),
    choice("`type({})` 是？", ["`set`", "`dict`", "`frozenset`", "`tuple`"], 1, "空的大括號是空 dict；空 set 要寫 `set()`。"),
    choice("`x = [3,1,2]; x = x.sort()` 之後 `x` 是？", ["`[1,2,3]`", "`[3,1,2]`", "`None`", "`TypeError`"], 2,
           "`list.sort()` 就地排序並回傳 `None`。"),
    choice("`heapq` 實作的是？", ["最大堆積", "最小堆積", "平衡二元搜尋樹", "雜湊表"], 1,
           "heapq 是最小堆積，`heap[0]` 為最小值；需要最大堆積時可存入負值，或用 `(-priority, item)`。"),
    choice("`first, *rest = 'abc'` 後 `rest` 是？", ["`'bc'`", "`['b', 'c']`", "`('b', 'c')`", "`SyntaxError`"], 1,
           "星號解包永遠產生 list。"),
    choice("Python 的 `sorted` 是穩定排序，意思是？", ["不會出錯", "相等的元素保持原本相對順序", "時間複雜度固定", "不修改原 list"], 1,
           "穩定性讓「多次排序實現多鍵排序」成為可能。"),
    qa("為什麼 list 不能當 dict 的 key，而 tuple 可以？如果 tuple 裡面有 list 呢？",
       "dict 依賴 key 的雜湊值決定存放位置，若 key 的內容改變，雜湊值改變就再也找不到了，所以 key 必須是不可變的（可雜湊）。\n\n"
       "tuple 只有在**所有元素都可雜湊**時才可雜湊：`hash((1, [2]))` 會 `TypeError: unhashable type: 'list'`。"),
    qa("說明淺拷貝與深拷貝的差異，並舉出會出問題的情境。",
       "淺拷貝（`lst.copy()`、`lst[:]`、`dict(d)`）只複製最外層容器，內部元素仍是同一批物件；"
       "深拷貝（`copy.deepcopy`）遞迴複製所有層。\n\n"
       "情境：複製二維棋盤 `board2 = board.copy()` 後修改 `board2[0][0]`，原 `board` 也會跟著變，因為各列是共用的。"),
    qa("要實作「最近最少使用 (LRU)」快取，你會選什麼資料結構？為什麼？",
       "`collections.OrderedDict`（或 Python 3.7+ 的一般 dict 加上刪除重插）：O(1) 查詢，"
       "存取時 `move_to_end(key)` 移到尾端，超過容量時 `popitem(last=False)` 刪除最舊的。"
       "標準庫也直接提供 `functools.lru_cache` 裝飾器。"),
]

EXERCISES = [
    exercise(
        "d1-topk", "字頻統計 Top-K", 2,
        r'''
        第一行為整數 `k`（0 ≤ k ≤ 1000）。之後的**所有行**（直到輸入結束，可能 0 行）都是文章內容。

        「單字」定義為連續的英文字母 `a-z`（不分大小寫，一律轉小寫），其他字元都是分隔符號。

        輸出出現次數最多的前 `k` 個單字，每行 `單字 次數`。排序規則：**次數遞減，次數相同時依字典序遞增**。
        不同單字數少於 `k` 時，全部輸出。

        ### 輸入範例
        ```text
        2
        the cat and the hat.
        The END and
        ```
        ### 輸出範例
        ```text
        the 3
        and 2
        ```
        ''',
        r'''
        import sys
        k = int(input())
        text = sys.stdin.read()
        ''',
        r'''
        import re
        import sys
        from collections import Counter

        k = int(input())
        words = re.findall(r"[a-z]+", sys.stdin.read().lower())
        for w, c in sorted(Counter(words).items(), key=lambda kv: (-kv[1], kv[0]))[:k]:
            print(w, c)
        ''',
        [
            T("2\nthe cat and the hat.\nThe END and\n", tag="sample", expect="the 3\nand 2"),
            T("3\n", tag="corner", note="沒有文章", expect=""),
            T("0\nhello hello\n", tag="corner", note="k = 0", expect=""),
            T("10\nb a c\n", tag="corner", note="k 大於單字數；全部同頻 → 字典序", expect="a 1\nb 1\nc 1"),
            T("2\nDon't stop-me now!!\n", tag="corner", note="撇號、連字號都是分隔符", expect="don 1\nme 1"),
            T("1\n123 456 ... !!!\n", tag="corner", note="完全沒有字母", expect=""),
            T("3\nApple apple APPLE banana Banana cherry\n", note="大小寫視為相同", expect="apple 3\nbanana 2\ncherry 1"),
            T("2\ncafé naïve\n", tag="corner", note="非 ASCII 字母也是分隔符", expect="caf 1\nna 1"),
            T("2\n\n\nzebra\n\nyak zebra\n\n", tag="corner", note="空行", expect="zebra 2\nyak 1"),
            T("5\n" + " ".join(f"w{'abcdefghij'[i % 10]}{'abcdefghij'[i // 10 % 10]}" for i in range(100000)) + "\n",
              tag="stress", note="10 萬個字"),
        ],
        gen=r'''
        def gen(rng):
            vocab = ["the", "a", "cat", "Dog", "it's", "x-y", "ZZ", "be"]
            lines = [" ".join(rng.choice(vocab) for _ in range(rng.randint(0, 8))) for _ in range(rng.randint(0, 4))]
            return f"{rng.randint(0, 6)}\n" + "".join(l + "\n" for l in lines)
        ''',
        hints=["`re.findall(r'[a-z]+', text.lower())`", "`Counter(words)` 計數。",
               "`Counter.most_common()` 同次數時不會依字典序，要自己 `sorted(key=lambda kv: (-kv[1], kv[0]))`。"],
        wrong=[r'''
        import re, sys
        from collections import Counter
        k = int(input())
        for w, c in Counter(re.findall(r"[a-z]+", sys.stdin.read().lower())).most_common(k):
            print(w, c)
        '''],
    ),
    exercise(
        "d2-intervals", "合併區間", 2,
        r'''
        第一行為 `n`（0 ≤ n ≤ 10⁵），接下來 `n` 行各有兩個整數 `l r`，代表閉區間 `[l, r]`（−10⁹ ≤ l, r ≤ 10⁹）。
        **注意：輸入可能 `l > r`，此時視為 `[r, l]`。** 區間未排序。

        將所有**重疊或端點相接**（例如 `[1,3]` 與 `[3,5]`）的區間合併，依起點遞增輸出每個合併後的區間 `l r`。

        > `[1,2]` 與 `[3,4]` **不**合併（中間有空隙 2~3）。

        ### 輸入範例
        ```text
        4
        8 10
        1 3
        2 6
        15 18
        ```
        ### 輸出範例
        ```text
        1 6
        8 10
        15 18
        ```
        ''',
        r'''
        n = int(input())
        ''',
        r'''
        import sys
        data = sys.stdin.read().split()
        n = int(data[0])
        iv = sorted(tuple(sorted((int(data[1 + 2 * i]), int(data[2 + 2 * i])))) for i in range(n))
        merged = []
        for l, r in iv:
            if merged and l <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], r)
            else:
                merged.append([l, r])
        print("\n".join(f"{l} {r}" for l, r in merged))
        ''',
        [
            T("4\n8 10\n1 3\n2 6\n15 18\n", tag="sample", expect="1 6\n8 10\n15 18"),
            T("0\n", tag="corner", note="沒有區間", expect=""),
            T("1\n5 5\n", tag="corner", note="單點區間", expect="5 5"),
            T("2\n1 3\n3 5\n", tag="corner", note="端點相接要合併", expect="1 5"),
            T("2\n1 2\n3 4\n", tag="corner", note="有空隙不合併", expect="1 2\n3 4"),
            T("3\n1 10\n2 3\n4 5\n", tag="corner", note="大區間包住小區間：右端要取 max", expect="1 10"),
            T("2\n5 1\n7 6\n", tag="corner", note="l > r 要交換", expect="1 5\n6 7"),
            T("3\n-5 -1\n-3 2\n-10 -8\n", tag="corner", note="負數", expect="-10 -8\n-5 2"),
            T("3\n4 4\n4 4\n4 4\n", tag="corner", note="完全相同的區間", expect="4 4"),
            T("2\n-1000000000 1000000000\n0 0\n", tag="corner", note="極值"),
            T("100000\n" + "".join(f"{i * 3} {i * 3 + (2 if i % 7 else 3)}\n" for i in range(100000)), tag="stress", note="10 萬個區間"),
        ],
        gen=r'''
        def gen(rng):
            n = rng.randint(0, 8)
            return f"{n}\n" + "".join(f"{rng.randint(-10, 10)} {rng.randint(-10, 10)}\n" for _ in range(n))
        ''',
        hints=["先排序再一次掃描：O(n log n)。", "合併時右端點取 `max`，因為可能被包含。"],
        wrong=[r'''
        n = int(input())
        iv = sorted(tuple(map(int, input().split())) for _ in range(n))
        merged = []
        for l, r in iv:
            if merged and l <= merged[-1][1]:
                merged[-1][1] = r
            else:
                merged.append([l, r])
        for l, r in merged:
            print(l, r)
        '''],
    ),
    exercise(
        "d3-twosum", "兩數之和（雜湊表）", 2,
        r'''
        第一行為 `n target`（1 ≤ n ≤ 2×10⁵），第二行為 `n` 個整數 `a[0..n-1]`。

        找出索引 `i < j` 使得 `a[i] + a[j] == target`。若有多組解，取 **`j` 最小**的；`j` 相同時取 **`i` 最小**的。
        輸出 `i j`（0-based），找不到輸出 `-1`。

        ### 輸入範例
        ```text
        5 9
        2 7 11 15 2
        ```
        ### 輸出範例
        ```text
        0 1
        ```

        > n 可達 2×10⁵，O(n²) 的雙重迴圈會逾時。
        ''',
        r'''
        n, target = map(int, input().split())
        a = list(map(int, input().split()))
        ''',
        r'''
        n, target = map(int, input().split())
        a = list(map(int, input().split()))
        first = {}
        for j, v in enumerate(a):
            if target - v in first:
                print(first[target - v], j)
                break
            first.setdefault(v, j)
        else:
            print(-1)
        ''',
        [
            T("5 9\n2 7 11 15 2\n", tag="sample", expect="0 1"),
            T("1 4\n2\n", tag="corner", note="只有一個數，不能自己加自己", expect="-1"),
            T("2 6\n3 3\n", tag="corner", note="相同的值", expect="0 1"),
            T("3 6\n3 1 2\n", tag="corner", note="不能重複使用同一個索引", expect="-1"),
            T("5 4\n2 1 2 3 2\n", tag="corner", note="多個 2：取 j 最小、i 最小", expect="0 2"),
            T("4 4\n1 1 3 3\n", tag="corner", note="j=2 時 i 可以是 0 或 1，取 0", expect="0 2"),
            T("4 -3\n-1 -2 5 0\n", tag="corner", note="負數", expect="0 1"),
            T("3 0\n0 5 0\n", tag="corner", note="目標 0", expect="0 2"),
            T("4 100\n1 2 3 4\n", note="無解", expect="-1"),
            T("2 2000000000\n1000000000 1000000000\n", tag="corner", note="大數"),
            T("200000 -1\n" + " ".join(str(i) for i in range(200000)) + "\n", tag="stress", note="無解的大量資料"),
            T("200000 399997\n" + " ".join(str(i) for i in range(200000)) + "\n", tag="stress", note="答案在最後面"),
        ],
        gen=r'''
        def gen(rng):
            n = rng.randint(1, 10)
            a = [rng.randint(-5, 5) for _ in range(n)]
            return f"{n} {rng.randint(-6, 6)}\n" + " ".join(map(str, a)) + "\n"
        ''',
        hints=["用 dict 記錄「值 → 第一次出現的索引」。", "先查詢 `target - v` 再存入 `v`，避免自己配自己。",
               "`setdefault` 只在 key 不存在時寫入，保留最小索引。"],
        wrong=[r'''
        n, target = map(int, input().split())
        a = list(map(int, input().split()))
        seen = {}
        for j, v in enumerate(a):
            if target - v in seen:
                print(seen[target - v], j)
                break
            seen[v] = j
        else:
            print(-1)
        '''],
    ),
    exercise(
        "d4-brackets", "括號配對（堆疊）", 2,
        r'''
        第一行為 `T`，接下來 `T` 行字串（**可能是空行**），字串可能包含 `()[]{}` 以及其他任意字元（其他字元忽略）。

        對每行判斷括號是否正確配對：
        - 正確：輸出 `YES`
        - 遇到無法配對的右括號：輸出 `NO p`，`p` 為該右括號的位置（**1-based**，以字元計算）
        - 掃描完畢仍有未閉合的左括號：輸出 `NO p`，`p` 為**最早**那個未閉合左括號的位置

        ### 輸入範例
        ```text
        4
        a(b[c]{d}e)f
        ([)]
        ((x)
        ]
        ```
        ### 輸出範例
        ```text
        YES
        NO 3
        NO 1
        NO 1
        ```
        ''',
        r'''
        t = int(input())
        for _ in range(t):
            s = input()
        ''',
        r'''
        PAIRS = {")": "(", "]": "[", "}": "{"}

        def check(s):
            stack = []
            for i, ch in enumerate(s, 1):
                if ch in "([{":
                    stack.append((ch, i))
                elif ch in PAIRS:
                    if not stack or stack[-1][0] != PAIRS[ch]:
                        return f"NO {i}"
                    stack.pop()
            return f"NO {stack[0][1]}" if stack else "YES"

        t = int(input())
        for _ in range(t):
            print(check(input()))
        ''',
        [
            T("4\na(b[c]{d}e)f\n([)]\n((x)\n]\n", tag="sample", expect="YES\nNO 3\nNO 1\nNO 1"),
            T("1\n\n", tag="corner", note="空字串", expect="YES"),
            T("1\nhello world\n", tag="corner", note="沒有括號", expect="YES"),
            T("1\n(\n", tag="corner", note="單一左括號", expect="NO 1"),
            T("1\n)(\n", tag="corner", note="先右後左", expect="NO 1"),
            T("1\n(()\n", tag="corner", note="未閉合：回報最早的位置 1，不是 2", expect="NO 1"),
            T("1\n()(()\n", tag="corner", note="前面配對完成後才有未閉合", expect="NO 3"),
            T("1\n{[()()]}\n", note="多層巢狀", expect="YES"),
            T("1\n([]{})]\n", tag="corner", note="多一個右括號", expect="NO 7"),
            T("1\n中文（全形括號）不算\n", tag="corner", note="全形括號不是括號", expect="YES"),
            T("2\n" + "(" * 50000 + ")" * 50000 + "\n" + "[" * 50000 + "]" * 49999 + "\n", tag="stress", note="深度 5 萬"),
        ],
        gen=r'''
        def gen(rng):
            lines = ["".join(rng.choice("()[]{}a") for _ in range(rng.randint(0, 10))) for _ in range(rng.randint(1, 5))]
            return f"{len(lines)}\n" + "".join(l + "\n" for l in lines)
        ''',
        hints=["堆疊中同時存「括號字元」與「位置」。", "結束時堆疊底部 `stack[0]` 就是最早未閉合的左括號。"],
        wrong=[r'''
        t = int(input())
        for _ in range(t):
            s = input()
            stack = []
            ans = "YES"
            for i, ch in enumerate(s, 1):
                if ch in "([{":
                    stack.append(i)
                elif ch in ")]}":
                    if not stack:
                        ans = f"NO {i}"
                        break
                    stack.pop()
            else:
                if stack:
                    ans = f"NO {stack[-1]}"
            print(ans)
        '''],
    ),
    exercise(
        "d5-window", "滑動視窗最大值（deque）", 3,
        r'''
        第一行為 `n k`（1 ≤ k ≤ n ≤ 2×10⁵），第二行為 `n` 個整數。

        輸出每個長度為 `k` 的連續視窗中的最大值（共 `n − k + 1` 個），以空白分隔在同一行。

        ### 輸入範例
        ```text
        8 3
        1 3 -1 -3 5 3 6 7
        ```
        ### 輸出範例
        ```text
        3 3 5 5 6 7
        ```

        > 要求 O(n)。對每個視窗呼叫 `max()` 是 O(nk)，在 n = k/2 = 10⁵ 時會逾時。
        ''',
        r'''
        from collections import deque
        n, k = map(int, input().split())
        a = list(map(int, input().split()))
        ''',
        r'''
        from collections import deque

        n, k = map(int, input().split())
        a = list(map(int, input().split()))
        dq = deque()          # 存索引，對應的值單調遞減
        out = []
        for i, v in enumerate(a):
            while dq and a[dq[-1]] <= v:
                dq.pop()
            dq.append(i)
            if dq[0] <= i - k:
                dq.popleft()
            if i >= k - 1:
                out.append(a[dq[0]])
        print(*out)
        ''',
        [
            T("8 3\n1 3 -1 -3 5 3 6 7\n", tag="sample", expect="3 3 5 5 6 7"),
            T("1 1\n42\n", tag="corner", note="最小輸入", expect="42"),
            T("5 1\n5 -1 3 0 2\n", tag="corner", note="k = 1：原樣輸出", expect="5 -1 3 0 2"),
            T("5 5\n5 -1 3 0 9\n", tag="corner", note="k = n：只有一個視窗", expect="9"),
            T("6 2\n6 5 4 3 2 1\n", tag="corner", note="遞減：最大值要正確過期", expect="6 5 4 3 2"),
            T("6 3\n1 2 3 4 5 6\n", tag="corner", note="遞增", expect="3 4 5 6"),
            T("5 2\n7 7 7 7 7\n", tag="corner", note="全部相同", expect="7 7 7 7"),
            T("4 2\n-5 -9 -1 -7\n", tag="corner", note="全負數", expect="-5 -1 -1"),
            T("200000 100000\n" + " ".join(str((i * 7919) % 100003) for i in range(200000)) + "\n", tag="stress", note="O(nk) 會逾時"),
        ],
        gen=r'''
        def gen(rng):
            n = rng.randint(1, 12)
            return f"{n} {rng.randint(1, n)}\n" + " ".join(str(rng.randint(-9, 9)) for _ in range(n)) + "\n"
        ''',
        hints=["deque 裡存「索引」，並維持對應值單調遞減。", "新值進來前，把隊尾比它小（或相等）的都丟掉——它們永遠不會再是最大值。",
               "隊首索引超出視窗就 `popleft()`。"],
        wrong=[r'''
        n, k = map(int, input().split())
        a = list(map(int, input().split()))
        print(*[max(a[i:i + k]) for i in range(n - k)])
        '''],
    ),
]

UNIT = {
    "id": "datastruct", "num": 3, "title": "資料結構", "icon": "🧱",
    "summary": "list/tuple/dict/set 底層與複雜度、拷貝、collections、heapq、bisect、排序",
    "lesson": LESSON, "quiz": QUIZ, "exercises": EXERCISES,
}
