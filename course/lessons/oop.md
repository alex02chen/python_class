# 單元五：物件導向

> **這個單元要解決的問題**：程式變大之後，資料和處理資料的函式會散落各處，很難管理。物件導向 (Object-Oriented Programming, OOP) 的核心想法是：**把「資料」和「操作這些資料的函式」綁在一起**，變成一個個「物件」。
> 但 Python 的 OOP 有自己的風格：沒有真正的 private、偏好「鴨子型別」、大量使用以雙底線包起來的特殊方法 (`__init__`、`__len__`…)。這個單元會帶你理解這些設計背後的道理，並讓你的類別用起來「像內建型別一樣自然」。

**讀完你會知道：**

1. 類別和實例是什麼，`self` 到底是誰
2. 類別屬性和實例屬性的差別（一個經典陷阱）
3. `@property`、`@classmethod`、`@staticmethod` 各自的用途
4. 繼承、`super()`，以及多重繼承時的 MRO
5. 抽象類別：規定子類別「一定要實作什麼」
6. 特殊方法：讓你的物件支援 `+`、`==`、`len()`、`for` 迴圈
7. `dataclass`：少寫一半的樣板程式碼
8. 什麼時候該用繼承、什麼時候該用組合

---

## 1. 類別與實例

### 1.1 類別是「設計圖」，實例是「依照設計圖做出來的東西」

```python
class Dog:                                   # 定義一個類別（設計圖）
    def __init__(self, name, age):           # 建立實例時自動呼叫，負責「初始化」
        self.name = name                     # 把資料存到這個實例身上
        self.age = age

    def bark(self):                          # 方法：屬於這個類別的函式
        return f"{self.name}：汪汪！"

    def birthday(self):
        self.age += 1
        return f"{self.name} 現在 {self.age} 歲了"

lucky = Dog("Lucky", 3)                      # 建立實例（依設計圖做出一隻狗）
max_ = Dog("Max", 5)
print(lucky.bark(), max_.bark())
print(lucky.birthday())
print(lucky.age, max_.age)                   # 每隻狗有自己的 age
```

### 1.2 `self` 是什麼？

`self` 就是「**目前這個實例**」。呼叫 `lucky.bark()` 時，Python 其實是在做 `Dog.bark(lucky)`，自動把 `lucky` 當成第一個參數傳進去。

```python
class Dog:
    def __init__(self, name):
        self.name = name
    def bark(self):
        return f"{self.name}：汪汪！"

lucky = Dog("Lucky")
print(lucky.bark())          # 平常的寫法
print(Dog.bark(lucky))       # 實際上發生的事，結果一模一樣
print(lucky.__dict__)        # 實例的屬性都存在 __dict__ 這個字典裡
```

> 💡 **白話說**：方法就是普通的函式，只是第一個參數會自動填入「是誰在呼叫」。`self` 只是慣例名稱，換成別的名字也能動，但請不要這樣做。

### 1.3 `__init__` 不是建構子

很多人說 `__init__` 是「建構子」，嚴格來說不對。物件是由 `__new__` **建立**的，`__init__` 收到的時候物件已經存在了，它只負責**設定初始值**。平常你幾乎不需要碰 `__new__`，知道這個區別就好。

---

## 2. 類別屬性 vs 實例屬性

### 2.1 兩種屬性

- **實例屬性**：在 `__init__` 裡用 `self.xxx = ...` 設定，**每個實例各自一份**。
- **類別屬性**：直接寫在 `class` 底下，**所有實例共用一份**。

```python
class Dog:
    species = "犬科"                  # 類別屬性：所有狗都一樣
    count = 0                         # 用來計算總共建立了幾隻狗

    def __init__(self, name):
        self.name = name              # 實例屬性：每隻狗不同
        Dog.count += 1                # 修改類別屬性：要透過「類別名稱」

a, b = Dog("A"), Dog("B")
print(a.species, b.species, Dog.species)
print("總共幾隻狗：", Dog.count)
```

