# 單元四：函式定義

> **這個單元要解決的問題**：函式不只是「把程式碼包起來重複使用」。在 Python 裡，函式本身也是一個物件，可以傳來傳去、放進變數、從另一個函式產生出來。理解這一點，你才能看懂裝飾器 (`@xxx`)、閉包、產生器這些「進階」寫法，它們在框架和函式庫裡隨處可見。
> 這個單元也會解釋幾個經典陷阱：為什麼預設參數用 `[]` 會出事？為什麼迴圈裡建立的 lambda 全部回傳同一個值？

**讀完你會知道：**

1. 函式是「一等公民」是什麼意思
2. 參數的五種寫法，以及 `/` 和 `*` 的用途
3. 預設參數的陷阱和正確寫法
4. Python 怎麼找變數（LEGB 規則）、`global` 和 `nonlocal`
5. 閉包：讓函式「記住」東西
6. 裝飾器：不改原函式也能幫它加功能
7. 產生器：需要時才算，處理大量資料的利器
8. 遞迴的限制與快取

---

## 1. 函式是物件

### 1.1 定義和呼叫

```python
def greet(name):
    """回傳一句問候語。"""          # 第一行字串是「文件字串 docstring」，說明這個函式做什麼
    return f"哈囉，{name}！"

print(greet("小明"))
print(greet.__doc__)

def no_return():
    x = 1 + 1                      # 沒有 return
print(no_return())                 # 沒寫 return 的函式會回傳 None
```

### 1.2 「一等公民」：函式可以像資料一樣被使用

「一等公民 (first-class)」的意思是：**函式跟數字、字串一樣是物件**，所以可以：

```python
def shout(text):
    return text.upper() + "!"

def whisper(text):
    return text.lower() + "..."

# 1. 指派給變數
say = shout
print(say("hello"))

# 2. 放進容器
styles = {"大聲": shout, "小聲": whisper}
for style, fn in styles.items():
    print(style, fn("Hello"))

# 3. 當作參數傳給別的函式
def apply_twice(fn, value):
    return fn(fn(value))
print(apply_twice(shout, "hi"))

# 4. 函式本身有屬性
print(shout.__name__, type(shout))
```

> 💡 **白話說**：`shout` 是函式本身（一個物件），`shout("hi")` 是**呼叫**它、拿到結果。把函式傳給別人時不要加括號，加了括號就變成傳結果了。

---

## 2. 參數的各種寫法

### 2.1 位置參數和關鍵字參數

```python
def make_profile(name, age, city="台北"):     # city 有預設值，可以不傳
    return f"{name}，{age} 歲，住在{city}"

print(make_profile("小明", 18))                 # 依位置傳
print(make_profile("小明", 18, "高雄"))
print(make_profile(age=20, name="小華"))        # 用名字傳，順序可以亂
print(make_profile("小美", city="台中", age=25))  # 混用：位置的要放前面
```

### 2.2 `*args` 和 `**kwargs`：收集「多出來的」

- `*args`：把多出來的**位置引數**收集成一個 **tuple**
- `**kwargs`：把多出來的**關鍵字引數**收集成一個 **dict**

（`args` 和 `kwargs` 只是慣例名稱，重點是 `*` 和 `**`）

```python
def total(*numbers):
    print("  收到：", numbers)
    return sum(numbers)

print(total(1, 2, 3))
print(total())

def build_tag(tag, **attrs):
    print("  attrs =", attrs)
    attr_text = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    return f"<{tag} {attr_text}>"

print(build_tag("a", href="https://python.org", target="_blank"))
```

### 2.3 呼叫時的「解包」

反過來，呼叫函式時也可以用 `*` 和 `**` 把 list / dict **拆開**當成引數：

```python
def area(width, height):
    return width * height

size = (3, 4)
print(area(*size))              # 等同 area(3, 4)

options = {"width": 5, "height": 6}
print(area(**options))          # 等同 area(width=5, height=6)

print(*[1, 2, 3], sep=" | ")    # print 也能這樣用
```

### 2.4 `/` 和 `*`：限制怎麼傳

```python
def f(a, b, /, c, d, *, e, f):
    print(a, b, c, d, e, f)

f(1, 2, 3, d=4, e=5, f=6)
```

| 位置 | 規則 |
|---|---|
| `/` **前面**的參數（a, b） | **只能**用位置傳 |
| `/` 和 `*` 之間（c, d） | 位置或名字都可以 |
| `*` **後面**的參數（e, f） | **只能**用名字傳 |

**為什麼需要？**

