# myAgent

myAgent 是一个基于 FastAPI、OpenAI LLM 和可扩展工具的智能 Agent 框架，使用 uv 进行包管理，支持 Python 3.13+。

## 目录结构

```
myagent/
  agent/
    __init__.py
    agent.py           # BaseAgent 类（异步）
    llm.py             # LLM 类，基于 OpenAI，支持异步和流式
    memory_manager.py  # MemoryManager 记忆管理
    tool_manager.py    # ToolManager 工具管理
  api/
    __init__.py
    main.py            # FastAPI 后端接口（异步）
  logger/
    __init__.py
    logger.py          # 日志模块
  prompt/
    __init__.py
    prompt.py          # Prompt 模板管理
  tool/
    __init__.py
    search.py          # search 工具
    math.py            # math 工具
    terminate.py       # terminate 工具
  main.py              # 异步命令行入口，集成日志
pyproject.toml         # 项目依赖和配置
```

## 依赖
- Python 3.13+
- uv 0.7.2
- fastapi
- uvicorn
- openai
- pydantic >=2.11.4

## 安装

1. 安装 [uv](https://github.com/astral-sh/uv):
   ```sh
   pip install uv==0.7.2
   ```
2. 创建虚拟环境并安装依赖：
   ```sh
   uv venv
   source .venv/bin/activate
   uv pip install --upgrade pip
   uv pip install -r requirements.txt  # 或使用 pyproject.toml
   ```

## 启动 API 服务

```sh
uvicorn api.main:app --reload
```

## 启动命令行 Agent

```sh
uv run main.py
```

## 主要特性说明
- **异步架构**：BaseAgent 仅支持 async def run，main.py 全异步交互。
- **LLM 支持流式/非流式**：LLM 默认流式（stream=True），可通过参数切换。
- **日志集成**：所有用户输入、Agent回复、异常均自动记录日志。
- **可扩展工具**：在 tool/ 目录下添加新工具并注册即可。

## LLM 流式/非流式用法示例

```python
# 默认流式（推荐）
reply = await agent.llm.chat(messages)

# 非流式
reply = await agent.llm.chat(messages, stream=False)
```

## 配置 OpenAI API Key

请在使用 LLM 前设置环境变量：
```sh
export OPENAI_API_KEY=your_openai_key
```

---

如需扩展工具或功能，请在 `tool/` 目录下添加新模块，并在 `ToolManager` 注册即可。 