### 2.2 Python 怎麼找屬性？

讀取 `obj.attr` 時，Python 依序找：

1. **實例自己的 `__dict__`**
2. 找不到 → 去**類別**找
3. 還找不到 → 去**父類別**找（依照 MRO，第 4 節會說明）

但是**賦值** `obj.attr = value` **永遠寫進實例自己的 `__dict__`**。這個不對稱會造成一些令人困惑的狀況：

```python
class Dog:
    count = 0

a = Dog()
a.count = 100                  # 這不是修改類別屬性！而是在 a 身上建立一個同名的實例屬性
print(a.count, Dog.count)      # 100 0
print(a.__dict__)              # a 自己多了 count
b = Dog()
print(b.count)                 # b 沒有自己的 count → 讀到類別的 0
```

### 2.3 ⚠️ 經典陷阱：可變的類別屬性

```python
class Team:
    members = []                       # ⚠️ 類別屬性：所有隊伍共用同一個 list！

    def add(self, name):
        self.members.append(name)      # self.members 讀到的是類別的 list，append 修改了它

red = Team()
blue = Team()
red.add("小明")
print("藍隊成員：", blue.members)      # ['小明'] ← 小明怎麼跑到藍隊了？
```

這和單元四「預設參數用 `[]`」是同一個道理：**只有一個 list，大家共用**。正確做法是在 `__init__` 裡建立：

```python
class Team:
    def __init__(self):
        self.members = []              # 每個實例建立自己的 list

red, blue = Team(), Team()
red.members.append("小明")
print(red.members, blue.members)
```

---

## 3. 三種方法與 property

### 3.1 `@property`：看起來像屬性，其實是方法

假設你有一個 `Circle` 類別，存了半徑，想取得面積。寫成 `c.area()` 可以，但面積感覺像是圓的「屬性」，寫成 `c.area` 更自然。`@property` 就是做這件事的：

```python
import math

class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):                         # 存取 c.area 時會自動呼叫這個方法
        return math.pi * self.radius ** 2

c = Circle(2)
print(c.area)                               # 不用加括號
c.radius = 3
print(c.area)                               # 每次都重新計算，永遠是最新的
```

### 3.2 用 property 做「驗證」

property 還能控制**賦值**。例如年齡不能是負數：

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age                      # 這裡會呼叫下面的 setter，所以建立時也會驗證

    @property
    def age(self):                          # getter：讀取時呼叫
        return self._age

    @age.setter
    def age(self, value):                   # setter：賦值時呼叫
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"年齡必須是非負整數，收到 {value!r}")
        self._age = value                   # 真正的資料存在 _age

p = Person("小明", 18)
p.age = 19
print(p.age)
for bad in [-1, "十八"]:
    try:
        p.age = bad
    except ValueError as e:
        print("ValueError:", e)
try:
    Person("小華", -5)
except ValueError as e:
    print("建立時也會檢查 →", e)
```

**只寫 getter、不寫 setter，就是唯讀屬性**：

```python
class Account:
    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance

acct = Account(100)
print(acct.balance)
try:
    acct.balance = 999999
except AttributeError as e:
    print("AttributeError:", e)
```

### 3.3 底線的慣例

| 寫法 | 意思 |
|---|---|
| `name` | 公開的，外面可以隨意使用 |
| `_name` | **慣例上**是內部使用，請外面不要碰（但技術上碰得到） |
| `__name` | 會被**改名**成 `_類別名__name`，主要用來避免子類別意外覆蓋 |
| `__name__` | Python 的特殊方法/屬性，不要自己發明這種名字 |

```python
class Secret:
    def __init__(self):
        self._hint = "請不要碰我"
        self.__key = 42