- `*` 後只能用名字：強迫呼叫的人寫清楚。像 `sorted(data, reverse=True)` 比 `sorted(data, True)` 好讀太多了。
- `/` 前只能用位置：參數名稱不算公開介面，以後可以改名而不會弄壞別人的程式。

```python
def connect(host, port, *, timeout=10, retries=3):
    return f"連線 {host}:{port}（逾時 {timeout}s，重試 {retries} 次）"

print(connect("localhost", 8080, timeout=5))
try:
    connect("localhost", 8080, 5)      # timeout 只能用名字傳
except TypeError as e:
    print("TypeError:", e)
```

### 2.5 所有參數種類的順序

```python
def everything(pos_only, /, normal, *args, kw_only, **kwargs):
    print(f"{pos_only=}, {normal=}, {args=}, {kw_only=}, {kwargs=}")

everything(1, 2, 3, 4, kw_only=5, x=6, y=7)
```

---

## 3. ⚠️ 預設參數的陷阱

這是 Python 最有名的陷阱之一：

```python
def add_item(item, bucket=[]):
    bucket.append(item)
    return bucket

print(add_item("蘋果"))      # ['蘋果']
print(add_item("香蕉"))      # ['蘋果', '香蕉'] ← 咦？上一次的蘋果還在！
print(add_item("橘子"))      # ['蘋果', '香蕉', '橘子']
```

**為什麼？** 預設值是在**定義函式的那一刻**（`def` 那一行執行時）建立的，而且**只建立一次**。之後每次呼叫，如果沒有傳 `bucket`，用的都是**同一個** list。

```python
def add_item(item, bucket=[]):
    bucket.append(item)
    return bucket

print(add_item.__defaults__)   # 預設值就存在函式物件身上
add_item("蘋果")
print(add_item.__defaults__)   # 被改掉了
```

**正確寫法**：用 `None` 當預設值，在函式裡面才建立新的 list：

```python
def add_item(item, bucket=None):
    if bucket is None:
        bucket = []              # 每次呼叫都建立一個新的
    bucket.append(item)
    return bucket

print(add_item("蘋果"))
print(add_item("香蕉"))
```

> ✅ **規則**：預設值**不要用可變物件**（list、dict、set）。需要的話用 `None` 代替。

同樣的道理，`def log(msg, time=datetime.now())` 的時間永遠是**定義函式時**的時間，不是呼叫時的時間。

---

## 4. 作用域：Python 怎麼找變數？

### 4.1 LEGB 規則

當你在函式裡用到一個名稱 `x`，Python 依照這個順序找：

| 順序 | 範圍 | 白話 |
|---|---|---|
| **L**ocal | 目前這個函式裡面 | 自己房間 |
| **E**nclosing | 外層函式（如果是巢狀函式） | 爸媽的房間 |
| **G**lobal | 這個檔案（模組）的最外層 | 客廳 |
| **B**uilt-in | Python 內建的名稱（`print`、`len`…） | 社區公共設施 |

找到就停，找不到就報 `NameError`。

```python
x = "全域"

def outer():
    x = "外層函式"
    def inner():
        print("inner 看到的 x：", x)    # 自己沒有 → 往外找到「外層函式」
    inner()

outer()
print("最外面的 x：", x)
```

### 4.2 ⚠️ UnboundLocalError：讀和寫的差別

**讀取**外面的變數沒問題，但**一旦在函式裡賦值**，Python 就會把它當成「這個函式自己的區域變數」，而且是**整個函式**都這樣認定：

```python
count = 0

def increment():
    count += 1          # 等同 count = count + 1：要先「讀」count，但它被認定是區域變數，還沒有值
    return count

try:
    increment()
except UnboundLocalError as e:
    print("UnboundLocalError:", e)
```

**為什麼這樣設計？** 「一個名稱是不是區域變數」是在**編譯時**就決定的（看函式裡有沒有對它賦值），不是執行到那一行才決定。這讓 Python 能更快地存取區域變數。

如果真的要改全域變數，用 `global` 宣告（但通常這是設計不良的徵兆）：

```python
count = 0
def increment():
    global count
    count += 1
    return count
print(increment(), increment())
```

---

## 5. 閉包：讓函式記住東西

### 5.1 什麼是閉包？

當一個**內層函式**用到了**外層函式的變數**，而且內層函式被傳到外面去，它會**一直記得**那些變數，即使外層函式已經執行完畢。這個「函式 + 它記住的變數」就叫**閉包 (closure)**。

