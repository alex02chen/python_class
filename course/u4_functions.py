from common import T, choice, exercise, lesson, md, qa

LESSON = lesson("functions")

QUIZ = [
    choice("下列程式第二次呼叫印出？\n```python\ndef f(x, acc=[]):\n    acc.append(x)\n    return acc\nf(1)\nprint(f(2))\n```",
           ["`[2]`", "`[1, 2]`", "`[1]`", "`TypeError`"], 1, "預設值在定義時建立一次，之後所有呼叫共用同一個 list。"),
    choice("`[f() for f in [lambda: i for i in range(3)]]` 的結果？", ["`[0, 1, 2]`", "`[2, 2, 2]`", "`[0, 0, 0]`", "`NameError`"], 1,
           "閉包延遲綁定：lambda 被呼叫時才查找 i，此時 i 已是 2。"),
    choice("`def f(a, /, b, *, c)` 中，下列哪個呼叫合法？", ["`f(1, 2, 3)`", "`f(a=1, b=2, c=3)`", "`f(1, b=2, c=3)`", "`f(1, 2, c=3, d=4)`"], 2,
           "a 只能用位置、c 只能用關鍵字、b 兩者皆可。"),
    choice("呼叫產生器函式 `g = gen()` 時，函式本體會？", ["立即執行到結束", "執行到第一個 yield", "完全不執行", "拋出 StopIteration"], 2,
           "呼叫只會建立產生器物件，第一次 `next(g)` 時才開始執行到第一個 `yield`。"),
    choice("裝飾器內使用 `functools.wraps(func)` 的主要目的？", ["加速執行", "保留原函式的名稱、docstring 等中繼資料", "讓裝飾器可以接收參數", "快取結果"], 1,
           "沒有 `wraps` 的話，被裝飾函式的 `__name__` 會變成 `wrapper`，影響除錯、文件與某些框架的行為。"),
    choice("下列哪個會造成 `UnboundLocalError`？",
           ["函式內只讀取全域變數 x", "函式內先 `print(x)` 再 `x = 1`", "函式內 `global x; x += 1`", "閉包內 `nonlocal x; x += 1`"], 1,
           "只要函式中有對 x 賦值，x 就是區域變數，賦值前讀取會出錯。"),
    choice("`@a\n@b\ndef f(): ...` 等同於？", ["`f = a(b(f))`", "`f = b(a(f))`", "`f = a(f); f = b(f)` 以外的順序", "`f = (a, b)(f)`"], 0,
           "裝飾器由下往上套用，最靠近函式的先套。"),
    qa("什麼是閉包 (closure)？它和全域變數相比有什麼好處？",
       "閉包是「內層函式 + 它所引用的外層函式變數」的組合；即使外層函式已經返回，內層函式仍能存取那些變數（存放於 `__closure__` 的 cell 中）。\n\n"
       "好處：狀態被**封裝**在函式內部，不會污染全域命名空間，也能建立多個彼此獨立的實例（如多個計數器）。"),
    qa("為什麼深度遞迴在 Python 中容易出問題？有哪些解法？",
       "CPython 每次呼叫都會建立 frame，且預設遞迴深度上限約 1000，超過會 `RecursionError`；Python 也不做尾遞迴最佳化。\n\n"
       "解法：(1) 改寫為迴圈 + 顯式堆疊 (list)；(2) 用 `lru_cache` 減少重複呼叫（不減少深度）；"
       "(3) `sys.setrecursionlimit` 調高上限（有 C stack 溢位而崩潰的風險，非根本解）。"),
    qa("比較 list comprehension 與 generator expression，何時用哪個？",
       "`[...]` 立刻建立完整 list，可多次迭代、可索引；`(...)` 是惰性的，一次產生一個，記憶體 O(1)，但只能迭代一次。\n\n"
       "只需要走一遍（如 `sum(x*x for x in data)`）或資料量很大/無限時用產生器；需要重複使用、索引、取長度時用 list。"),
]

