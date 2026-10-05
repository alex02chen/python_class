# 🐍 Python 深入教學

純靜態的 Python 教學網站：6 個單元的深入教材、重點問答、30 道練習題（312 組測資，含大量邊界情況），
以及**在瀏覽器內直接執行與判題**的線上環境（[Pyodide](https://pyodide.org/)，支援 NumPy / Pandas）。不需要後端伺服器。

| 單元 | 內容 |
|---|---|
| 1. 基礎語法 | 物件模型、可變性、`is` vs `==`、整數與浮點陷阱、`Decimal`、字串切片、f-string 格式規格 |
| 2. 流程控制 | 真值、短路求值、海象運算子、`match` 模式比對、迭代協定、`for-else`、例外處理 |
| 3. 資料結構 | list/tuple/dict/set 底層與複雜度、深淺拷貝、`collections`、`heapq`、`bisect`、排序 |
| 4. 函式定義 | 參數種類、預設值陷阱、LEGB 與閉包、裝飾器、產生器、遞迴與快取、型別提示 |
| 5. 物件導向 | 類別/實例屬性、property、繼承與 MRO、ABC、dunder methods、dataclass、組合 |
| 6. 套件應用 | import 機制、itertools/functools/datetime/json/re、NumPy 向量化、Pandas |

## 功能

- **可執行的範例**：課程中每段 Python 程式碼都能直接修改並執行。
- **重點問答**：每單元 10 題（選擇題即時批改 + 問答題參考答案）。
- **練習題與自動判題**：每題 8–12 組測資，分為「範例 / 一般 / 邊界 / 壓力」，可查看每組的輸入與期望輸出、下載 JSON。
  判題結果顯示 AC / WA / RE / TLE，並標出與期望輸出第一個不同的行。
- **隨機對拍**：每題附隨機測資產生器，平台用它出題，拿你的程式與參考解答比對。
- **自由練習場**：任意程式碼 + 自訂標準輸入。
- 進度、程式碼自動儲存在瀏覽器 (localStorage)；支援深色模式與手機版面。
- 逾時保護：程式在 Web Worker 中執行，超過 10 秒自動中止（無窮迴圈不會卡住頁面）。

## 本機執行

Pyodide 需要透過 HTTP 載入（不能直接雙擊開啟 `index.html`）：

```bash
python3 -m http.server 8000
# 開啟 http://localhost:8000
```

第一次執行程式時會從 CDN 下載 Python 執行環境（約 10 MB），用到 Pandas 時另外下載。

## 部署到 GitHub Pages

Repo 的 **Settings → Pages → Build and deployment**，Source 選 *Deploy from a branch*，
選擇要發布的分支與 `/ (root)` 資料夾即可。網站就是根目錄的 `index.html`。

## 專案結構

```text
index.html          單頁應用外殼
css/style.css       樣式（淺色/深色主題、RWD）
js/app.js           路由與畫面：首頁、單元、問答、練習題、練習場
js/runner.js        主執行緒端的執行器：排隊、逾時中止並重建 worker、判題
js/worker.js        Web Worker：載入 Pyodide、依 import 自動載入套件
py/harness.py       判題核心（瀏覽器與建置腳本共用同一份）
course/lessons/*.md 各單元的教材內容（Markdown，```python 區塊會變成可執行範例）
course/u*.py        問答、練習題與測資的原始檔（每單元一個檔案）
course/common.py    撰寫教材用的輔助函式
tools/build.py      建置：產生期望輸出並驗證 → data/course.js
data/course.js      建置產物（已提交，網站直接載入）
```

## 新增或修改題目

教材寫在 `course/lessons/*.md`，問答與題目寫在 `course/u*.py`，修改後執行：

```bash
python3 tools/build.py            # 需要 pandas（單元六的題目），pip install pandas
```

建置腳本會：

1. 用**參考解答**跑每組測資，產生期望輸出（不用手寫，避免錯誤）。
2. 若測資有手寫的 `expect=`，與參考解答的輸出交叉比對。
3. 用隨機產生器跑 30 組資料，確認參考解答不會出錯。
4. 確認每個 `wrong=`（常見錯誤寫法）至少會在一組測資上失敗——證明測資真的抓得到那個 bug。

5. 教材中每一段 Python 範例都會實際執行一次，不允許出現未預期的錯誤。

任何一項失敗都會中止建置。題目格式範例：

```python
exercise(
    "x1-sum", "兩數相加", 1,
    statement="讀入兩個整數，輸出它們的和。",
    starter="a, b = map(int, input().split())\n",
    solution="a, b = map(int, input().split())\nprint(a + b)\n",
    tests=[
        T("1 2\n", tag="sample", expect="3"),
        T("-5 5\n", tag="corner", note="和為 0"),
        T(f"{10**30} 1\n", tag="corner", note="大數"),
    ],
    gen="def gen(rng):\n    return f'{rng.randint(-9, 9)} {rng.randint(-9, 9)}\\n'\n",
    wrong=["a, b = input().split()\nprint(a + b)\n"],   # 忘了轉 int：字串相接
)
```

「函式題」(`mode="func"`) 的測資用 `after=` 提供測試程式，它會在使用者程式碼之後、於同一命名空間執行。