s = Secret()
print(s._hint)                  # 還是讀得到
print(s.__dict__)               # __key 被改名成 _Secret__key
```

> 💡 Python 沒有真正的 private。它的哲學是「**我們都是成年人**」：用底線表達「這是內部細節」，信任使用者不會亂用。

### 3.4 `@classmethod` 和 `@staticmethod`

| 種類 | 第一個參數 | 用途 |
|---|---|---|
| 一般方法 | `self`（實例） | 需要存取實例資料 |
| `@classmethod` | `cls`（類別本身） | **另一種建立實例的方式**（替代建構子） |
| `@staticmethod` | 沒有 | 跟類別有關，但不需要實例或類別的資料 |

```python
from datetime import date

class Person:
    def __init__(self, name, birth_year):
        self.name = name
        self.birth_year = birth_year

    @classmethod
    def from_string(cls, text):              # 從 "小明,2005" 這種字串建立
        name, year = text.split(",")
        return cls(name.strip(), int(year))  # 用 cls 而不是 Person，子類別呼叫時才會建立子類別

    @classmethod
    def from_age(cls, name, age):
        return cls(name, date.today().year - age)

    @staticmethod
    def is_valid_year(year):                 # 只是個工具函式，放在這裡比較有組織
        return 1900 <= year <= date.today().year

p1 = Person.from_string("小明, 2005")
p2 = Person.from_age("小華", 30)
print(p1.name, p1.birth_year)
print(p2.name, p2.birth_year)
print(Person.is_valid_year(1800))

class Student(Person):
    pass

s = Student.from_string("小美, 2008")
print(type(s).__name__)                      # Student：因為用了 cls
```

---

## 4. 繼承

### 4.1 基本繼承

**繼承**讓子類別自動擁有父類別的所有屬性和方法，再加上自己的東西或修改某些行為：

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "……"

    def introduce(self):
        return f"我是 {self.name}，我會說「{self.speak()}」"

class Cat(Animal):                            # Cat 繼承 Animal
    def speak(self):                          # 覆寫 (override) 父類別的方法
        return "喵"

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)                # 先讓父類別做它的初始化
        self.breed = breed                    # 再加上自己的

    def speak(self):
        return "汪"

for pet in [Cat("咪咪"), Dog("小黑", "柴犬"), Animal("不明生物")]:
    print(pet.introduce())                    # introduce 是父類別的，但呼叫到的 speak 是各自的
print(isinstance(Cat("x"), Animal), issubclass(Dog, Animal))
```

注意 `introduce` 只寫在 `Animal` 裡，但它呼叫的 `self.speak()` 會**依照實際的物件**去找 `speak`。這叫做**多型 (polymorphism)**：同一段程式碼，面對不同物件有不同行為。

### 4.2 多重繼承與 MRO

Python 允許一個類別繼承好幾個父類別。這時要決定「找方法時先找誰」，這個順序叫 **MRO (Method Resolution Order)**。

```python
class A:
    def hello(self):
        return "A"

class B(A):
    def hello(self):
        return "B → " + super().hello()

class C(A):
    def hello(self):
        return "C → " + super().hello()

class D(B, C):
    def hello(self):
        return "D → " + super().hello()

print(D().hello())
print([cls.__name__ for cls in D.__mro__])
```

```text
        A
       / \
      B   C        ← 菱形繼承
       \ /
        D
MRO: D → B → C → A → object
```

**重點**：在 B 裡呼叫 `super().hello()`，呼叫到的是 **C**，不是 A！因為 `super()` 的意思不是「呼叫我的父類別」，而是「**呼叫 MRO 中排在我後面的下一個**」。這個設計保證了菱形繼承時，A 只會被呼叫一次。

---

## 5. 抽象類別：規定「一定要實作」

有時候父類別只是「概念」，本身不應該被建立，而是規定子類別**必須**提供某些方法。例如「形狀」一定要能算面積，但「形狀」本身不知道怎麼算：

