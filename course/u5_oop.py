from common import T, choice, exercise, lesson, md, qa

LESSON = lesson("oop")

QUIZ = [
    choice("`class A: items = []`，`a, b = A(), A(); a.items.append(1)` 後 `b.items` 是？",
           ["`[]`", "`[1]`", "`AttributeError`", "`None`"], 1,
           "`items` 是類別屬性，所有實例共享同一個 list。`append` 修改了它而不是建立實例屬性。"),
    choice("`__eq__` 遇到無法比較的型別時，最佳做法是回傳？", ["`False`", "`None`", "`NotImplemented`", "拋出 `TypeError`"], 2,
           "回傳 `NotImplemented` 讓 Python 嘗試對方的反射方法，兩邊都不支援時 `==` 退回比較身分、`+` 則拋 TypeError。"),
    choice("只定義 `__eq__` 而沒定義 `__hash__` 的類別，其實例？", ["可以放進 set", "不可雜湊", "以 id 雜湊", "雜湊值固定為 0"], 1,
           "定義 `__eq__` 會讓 `__hash__` 被設為 `None`，避免「相等但雜湊不同」的不一致。"),
    choice("`class D(B, C)`、`B(A)`、`C(A)`，D 的 MRO 是？", ["D B A C", "D B C A", "D C B A", "D A B C"], 1,
           "C3 線性化保證子類別在父類別之前、並保留宣告順序：D → B → C → A → object。"),
    choice("`@classmethod` 的第一個參數 `cls` 在**子類別**呼叫時是？", ["定義方法的類別", "子類別", "實例", "`object`"], 1,
           "所以替代建構子用 `cls(...)` 而非寫死類別名稱，子類別才能得到正確型別的物件。"),
    choice("`dataclass` 的 list 欄位預設值應寫成？", ["`items: list = []`", "`items: list = None`", "`items: list = field(default_factory=list)`", "`items = list`"], 2,
           "dataclass 直接拒絕可變預設值（ValueError），必須用 `default_factory`。"),
    choice("`with obj:` 區塊中發生例外，若 `__exit__` 回傳 `True` 會？", ["例外照常拋出", "例外被吞掉", "重新執行區塊", "`RuntimeError`"], 1,
           "回傳真值表示「例外已處理」，`with` 之後的程式繼續執行。"),
    qa("`__repr__` 與 `__str__` 有何不同？只能寫一個時該寫哪個？",
       "`__repr__` 給開發者看（除錯、互動式環境、容器內元素的顯示），理想上是能重建物件的運算式；"
       "`__str__` 給使用者看（`print`、`str()`）。\n\n只寫一個時寫 `__repr__`：沒有 `__str__` 時 `str()` 會退回使用 `__repr__`，反之則不會。"),
    qa("什麼時候該用繼承？什麼時候該用組合？",
       "繼承適合真正的 is-a 關係、且子類別能完全替代父類別（里氏替換原則），例如 `Circle` 是一種 `Shape`。\n\n"
       "組合適合 has-a 或「只是想重用部分功能」的情境：它只公開需要的介面、耦合度低、可在執行期替換元件。"
       "例如 Stack 應該「擁有」一個 list，而不是「是」一個 list（否則 `insert`、`sort` 等方法會破壞堆疊語意）。"),
    qa("`super()` 真的是「呼叫父類別」嗎？",
       "不完全是。`super()` 回傳的是一個代理，會依照**實例所屬類別的 MRO**，找出目前類別「之後」的下一個類別。"
       "在單一繼承中剛好就是父類別；在多重繼承（如菱形）中可能是兄弟類別。這讓協作式多重繼承中每個 `__init__` 只被呼叫一次。"),
]

