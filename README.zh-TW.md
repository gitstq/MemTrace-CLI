<div align="center">
  <pre>
███╗   ███╗███████╗███╗   ███╗████████╗██████╗  █████╗  ██████╗███████╗
████╗ ████║██╔════╝████╗ ████║╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝
██╔████╔██║█████╗  ██╔████╔██║   ██║   ██████╔╝███████║██║     █████╗
██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║   ██║   ██╔══██╗██╔══██║██║     ██╔══╝
██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║   ██║   ██║  ██║██║  ██║╚██████╗███████╗
╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝
  </pre>
  <h1>MemTrace-CLI</h1>
  <p><strong>輕量級終端 AI 代理共享記憶引擎</strong></p>
  <p>零外部依賴 · 純 Python 3.8+ · SQLite FTS5 全文檢索</p>

  <p>
    <a href="https://github.com/gitstq/MemTrace-CLI">
      <img src="https://img.shields.io/github/stars/gitstq/MemTrace-CLI?style=flat&logo=github" alt="GitHub stars">
    </a>
    <a href="https://github.com/gitstq/MemTrace-CLI/blob/main/LICENSE">
      <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License">
    </a>
    <a href="https://www.python.org/downloads/">
      <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
    </a>
    <a href="https://github.com/gitstq/MemTrace-CLI/issues">
      <img src="https://img.shields.io/github/issues/gitstq/MemTrace-CLI?style=flat&logo=github" alt="GitHub issues">
    </a>
    <a href="https://github.com/gitstq/MemTrace-CLI">
      <img src="https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey" alt="Platform">
    </a>
    <a href="https://github.com/gitstq/MemTrace-CLI/blob/main/Makefile">
      <img src="https://img.shields.io/badge/build-passing-brightgreen" alt="Build">
    </a>
  </p>
</div>

---

## 📖 專案介紹

**MemTrace-CLI** 是一個輕量級的終端 AI 代理共享記憶引擎，專為 AI 編碼代理（如 Claude、ChatGPT 等 CLI 工具）設計。它能夠自動**捕獲**、**索引**和**檢索** AI 代理的對話會話，將每一次互動轉化為持久化、可搜索的結構化記憶。

啟發自共享代理記憶（shared agent memory）的概念，MemTrace-CLI 將其重新詮釋為一個純粹的本地優先、跨平台的 CLI 工具——**零外部依賴**，僅需 Python 標準庫即可運行。

底層採用 **SQLite** 資料庫搭配 **FTS5** 全文檢索引擎，資料存儲在本機 `~/.memtrace/memory.db`，確保你的數據始終在你的掌控之中，無需網路連接，無需第三方服務。

---

## ✨ 核心特色

### 🧠 自動會話捕獲
- 可直接包裝任何 CLI 命令，自動捕獲其標準輸入/輸出作為會話記錄
- 支援 `user`、`assistant`、`tool`、`system` 四種訊息角色
- 完整的上下文管理器支援（`with` 語句），自動管理會話生命週期

### 🔍 SQLite FTS5 全文檢索
- 基於 SQLite FTS5 引擎的高效能全文檢索
- 支援模糊查詢、關鍵字匹配
- 當 FTS5 語法解析失敗時自動降級為 `LIKE` 模糊搜索
- 可依代理名稱、工作區、標籤、時間範圍進行多維度過濾

### 🏷️ 靈活的標籤系統
- 為每個會話添加任意數量的標籤
- 支援按標籤搜索、按標籤分組檢視
- 自動統計標籤使用頻率

### 📊 豐富的終端 UI
- 純 ANSI 渲染的儀表板（Dashboard），零依賴實現交互式瀏覽
- 會話列表、詳情檢視、搜索結果渲染
- 分頁瀏覽、即時搜索
- 統計資訊面板

### 📤 多格式匯出
- 支援 **Markdown**、**JSON**、**純文字** 三種匯出格式
- 可輸出到標準輸出或指定檔案

### 🔒 隱私優先 · 本地儲存
- 所有數據存放在 `~/.memtrace/memory.db`
- 無需網路連接，無數據外洩風險
- 支援資料庫目錄自定義

