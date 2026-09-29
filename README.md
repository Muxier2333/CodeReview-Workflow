# 🔍 代码审查 Workflow（编码 → 审查 → 修复）

基于 **Python + LangChain + GLM + Streamlit** 的三 Agent 协作流水线，衔接课程项目一（CodeReview Agent）：
**小A 写代码 → 小B 审查 → 有问题小C 修复 → 复审通过**，全流程自动执行并记录日志。

---

## 项目简介

本项目是课程项目二，目标是通过搭建 2~3 个 Agent 协作的 Workflow，理解三大核心概念：

- **Workflow 编排**：谁决定执行顺序、谁启动下一个 Agent
- **Agent 间通信**：上一个 Agent 的输出如何成为下一个 Agent 的输入
- **状态管理**：中间产物与进度记录在哪里、如何追踪

项目一已实现单 Agent 代码审查（`CodeReviewAgent`），本项目将其**复用为审查节点**，并新增"编码 Agent"与"修复 Agent"，组成一条完整的代码审查流水线。

### 与项目一的关系（复用清单）

| 项目一模块 | 本项目中的角色 |
|------------|----------------|
| `agent.py`（CodeReviewAgent） | 审查 Agent（小B），直接复用 |
| `tools.py`（execute_python） | 审查实测工具，直接复用 |
| `config.py` | 配置入口，直接复用 |
| `prompts.py` | 审查 Prompt 复用，新增编码/修复 Prompt |
| `main_v1.py` | 项目一原版界面（备份，可对照） |

---

## 核心功能

| 功能 | 说明 |
|------|------|
| 三 Agent 协作 | 编码 Agent → 审查 Agent → 修复 Agent 接力完成完整流程 |
| 条件分支 | 审查结论 PASS 则流程结束，FAIL 则进入修复 |
| 循环控制 | 修复后送回复审，最多 N 轮（默认 3 轮），防止死循环 |
| 执行日志 | 每一步写入 `workflow.log`（时间/阶段/轮次/结论），可追踪可演示 |
| 实时进度 | 网页端实时显示当前正在执行哪个 Agent、哪个阶段 |
| 结构化报告 | 审查报告固定五段式 + 结论行（PASS / FAIL） |

---

## 工作流程

```text
任务描述
   ↓
┌────────────────┐
│  编码 Agent     │ 小A：根据任务生成第一版代码（纯 LLM，单次请求，无工具）
└───────┬────────┘
        ↓ 第一版代码
┌────────────────┐
│  审查 Agent     │ 小B：复用项目一（静态分析 + 必要时工具实测，工具限 1 次）
└───────┬────────┘
        ↓ 审查报告（含"审查结论: PASS / FAIL"）
        │
   PASS ┤──── 流程结束，交付最终代码 ✔
        │
   FAIL（且未超过最大轮数）
        ↓
┌────────────────┐
│  修复 Agent     │ 小C：对照审查报告逐条修复
└───────┬────────┘
        ↓ 修复后代码 ──► 送回审查（循环，最多 N 轮）
```

---

## 快速开始

### 环境要求

- Python 3.10+

### 安装

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 配置 API Key

复制 `.env.example` 为 `.env` 并填写（项目一已配置，可直接继承）：

```text
OPENAI_API_KEY=你的API_KEY
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
MODEL_NAME=glm-5.3-flash
```

### 启动

```bash
python -m streamlit run main.py
```

浏览器打开 `http://localhost:8501`，输入任务描述，点击「运行流程」。

### 命令行快速验证（不开网页）

```bash
python test_workflow_run.py
```

### 演示

默认任务：写一个 `divide(a, b)` 函数并调用 `divide(10, 0)`。

| 阶段 | 预期 |
|------|------|
| 1. 小A 编码 | 生成 `return a / b`，未处理除零 |
| 2. 小B 审查 | 发现运行时风险，结论 FAIL |
| 3. 小C 修复 | 增加 `b == 0` 检查 / try-except 捕获 |
| 4. 小B 复审 | 通过，流程结束，状态 PASS |

---

## 项目结构

```text
CodeReview-Agent/
├── main.py              # Streamlit 界面（流程展示 + 实时进度 + 日志面板）
├── workflow.py          # 编排器：编码→审查→(修复→复审)，状态管理 + 执行日志
├── coding_agent.py      # 编码 Agent（小A，新增）
├── fix_agent.py         # 修复 Agent（小C，新增）
├── agent.py             # 审查 Agent（小B，复用项目一）
├── tools.py             # execute_python 执行工具（复用项目一）
├── prompts.py           # Prompt 定义（审查 + 编码 + 修复）
├── config.py            # 配置加载（复用项目一）
├── main_v1.py           # 项目一原版界面（备份）
├── test_workflow_run.py # 端到端验证脚本
├── workflow.log         # 执行日志（运行后生成）
├── requirements.txt
├── .env.example
├── README.md            # 本文档
├── Design.md            # 设计文档
└── examples/            # 项目一示例代码
```

---

## 执行日志说明

`workflow.log` 记录每一步：

- 时间戳、阶段（ENCODE / REVIEW / FIX）、审查轮次
- 各 Agent 输入输出摘要（代码长度、结论）
- 最终状态（PASS / FAIL / MAX_ROUND）

示例：

```text
2026-09-29 10:37:49 | INFO | [ENCODE] 编码完成（270 字符）
2026-09-29 10:39:38 | INFO | [REVIEW] 第 1 轮发现问题，进入修复
2026-09-29 10:41:38 | INFO | [REVIEW] 第 2 轮：通过，流程结束
```

---

## 评审标准对照

| 评审维度 | 权重 | 本项目落实情况 |
|----------|------|----------------|
| 流程完整性 | 40% | 编码→审查→修复→复审端到端跑通，实测状态 PASS、2 轮完成 |
| Agent 协作 | 30% | 三 Agent 通过参数传递通信，WorkflowState 管理状态，workflow.log 全程可追踪 |
| 可扩展性 | 20% | 每个 Agent 独立成类，编排器只按流程调用；新增 Agent 零侵入；换模型只改 .env |
| 文档 | 10% | README（本文档）+ Design.md（设计文档）+ 流程图 |

---

## 常见问题

| 问题 | 处理 |
|------|------|
| 浏览器打开提示拒绝连接 | 服务器未启动：执行 `python -m streamlit run main.py` 后再访问 http://localhost:8501 |
| 运行较慢 | 属正常：审查需多次调用大模型；已优化（工具限 1 次），全流程约 3 分钟 |
| 流程一直修复不结束 | 达到最大轮数（默认 3）会强制结束并标记 MAX_ROUND，不会死循环 |
| 审查报告没有结论行 | 检查 `prompts.py` 是否包含"审查结论: PASS / FAIL"输出要求 |
