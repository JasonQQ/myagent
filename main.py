from agent.agent import ToolCallingAgent
from agent.llm import LLM
from agent.memory_manager import MemoryManager
from agent.tool_manager import ToolManager
from tool import search_tool, add, terminate
from prompt import SYSTEM_PROMPT
from logger import get_logger
import os
import asyncio

logger = get_logger()

# 初始化 LLM
llm = LLM()  # 自动从环境变量加载配置

# 初始化 MemoryManager
memory_manager = MemoryManager()
# ToolCallingAgent会自动添加系统提示词，无需手动添加

# 初始化 ToolManager 并注册工具
tool_manager = ToolManager()
tool_manager.register("search", search_tool)
tool_manager.register("add", add)
tool_manager.register("terminate", terminate)

# 初始化 ToolCallingAgent
agent = ToolCallingAgent(
    name="myAgent",
    llm=llm,
    memory_manager=memory_manager,
    tool_manager=tool_manager,
    max_iterations=3
)

async def main():
    print("欢迎使用 ToolCallingAgent CLI。输入 'exit' 退出。")
    while True:
        user_input = await asyncio.to_thread(input, "你: ")
        logger.info(f"用户输入: {user_input}")
        if user_input.strip().lower() == "exit":
            print("再见！")
            logger.info("用户退出会话。")
            break
        try:
            result = await agent.run(user_input)
            logger.info(f"Agent回复: {result}")
            print(f"Agent: {result}")
        except NotImplementedError:
            logger.error("Agent.run() 方法未实现。")
            print("Agent.run() 方法未实现。请在 ToolCallingAgent 子类中实现具体逻辑。")
        except Exception as e:
            logger.exception(f"发生错误: {e}")
            print(f"发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 