### 🧵 執行緒安全
- 基於 `threading.local()` 的執行緒本地連接管理
- WAL 日誌模式，支援並發讀寫
- `synchronous=NORMAL` 優化，兼顧效能與安全性

---

## 🚀 快速開始

### 系統需求

- **Python 3.8 或更高版本**
- 作業系統：Linux、macOS、Windows（跨平台支援）
- **無需任何第三方 Python 套件**

### 安裝方式

#### 方式一：從原始碼安裝（推薦）

```bash
# 克隆儲存庫
git clone https://github.com/gitstq/MemTrace-CLI.git
cd MemTrace-CLI

# 安裝套件（開發模式）
make install

# 或手動安裝
pip install -e .
```

#### 方式二：直接使用 pip

```bash
pip install memtrace-cli
```

> **注意：** 如果你在 Linux 系統上遇到 `--break-system-packages` 相關錯誤，請改用虛擬環境（venv）安裝。

### 驗證安裝

```bash
# 檢查版本
memtrace --version

# 初始化記憶庫
memtrace init
```

如果一切正常，你應該會看到類似以下的輸出：

```
✅ MemTrace store initialized at: /home/user/.memtrace/memory.db
   Sessions: 0
   Messages: 0
```

### 三分鐘快速入門

```bash
# 1️⃣ 捕獲一個會話（包裝 CLI 命令）
memtrace capture --agent claude --workspace my-project --tag python --tag debug \
  claude -p "Explain this Python function"

# 2️⃣ 搜索記憶
memtrace search "Python function" --tag python

# 3️⃣ 列出最近的會話
memtrace list --limit 10

# 4️⃣ 檢視會話詳情
memtrace show <session-id>

# 5️⃣ 查看統計資訊
memtrace stats

# 6️⃣ 啟動互動式儀表板
memtrace dashboard
```

### 使用 Python API

```python
from memtrace import MemoryStore, SessionCapture, MemorySearch

# 建立記憶庫（指定自定義目錄）
store = MemoryStore(db_dir="/path/to/custom/db")

# 建立並捕獲一個會話
with SessionCapture(store=store, agent="my-agent", workspace="docs") as cap:
    cap.log_user("幫我解釋這段程式碼")
    cap.log_assistant("這是一個排序演算法...")
    cap.log_tool("執行結果: OK", tool_name="pytest")

# 搜索記憶
results = store.search("排序演算法")
for msg in results:
    print(f"[{msg['role']}] {msg['content'][:100]}")

# 獲取統計資訊
stats = store.stats()
print(f"總共 {stats['sessions']} 個會話，{stats['messages']} 條訊息")
```

---

## 📖 使用指南

### CLI 命令參考

| 命令 | 功能 | 範例 |
|------|------|------|
| `capture` | 捕獲一個 AI 代理會話 | `memtrace capture claude -p "hello"` |
| `search`  | 全文檢索記憶內容 | `memtrace search "error handling"` |
| `list`    | 列出最近的會話 | `memtrace list --limit 20` |
| `show`    | 檢視指定會話的詳細資訊 | `memtrace show abc123def456` |
| `stats`   | 顯示記憶庫統計資訊 | `memtrace stats` |
| `export`  | 匯出會話（支援 markdown/json/text） | `memtrace export abc123 -o session.md` |
| `tags`    | 列出所有標籤及其使用次數 | `memtrace tags` |
| `dashboard` | 開啟互動式 TUI 儀表板 | `memtrace dashboard` |
| `init`    | 初始化記憶庫 | `memtrace init` |
| `delete`  | 刪除一個會話 | `memtrace delete abc123 -y` |

### 詳細使用說明

#### `capture` — 捕獲會話

包裝任何 CLI 命令，將其輸入輸出記錄為一個 AI 代理會話：

```bash
memtrace capture [options] <command> [args...]

# 選項
--agent TEXT       代理名稱（預設: cli）
--workspace TEXT   工作區名稱（預設: default）
--tag TEXT         添加標籤（可重複使用）

# 範例
memtrace capture --agent claude --workspace backend --tag bugfix \
  claude -p "Fix this memory leak in the cache module"

memtrace capture --agent chatgpt --tag research \
  chatgpt -p "Compare Redis and SQLite for local AI agent memory"
```

#### `search` — 全文檢索

跨所有會話進行全文檢索：

