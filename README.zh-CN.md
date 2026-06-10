<div align="center">
  <img src="assets/logo.svg" alt="MemTrace-CLI Logo" width="120" height="120">
  <h1 align="center">MemTrace-CLI</h1>
  <p align="center">
    <strong>轻量级终端 AI 智能体共享内存引擎</strong>
    <br>
    零外部依赖 · 纯 Python 3.8+ · 跨平台
  </p>
  <p align="center">
    <a href="https://pypi.org/project/memtrace-cli/">
      <img src="https://img.shields.io/pypi/v/memtrace-cli?style=flat-square&logo=pypi&logoColor=white&label=PyPI" alt="PyPI">
    </a>
    <a href="https://github.com/gitstq/MemTrace-CLI">
      <img src="https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python">
    </a>
    <a href="https://github.com/gitstq/MemTrace-CLI/blob/main/LICENSE">
      <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT License">
    </a>
    <a href="https://github.com/gitstq/MemTrace-CLI">
      <img src="https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey?style=flat-square" alt="Platform">
    </a>
    <a href="https://github.com/gitstq/MemTrace-CLI">
      <img src="https://img.shields.io/github/stars/gitstq/MemTrace-CLI?style=flat-square&logo=github" alt="GitHub Stars">
    </a>
    <a href="https://github.com/gitstq/MemTrace-CLI">
      <img src="https://img.shields.io/github/last-commit/gitstq/MemTrace-CLI?style=flat-square&logo=git" alt="Last Commit">
    </a>
    <br>
    <a href="./README.md">English</a> · <strong>简体中文</strong>
  </p>
</div>

---

## 目录