```python
from abc import ABC, abstractmethod
import math

class Shape(ABC):                          # 繼承 ABC = 這是抽象類別
    @abstractmethod
    def area(self):                        # 抽象方法：子類別「必須」實作
        ...

    def describe(self):                    # 一般方法：可以呼叫還沒實作的 area
        return f"{type(self).__name__} 面積 = {self.area():.2f}"

class Circle(Shape):
    def __init__(self, r):
        self.r = r
    def area(self):
        return math.pi * self.r ** 2

class Square(Shape):
    def __init__(self, side):
        self.side = side
    def area(self):
        return self.side ** 2

for s in [Circle(1), Square(3)]:
    print(s.describe())

try:
    Shape()                                # 抽象類別不能直接建立
except TypeError as e:
    print("TypeError:", e)

class Triangle(Shape):                     # 忘了實作 area
    pass
try:
    Triangle()
except TypeError as e:
    print("TypeError:", e)
```

好處：**忘了實作會在建立物件時就報錯**，而不是等到某天呼叫 `area()` 才發現。

---

## 6. 特殊方法：讓物件像內建型別一樣好用

### 6.1 什麼是特殊方法？

為什麼 `len([1, 2, 3])` 能用？為什麼 `1 + 2` 和 `"a" + "b"` 都能用 `+`？因為 Python 在背後會呼叫物件的**特殊方法**（又叫 dunder method，double underscore 的縮寫）：

| 你寫的 | Python 實際呼叫 |
|---|---|
| `len(x)` | `x.__len__()` |
| `x + y` | `x.__add__(y)` |
| `x == y` | `x.__eq__(y)` |
| `x < y` | `x.__lt__(y)` |
| `x[i]` | `x.__getitem__(i)` |
| `for v in x` | `x.__iter__()` |
| `print(x)` / `str(x)` | `x.__str__()` |
| 互動環境顯示 / `repr(x)` | `x.__repr__()` |
| `bool(x)`、`if x:` | `x.__bool__()`（沒有則用 `__len__`） |
| `x()` | `x.__call__()` |
| `hash(x)` | `x.__hash__()` |

所以只要你的類別定義了這些方法，就能使用對應的語法。

### 6.2 `__repr__` 和 `__str__`

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

p = Point(1, 2)
print(p)                 # <__main__.Point object at 0x...> 完全看不出內容

class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __repr__(self):                       # 給開發者看：最好能直接複製貼上重建物件
        return f"Point({self.x!r}, {self.y!r})"
    def __str__(self):                        # 給使用者看：好讀就好
        return f"({self.x}, {self.y})"

p = Point(1, 2)
print(p)                 # 用 __str__
print(repr(p))           # 用 __repr__
print([p, Point(3, 4)])  # 容器裡的元素用 __repr__
```

> ✅ **只寫一個的話，寫 `__repr__`**。沒有 `__str__` 時，`str()` 會自動退回用 `__repr__`。

### 6.3 一個完整範例：金額類別

```python
from functools import total_ordering

@total_ordering                               # 只要定義 __eq__ 和 __lt__，自動補齊 <=、>、>=
class Money:
    def __init__(self, amount, currency="TWD"):
        self.amount = amount
        self.currency = currency

    def __repr__(self):
        return f"Money({self.amount!r}, {self.currency!r})"

    def __str__(self):
        return f"{self.currency} {self.amount:,}"

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented             # 不是 False！下面解釋
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __hash__(self):                       # 定義了 __eq__ 就要自己定義 __hash__
        return hash((self.amount, self.currency))

    def __lt__(self, other):
        if not isinstance(other, Money) or other.currency != self.currency:
            return NotImplemented
        return self.amount < other.amount

    def __add__(self, other):
        if isinstance(other, Money) and other.currency == self.currency:
            return Money(self.amount + other.amount, self.currency)
        return NotImplemented

    def __radd__(self, other):                # 讓 sum() 能用（sum 會從 0 + 第一個開始加）
        if other == 0:
            return self
        return NotImplemented

wallet = [Money(100), Money(2500), Money(50)]
print(sum(wallet))
print(max(wallet), sorted(wallet))
print(Money(100) == Money(100), Money(100) >= Money(50))
print(len({Money(5), Money(5)}))              # 可以放進 set，相等的會被當成同一個
try:
    Money(100) + 5