```python
def make_multiplier(factor):
    def multiply(x):
        return x * factor        # 用到了外層的 factor
    return multiply              # 把內層函式回傳出去（注意沒有括號）

double = make_multiplier(2)      # make_multiplier 已經執行完了……
triple = make_multiplier(3)
print(double(10), triple(10))    # ……但 double 還記得 factor=2，triple 記得 factor=3
print(double.__closure__[0].cell_contents)   # 偷看它記住的值
```

> 💡 **白話說**：閉包像一個「帶著背包的函式」，背包裡裝著它出生時外層的變數。

### 5.2 `nonlocal`：修改外層的變數

和 `global` 一樣的道理，要**修改**（而不只是讀取）外層函式的變數，要用 `nonlocal` 宣告：

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count           # 宣告：這個 count 是外層的，不是新的區域變數
        count += 1
        return count
    return increment

counter_a = make_counter()
counter_b = make_counter()       # 每次呼叫 make_counter 都會產生「獨立」的 count
print(counter_a(), counter_a(), counter_a())
print(counter_b())
```

**閉包的好處**：狀態被封裝在函式內部，外面改不到，也不會污染全域變數，而且可以建立很多個互不干擾的計數器。

### 5.3 ⚠️ 延遲綁定陷阱

```python
functions = []
for i in range(3):
    functions.append(lambda: i)

print([f() for f in functions])     # 你以為是 [0, 1, 2]，結果是 [2, 2, 2]
```

**為什麼？** 閉包記住的是「**變數 i 本身**」，不是「**建立 lambda 當下 i 的值**」。等到你呼叫這些 lambda 時，迴圈早就跑完了，i 的值是 2，三個 lambda 去看的都是同一個 i。

**解法**：用預設參數，在**建立的當下**就把值存起來（預設值是在定義時求值的，這次反而派上用場）：

```python
functions = []
for i in range(3):
    functions.append(lambda i=i: i)   # 把當下的 i 存成預設值
print([f() for f in functions])
```

---

## 6. lambda 與高階函式

**lambda** 是「沒有名字的小函式」，只能寫**一個運算式**：

```python
square = lambda x: x * x            # 等同 def square(x): return x * x
print(square(5))
```

lambda 最常用在**需要一個簡單函式當參數**的時候：

```python
students = [("小明", 85), ("小華", 92), ("小美", 78)]
print(sorted(students, key=lambda s: s[1]))           # 依分數排序
print(max(students, key=lambda s: s[1]))              # 最高分
print(list(filter(lambda s: s[1] >= 80, students)))   # 篩選
print(list(map(lambda s: s[0], students)))            # 只取名字
```

> 💡 `map` 和 `filter` 通常可以改寫成推導式，而且更好讀：`[s[0] for s in students]`、`[s for s in students if s[1] >= 80]`。

`functools` 裡有幾個實用的高階函式工具：

```python
from functools import reduce, partial

print(reduce(lambda acc, x: acc * x, [1, 2, 3, 4, 5]))   # 累積運算：((((1*2)*3)*4)*5)

def power(base, exponent):
    return base ** exponent
square = partial(power, exponent=2)       # 固定某些參數，做出新函式
cube = partial(power, exponent=3)
print(square(7), cube(2))
```

> ⚠️ lambda 適合「一眼就看得懂」的小邏輯。稍微複雜就該寫成有名字的 `def`：有名字、能寫 docstring、出錯時錯誤訊息也比較清楚。

---

## 7. 裝飾器：不改原函式，替它加功能

### 7.1 從一個需求開始

假設你想知道好幾個函式各自跑多久。最笨的方法是每個函式裡都加計時的程式碼。更好的方法是：**寫一個「包裝函式」，把原函式包起來**。

```python
import time

def slow_add(a, b):
    time.sleep(0.1)
    return a + b

def timed(func):                          # 接收一個函式
    def wrapper(*args, **kwargs):         # 做一個新的函式，接收任何參數
        start = time.perf_counter()
        result = func(*args, **kwargs)    # 呼叫原本的函式
        print(f"  {func.__name__} 花了 {time.perf_counter() - start:.3f} 秒")
        return result                     # 把原本的結果傳回去
    return wrapper                        # 回傳新函式

slow_add = timed(slow_add)                # 用包裝過的版本取代原本的
print(slow_add(1, 2))
```

### 7.2 `@` 語法糖

`slow_add = timed(slow_add)` 這種寫法很常見，所以 Python 提供了簡寫：

```python
import functools
import time