```bash
memtrace search [options] <query>

# 選項
--agent TEXT       按代理名稱過濾
--workspace TEXT   按工作區過濾
--tag TEXT         按標籤過濾
--days INT         時間範圍（最近 N 天）
--limit INT        最大結果數（預設: 20）

# 範例
memtrace search "binary search tree"
memtrace search "deployment" --agent claude --days 7
memtrace search "performance" --tag optimization --limit 50
```

#### `export` — 匯出會話

將會話匯出為指定格式：

```bash
memtrace export <session-id> [options]

# 選項
--format FORMAT    匯出格式: markdown（預設）, json, text
-o, --output FILE  輸出檔案（預設輸出到終端）

# 範例
memtrace export abc123def456 --format markdown -o session-report.md
memtrace export abc123def456 --format json
```

#### `dashboard` — 互動式儀表板

一個純終端的互動式儀表板，無需任何外部 TUI 函式庫：

```bash
memtrace dashboard
```

儀表板支援的操作：

| 按鍵 | 功能 |
|------|------|
| `n`   | 下一頁 |
| `p`   | 上一頁 |
| `s`   | 搜索會話 |
| `v`   | 檢視會話詳情 |
| `q`   | 退出 |
| `<ID>` | 直接輸入數字跳轉到該會話 |

### Python API 詳解

#### MemoryStore — 記憶庫核心

```python
from memtrace import MemoryStore

# 初始化
store = MemoryStore()                           # 預設目錄 ~/.memtrace
store = MemoryStore(db_dir="/custom/path")      # 自定義目錄

# 會話 CRUD
sid = store.create_session(agent="claude", workspace="project-x")
store.end_session(sid, summary="完成了重構", token_count=1500)
session = store.get_session(sid)
sessions = store.list_sessions(agent="claude", limit=10)
deleted = store.delete_session(sid)

# 訊息管理
msg_id = store.add_message(sid, "user", "你好", token_count=10)
store.add_message(sid, "assistant", "你好！有什麼可以幫你的嗎？")
messages = store.get_messages(sid)

# 標籤管理
store.add_tag(sid, "python")
store.add_tags(sid, ["debug", "performance"])
tags = store.get_tags(sid)
all_tags = store.list_all_tags()  # [(tag, count), ...]

# 全文檢索
results = store.search("演算法", limit=20)

# 統計資訊
stats = store.stats()
# 回傳: {sessions, messages, active_sessions, total_tokens, agents, db_size_bytes, db_path}
```

#### SessionCapture — 會話捕獲器

```python
from memtrace import SessionCapture, MemoryStore

store = MemoryStore()

# 方式一：上下文管理器（推薦）
with SessionCapture(store=store, agent="claude", workspace="project") as cap:
    cap.log_user("幫我優化這段 SQL")
    cap.log_assistant("使用索引可以優化...")
    cap.log_tool("EXPLAIN 結果: INDEX SCAN", tool_name="sqlite")
# 退出 with 區塊時自動結束會話

# 方式二：手動控制
cap = SessionCapture(store=store, agent="claude", auto_tag=["urgent"])
sid = cap.start(metadata={"task": "code-review"})
cap.log_user("Review this PR")
cap.log_assistant("Looks good, minor suggestions...")
cap.stop(summary="Code review completed")

# 方式三：一鍵包裝 CLI 命令
SessionCapture.quick_capture(
    ["claude", "-p", "Explain this Dockerfile"],
    agent="cli",
    workspace="devops",
    tags=["docker", "devops"],
)
```

#### MemorySearch — 高級檢索引擎

```python
from memtrace import MemorySearch

engine = MemorySearch(store)

# 多維度搜索
results = engine.search(
    query="machine learning",
    agent="claude",
    workspace="ml-project",
    tag="tutorial",
    days=30,
    limit=50,
)
# 回傳: {results: [...], total: int, query: str}

# 最近會話
recent = engine.recent_sessions(days=7, limit=20)

# 按標籤查找會話
tagged = engine.sessions_by_tag("bugfix")

# 查找相似會話
similar = engine.find_similar("abc123")

# 匯出會話
markdown = engine.export_session("abc123", format="markdown")
json_str = engine.export_session("abc123", format="json")

# 活動摘要
summary = engine.summarize(days=7)
```