except TypeError as e:
    print("TypeError:", e)
```

**為什麼回傳 `NotImplemented` 而不是 `False` 或丟出錯誤？**

`NotImplemented` 的意思是「**我不知道怎麼處理這個，請問問對方**」。例如 `5 + Money(1)`：

1. Python 先問 `int` 的 `__add__`：「你會加 Money 嗎？」→ 回答 NotImplemented
2. Python 再問 `Money` 的 `__radd__`（r = reflected，反向）：「那你會嗎？」
3. 兩邊都不會，才丟出 `TypeError`

如果你直接回傳 `False` 或丟錯誤，就斷了「問問對方」的機會。

**為什麼定義 `__eq__` 就要定義 `__hash__`？** 規則是「**相等的物件，雜湊值必須相同**」，否則 dict 和 set 會出錯。所以 Python 在你定義 `__eq__` 後，會把 `__hash__` 設成 `None`（讓物件變得不能雜湊），強迫你自己決定。

### 6.4 容器協定：只要 `__getitem__` 和 `__len__`

```python
class Deck:
    def __init__(self):
        self._cards = [rank + suit for suit in "♠♥" for rank in "A23"]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, index):
        return self._cards[index]

deck = Deck()
print(len(deck), deck[0], deck[-1])
print(deck[1:3])                    # 切片：免費得到（因為 index 直接交給 list 處理）
print("2♥" in deck)                 # in：免費得到
for card in deck:                   # for：免費得到
    print(card, end=" ")
print()
print(list(reversed(deck)))         # reversed：免費得到
```

只實作兩個方法，就自動得到切片、`in`、`for`、`reversed`……這就是 Python「資料模型」的威力。

### 6.5 `__call__`：讓物件可以被呼叫

```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor
    def __call__(self, x):
        return x * self.factor

triple = Multiplier(3)
print(triple(10))                   # 物件被當成函式呼叫
print(list(map(triple, [1, 2, 3])))
```

這是除了閉包（單元四）之外，另一種「**帶著狀態的函式**」。

### 6.6 Context manager：`with` 背後的機制

```python
import time

class Timer:
    def __enter__(self):                       # 進入 with 區塊時呼叫
        self.start = time.perf_counter()
        return self                            # 這個會被 as 接住
    def __exit__(self, exc_type, exc, tb):     # 離開 with 區塊時呼叫（就算出錯也會）
        self.elapsed = time.perf_counter() - self.start
        print(f"  經過 {self.elapsed * 1000:.2f} ms，例外：{exc_type}")
        return False                           # False：不吞掉例外

with Timer() as t:
    sum(range(1_000_000))

try:
    with Timer():
        1 / 0
except ZeroDivisionError:
    print("  例外照常往外丟")
```

`with open(...) as f:` 能保證檔案一定被關閉，就是因為檔案物件的 `__exit__` 會關閉檔案。

---

## 7. dataclass：省掉樣板程式碼

很多類別只是「裝資料」，但每次都要寫 `__init__`、`__repr__`、`__eq__`，很煩。`@dataclass` 會**自動幫你產生**：

```python
from dataclasses import dataclass, field

@dataclass
class Product:
    name: str
    price: int
    tags: list = field(default_factory=list)   # 可變的預設值必須這樣寫

p = Product("咖啡", 120)
print(p)                                       # 自動有好看的 __repr__
print(p == Product("咖啡", 120))               # 自動有 __eq__
p.tags.append("飲料")
print(p)
```

常用選項：

```python
from dataclasses import dataclass

@dataclass(order=True, frozen=True)    # order：自動產生 < > 比較；frozen：不可修改（因此可以雜湊）
class Version:
    major: int
    minor: int = 0
    patch: int = 0

    def __str__(self):
        return f"v{self.major}.{self.minor}.{self.patch}"

