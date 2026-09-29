# 🔍 CodeReview Agent

基于 **Python + LangChain + LLM + Tool + Streamlit** 的智能代码审查 Agent。

用户输入代码后，Agent 通过大语言模型进行多维度分析；当运行验证有助于确认问题时，Agent 会自主调用 `execute_python` 工具执行代码，并结合工具的真实结果生成结构化中文审查报告。

---

## 项目简介

本项目是一个完整的 **LLM Agent 课程实践项目**，完整覆盖以下技术点：

- LLM 调用与 Prompt 工程
- Agent 设计模式（ReAct：推理 → 工具调用 → 综合分析）
- Tool 自定义与注册（`@tool`）
- 上下文记忆
- 错误处理与重试
- Web 交互界面（Streamlit）

---

## 核心功能

| 功能 | 说明 |
|------|------|
| 代码审查 | 覆盖**语法错误、运行时错误、逻辑错误、代码质量**四类问题 |
| 执行验证 | Agent 自主判断是否需要运行代码，调用 `execute_python` 工具实测 |
| 真实结果溯源 | 基于工具真实输出分析，杜绝模型凭空编造执行结果 |
| 结构化报告 | 固定输出：总体评价 / 发现的问题 / 工具验证结果 / 修改建议 / 参考代码 |
| 轻量上下文记忆 | 保存最近一次审查的代码与结果，支持后续追问 |
| Web 界面 | Streamlit 图形界面，输入代码一键审查 |

### 边界情况处理

| 场景 | 处理方式 |
|------|----------|
| 除数为零等运行时异常 | 工具捕获 Traceback 并返回给 LLM，报告给出定位与修复代码 |
| 空输入 | Web 界面提示「请输入需要审查的代码」，不发起 LLM 请求 |
| 语法错误 | 工具执行失败并返回完整堆栈，LLM 据此给出语法修复建议 |
| API Key 缺失 | Agent 初始化即报错并提示配置 `.env` |
| LLM 请求失败 | `max_retries=2` 自动重试，仍失败则转换为可读中文错误 |
| 工具执行异常 | 任何异常均被捕获，不影响后续分析流程 |
| 无需运行验证的代码 | System Prompt 约束「不要为了调用工具而调用工具」 |

---

## Agent 架构设计

### 工作流程（ReAct 模式）

```text
用户输入
   ↓
┌─────────────────────────┐
│   CodeReview Agent      │
│   (LangChain Agent)     │
│                         │
│  LLM 推理分析           │
│      ↓                  │
│  判断是否需要工具？     │
│    /          \         │
│   否           是       │
│   ↓             ↓       │
│  直接回答    execute_   │
│             python 工具  │
│                  ↓      │
│            工具真实结果  │
│                  ↓      │
│    LLM 结合结果综合分析  │
│         ↓               │
│   结构化审查报告         │
└─────────────────────────┘
   ↓
最终输出
```

### 设计模式说明

1. **Agent 循环**：LLM 推理 → 自主决策工具调用 → 观察工具结果 → 再次推理，体现典型的 ReAct（Reasoning + Acting）设计模式
2. **工具抽象**：`execute_python` 通过 `@tool` 装饰器注册为可调用工具，Agent 按需调用，与业务逻辑解耦
3. **System Prompt 约束**：规定 Agent 身份、审查原则、工具调用条件与输出格式，防止模型幻觉（如谎称执行过代码）
4. **记忆机制**：保存最近一次审查的 `code` 与 `result`，为后续多轮对话提供上下文

### 模块职责划分

| 模块 | 职责 | 对应评审点 |
|------|------|-----------|
| `main.py` | Streamlit Web 界面、输入输出交互 | 功能完整性 |
| `agent.py` | Agent 组装（LLM + Tool + Prompt）、审查流程编排 | Agent 架构 |
| `tools.py` | `execute_python` 工具定义、安全执行环境 | Agent 架构 / 代码质量 |
| `prompts.py` | System Prompt 与审查要求 | Agent 架构 |
| `config.py` | 环境变量加载与配置（API Key / Base URL / Model） | 代码质量 |

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

复制 `.env.example` 为 `.env`，填写：

```text
OPENAI_API_KEY=你的API_KEY
OPENAI_BASE_URL=
MODEL_NAME=gpt-4o-mini
```

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | 必填，模型服务商密钥 |
| `OPENAI_BASE_URL` | 接口地址；OpenAI 官方可留空，第三方兼容接口必填 |
| `MODEL_NAME` | 模型名称 |

支持任何 **OpenAI 兼容接口**，常用配置示例：

| 服务商 | OPENAI_BASE_URL | MODEL_NAME |
|--------|-----------------|------------|
| OpenAI | （留空） | gpt-4o-mini |
| 智谱 GLM | `https://open.bigmodel.cn/api/paas/v4` | `glm-5.3-flash` |
| 火山方舟（豆包） | `https://ark.cn-beijing.volces.com/api/v3` | 开通的模型 ID / 接入点 `ep-xxx` |

> 提示：`glm-5.3-flash` 等 Flash 系列模型响应更快，适合快速演示。

### 启动

```bash
streamlit run main.py
```

或（`streamlit` 未加入 PATH 时）：

```bash
python -m streamlit run main.py
```

浏览器自动打开 `http://localhost:8501`，输入代码后点击「🚀 开始审查」。

### 演示

输入以下代码：

```python
def divide(a, b):
    return a / b

print(divide(10, 0))
```

Agent 会自主调用 `execute_python` 工具验证，并输出：

```text
ZeroDivisionError: division by zero
```

最终报告中包含问题定位、工具验证结果、修改建议与参考代码。

---

## 错误处理与健壮性

- **API Key 缺失**：初始化时给出明确中文提示
- **LLM 请求失败**：`max_retries=2` 自动重试
- **Agent 异常**：捕获并转换为可读错误信息
- **Tool 异常**：完整 Traceback 返回给 LLM，作为分析依据
- **Web 异常**：Streamlit 界面展示错误而非崩溃

---

## 项目结构

```text
CodeReview-Agent/
├── main.py            # Streamlit UI
├── agent.py           # Agent 核心（LLM + Tool + 编排）
├── tools.py           # Python 执行工具
├── prompts.py         # Prompt 定义
├── config.py          # 配置加载
├── requirements.txt   # 依赖清单
├── .env.example       # 环境变量模板
├── .gitignore
├── README.md          # 本文档
├── Design.md          # 设计文档
└── examples/          # 示例代码
```

---

## 评审标准对照

| 评审维度 | 权重 | 本项目落实情况 |
|----------|------|----------------|
| 功能完整性 | 40% | 语法/运行时/逻辑/质量四类审查 + 工具实测验证 + 边界情况处理（见上文表格） |
| Agent 架构 | 30% | ReAct 循环、`@tool` 工具注册、System Prompt 约束、上下文记忆、模块职责分离 |
| 代码质量 | 20% | 职责分离（UI/Agent/Tool/Prompt/Config 五模块）、统一错误处理、异常捕获 |
| 文档 | 10% | README（本项目）、Design.md（设计文档）、示例代码（examples/） |

---

## 安全说明

`execute_python` 为课程演示工具，**不是生产环境安全沙箱**。它通过受限 builtins 执行代码，但仅适用于可信输入，不要执行来源不明或恶意代码。生产环境建议使用 Docker 等隔离机制。

---

## 后续改进

- [ ] 多语言代码审查（Java / Go / JS）
- [ ] Docker 沙箱执行环境
- [ ] 文件上传与多文件审查
- [ ] 审查历史记录持久化
- [ ] 单元测试自动生成
- [ ] GitHub 仓库级分析