EXERCISES = [
    exercise(
        "f1-fib", "費氏數列：快、深、會報錯", 2, r'''
        實作函式 `fib(n)`，回傳第 `n` 項費氏數（`fib(0) = 0`、`fib(1) = 1`）。

        要求：
        1. `n` 最大到 **20000**，結果是精確整數（Python int 無上限）。
        2. 同一程式中會**大量重複呼叫**，每次都要快。
        3. `n` 為負數時，拋出 `ValueError`；`n` 不是 `int`（包括 `bool`、`float`）時，拋出 `TypeError`。

        > 這是「函式題」：你只需要定義 `fib`，測試程式會在你的程式碼之後呼叫它並印出結果。
        > 想想看：天真的遞迴會怎樣？加上 `@lru_cache` 的遞迴，在 n = 20000 時又會怎樣？

        ### 範例測試程式
        ```python
        print(fib(10))
        print(fib(0), fib(1), fib(2))
        ```
        ### 輸出
        ```text
        55
        0 1 1
        ```
        ''',
        r'''
        def fib(n):
            ...
        ''',
        r'''
        _memo = [0, 1]

        def fib(n):
            if type(n) is not int:
                raise TypeError("n 必須是 int")
            if n < 0:
                raise ValueError("n 必須 >= 0")
            while len(_memo) <= n:
                _memo.append(_memo[-1] + _memo[-2])
            return _memo[n]
        ''',
        [
            T(after="print(fib(10))\nprint(fib(0), fib(1), fib(2))", tag="sample", expect="55\n0 1 1"),
            T(after="print([fib(i) for i in range(15)])", note="前 15 項"),
            T(after="print(fib(90))", note="超過 32 位元整數", expect="2880067194370816120"),
            T(after="print(fib(40))", tag="corner", note="天真遞迴需要約 3 億次呼叫 → 逾時", expect="102334155"),
            T(after="print(len(str(fib(20000))))", tag="corner", note="n=20000：遞迴 + lru_cache 會 RecursionError", expect="4180"),
            T(after="print(sum(fib(i) for i in range(3000)) % 1000000007)", tag="stress", note="大量重複呼叫"),
            T(after="""
              for bad in [-1, -100]:
                  try:
                      fib(bad)
                  except ValueError:
                      print("ValueError")
              """, tag="corner", note="負數要 ValueError", expect="ValueError\nValueError"),
            T(after="""
              for bad in [2.0, "3", True, None]:
                  try:
                      fib(bad)
                      print("沒有報錯", repr(bad))
                  except TypeError:
                      print("TypeError")
              """, tag="corner", note="bool 是 int 的子類別！要特別排除", expect="TypeError\nTypeError\nTypeError\nTypeError"),
            T(after="print(fib(5000) % 10**9, fib(100))", note="先算大的再算小的"),
        ],
        gen=r'''
        def gen(rng):
            ns = [rng.randint(0, 3000) for _ in range(rng.randint(1, 5))]
            return {"after": f"print([fib(n) % 1000003 for n in {ns}])"}
        ''',
        hints=["迭代法 + 一個模組層級的 list 當快取，既無遞迴深度問題又能重複利用。",
               "`isinstance(True, int)` 是 True，要用 `type(n) is int` 排除 bool。"],
        wrong=[r'''
        from functools import lru_cache
        @lru_cache(None)
        def fib(n):
            if n < 0:
                raise ValueError
            return n if n < 2 else fib(n - 1) + fib(n - 2)
        '''],
        mode="func",
    ),
    exercise(
        "f2-flatten", "攤平任意深度的巢狀結構", 2, r'''
        實作 `flatten(obj)`：把任意深度巢狀的 `list` 與 `tuple` 攤平成一個 `list`，保留原本由左到右的順序。

        - 只有 `list` 和 `tuple` 需要展開；**字串、dict、set、數字、None 等都視為單一元素**（字串不能被拆成字元！）
        - 巢狀深度可能高達 **10 萬層**（遞迴會 `RecursionError`）
        - 不可修改傳入的物件

        ### 範例測試程式
        ```python
        print(flatten([1, [2, (3, "ab")], [[[]]], 4]))
        ```
        ### 輸出
        ```text
        [1, 2, 3, 'ab', 4]
        ```
        ''',
        r'''
        def flatten(obj):
            ...
        ''',
        r'''
        def flatten(obj):
            result = []
            stack = [iter([obj])]
            while stack:
                for item in stack[-1]:
                    if isinstance(item, (list, tuple)):
                        stack.append(iter(item))
                        break
                    result.append(item)
                else:
                    stack.pop()
            return result
        ''',
        [
            T(after='print(flatten([1, [2, (3, "ab")], [[[]]], 4]))', tag="sample", expect="[1, 2, 3, 'ab', 4]"),
            T(after="print(flatten([]))", tag="corner", note="空 list", expect="[]"),
            T(after="print(flatten([[], [[]], ([],)]))", tag="corner", note="全是空的容器", expect="[]"),
            T(after="print(flatten(5))", tag="corner", note="最外層就不是容器", expect="[5]"),
            T(after='print(flatten(["hello", ["", "x"]]))', tag="corner", note="字串（含空字串）不可拆", expect="['hello', '', 'x']"),
            T(after='print(flatten([{"a": 1}, {2, 3}, None, 0, False]))', tag="corner", note="dict/set/None/0/False 都是元素",
              expect="[{'a': 1}, {2, 3}, None, 0, False]"),
            T(after="print(flatten((1, (2, [3, (4,)]))))", note="tuple 與 list 混合", expect="[1, 2, 3, 4]"),
            T(after="""
              x = [1, [2, 3]]
              flatten(x)
              print(x)
              """, tag="corner", note="不能修改輸入", expect="[1, [2, 3]]"),
            T(after="""
              deep = [0]
              for i in range(1, 100000):
                  deep = [i, deep]
              r = flatten(deep)
              print(len(r), r[:3], r[-1])
              """, tag="stress", note="深度 10 萬層", expect="100000 [99999, 99998, 99997] 0"),
            T(after="print(len(flatten([[i, [i]] for i in range(100000)])))", tag="stress", note="寬度很大", expect="200000"),
        ],
        gen=r'''
        def gen(rng):
            def make(d):
                if d == 0 or rng.random() < 0.3:
                    return rng.choice([1, 2, "s", None, (), []])
                return rng.choice([list, tuple])(make(d - 1) for _ in range(rng.randint(0, 3)))
            return {"after": f"print(flatten({make(4)!r}))"}
        ''',
        hints=["遞迴版很直觀，但 10 萬層一定會爆。", "改用「迭代器的堆疊」：堆疊頂端是目前正在走的容器的 iterator。",
               "`for ... break ... else` 很適合「遇到子容器就暫停、走完才 pop」。"],
        wrong=[r'''
        def flatten(obj):
            if isinstance(obj, (list, tuple)):
                out = []
                for x in obj:
                    out.extend(flatten(x))
                return out
            return [obj]
        ''', r'''
        def flatten(obj):
            stack, out = [obj], []
            while stack:
                x = stack.pop()
                if isinstance(x, (list, tuple, str)) and not (isinstance(x, str) and len(x) <= 1):
                    stack.extend(reversed(x))
                else:
                    out.append(x)
            return out
        '''],
        mode="func",
    ),
    exercise(
        "f3-retry", "帶參數的重試裝飾器", 3, r'''
        實作裝飾器工廠 `retry(times, exceptions=(Exception,))`：

        - 被裝飾的函式最多**總共執行** `times` 次。
        - 若拋出的例外屬於 `exceptions`（一個例外類別的 tuple），就重試；成功就立刻回傳結果。
        - 若拋出的例外**不屬於** `exceptions`，立即往外拋，不再重試。
        - 全部 `times` 次都失敗，拋出**最後一次**的例外。
        - `times < 1` 時，在**套用裝飾器時**（`retry(0)` 被呼叫時）就拋出 `ValueError`。
        - 必須保留原函式的 `__name__` 與 `__doc__`（提示：`functools.wraps`），並正確傳遞所有位置與關鍵字引數。

        ### 範例測試程式
        ```python
        calls = 0
        @retry(3)
        def flaky():
            global calls
            calls += 1
            if calls < 3:
                raise ConnectionError("fail")
            return "ok"
        print(flaky(), calls)
        ```
        ### 輸出
        ```text
        ok 3
        ```
        ''',
        r'''
        import functools

        def retry(times, exceptions=(Exception,)):
            ...
        ''',
        r'''
        import functools

        def retry(times, exceptions=(Exception,)):
            if times < 1:
                raise ValueError("times 必須 >= 1")

            def decorator(func):
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    for attempt in range(1, times + 1):
                        try:
                            return func(*args, **kwargs)
                        except exceptions:
                            if attempt == times:
                                raise
                return wrapper
            return decorator
        ''',
        [
            T(after="""
              calls = 0
              @retry(3)
              def flaky():
                  global calls
                  calls += 1
                  if calls < 3:
                      raise ConnectionError("fail")
                  return "ok"
              print(flaky(), calls)
              """, tag="sample", expect="ok 3"),
            T(after="""
              n = 0
              @retry(3)
              def always():
                  global n
                  n += 1
                  raise KeyError(n)
              try:
                  always()
              except KeyError as e:
                  print("KeyError", e, "calls =", n)
              """, tag="corner", note="全部失敗：拋出最後一次的例外，總共 3 次", expect="KeyError 3 calls = 3"),
            T(after="""
              n = 0
              @retry(5, exceptions=(ValueError,))
              def wrong_kind():
                  global n
                  n += 1
                  raise TypeError("no")
              try:
                  wrong_kind()
              except TypeError:
                  print("TypeError after", n)
              """, tag="corner", note="非指定例外：不重試", expect="TypeError after 1"),
            T(after="""
              n = 0
              @retry(1)
              def once():
                  global n
                  n += 1
                  raise RuntimeError
              try:
                  once()
              except RuntimeError:
                  print("calls", n)
              """, tag="corner", note="times = 1：不重試", expect="calls 1"),
            T(after="""
              for t in [0, -3]:
                  try:
                      retry(t)
                      print("no error")
                  except ValueError:
                      print("ValueError")
              """, tag="corner", note="times < 1 在建立裝飾器時就報錯", expect="ValueError\nValueError"),
            T(after="""
              @retry(2)
              def add(a, b=10, *rest, scale=1, **kw):
                  "加法"
                  return (a + b + sum(rest)) * scale + len(kw)
              print(add(1), add(1, 2, 3, 4, scale=2, x=0, y=0))
              print(add.__name__, add.__doc__)
              """, note="引數傳遞與 wraps", expect="11 22\nadd 加法"),
            T(after="""
              @retry(3)
              def returns_none():
                  return None
              print(returns_none())
              """, tag="corner", note="成功但回傳 None", expect="None"),
            T(after="""
              n = 0
              @retry(4, exceptions=(KeyError, IndexError))
              def mixed():
                  global n
                  n += 1
                  if n == 1: raise KeyError
                  if n == 2: raise IndexError
                  return n
              print(mixed())
              """, note="多種可重試例外", expect="3"),
            T(after="""
              n = 0
              @retry(3, exceptions=(LookupError,))
              def sub():
                  global n
                  n += 1
                  if n < 3: raise KeyError
                  return "done"
              print(sub(), n)
              """, tag="corner", note="子類別例外也要被捕捉（KeyError 是 LookupError 的子類別）", expect="done 3"),
            T(after="""
              r = retry(2)
              @r
              def f(x): return x * 2
              @r
              def g(x): return x + 1
              print(f(5), g(5), f.__name__, g.__name__)
              """, tag="corner", note="同一個裝飾器重複使用", expect="10 6 f g"),
        ],
        hints=["三層：`retry(times)` → `decorator(func)` → `wrapper(*args, **kwargs)`。",
               "`except exceptions:` 可以直接接 tuple。", "在 except 區塊內單獨寫 `raise` 會重新拋出目前的例外。"],
        wrong=[r'''
        def retry(times, exceptions=(Exception,)):
            def decorator(func):
                def wrapper(*args, **kwargs):
                    for _ in range(times):
                        try:
                            return func(*args, **kwargs)
                        except exceptions as e:
                            last = e
                    raise last
                return wrapper
            return decorator
        '''],
        mode="func",
    ),
    exercise(
        "f4-batched", "惰性分批產生器", 2, r'''
        實作 `batched(iterable, n)`，把可迭代物件依序切成每批 `n` 個元素的 **tuple**，最後一批可能不足 `n` 個。（與 Python 3.12 的 `itertools.batched` 相同，但請自己實作，不要呼叫它。）

        - 必須是**惰性**的：能處理無限長的迭代器（如 `itertools.count()`）
        - `n < 1` 時，在**呼叫 `batched` 的當下**就拋出 `ValueError`（不是等到開始迭代）
        - 空的 iterable 不產生任何批次

        ### 範例測試程式
        ```python
        print(list(batched("ABCDEFG", 3)))
        ```
        ### 輸出
        ```text
        [('A', 'B', 'C'), ('D', 'E', 'F'), ('G',)]
        ```
        ''',
        r'''
        def batched(iterable, n):
            ...
        ''',
        r'''
        from itertools import islice

        def batched(iterable, n):
            if n < 1:
                raise ValueError("n 必須 >= 1")
            return _batched(iter(iterable), n)

        def _batched(it, n):
            while batch := tuple(islice(it, n)):
                yield batch
        ''',
        [
            T(after='print(list(batched("ABCDEFG", 3)))', tag="sample", expect="[('A', 'B', 'C'), ('D', 'E', 'F'), ('G',)]"),
            T(after="print(list(batched([], 2)))", tag="corner", note="空", expect="[]"),
            T(after="print(list(batched(range(6), 3)))", tag="corner", note="剛好整除：最後不能多一個空 tuple", expect="[(0, 1, 2), (3, 4, 5)]"),
            T(after="print(list(batched([1, 2], 5)))", tag="corner", note="n 大於長度", expect="[(1, 2)]"),
            T(after="print(list(batched('ab', 1)))", tag="corner", note="n = 1", expect="[('a',), ('b',)]"),
            T(after="""
              for n in [0, -1]:
                  try:
                      batched([1, 2, 3], n)
                      print("沒有立即報錯")
                  except ValueError:
                      print("ValueError")
              """, tag="corner", note="必須在呼叫時就報錯", expect="ValueError\nValueError"),
            T(after="""
              import itertools
              g = batched(itertools.count(), 4)
              print(next(g), next(g))
              """, tag="corner", note="無限迭代器：必須惰性", expect="(0, 1, 2, 3) (4, 5, 6, 7)"),
            T(after="""
              it = iter(range(10))
              b = batched(it, 3)
              print(next(b), next(it), next(b))
              """, tag="corner", note="與原迭代器共享進度", expect="(0, 1, 2) 3 (4, 5, 6)"),
            T(after="""
              b = batched({"x": 1, "y": 2, "z": 3}, 2)
              print(type(b).__name__ in ("generator", "batched"), list(b))
              """, note="dict 迭代的是 key", expect="True [('x', 'y'), ('z',)]"),
            T(after="print(sum(len(b) for b in batched(range(10**6), 1000)))", tag="stress", note="一百萬個元素", expect="1000000"),
        ],
        gen=r'''
        def gen(rng):
            return {"after": f"print(list(batched({list(range(rng.randint(0, 12)))}, {rng.randint(1, 5)})))"}
        ''',
        hints=["`yield` 函式的本體要到第一次 `next()` 才執行——所以參數檢查要放在「外層的一般函式」裡。",
               "`tuple(itertools.islice(it, n))` 一次取 n 個。", "記得先 `iter(iterable)`，否則對 list 用 islice 會一直從頭開始。"],
        wrong=[r'''
        def batched(iterable, n):
            if n < 1:
                raise ValueError
            batch = []
            for x in iterable:
                batch.append(x)
                if len(batch) == n:
                    yield tuple(batch)
                    batch = []
            if batch:
                yield tuple(batch)
        '''],
        mode="func",
    ),
    exercise(
        "f5-memoize", "自製快取裝飾器", 3, r'''
        實作裝飾器 `memoize`（不帶參數，直接 `@memoize` 使用），不可使用 `functools.lru_cache` / `cache`：

        1. 以「位置引數 + 關鍵字引數」為鍵快取回傳值。**關鍵字引數的順序不同應視為同一個呼叫**（`f(a=1, b=2)` 與 `f(b=2, a=1)`）。
        2. 若引數中有**不可雜湊**的值（如 list），不要快取，直接呼叫原函式（也不算 hit 或 miss）。
        3. 被裝飾的函式要有 `cache_info()` 方法，回傳 tuple `(hits, misses)`。
        4. 要有 `cache_clear()` 方法，清除快取並把計數歸零。
        5. 函式**拋出例外時不快取**（下次相同引數會重新呼叫），但仍算一次 miss。
        6. 回傳值為 `None` 也要被快取。
        7. 保留原函式的 `__name__`。

        ### 範例測試程式
        ```python
        @memoize
        def square(x):
            print("computing", x)
            return x * x
        print(square(4), square(4))
        print(square.cache_info())
        ```
        ### 輸出
        ```text
        computing 4
        16 16
        (1, 1)
        ```
        ''',
        r'''
        import functools

        def memoize(func):
            ...
        ''',
        r'''
        import functools

        def memoize(func):
            cache = {}
            stats = [0, 0]  # hits, misses

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                key = (args, frozenset(kwargs.items()))
                try:
                    hash(key)
                except TypeError:
                    return func(*args, **kwargs)
                if key in cache:
                    stats[0] += 1
                    return cache[key]
                stats[1] += 1
                result = func(*args, **kwargs)
                cache[key] = result
                return result

            def cache_clear():
                cache.clear()
                stats[0] = stats[1] = 0

            wrapper.cache_info = lambda: tuple(stats)
            wrapper.cache_clear = cache_clear
            return wrapper
        ''',
        [
            T(after="""
              @memoize
              def square(x):
                  print("computing", x)
                  return x * x
              print(square(4), square(4))
              print(square.cache_info())
              """, tag="sample", expect="computing 4\n16 16\n(1, 1)"),
            T(after="""
              @memoize
              def f(a, b):
                  print("call")
                  return a - b
              print(f(a=5, b=1), f(b=1, a=5), f.cache_info())
              """, tag="corner", note="關鍵字順序不同 → 同一個鍵", expect="call\n4 4 (1, 1)"),
            T(after="""
              @memoize
              def total(xs):
                  print("sum")
                  return sum(xs)
              print(total([1, 2]), total([1, 2]), total.cache_info())
              """, tag="corner", note="不可雜湊的引數：不快取也不計數", expect="sum\nsum\n3 3 (0, 0)"),
            T(after="""
              @memoize
              def nothing(x):
                  print("run")
              nothing(1); nothing(1)
              print(nothing.cache_info())
              """, tag="corner", note="回傳 None 也要快取", expect="run\n(1, 1)"),
            T(after="""
              n = 0
              @memoize
              def boom(x):
                  global n
                  n += 1
                  raise ValueError(x)
              for _ in range(2):
                  try:
                      boom(1)
                  except ValueError:
                      pass
              print(n, boom.cache_info())
              """, tag="corner", note="例外不快取，但算 miss", expect="2 (0, 2)"),
            T(after="""
              @memoize
              def fib(n):
                  return n if n < 2 else fib(n - 1) + fib(n - 2)
              print(fib(80), fib.cache_info())
              fib.cache_clear()
              print(fib.cache_info(), fib(10), fib.cache_info())
              """, note="遞迴使用、cache_clear", expect="23416728348467685 (78, 81)\n(0, 0) 55 (8, 11)"),
            T(after="""
              @memoize
              def g(x):
                  return type(x).__name__
              print(g(1), g(1.0), g(True), g.cache_info())
              """, tag="corner", note="1、1.0、True 相等且雜湊相同 → 視為同一個鍵（與 lru_cache 預設行為一致）",
              expect="int int int (2, 1)"),
            T(after="""
              @memoize
              def h(*args, **kw):
                  return len(args) + len(kw)
              print(h(), h(1, 2), h(1, x=2), h(1, x=2), h.__name__, h.cache_info())
              """, note="可變參數", expect="0 2 2 2 h (1, 3)"),
            T(after="""
              @memoize
              def a(x): return x
              @memoize
              def b(x): return -x
              print(a(1), b(1), a.cache_info(), b.cache_info())
              """, tag="corner", note="不同函式的快取彼此獨立", expect="1 -1 (0, 1) (0, 1)"),
            T(after="""
              @memoize
              def p(a, b=2):
                  return a * b
              print(p(3), p(3, 2), p(3, b=2), p.cache_info())
              """, tag="corner", note="（設計決策）位置/關鍵字/預設值的寫法不同就視為不同鍵", expect="6 6 6 (0, 3)"),
        ],
        hints=["鍵可以用 `(args, frozenset(kwargs.items()))`。", "先 `hash(key)`，若 TypeError 就跳過快取。",
               "函式也是物件，可以直接設屬性：`wrapper.cache_info = ...`。", "用 `key in cache` 判斷，不要用 `cache.get(key)` 判斷 None。"],
        wrong=[r'''
        def memoize(func):
            cache, stats = {}, [0, 0]
            def wrapper(*args, **kwargs):
                key = (args, tuple(kwargs.items()))
                try:
                    hash(key)
                except TypeError:
                    return func(*args, **kwargs)
                if cache.get(key) is not None:
                    stats[0] += 1
                    return cache[key]
                stats[1] += 1
                cache[key] = func(*args, **kwargs)
                return cache[key]
            wrapper.cache_info = lambda: tuple(stats)
            def clear():
                cache.clear(); stats[:] = [0, 0]
            wrapper.cache_clear = clear
            return wrapper
        '''],
        mode="func",
    ),
]

UNIT = {
    "id": "functions", "num": 4, "title": "函式定義", "icon": "🧩",
    "summary": "參數機制、預設值陷阱、LEGB 與閉包、裝飾器、產生器、遞迴與快取",
    "lesson": LESSON, "quiz": QUIZ, "exercises": EXERCISES,
}