---

## 💡 設計理念

### 為何選擇 SQLite？

SQLite 是市面上部署最廣泛的資料庫引擎，它不需要獨立的伺服器程序，不需要配置，不需要管理。對於 AI 代理的記憶管理場景，SQLite 提供了恰到好處的功能組合：

- **零配置**：開箱即用，無需安裝資料庫服務
- **嵌入式**：與應用程序存在於同一個行程中
- **FTS5**：內建全文檢索，無需額外的搜索基礎設施
- **跨平台**：在所有主流作業系統上行為一致
- **持久化**：數據安全地存儲在磁碟檔案中

### 零依賴的哲學

MemTrace-CLI 僅依賴 Python 標準庫，刻意避免引入任何第三方依賴。這項設計決策帶來了以下好處：

- **即裝即用**：`pip install` 後立即可用，無需處理依賴衝突
- **長期穩定**：不會因上游套件的 breaking change 而損壞
- **最小攻擊面**：更少的依賴意味著更小的安全風險
- **易於審計**：程式碼庫精簡，易於全面審查

### 共享記憶的價值

AI 編碼代理的效能極大程度上取決於上下文（context）。MemTrace-CLI 旨在解決以下痛點：

- **跨會話記憶**：讓 AI 代理記住你在數小時甚至數天前的對話中做過的決定
- **知識積累**：每一次互動都成為可檢索的知識庫
- **模式識別**：通過檢索過去的解決方案，加速問題解決
- **團隊協作**：共享的記憶庫允許團隊成員之間透明的知識傳遞

### 架構設計

```
┌─────────────────────────────────────────────────┐
│                   CLI Layer                      │
│   memtrace capture │ search │ list │ dashboard   │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│                 TUI Layer                        │
│   ANSI rendering │ pagination │ interaction      │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│               Search Engine                      │
│   MemorySearch │ FTS5 │ filters │ export         │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│             Session Management                   │
│   SessionCapture │ lifecycle │ wrap_command      │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│              Storage Layer                       │
│   MemoryStore │ SQLite │ FTS5 │ WAL │ thread-safe│
└─────────────────────────────────────────────────┘
```

### 資料庫 Schema

```sql
-- 會話表
CREATE TABLE sessions (
    id          TEXT PRIMARY KEY,           -- UUID (12字符)
    agent       TEXT NOT NULL DEFAULT 'unknown',
    workspace   TEXT NOT NULL DEFAULT 'default',
    started_at  TEXT NOT NULL,              -- ISO-8601
    ended_at    TEXT,                       -- ISO-8601
    summary     TEXT,
    token_count INTEGER DEFAULT 0,
    metadata    TEXT DEFAULT '{}'           -- JSON
);

-- 訊息表
CREATE TABLE messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL REFERENCES sessions(id),
    role        TEXT NOT NULL CHECK(role IN ('user','assistant','tool','system')),
    content     TEXT NOT NULL,
    tool_name   TEXT,
    token_count INTEGER DEFAULT 0,
    created_at  TEXT NOT NULL
);

-- 標籤表
CREATE TABLE tags (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL REFERENCES sessions(id),
    tag         TEXT NOT NULL,
    UNIQUE(session_id, tag)
);

-- FTS5 全文檢索引擎
CREATE VIRTUAL TABLE messages_fts 
USING fts5(content, tokenize='unicode61');
```

---

## 📦 專案結構

```
MemTrace-CLI/
├── memtrace/                  # 核心套件
│   ├── __init__.py            # 套件入口，版本資訊，公開 API
│   ├── store.py               # MemoryStore — SQLite 持久化存儲層
│   ├── session.py             # SessionCapture — 會話捕獲與管理
│   ├── search.py              # MemorySearch — 高級檢索與匯出
│   ├── tui.py                 # 終端 UI 渲染器（ANSI 儀表板）
│   ├── cli.py                 # CLI 命令解析與分發
│   └── utils.py               # 工具函數（Token估算、時間格式化等）
├── tests/                     # 測試套件
│   └── test_core.py           # 核心模組單元測試（pytest）
├── assets/                    # 資源檔案
│   └── logo.svg               # 專案標誌
├── __main__.py                # Python -m 入口點
├── setup.py                   # Setuptools 安裝配置
├── pyproject.toml             # 專案元數據與構建設定
├── Makefile                   # 開發自動化（安裝/測試/建置/清理）
├── .gitignore                 # Git 忽略規則
└── README.md                  # 專案說明文件
```