- [项目介绍](#-项目介绍)
- [核心特性](#-核心特性)
- [快速开始](#-快速开始)
- [使用指南](#-使用指南)
- [设计理念](#-设计理念)
- [项目结构](#-项目结构)
- [贡献指南](#-贡献指南)
- [开源协议](#-开源协议)

---

## 项目介绍

**MemTrace-CLI** 是一款专为 AI 编码智能体设计的轻量级终端共享内存引擎。它能够捕获、索引和检索 AI 编程助手的会话记录，将每次交互转化为持久化、可搜索的结构化记忆。

受 [Hivemind](https://github.com/activeloopai/hivemind) 的共享智能体内存概念启发，MemTrace-CLI 重新构想并实现了一个**本地优先、零依赖、跨平台**的命令行工具。无论你使用 Claude、GPT、Copilot 还是其他 AI 编码工具，MemTrace-CLI 都能无缝记录并管理你的所有智能体交互。

```bash
# 捕获一次智能体会话
memtrace capture claude -p "解释这段代码的工作原理"

# 搜索历史记忆
memtrace search "二分查找"

# 打开交互式仪表盘
memtrace dashboard
```

---

## 核心特性

| 特性 | 说明 |
|------|------|
| **会话捕获** | 通过包装 CLI 命令，自动捕获智能体的完整会话（提示词、回复、工具调用） |
| **持久化存储** | 基于 SQLite 的本地存储引擎，数据安全可靠，无需联网 |
| **全文检索** | 利用 SQLite FTS5 实现毫秒级全文搜索，支持模糊匹配和语义查询 |
| **标签管理** | 灵活的标签系统，轻松组织和过滤会话记录 |
| **TUI 仪表盘** | 内置终端交互式仪表盘，支持浏览、搜索、分页操作 |
| **多工作区** | 支持多智能体、多工作区隔离，适合团队协作场景 |
| **零外部依赖** | 纯 Python 标准库实现，无需安装任何第三方包 |
| **跨平台** | 完美支持 Linux、macOS、Windows 三大操作系统 |
| **多种导出** | 支持 Markdown / JSON / 纯文本三种格式导出会话 |

---

## 快速开始

### 安装

**方式一：通过 pip 安装（推荐）**

```bash
pip install memtrace-cli
```

**方式二：从源码安装**

```bash
git clone https://github.com/gitstq/MemTrace-CLI.git
cd MemTrace-CLI
pip install .
```

**方式三：使用 pipx（隔离环境）**

```bash
pipx install memtrace-cli
```

### 验证安装

```bash
memtrace --version
# 输出: MemTrace-CLI v0.1.0
```

### 初始化存储

```bash
memtrace init
# 输出: MemTrace store initialized at: /home/user/.memtrace/memory.db
# 输出: Sessions: 0  Messages: 0
```

### 第一个会话

```bash
# 捕获一条简单命令
memtrace capture --agent claude --workspace my-project claude -p "用 Python 写一个快速排序"

# 查看所有会话
memtrace list

# 搜索刚才的内容
memtrace search "快速排序"
```

---

## 使用指南

MemTrace-CLI 提供了 9 个子命令，覆盖智能体会话的完整生命周期。

### 命令一览

| 命令 | 功能 | 常用选项 |
|------|------|----------|
| `capture` | 捕获智能体会话 | `--agent`, `--workspace`, `--tag` |
| `search` | 全文搜索记忆 | `--agent`, `--workspace`, `--tag`, `--days`, `--limit` |
| `list` | 列出最近会话 | `--agent`, `--workspace`, `--limit` |
| `show` | 查看会话详情 | `session_id` |
| `stats` | 查看存储统计 | `--db-dir` |
| `export` | 导出会话 | `--format`, `--output` |
| `tags` | 列出所有标签 | 无 |
| `dashboard` | 打开交互式仪表盘 | 无 |
| `delete` | 删除会话 | `-y`（跳过确认） |

### 全局选项

所有命令均支持以下全局选项：

| 选项 | 说明 |
|------|------|
| `--db-dir PATH` | 自定义数据库存储路径（默认：`~/.memtrace/`） |
| `--version` | 显示版本号 |

---

### capture —— 捕获会话

`capture` 是 MemTrace-CLI 的核心命令。它包装一个 CLI 命令，自动记录其标准输入和输出，生成结构化的会话记录。

```bash
# 基本用法
memtrace capture <command> [args...]

# 示例：捕获 Claude 会话
memtrace capture claude -p "帮我优化这段代码"

# 示例：指定智能体和工作区
memtrace capture --agent claude --workspace my-app claude -p "解释这个 API"

# 示例：添加标签（可重复使用）
memtrace capture --tag python --tag algorithm claude -p "实现二分查找"

# 示例：捕获任意命令
memtrace capture --agent bash ls -la src/
```

**工作原理**：
1. 创建新会话并生成唯一 ID
2. 运行指定命令，实时捕获 stdout/stderr
3. 命令执行完毕后，自动终止会话并生成摘要
4. 所有数据持久化到 SQLite 数据库

---

### search —— 搜索记忆

利用 SQLite FTS5 全文检索引擎，快速在海量会话中定位目标内容。

```bash
memtrace search <query> [options]
```

```bash
# 基本全文搜索
memtrace search "二分查找"

# 按智能体过滤
memtrace search "Python" --agent claude

# 按工作区过滤
memtrace search "API 设计" --workspace my-app

# 按标签过滤
memtrace search "排序算法" --tag algorithm

# 限定时间范围（最近 7 天）
memtrace search "优化" --days 7

# 限制结果数量
memtrace search "测试" --limit 5
```

**搜索提示**：FTS5 搜索引擎支持精确短语匹配、前缀搜索等高级语法。当 FTS5 语法不兼容时，自动回退到 `LIKE` 模糊匹配。

---

### list —— 列出会话

以列表形式展示最近的会话记录，包含智能体、时间、摘要和标签信息。

```bash
# 列出最近 20 条会话
memtrace list

# 按智能体过滤
memtrace list --agent claude

# 按工作区过滤
memtrace list --workspace my-app

# 自定义数量
memtrace list --limit 50
```

---

### show —— 查看会话详情

展示指定会话的完整信息，包括元数据和所有消息记录。

```bash
memtrace show <session_id>
```

```bash
# 示例
memtrace show a1b2c3d4e5f6
```

输出包含：
- 会话元数据：ID、智能体、工作区、起止时间、Token 数
- 完整消息列表：每条消息的角色（USER / ASSISTANT / TOOL / SYSTEM）和内容
- 标签信息
- 自动生成的摘要

---

### stats —— 查看统计

快速了解存储引擎的全局统计信息。

```bash
memtrace stats
```

输出示例：
```
Sessions: 42
Active: 3
Messages: 1258
Total Tokens: 89231
DB Size: 2.3 MB

Agents:
  claude:  28 sessions
  gpt:     10 sessions
  copilot: 4 sessions
```

---

### tags —— 标签管理

列出所有已使用的标签及其关联的会话数量。

```bash
memtrace tags
```

输出示例：
```
12 tags:

  #python               8 sessions
  #algorithm            5 sessions
  #web-development      4 sessions
  #debug                3 sessions
  #refactor             2 sessions
```

---

### export —— 导出会话

将会话导出为可分享的格式，支持三种输出格式。

```bash
memtrace export <session_id> [options]
```

```bash
# 导出为 Markdown（默认）
memtrace export a1b2c3d4e5f6
memtrace export a1b2c3d4e5f6 --format markdown

# 导出为 JSON（适合程序处理）
memtrace export a1b2c3d4e5f6 --format json

# 导出为纯文本
memtrace export a1b2c3d4e5f6 --format text

# 输出到文件
memtrace export a1b2c3d4e5f6 --format markdown -o session.md
```

---

### delete —— 删除会话

从存储中永久删除指定会话及其所有关联数据。

```bash
memtrace delete <session_id>

# 跳过确认提示
memtrace delete <session_id> -y
```

---

### dashboard —— 交互式仪表盘

打开终端交互式仪表盘（TUI），通过键盘快捷键浏览和搜索会话。

```bash
memtrace dashboard
```

仪表盘支持的操作：

| 按键 | 功能 |
|------|------|
| `n` | 下一页 |
| `p` | 上一页 |
| `s` | 搜索会话 |
| `v` | 查看会话详情 |
| `q` | 退出 |
| 数字 | 直接输入会话 ID 查看详情 |

仪表盘采用纯 ANSI 终端序列实现，无需 ncurses 或其他 TUI 库。

---

## 设计理念

### 本地优先 · 隐私至上

MemTrace-CLI 坚持**本地优先**原则。所有会话数据存储在本地 SQLite 数据库中，无需注册账号、无需联网、无需担心数据泄露。你的智能体记忆完全由你掌控。

### 零依赖 · 极致轻量

整个项目仅依赖 Python 标准库（`sqlite3`、`argparse`、`subprocess`、`json` 等），没有任何第三方包依赖。安装体积仅几十 KB，启动速度毫秒级。真正做到 "pip install" 即装即用。

### 简约而不简单

项目核心只有 6 个模块文件，总代码量约 1500 行，却实现了会话捕获、持久存储、全文检索、标签管理、TUI 仪表盘、多格式导出等完整功能。每个模块职责单一、高度内聚。

### 可组合 · 可嵌入

MemTrace-CLI 的设计考虑了两种使用场景：
- **CLI 工具**：通过命令行直接使用，适合日常开发
- **Python API**：通过 `MemoryStore`、`SessionCapture`、`MemorySearch` 等类，可以将其嵌入到任何 Python 项目中

```python
from memtrace import MemoryStore, SessionCapture, MemorySearch

# 编程式使用
store = MemoryStore()
capture = SessionCapture(store=store, agent="my-agent")
session_id = capture.start()
capture.log_user("你好，智能体")
capture.log_assistant("你好！有什么可以帮助你的？")
capture.stop()

# 搜索
engine = MemorySearch(store)
results = engine.search("你好")
```

### SQLite FTS5 全文检索

不同于许多项目依赖 Elasticsearch 或其他重型搜索引擎，MemTrace-CLI 利用 SQLite 内置的 FTS5 扩展实现毫秒级全文检索。这意味着：
- 无需搭建和维护独立的搜索引擎服务
- 数据库和搜索引擎合二为一，简化部署
- 单机即可支持数万条会话的高效检索

---

## 项目结构

```
MemTrace-CLI/
├── memtrace/                # 核心库目录
│   ├── __init__.py          # 包入口，版本号与公有 API
│   ├── cli.py               # CLI 入口，子命令分发（9 个子命令）
│   ├── store.py             # SQLite 持久化存储引擎（FTS5 全文检索）
│   ├── session.py           # 会话捕获与管理
│   ├── search.py            # 高级搜索与检索接口
│   ├── tui.py               # 终端 UI 仪表盘（纯 ANSI 实现）
│   └── utils.py             # 工具函数（Token 估算、文本处理等）
├── tests/                   # 测试目录
│   └── test_core.py         # 核心模块测试套件（pytest）
├── assets/
│   └── logo.svg             # 项目 Logo
├── pyproject.toml           # 项目构建配置
├── setup.py                 # 兼容性安装脚本
├── Makefile                 # 开发辅助命令
├── __main__.py              # 直接运行入口（python -m memtrace）
├── .gitignore               # Git 忽略规则
├── LICENSE                  # MIT 开源协议
└── README.md                # 项目文档（英文）
```

### 各模块职责

| 模块 | 职责 | 核心类/函数 |
|------|------|-------------|
| `store.py` | SQLite 数据库管理，会话/消息/标签的 CRUD 操作，FTS5 全文索引 | `MemoryStore` |
| `session.py` | 会话生命周期管理，CLI 命令包装，消息日志 | `SessionCapture` |
| `search.py` | 高级搜索接口，结果格式化，多格式导出 | `MemorySearch` |
| `tui.py` | 终端渲染，ANSI 样式，交互式仪表盘 | `render_stats()` 等渲染函数 |
| `cli.py` | CLI 参数解析，子命令路由 | `build_parser()`, `main()` |
| `utils.py` | Token 估算、文本截断、内容类型检测等辅助功能 | `estimate_tokens()` 等 |

---

## 贡献指南

欢迎为 MemTrace-CLI 贡献力量！无论是报告 Bug、提交功能请求，还是直接提交代码，我们都非常欢迎。

### 开发流程

1. **Fork 仓库**：点击 GitHub 页面右上角的 Fork 按钮

2. **克隆项目**

   ```bash
   git clone https://github.com/你的用户名/MemTrace-CLI.git
   cd MemTrace-CLI
   ```

3. **创建虚拟环境**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

4. **安装开发依赖**

   ```bash
   pip install -e .
   pip install pytest
   ```

5. **运行测试**

   ```bash
   pytest tests/ -v
   ```

6. **创建分支并提交**

   ```bash
   git checkout -b feature/你的新功能
   # 开发你的代码...
   git commit -m "feat: 添加了某项新功能"
   git push origin feature/你的新功能
   ```

7. **提交 Pull Request**：在 GitHub 上向 `main` 分支发起 PR

### 代码规范

- 遵循 PEP 8 编码风格
- 保持零外部依赖 —— 新增功能不得引入第三方包
- 为所有公开函数和类编写文档字符串
- 新增功能必须包含对应的单元测试
- 保持跨平台兼容（Linux / macOS / Windows）

### 贡献方向

- 更多智能体适配（如 Claude Code、GitHub Copilot CLI 等）
- 增强的 TUI 功能（主题、排序、筛选等）
- 性能优化和数据库压缩
- 导入/导出功能增强
- 读者友好度改进（文档、错误提示等）

---

## 开源协议

本项目基于 [MIT 许可证](LICENSE) 开源。

```
MIT License

Copyright (c) 2024 MemTrace Team

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
  <sub>
    Built with ❤️ for the AI coding agent community · 
    <a href="https://github.com/gitstq/MemTrace-CLI">GitHub</a> ·
    <a href="https://pypi.org/project/memtrace-cli/">PyPI</a>
  </sub>
  <br>
  <sub>如果觉得这个项目有帮助，请给一个 ⭐ Star！</sub>
</div>