EXERCISES = [
    exercise(
        "o1-account", "銀行帳戶（封裝、例外、property）", 2, r'''
        實作自訂例外 `InsufficientFunds`（繼承 `Exception`）與類別 `BankAccount`：

        | 成員 | 規格 |
        |---|---|
        | `BankAccount(owner, balance=0)` | `balance` 為負時拋 `ValueError` |
        | `.owner` | 一般屬性 |
        | `.balance` | **唯讀** property（`acct.balance = 5` 要拋 `AttributeError`） |
        | `.deposit(amount)` | `amount <= 0` 拋 `ValueError`；回傳新餘額 |
        | `.withdraw(amount)` | `amount <= 0` 拋 `ValueError`；餘額不足拋 `InsufficientFunds`（餘額不變）；回傳新餘額 |
        | `.transfer(other, amount)` | 從自己轉到 `other`；失敗時**兩邊餘額都不變**；`other` 不是 `BankAccount` 時拋 `TypeError` |
        | `.history` | 回傳交易紀錄 list 的**副本**，每筆為 `(類型, 金額)`，類型為 `'deposit'`、`'withdraw'`、`'transfer_out'`、`'transfer_in'`；失敗的操作不記錄 |
        | `repr(acct)` | `BankAccount('amy', 100)` |
        | `BankAccount.count` | 類別屬性：至今成功建立的帳戶數（建立失敗不算） |

        ### 範例測試程式
        ```python
        a = BankAccount("amy", 100)
        a.deposit(50)
        a.withdraw(30)
        print(a, a.history)
        ```
        ### 輸出
        ```text
        BankAccount('amy', 120) [('deposit', 50), ('withdraw', 30)]
        ```
        ''',
        r'''
        class InsufficientFunds(Exception):
            pass


        class BankAccount:
            count = 0

            def __init__(self, owner, balance=0):
                ...
        ''',
        r'''
        class InsufficientFunds(Exception):
            pass


        class BankAccount:
            count = 0

            def __init__(self, owner, balance=0):
                if balance < 0:
                    raise ValueError("初始餘額不可為負")
                self.owner = owner
                self._balance = balance
                self._history = []
                BankAccount.count += 1

            @property
            def balance(self):
                return self._balance

            @property
            def history(self):
                return list(self._history)

            @staticmethod
            def _check(amount):
                if amount <= 0:
                    raise ValueError("金額必須為正")

            def deposit(self, amount):
                self._check(amount)
                self._balance += amount
                self._history.append(("deposit", amount))
                return self._balance

            def withdraw(self, amount):
                self._check(amount)
                if amount > self._balance:
                    raise InsufficientFunds(f"餘額 {self._balance} 不足")
                self._balance -= amount
                self._history.append(("withdraw", amount))
                return self._balance

            def transfer(self, other, amount):
                if not isinstance(other, BankAccount):
                    raise TypeError("只能轉帳給 BankAccount")
                self._check(amount)
                if amount > self._balance:
                    raise InsufficientFunds(f"餘額 {self._balance} 不足")
                self._balance -= amount
                other._balance += amount
                self._history.append(("transfer_out", amount))
                other._history.append(("transfer_in", amount))

            def __repr__(self):
                return f"BankAccount({self.owner!r}, {self._balance!r})"
        ''',
        [
            T(after="""
              a = BankAccount("amy", 100)
              a.deposit(50)
              a.withdraw(30)
              print(a, a.history)
              """, tag="sample", expect="BankAccount('amy', 120) [('deposit', 50), ('withdraw', 30)]"),
            T(after="""
              a = BankAccount("bob")
              print(a.balance, a.deposit(10), a.withdraw(10), a.balance)
              """, note="預設餘額 0、回傳值", expect="0 10 0 0"),
            T(after="""
              a = BankAccount("c", 50)
              try:
                  a.withdraw(51)
              except InsufficientFunds:
                  print("InsufficientFunds", a.balance, a.history)
              print(a.withdraw(50))
              """, tag="corner", note="差 1 元不足、剛好提領全部", expect="InsufficientFunds 50 []\n0"),
            T(after="""
              a = BankAccount("d", 10)
              for op in (a.deposit, a.withdraw):
                  for amt in (0, -5):
                      try:
                          op(amt)
                      except ValueError:
                          print("ValueError")
              print(a.balance, len(a.history))
              """, tag="corner", note="0 與負數金額", expect="ValueError\nValueError\nValueError\nValueError\n10 0"),
            T(after="""
              a = BankAccount("e", 10)
              try:
                  a.balance = 999
              except AttributeError:
                  print("AttributeError", a.balance)
              """, tag="corner", note="balance 唯讀", expect="AttributeError 10"),
            T(after="""
              a = BankAccount("f", 10)
              h = a.history
              h.append(("hack", 1))
              print(a.history)
              """, tag="corner", note="history 回傳副本", expect="[]"),
            T(after="""
              a, b = BankAccount("a", 100), BankAccount("b")
              a.transfer(b, 70)
              try:
                  a.transfer(b, 31)
              except InsufficientFunds:
                  print("fail")
              print(a.balance, b.balance, a.history, b.history)
              """, note="轉帳成功與失敗", expect="fail\n30 70 [('transfer_out', 70)] [('transfer_in', 70)]"),
            T(after="""
              a = BankAccount("a", 100)
              for bad in ["b", None, 5]:
                  try:
                      a.transfer(bad, 10)
                  except TypeError:
                      print("TypeError", a.balance)
              """, tag="corner", note="轉帳對象型別錯誤", expect="TypeError 100\nTypeError 100\nTypeError 100"),
            T(after="""
              start = BankAccount.count
              BankAccount("x"); BankAccount("y", 5)
              try:
                  BankAccount("z", -1)
              except ValueError:
                  print("ValueError")
              print(BankAccount.count - start)
              """, tag="corner", note="建立失敗不計數", expect="ValueError\n2"),
            T(after="""
              print(issubclass(InsufficientFunds, Exception), repr(BankAccount("O'Neil", 1.5)))
              """, tag="corner", note="repr 要正確處理引號與 float", expect="True BankAccount(\"O'Neil\", 1.5)"),
            T(after="""
              a = BankAccount("self", 50)
              a.transfer(a, 20)
              print(a.balance, a.history)
              """, tag="corner", note="轉給自己：餘額不變，兩筆紀錄", expect="50 [('transfer_out', 20), ('transfer_in', 20)]"),
        ],
        hints=["`@property` 只寫 getter 不寫 setter，就是唯讀。", "repr 用 `{self.owner!r}` 才會正確加引號。",
               "類別屬性要用 `BankAccount.count += 1` 修改，而且放在驗證之後。"],
        wrong=[r'''
        class InsufficientFunds(Exception):
            pass
        class BankAccount:
            count = 0
            def __init__(self, owner, balance=0):
                BankAccount.count += 1
                if balance < 0:
                    raise ValueError
                self.owner, self.balance, self.history = owner, balance, []
            def deposit(self, amount):
                if amount <= 0: raise ValueError
                self.balance += amount; self.history.append(("deposit", amount)); return self.balance
            def withdraw(self, amount):
                if amount <= 0: raise ValueError
                if amount > self.balance: raise InsufficientFunds
                self.balance -= amount; self.history.append(("withdraw", amount)); return self.balance
            def transfer(self, other, amount):
                self.withdraw(amount); other.deposit(amount)
            def __repr__(self):
                return f"BankAccount('{self.owner}', {self.balance})"
        '''],
        mode="func",
    ),
    exercise(
        "o2-vector", "N 維向量（運算子多載）", 3, r'''
        實作**不可變**的 `Vector` 類別：

        | 語法 | 規格 |
        |---|---|
        | `Vector(1, 2, 3)` | 任意維度（可為 0 維）；元素存成 `float` 以外的原樣數值即可 |
        | `repr(v)` | `Vector(1, 2, 3)`，0 維為 `Vector()` |
        | `len(v)`、`v[i]`、`for x in v` | 維度、索引（支援負索引）、迭代 |
        | `v + w`、`v - w` | 逐元素運算；維度不同拋 `ValueError` |
        | `v * k`、`k * v` | 純量乘法（`k` 為 `int` 或 `float`）；`v * w`（兩向量相乘）要拋 `TypeError` |
        | `v @ w` | 內積；維度不同拋 `ValueError` |
        | `abs(v)` | 長度（歐氏範數），回傳 float |
        | `bool(v)` | 零向量（或 0 維）為 `False` |
        | `v == w` | 維度與元素都相同；和非 Vector 比較回傳 `False`（不可拋錯） |
        | `hash(v)` | 可雜湊，且相等的向量雜湊相同 |
        | `v + 1`、`v - "a"` | 拋 `TypeError`（提示：回傳 `NotImplemented`） |

        ### 範例測試程式
        ```python
        v, w = Vector(1, 2), Vector(3, 4)
        print(v + w, w - v, v * 2, 3 * v, v @ w, abs(w))
        ```
        ### 輸出
        ```text
        Vector(4, 6) Vector(2, 2) Vector(2, 4) Vector(3, 6) 11 5.0
        ```
        ''',
        r'''
        class Vector:
            def __init__(self, *components):
                self._c = tuple(components)
        ''',
        r'''
        import math
        from numbers import Real


        class Vector:
            __slots__ = ("_c",)

            def __init__(self, *components):
                self._c = tuple(components)

            def __repr__(self):
                return f"Vector({', '.join(map(repr, self._c))})"

            def __len__(self):
                return len(self._c)

            def __getitem__(self, i):
                return self._c[i]

            def __iter__(self):
                return iter(self._c)

            def _same_dim(self, other):
                if len(self) != len(other):
                    raise ValueError("維度不同")

            def __add__(self, other):
                if not isinstance(other, Vector):
                    return NotImplemented
                self._same_dim(other)
                return Vector(*(a + b for a, b in zip(self, other)))

            def __sub__(self, other):
                if not isinstance(other, Vector):
                    return NotImplemented
                self._same_dim(other)
                return Vector(*(a - b for a, b in zip(self, other)))

            def __mul__(self, k):
                if isinstance(k, Real) and not isinstance(k, bool):
                    return Vector(*(a * k for a in self))
                return NotImplemented

            __rmul__ = __mul__

            def __matmul__(self, other):
                if not isinstance(other, Vector):
                    return NotImplemented
                self._same_dim(other)
                return sum(a * b for a, b in zip(self, other))

            def __abs__(self):
                return math.sqrt(sum(a * a for a in self))

            def __bool__(self):
                return any(self._c)

            def __eq__(self, other):
                return isinstance(other, Vector) and self._c == other._c

            def __hash__(self):
                return hash(self._c)
        ''',
        [
            T(after="""
              v, w = Vector(1, 2), Vector(3, 4)
              print(v + w, w - v, v * 2, 3 * v, v @ w, abs(w))
              """, tag="sample", expect="Vector(4, 6) Vector(2, 2) Vector(2, 4) Vector(3, 6) 11 5.0"),
            T(after="""
              z = Vector()
              print(repr(z), len(z), bool(z), abs(z), z + z, z @ z)
              """, tag="corner", note="0 維向量", expect="Vector() 0 False 0.0 Vector() 0"),
            T(after="""
              v = Vector(1, -2.5, 3)
              print(v[0], v[-1], list(v), len(v), 2.5 in v, -2.5 in v)
              """, note="索引、迭代、in", expect="1 3 [1, -2.5, 3] 3 False True"),
            T(after="""
              for a, b in [(Vector(1, 2), Vector(1, 2, 3)), (Vector(1), Vector())]:
                  for op in ("+", "-", "@"):
                      try:
                          eval(f"a {op} b")
                      except ValueError:
                          print("ValueError", end=" ")
              print()
              """, tag="corner", note="維度不符", expect="ValueError ValueError ValueError ValueError ValueError ValueError"),
            T(after="""
              v = Vector(1, 2)
              for expr in ["v + 1", "1 + v", "v - 'a'", "v * v", "v * 'x'", "v @ 3"]:
                  try:
                      eval(expr)
                      print("no error:", expr)
                  except TypeError:
                      print("TypeError")
              """, tag="corner", note="不支援的運算要 TypeError", expect="TypeError\nTypeError\nTypeError\nTypeError\nTypeError\nTypeError"),
            T(after="""
              print(Vector(1, 2) == Vector(1, 2), Vector(1, 2) == Vector(1, 2, 0), Vector(1, 2) == (1, 2), Vector() == None)
              print(Vector(1, 2) != Vector(2, 1), Vector(1.0, 2) == Vector(1, 2))
              """, tag="corner", note="相等比較：不同型別回傳 False", expect="True False False False\nTrue True"),
            T(after="""
              s = {Vector(1, 2), Vector(1, 2), Vector(1.0, 2.0), Vector(2, 1)}
              d = {Vector(0, 0): "origin"}
              print(len(s), d[Vector(0, 0)])
              """, tag="corner", note="可雜湊、相等者雜湊相同", expect="2 origin"),
            T(after="""
              print(bool(Vector(0, 0, 0)), bool(Vector(0, 0.0, 1e-300)), bool(Vector(-1)))
              """, tag="corner", note="零向量為 False", expect="False True True"),
            T(after="""
              v = Vector(1, 2)
              w = v
              w += Vector(1, 1)
              print(v, w, v is w)
              """, tag="corner", note="不可變：+= 要產生新物件", expect="Vector(1, 2) Vector(2, 3) False"),
            T(after="""
              print(Vector(1, 2) * 0.5, Vector(3, 4) * 0, abs(Vector(1, 1, 1, 1)), Vector(2, 3) @ Vector(-3, 2))
              """, note="浮點純量、零向量、正交", expect="Vector(0.5, 1.0) Vector(0, 0) 2.0 0"),
            T(after="""
              print(sum([Vector(1, 1), Vector(2, 2)], Vector(0, 0)), Vector(*range(5)))
              """, note="搭配 sum 與解包建立", expect="Vector(3, 3) Vector(0, 1, 2, 3, 4)"),
        ],
        hints=["不支援的型別要 `return NotImplemented`，Python 會自動轉成 TypeError。", "`__rmul__` 讓 `3 * v` 能運作。",
               "內部用 tuple 儲存，`__eq__` 和 `__hash__` 都可以直接借用 tuple 的。", "定義了 `__eq__` 就必須自己定義 `__hash__`。"],
        wrong=[r'''
        import math
        class Vector:
            def __init__(self, *c):
                self.c = list(c)
            def __repr__(self):
                return f"Vector({', '.join(map(str, self.c))})"
            def __len__(self): return len(self.c)
            def __getitem__(self, i): return self.c[i]
            def __add__(self, o):
                return Vector(*(a + b for a, b in zip(self, o)))
            def __sub__(self, o):
                return Vector(*(a - b for a, b in zip(self, o)))
            def __mul__(self, k): return Vector(*(a * k for a in self))
            __rmul__ = __mul__
            def __matmul__(self, o): return sum(a * b for a, b in zip(self, o))
            def __abs__(self): return math.sqrt(sum(a * a for a in self))
            def __eq__(self, o): return self.c == o.c
            def __hash__(self): return hash(tuple(self.c))
        '''],
        mode="func",
    ),
    exercise(
        "o3-shapes", "形狀家族（ABC、繼承、排序）", 2, r'''
        實作：

        1. 抽象基底類別 `Shape`（繼承 `abc.ABC`），抽象方法 `area()`、`perimeter()`。直接 `Shape()` 必須拋 `TypeError`。
           - `Shape` 提供一般方法 `describe()`，回傳 `"{類別名稱} area={面積:.2f} perimeter={周長:.2f}"`
           - `Shape` 之間可以用 `<`、`<=`、`>`、`>=` 依**面積**比較（提示：`functools.total_ordering`），因此可以 `sorted()`
        2. `Circle(r)`、`Rectangle(w, h)`、`Square(side)`（`Square` **繼承** `Rectangle`）
           - 任何邊長/半徑 `<= 0` 拋 `ValueError`
           - `repr`：`Circle(r=1)`、`Rectangle(w=2, h=3)`、`Square(side=2)`

        ### 範例測試程式
        ```python
        shapes = [Rectangle(2, 3), Circle(1), Square(2)]
        for s in sorted(shapes):
            print(s.describe())
        ```
        ### 輸出
        ```text
        Circle area=3.14 perimeter=6.28
        Square area=4.00 perimeter=8.00
        Rectangle area=6.00 perimeter=10.00
        ```
        ''',
        r'''
        import math
        from abc import ABC, abstractmethod
        from functools import total_ordering


        class Shape(ABC):
            ...
        ''',
        r'''
        import math
        from abc import ABC, abstractmethod
        from functools import total_ordering


        @total_ordering
        class Shape(ABC):
            @abstractmethod
            def area(self): ...

            @abstractmethod
            def perimeter(self): ...

            def describe(self):
                return f"{type(self).__name__} area={self.area():.2f} perimeter={self.perimeter():.2f}"

            def __eq__(self, other):
                if not isinstance(other, Shape):
                    return NotImplemented
                return self.area() == other.area()

            def __lt__(self, other):
                if not isinstance(other, Shape):
                    return NotImplemented
                return self.area() < other.area()

            __hash__ = object.__hash__

            @staticmethod
            def _positive(*values):
                if any(v <= 0 for v in values):
                    raise ValueError("尺寸必須為正")


        class Circle(Shape):
            def __init__(self, r):
                self._positive(r)
                self.r = r

            def area(self):
                return math.pi * self.r ** 2

            def perimeter(self):
                return 2 * math.pi * self.r

            def __repr__(self):
                return f"Circle(r={self.r!r})"


        class Rectangle(Shape):
            def __init__(self, w, h):
                self._positive(w, h)
                self.w, self.h = w, h

            def area(self):
                return self.w * self.h

            def perimeter(self):
                return 2 * (self.w + self.h)

            def __repr__(self):
                return f"Rectangle(w={self.w!r}, h={self.h!r})"


        class Square(Rectangle):
            def __init__(self, side):
                super().__init__(side, side)

            def __repr__(self):
                return f"Square(side={self.w!r})"
        ''',
        [
            T(after="""
              shapes = [Rectangle(2, 3), Circle(1), Square(2)]
              for s in sorted(shapes):
                  print(s.describe())
              """, tag="sample", expect="Circle area=3.14 perimeter=6.28\nSquare area=4.00 perimeter=8.00\nRectangle area=6.00 perimeter=10.00"),
            T(after="""
              try:
                  Shape()
              except TypeError:
                  print("TypeError")
              """, tag="corner", note="抽象類別不可實例化", expect="TypeError"),
            T(after="""
              class Bad(Shape):
                  def area(self): return 1
              try:
                  Bad()
              except TypeError:
                  print("TypeError")
              """, tag="corner", note="子類別沒實作全部抽象方法也不行", expect="TypeError"),
            T(after="""
              for make in [lambda: Circle(0), lambda: Circle(-1), lambda: Rectangle(1, 0), lambda: Rectangle(-2, 3), lambda: Square(0)]:
                  try:
                      make()
                  except ValueError:
                      print("ValueError", end=" ")
              print()
              """, tag="corner", note="非正尺寸", expect="ValueError ValueError ValueError ValueError ValueError"),
            T(after="""
              print(Circle(1), Rectangle(2, 3.5), Square(2), [Square(1)])
              """, note="repr", expect="Circle(r=1) Rectangle(w=2, h=3.5) Square(side=2) [Square(side=1)]"),
            T(after="""
              sq = Square(3)
              print(isinstance(sq, Rectangle), isinstance(sq, Shape), sq.area(), sq.perimeter())
              """, note="繼承關係", expect="True True 9 12"),
            T(after="""
              print(Square(2) <= Rectangle(1, 4), Square(2) >= Rectangle(1, 4), Circle(1) > Square(1), Circle(1) < Square(2))
              """, tag="corner", note="面積相等時的 <= 與 >=", expect="True True True True"),
            T(after="""
              try:
                  Circle(1) < 5
              except TypeError:
                  print("TypeError")
              """, tag="corner", note="和非 Shape 比較要 TypeError", expect="TypeError"),
            T(after="""
              print(Circle(0.5).describe())
              print(Rectangle(0.1, 0.2).describe())
              """, tag="corner", note="小數尺寸與格式化", expect="Circle area=0.79 perimeter=3.14\nRectangle area=0.02 perimeter=0.60"),
            T(after="""
              s = sorted([Rectangle(1, 4), Square(2), Circle(0.1)])
              print(s)
              """, tag="corner", note="面積相同保持原順序（sorted 穩定）", expect="[Circle(r=0.1), Rectangle(w=1, h=4), Square(side=2)]"),
        ],
        hints=["`@total_ordering` 只要你定義 `__eq__` 和 `__lt__`。", "`Square.__init__` 呼叫 `super().__init__(side, side)`。",
               "`type(self).__name__` 取得實際的類別名稱。"],
        wrong=[r'''
        import math
        from functools import total_ordering
        @total_ordering
        class Shape:
            def area(self): raise NotImplementedError
            def perimeter(self): raise NotImplementedError
            def describe(self):
                return f"{type(self).__name__} area={self.area():.2f} perimeter={self.perimeter():.2f}"
            def __eq__(self, o): return self.area() == o.area()
            def __lt__(self, o): return self.area() < o.area()
        class Circle(Shape):
            def __init__(self, r):
                if r <= 0: raise ValueError
                self.r = r
            def area(self): return math.pi * self.r ** 2
            def perimeter(self): return 2 * math.pi * self.r
            def __repr__(self): return f"Circle(r={self.r})"
        class Rectangle(Shape):
            def __init__(self, w, h):
                if w <= 0 or h <= 0: raise ValueError
                self.w, self.h = w, h
            def area(self): return self.w * self.h
            def perimeter(self): return 2 * (self.w + self.h)
            def __repr__(self): return f"Rectangle(w={self.w}, h={self.h})"
        class Square(Rectangle):
            def __init__(self, side): super().__init__(side, side)
            def __repr__(self): return f"Square(side={self.w})"
        '''],
        mode="func",
    ),
    exercise(
        "o4-minstack", "MinStack（容器協定 + 繼承）", 2, r'''
        實作兩個類別：

        **`Stack`**
        - `push(x)`、`pop()`（回傳並移除頂端）、`peek()`（回傳頂端不移除）
        - 空堆疊 `pop()`/`peek()` 拋 `IndexError`
        - `len(s)`、`bool(s)`（空為 False）、`x in s`
        - `for x in s`：由**頂端到底部**迭代
        - `repr(s)`：`Stack([底, ..., 頂])`，例如 `Stack([1, 2, 3])`

        **`MinStack(Stack)`**：繼承 `Stack`，額外提供 `get_min()`，**O(1)** 回傳目前最小值，空時拋 `IndexError`。
        `repr` 為 `MinStack([...])`。

        > 注意：堆疊中可能有重複的最小值、也可能放入任何可比較的物件（如字串）。

        ### 範例測試程式
        ```python
        s = MinStack()
        for x in [5, 3, 7, 3]:
            s.push(x)
        print(s, s.get_min())
        print(s.pop(), s.get_min(), list(s))
        ```
        ### 輸出
        ```text
        MinStack([5, 3, 7, 3]) 3
        3 3 [7, 3, 5]
        ```
        ''',
        r'''
        class Stack:
            def __init__(self):
                self._items = []


        class MinStack(Stack):
            pass
        ''',
        r'''
        class Stack:
            def __init__(self):
                self._items = []

            def push(self, x):
                self._items.append(x)

            def pop(self):
                if not self._items:
                    raise IndexError("pop from empty stack")
                return self._items.pop()

            def peek(self):
                if not self._items:
                    raise IndexError("peek from empty stack")
                return self._items[-1]

            def __len__(self):
                return len(self._items)

            def __iter__(self):
                return reversed(self._items)

            def __contains__(self, x):
                return x in self._items

            def __repr__(self):
                return f"{type(self).__name__}({self._items!r})"


        class MinStack(Stack):
            def __init__(self):
                super().__init__()
                self._mins = []

            def push(self, x):
                super().push(x)
                self._mins.append(x if not self._mins or x < self._mins[-1] else self._mins[-1])

            def pop(self):
                x = super().pop()
                self._mins.pop()
                return x

            def get_min(self):
                if not self._mins:
                    raise IndexError("get_min from empty stack")
                return self._mins[-1]
        ''',
        [
            T(after="""
              s = MinStack()
              for x in [5, 3, 7, 3]:
                  s.push(x)
              print(s, s.get_min())
              print(s.pop(), s.get_min(), list(s))
              """, tag="sample", expect="MinStack([5, 3, 7, 3]) 3\n3 3 [7, 3, 5]"),
            T(after="""
              s = Stack()
              print(s, len(s), bool(s), 1 in s, list(s))
              """, tag="corner", note="空堆疊", expect="Stack([]) 0 False False []"),
            T(after="""
              for cls in (Stack, MinStack):
                  s = cls()
                  for name in ("pop", "peek") + (("get_min",) if cls is MinStack else ()):
                      try:
                          getattr(s, name)()
                      except IndexError:
                          print(cls.__name__, name, "IndexError")
              """, tag="corner", note="空時的 IndexError",
              expect="Stack pop IndexError\nStack peek IndexError\nMinStack pop IndexError\nMinStack peek IndexError\nMinStack get_min IndexError"),
            T(after="""
              s = MinStack()
              for x in [2, 1, 1, 3]:
                  s.push(x)
              out = []
              while s:
                  out.append((s.get_min(), s.pop()))
              print(out)
              """, tag="corner", note="重複的最小值：彈出一個 1 後最小值仍是 1", expect="[(1, 3), (1, 1), (1, 1), (2, 2)]"),
            T(after="""
              s = MinStack()
              for w in ["pear", "apple", "zoo"]:
                  s.push(w)
              print(s.get_min(), s.peek(), "apple" in s, "kiwi" in s)
              """, note="字串", expect="apple zoo True False"),
            T(after="""
              s = MinStack()
              for x in range(10, 0, -1):
                  s.push(x)
              print(s.get_min(), [s.pop() for _ in range(5)], s.get_min())
              """, note="遞減推入", expect="1 [1, 2, 3, 4, 5] 6"),
            T(after="""
              print(issubclass(MinStack, Stack), isinstance(MinStack(), Stack))
              s = Stack(); t = Stack()
              s.push(1)
              print(len(t), t)
              """, tag="corner", note="繼承、實例之間不能共用資料", expect="True True\n0 Stack([])"),
            T(after="""
              s = MinStack()
              s.push(0); s.push(-1); s.push(None if False else -1)
              s.pop(); s.pop()
              print(s.get_min(), s)
              """, tag="corner", note="最小值是 0（假值！）", expect="0 MinStack([0])"),
            T(after="""
              import time
              s = MinStack()
              t0 = time.perf_counter()
              for i in range(200000):
                  s.push(i)
                  s.get_min()
              print(s.get_min(), len(s), time.perf_counter() - t0 < 3)
              """, tag="stress", note="get_min 必須 O(1)（每次 min() 會逾時）", expect="0 200000 True"),
        ],
        hints=["另外維護一個「每一層的目前最小值」堆疊。", "`__iter__` 回傳 `reversed(self._items)`。",
               "`repr` 用 `type(self).__name__`，子類別就會自動顯示 MinStack。", "有了 `__len__`，`bool()` 自動可用。"],
        wrong=[r'''
        class Stack:
            def __init__(self): self._items = []
            def push(self, x): self._items.append(x)
            def pop(self): return self._items.pop()
            def peek(self): return self._items[-1]
            def __len__(self): return len(self._items)
            def __iter__(self): return reversed(self._items)
            def __contains__(self, x): return x in self._items
            def __repr__(self): return f"{type(self).__name__}({self._items!r})"
        class MinStack(Stack):
            def get_min(self):
                if not self._items: raise IndexError
                return min(self._items)
        '''],
        mode="func",
    ),
    exercise(
        "o5-temperature", "溫度類別（property、classmethod、比較）", 2, r'''
        實作 `Temperature`，內部只以**克氏 (Kelvin)** 儲存：

        - `Temperature(kelvin)`：小於 0 拋 `ValueError`
        - 類別方法 `from_celsius(c)`、`from_fahrenheit(f)`：替代建構子（子類別呼叫時要回傳子類別實例）
        - property `kelvin`、`celsius`、`fahrenheit`：**都可讀可寫**，寫入時同樣驗證不可低於絕對零度
          （`C = K − 273.15`、`F = C × 9/5 + 32`）
        - `repr`：`Temperature(273.15K)`，克氏值以 `:.2f` 格式化
        - `==`、`<`、`<=`、`>`、`>=`：依溫度比較，**差距小於 1e-9 視為相等**；與非 Temperature 比較：`==` 回 False，大小比較拋 TypeError
        - 可雜湊，且 `==` 的物件雜湊相同（提示：依 `round(kelvin, 6)` 雜湊）

        ### 範例測試程式
        ```python
        t = Temperature.from_celsius(100)
        print(t, round(t.fahrenheit, 2))
        t.fahrenheit = 32
        print(round(t.celsius, 2), t.kelvin)
        ```
        ### 輸出
        ```text
        Temperature(373.15K) 212.0
        0.0 273.15
        ```
        ''',
        r'''
        class Temperature:
            def __init__(self, kelvin):
                ...
        ''',
        r'''
        from functools import total_ordering


        @total_ordering
        class Temperature:
            EPS = 1e-9

            def __init__(self, kelvin):
                self.kelvin = kelvin

            @classmethod
            def from_celsius(cls, c):
                return cls(c + 273.15)

            @classmethod
            def from_fahrenheit(cls, f):
                return cls.from_celsius((f - 32) * 5 / 9)

            @property
            def kelvin(self):
                return self._k

            @kelvin.setter
            def kelvin(self, value):
                if value < 0:
                    raise ValueError("低於絕對零度")
                self._k = value

            @property
            def celsius(self):
                return self._k - 273.15

            @celsius.setter
            def celsius(self, value):
                self.kelvin = value + 273.15

            @property
            def fahrenheit(self):
                return self.celsius * 9 / 5 + 32

            @fahrenheit.setter
            def fahrenheit(self, value):
                self.celsius = (value - 32) * 5 / 9

            def __repr__(self):
                return f"{type(self).__name__}({self._k:.2f}K)"

            def __eq__(self, other):
                if not isinstance(other, Temperature):
                    return NotImplemented
                return abs(self._k - other._k) < self.EPS

            def __lt__(self, other):
                if not isinstance(other, Temperature):
                    return NotImplemented
                return self._k < other._k and not self == other

            def __hash__(self):
                return hash(round(self._k, 6))
        ''',
        [
            T(after="""
              t = Temperature.from_celsius(100)
              print(t, round(t.fahrenheit, 2))
              t.fahrenheit = 32
              print(round(t.celsius, 2), t.kelvin)
              """, tag="sample", expect="Temperature(373.15K) 212.0\n0.0 273.15"),
            T(after="""
              print(Temperature(0), Temperature.from_celsius(-273.15).kelvin)
              """, tag="corner", note="絕對零度本身合法", expect="Temperature(0.00K) 0.0"),
            T(after="""
              for make in [lambda: Temperature(-0.01), lambda: Temperature.from_celsius(-300), lambda: Temperature.from_fahrenheit(-460)]:
                  try:
                      make()
                  except ValueError:
                      print("ValueError")
              """, tag="corner", note="建構時低於絕對零度", expect="ValueError\nValueError\nValueError"),
            T(after="""
              t = Temperature(300)
              for attr, v in [("kelvin", -1), ("celsius", -274), ("fahrenheit", -500)]:
                  try:
                      setattr(t, attr, v)
                  except ValueError:
                      print("ValueError", t)
              """, tag="corner", note="setter 也要驗證，且失敗時值不變",
              expect="ValueError Temperature(300.00K)\nValueError Temperature(300.00K)\nValueError Temperature(300.00K)"),
            T(after="""
              print(round(Temperature.from_fahrenheit(-40).celsius, 6), Temperature.from_fahrenheit(-40) == Temperature.from_celsius(-40))
              """, note="-40 度交會點", expect="-40.0 True"),
            T(after="""
              a = Temperature.from_celsius(0.1 + 0.2)
              b = Temperature.from_celsius(0.3)
              print(a == b, a <= b, a >= b, a < b, a > b, len({a, b}))
              """, tag="corner", note="浮點誤差：要視為相等，且雜湊相同", expect="True True True False False 1"),
            T(after="""
              ts = [Temperature(300), Temperature.from_celsius(0), Temperature.from_fahrenheit(100)]
              print(sorted(ts), max(ts))
              """, note="排序", expect="[Temperature(273.15K), Temperature(300.00K), Temperature(310.93K)] Temperature(310.93K)"),
            T(after="""
              t = Temperature(10)
              print(t == 10, t != "10K")
              try:
                  t < 5
              except TypeError:
                  print("TypeError")
              """, tag="corner", note="與其他型別比較", expect="False True\nTypeError"),
            T(after="""
              class Kelvin(Temperature):
                  pass
              k = Kelvin.from_fahrenheit(212)
              print(type(k).__name__, k)
              """, tag="corner", note="classmethod 用 cls 建立 → 子類別正確", expect="Kelvin Kelvin(373.15K)"),
            T(after="""
              t = Temperature(1)
              t.celsius = 25
              print(t, round(t.fahrenheit, 6))
              """, note="寫入 celsius", expect="Temperature(298.15K) 77.0"),
        ],
        hints=["`__init__` 裡寫 `self.kelvin = kelvin`，就能重用 setter 的驗證。", "`celsius` 的 setter 呼叫 `self.kelvin = ...` 來共用驗證。",
               "`from_celsius` 要用 `cls(...)` 而不是 `Temperature(...)`。"],
        wrong=[r'''
        class Temperature:
            def __init__(self, kelvin):
                if kelvin < 0: raise ValueError
                self.kelvin = kelvin
            @classmethod
            def from_celsius(cls, c): return Temperature(c + 273.15)
            @classmethod
            def from_fahrenheit(cls, f): return Temperature((f - 32) * 5 / 9 + 273.15)
            @property
            def celsius(self): return self.kelvin - 273.15
            @celsius.setter
            def celsius(self, v): self.kelvin = v + 273.15
            @property
            def fahrenheit(self): return self.celsius * 9 / 5 + 32
            @fahrenheit.setter
            def fahrenheit(self, v): self.celsius = (v - 32) * 5 / 9
            def __repr__(self): return f"Temperature({self.kelvin:.2f}K)"
            def __eq__(self, o): return isinstance(o, Temperature) and self.kelvin == o.kelvin
            def __lt__(self, o): return self.kelvin < o.kelvin
            def __le__(self, o): return self.kelvin <= o.kelvin
            def __gt__(self, o): return self.kelvin > o.kelvin
            def __ge__(self, o): return self.kelvin >= o.kelvin
            def __hash__(self): return hash(self.kelvin)
        '''],
        mode="func",
    ),
]

UNIT = {
    "id": "oop", "num": 5, "title": "物件導向", "icon": "🏛️",
    "summary": "類別/實例屬性、property、繼承與 MRO、ABC、dunder methods、dataclass、組合",
    "lesson": LESSON, "quiz": QUIZ, "exercises": EXERCISES,
}