def timed(func):
    @functools.wraps(func)                # 保留原函式的名稱和說明（下面解釋）
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"  {func.__name__} 花了 {(time.perf_counter() - start) * 1000:.2f} ms")
        return result
    return wrapper

@timed                                    # 完全等同於在下面寫 total = timed(total)
def total(n):
    """計算 0 到 n-1 的總和"""
    return sum(range(n))

print(total(1_000_000))
print(total.__name__, total.__doc__)
```

**為什麼要 `functools.wraps`？** 沒有它的話，`total.__name__` 會變成 `"wrapper"`，說明文字也不見了，除錯時會很困擾。**寫裝飾器時一律加上它**。

### 7.3 帶參數的裝飾器：三層函式

如果裝飾器本身也要參數，例如 `@repeat(3)` 讓函式執行 3 次，就需要**再多包一層**：

```python
import functools

def repeat(times):                         # 第 1 層：接收裝飾器的參數 → 回傳裝飾器
    def decorator(func):                   # 第 2 層：接收要被裝飾的函式 → 回傳 wrapper
        @functools.wraps(func)
        def wrapper(*args, **kwargs):      # 第 3 層：實際被呼叫的函式
            return [func(*args, **kwargs) for _ in range(times)]
        return wrapper
    return decorator

@repeat(3)                                 # 先執行 repeat(3) 得到 decorator，再用它裝飾 greet
def greet(name):
    return f"嗨 {name}"

print(greet("小明"))
```

> 💡 **拆解 `@repeat(3)`**：`greet = repeat(3)(greet)`。先呼叫 `repeat(3)`，它回傳 `decorator`；再呼叫 `decorator(greet)`，它回傳 `wrapper`。

### 7.4 多個裝飾器的順序

```python
def bold(f):
    def w():
        return "<b>" + f() + "</b>"
    return w

def italic(f):
    def w():
        return "<i>" + f() + "</i>"
    return w

@bold
@italic            # 離函式最近的先套用
def text():
    return "hello"

print(text())      # 等同 bold(italic(text))()
```

---

## 8. 產生器：需要時才計算

### 8.1 問題：資料太多，記憶體放不下

假設要處理 10 億筆資料，如果先全部放進一個 list，記憶體會爆掉。但很多時候我們其實只需要「**一次處理一筆**」。

**產生器 (generator)** 就是「**每次被要求時，才算出下一筆資料**」的東西。

### 8.2 `yield`：暫停並交出一個值

只要函式裡有 `yield`，它就變成**產生器函式**。和一般函式最大的不同：

- 呼叫它時，**函式本體完全不會執行**，只會拿到一個產生器物件
- 每次 `next()` 時，執行到下一個 `yield` 就**暫停**，把值交出去
- 下次 `next()` 時，**從暫停的地方繼續**

```python
def countdown(n):
    print("  （開始倒數）")
    while n > 0:
        print(f"  （準備交出 {n}）")
        yield n                  # 交出 n，然後暫停在這裡
        n -= 1                   # 下次 next() 從這裡繼續
    print("  （倒數結束）")

g = countdown(3)
print("建立了產生器，但什麼都還沒印出來")
print("拿到", next(g))
print("拿到", next(g))
print("剩下的：", list(g))      # list() 會一直 next() 直到結束
```

### 8.3 產生器管線：像工廠流水線

產生器可以串起來，每一筆資料**一路流過所有步驟**，記憶體裡同時只有一筆：

```python
import itertools

def read_records():                  # 第 1 站：模擬讀取一百萬筆資料
    for i in range(1, 1_000_001):
        yield f"record-{i}: value={i * 3}"

def parse(lines):                    # 第 2 站：解析
    for line in lines:
        yield int(line.split("=")[1])

def only_even(values):               # 第 3 站：篩選
    for v in values:
        if v % 2 == 0:
            yield v

pipeline = only_even(parse(read_records()))
print(list(itertools.islice(pipeline, 5)))    # 只拿前 5 個 → 實際上只處理了大約 10 筆資料
```

### 8.4 `yield from`：委派給另一個產生器

```python
def walk(tree):
    for node in tree:
        if isinstance(node, list):
            yield from walk(node)    # 把子串列的所有元素都交出去
        else:
            yield node