### 模組職責說明

| 模組 | 檔案 | 核心類別/功能 | 職責 |
|------|------|---------------|------|
| **Storage** | `store.py` | `MemoryStore` | SQLite 資料庫管理、會話 CRUD、訊息管理、標籤管理、FTS5 索引、統計資訊 |
| **Session** | `session.py` | `SessionCapture` | 會話生命週期管理、訊息記錄、CLI 命令包裝、上下文管理器、簡單 Token 估算 |
| **Search** | `search.py` | `MemorySearch` | 多維度全文檢索、按標籤/時間/代理過濾、相似會話發現、多格式匯出 |
| **TUI** | `tui.py` | 渲染函數群 | ANSI 風格渲染、統計面板、會話列表、搜索結果、詳情檢視、互動式儀表板 |
| **CLI** | `cli.py` | 命令分發 | 參數解析、子命令路由、用戶交互入口 |
| **Utils** | `utils.py` | 工具函數群 | Token 估算、內容類型檢測、檔案路徑管理、時間格式化、安全 JSON 解析 |

---

## 🤝 貢獻指南

歡迎對 MemTrace-CLI 貢獻程式碼、回報問題或提出功能建議！

### 開發環境設置

```bash
# 克隆儲存庫
git clone https://github.com/gitstq/MemTrace-CLI.git
cd MemTrace-CLI

# 建議使用虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝開發依賴
make dev
```

### 運行測試

```bash
# 運行所有測試
make test

# 運行測試並生成覆蓋率報告
make test-cov

# 快速冒煙測試
make smoke
```

### 程式碼風格

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 編碼風格
- 所有公開 API 必須有完整的 docstring（Google 風格）
- 型別提示（Type Hints）為必須，使用 Python 3.8+ 相容語法
- 新增功能必須附帶對應的單元測試

### 提交 PR 流程

1. Fork 本儲存庫
2. 建立你的功能分支：`git checkout -b feat/amazing-feature`
3. 提交你的變更：`git commit -m 'feat: add amazing feature'`
4. 推送到分支：`git push origin feat/amazing-feature`
5. 開啟一個 Pull Request

### 開發指引

- **新增 Store 功能**：在 `store.py` 中添加方法，並確保 SQL 語句使用參數化查詢防止 SQL 注入
- **新增 CLI 命令**：在 `cli.py` 中添加 `cmd_*` 函數，並在 `build_parser()` 中註冊子命令
- **新增 TUI 組件**：在 `tui.py` 中添加 `render_*` 函數，遵循現有的 ANSI 風格系統
- **資料庫遷移**：如需修改 Schema，請在 `_init_db()` 中使用 `CREATE TABLE IF NOT EXISTS` 以保持向下相容

### 回報問題

請在 [GitHub Issues](https://github.com/gitstq/MemTrace-CLI/issues) 中回報問題，並盡可能包含：

- 操作步驟
- 預期行為與實際行為
- Python 版本與作業系統
- 錯誤訊息或追蹤棧（traceback）

---

## 📄 開源協議

本專案採用 **MIT 授權條款** 發布。

```
MIT License

Copyright (c) 2026 MemTrace Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">
  <p>
    <a href="https://github.com/gitstq/MemTrace-CLI">
      <img src="https://img.shields.io/badge/View_on-GitHub-181717?style=for-the-badge&logo=github" alt="View on GitHub">
    </a>
    <a href="https://github.com/gitstq/MemTrace-CLI/issues">
      <img src="https://img.shields.io/badge/Report-Bug-ff4444?style=for-the-badge&logo=github" alt="Report Bug">
    </a>
    <a href="https://github.com/gitstq/MemTrace-CLI/issues">
      <img src="https://img.shields.io/badge/Request-Feature-44bb44?style=for-the-badge&logo=github" alt="Request Feature">
    </a>
  </p>
  <p>
    <sub>Built with ❤️ for the AI developer community</sub>
  </p>
</div>