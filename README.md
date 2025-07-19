# myAgent

myAgent 是一个基于 FastAPI、OpenAI LLM 和可扩展工具的智能 Agent 框架，使用 uv 进行包管理，支持 Python 3.13+。

## 目录结构

```
myagent/
  agent/
    __init__.py
    agent.py           # BaseAgent 和 ToolCallingAgent 类（异步）
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
  example_tool_calling_agent.py  # ToolCallingAgent 使用示例
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

## 启动 ToolCallingAgent 示例

```sh
uv run example_tool_calling_agent.py
```

## 主要特性说明
- **异步架构**：BaseAgent 仅支持 async def run，main.py 全异步交互。
- **LLM 支持流式/非流式**：LLM 默认流式（stream=True），可通过参数切换。
- **日志集成**：所有用户输入、Agent回复、异常均自动记录日志。
- **可扩展工具**：在 tool/ 目录下添加新工具并注册即可。

## ToolCallingAgent

ToolCallingAgent 是一个基于 React 框架的智能体，实现了 think-act 模式：

### 特点
- **React 框架**：实现 think-act 模式，先思考再行动
- **工具调用**：支持动态工具调用和参数传递
- **对话功能**：支持自然语言对话
- **可扩展性**：可作为其他智能体的基座
- **记忆管理**：完整的对话历史记录
- **迭代控制**：防止无限循环的安全机制

### 使用方法

```python
from agent import ToolCallingAgent
from agent.llm import LLM
from agent.memory_manager import MemoryManager
from agent.tool_manager import ToolManager

# 初始化组件
llm = LLM(api_key="your_openai_key")
memory_manager = MemoryManager()
tool_manager = ToolManager()

# 注册工具
tool_manager.register("add", lambda a, b: a + b)
tool_manager.register("search", search_function)

# 创建 ToolCallingAgent
agent = ToolCallingAgent(
    name="MyAgent",
    llm=llm,
    memory_manager=memory_manager,
    tool_manager=tool_manager,
    max_iterations=5
)

# 运行智能体
result = await agent.run("请计算 15 + 27")
```

### React 模式示例

ToolCallingAgent 使用以下格式进行思考和行为：

```
THINK: 用户要求计算 15 + 27，我需要使用 add 工具来完成这个任务。
ACT: add 15 27
```

系统会自动解析这种格式，执行工具调用，然后基于结果继续思考。

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