print(list(walk([1, [2, [3, 4]], 5, [[6]]])))
```

### 8.5 ⚠️ 產生器只能用一次

```python
squares = (x * x for x in range(5))
print(sum(squares))     # 30
print(sum(squares))     # 0 ← 已經用完了，空的
```

| | list | 產生器 |
|---|---|---|
| 記憶體 | 全部存起來 | 只存「目前狀態」 |
| 可以重複走訪 | ✅ | ❌ 只能一次 |
| 可以用索引、`len()` | ✅ | ❌ |
| 可以處理無限資料 | ❌ | ✅ |

---

## 9. 遞迴與快取

### 9.1 遞迴：函式呼叫自己

```python
def factorial(n):
    if n <= 1:                   # 終止條件（一定要有！）
        return 1
    return n * factorial(n - 1)  # 把問題縮小，交給自己處理

print(factorial(5))
```

### 9.2 Python 遞迴的限制

每次函式呼叫都要佔用一些記憶體（叫做「堆疊框架 stack frame」）。Python 預設最多大約 **1000 層**，超過就會 `RecursionError`。而且 Python **不做尾遞迴最佳化**（某些語言會把特定形式的遞迴自動轉成迴圈，Python 不會）。

```python
import sys
print("遞迴深度上限：", sys.getrecursionlimit())

def depth(n):
    return 0 if n == 0 else 1 + depth(n - 1)

print(depth(500))
try:
    depth(100_000)
except RecursionError as e:
    print("RecursionError:", e)
```

> ✅ 遞迴深度可能很大時（例如處理很深的巢狀資料），請改寫成**迴圈 + 自己維護一個堆疊 (list)**。單元四的「攤平巢狀結構」練習題就是在練這個。

### 9.3 快取：避免重複計算

費氏數列的天真遞迴寫法慢得驚人，因為**同樣的東西被算了無數次**：

```python
calls = 0
def fib(n):
    global calls
    calls += 1
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(25), "呼叫了", calls, "次")   # 算 fib(25) 竟然要呼叫二十多萬次
```

`fib(5)` 會算 `fib(4)` 和 `fib(3)`，而 `fib(4)` 又會再算一次 `fib(3)`……越往下重複越多。

解法是**快取 (cache)**：算過的結果記起來，下次直接查表。`functools.cache` 一行搞定：

```python
from functools import cache

@cache
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(200))
print(fib.cache_info())    # hits = 直接查表的次數，misses = 真的去計算的次數
```

> ⚠️ 快取解決了「重複計算」，但**沒有減少遞迴深度**。`fib(5000)` 一樣會 RecursionError，這時要改用迴圈。

---

## 10. 型別提示：讓程式碼自己說明

```python
def average(scores: list[float], *, ndigits: int = 2) -> float:
    """計算平均分數，四捨五入到 ndigits 位。"""
    return round(sum(scores) / len(scores), ndigits)

print(average([90, 85.5, 77]))
print(average.__annotations__)

def double(x: int) -> int:
    return x * 2

print(double("哈"))      # 明明標示要 int，傳字串 Python 也不會阻止 → '哈哈'
```

- `scores: list[float]`：這個參數「應該」是浮點數的 list
- `-> float`：這個函式「應該」回傳 float

**型別提示在執行時不會被檢查**，傳錯型別 Python 也不會阻止你。它的價值在於：讓人一眼看懂函式怎麼用、讓編輯器能自動完成和提示錯誤、讓 mypy 等工具能在執行前找出 bug。

---

## 11. 本章小結

| 觀念 | 一句話記住 |
|---|---|
| 一等公民 | 函式是物件，可以傳遞、存放、回傳 |
| `*args` / `**kwargs` | 收集多出來的位置 / 關鍵字引數 |
| `/` 和 `*` | 前面只能用位置、後面只能用名字 |
| 預設參數 | 只建立一次；可變物件請用 `None` 代替 |
| LEGB | 區域 → 外層 → 全域 → 內建；有賦值就是區域變數 |
| 閉包 | 帶著外層變數的函式；記住的是變數不是值 |
| 裝飾器 | `@deco` 等於 `f = deco(f)`；記得 `functools.wraps` |
| 產生器 | `yield` 暫停並交出值；省記憶體但只能用一次 |
| 遞迴 | 深度上限約 1000；太深就改用迴圈 |
| 快取 | `@cache` 避免重複計算 |

### 常見錯誤速查

1. 預設參數用 `[]` 或 `{}`，資料會在呼叫之間累積。
2. 函式裡 `count += 1` 修改全域變數 → `UnboundLocalError`。
3. 迴圈裡建立的 lambda 全部回傳最後一個值。
4. 裝飾器忘了 `functools.wraps`，函式名稱變成 `wrapper`。
5. 產生器用完一次就空了。
6. 把產生器函式裡的參數檢查放在 `yield` 前面，結果要等到第一次 `next()` 才會檢查。