versions = [Version(1, 10), Version(1, 2), Version(0, 9, 9)]
print(sorted(versions))                # 依欄位順序比較：先比 major，再比 minor……
print(max(versions))
print({Version(1): "穩定版"})          # frozen 所以可以當 key
try:
    versions[0].major = 2
except Exception as e:
    print(type(e).__name__, e)
```

---

## 8. 設計原則：組合優於繼承

### 8.1 繼承的問題

**繼承**表達「**是一種 (is-a)**」：貓**是一種**動物。
**組合**表達「**有一個 (has-a)**」：汽車**有一個**引擎。

很多人為了「重用程式碼」而濫用繼承，結果繼承了一堆不該有的東西：

```python
class Stack(list):                 # ⚠️ 想做一個堆疊，直接繼承 list
    def push(self, x):
        self.append(x)

s = Stack()
s.push(1)
s.push(2)
s.insert(0, 99)                    # 堆疊不該能從底部插入，但 list 的方法全部都繼承來了
s.sort()
print(s)
```

用**組合**就乾淨多了——Stack **擁有**一個 list，但只對外公開堆疊該有的操作：

```python
class Stack:
    def __init__(self):
        self._items = []           # 擁有一個 list
    def push(self, x):
        self._items.append(x)
    def pop(self):
        return self._items.pop()
    def __len__(self):
        return len(self._items)

s = Stack()
s.push(1)
print(hasattr(s, "insert"))        # False：不會有不該有的方法
```

> ✅ **原則**：只有在「子類別真的可以完全取代父類別」時才用繼承。只是想重用某些功能，用組合。

### 8.2 鴨子型別

> 「如果它走起來像鴨子、叫起來像鴨子，那它就是鴨子。」

Python 不太在意物件「**是什麼型別**」，只在意它「**有沒有需要的方法**」：

```python
class Duck:
    def speak(self):
        return "呱呱"

class Robot:                       # 跟 Duck 沒有任何繼承關係
    def speak(self):
        return "嗶嗶，我是機器人"

for thing in [Duck(), Robot()]:
    print(thing.speak())           # 只要有 speak 就能用

class FakeFile:
    def __init__(self):
        self.lines = []
    def write(self, text):
        self.lines.append(text)

f = FakeFile()
print("寫到假檔案", file=f)        # print 只需要 file 參數有 write 方法
print(f.lines)
```

---

## 9. 本章小結

| 觀念 | 一句話記住 |
|---|---|
| `self` | 就是「目前這個實例」，`obj.m()` 等於 `Class.m(obj)` |
| 類別屬性 | 所有實例共用；可變的類別屬性是陷阱 |
| `@property` | 像屬性一樣存取，背後可以計算或驗證 |
| `@classmethod` | 替代建構子，用 `cls(...)` 建立 |
| `super()` | 呼叫 MRO 的下一個，不一定是父類別 |
| 抽象類別 | 沒實作抽象方法就不能建立實例 |
| 特殊方法 | 讓物件支援 `+`、`==`、`len`、`for`… |
| `NotImplemented` | 「我不會，請問對方」，不是 False |
| `__eq__` + `__hash__` | 定義了相等就要定義雜湊 |
| `dataclass` | 自動產生 `__init__`、`__repr__`、`__eq__` |
| 組合 vs 繼承 | is-a 用繼承，has-a 用組合 |

### 常見錯誤速查

1. 類別屬性用 `[]`，所有實例共用同一個 list。
2. `obj.count = 1` 只是建立實例屬性，不會修改類別屬性。
3. 替代建構子寫 `Person(...)` 而不是 `cls(...)`，子類別會拿到錯的型別。
4. `__eq__` 遇到不認得的型別回傳 `False` 而不是 `NotImplemented`。
5. 定義了 `__eq__` 卻沒定義 `__hash__`，物件無法放進 set。
6. 為了重用程式碼而繼承 list/dict，結果繼承了一堆不該有的方法。
