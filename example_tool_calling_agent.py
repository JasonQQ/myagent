#!/usr/bin/env python3
"""
ToolCallingAgent 使用示例

这个示例展示了如何使用 ToolCallingAgent 进行对话和工具调用。
"""

import asyncio
import os
from agent import ToolCallingAgent
from agent.llm import LLM
from agent.memory_manager import MemoryManager
from agent.tool_manager import ToolManager
from tool import search_tool, add, terminate
from logger import get_logger

logger = get_logger()

def create_sample_data():
    """创建示例数据用于搜索工具"""
    return [
        "Python是一种编程语言",
        "JavaScript是前端开发语言", 
        "Java是企业级开发语言",
        "C++是系统编程语言",
        "Go是云原生开发语言"
    ]

async def main():
    """主函数，演示ToolCallingAgent的使用"""
    
    # 初始化 LLM
    openai_key = os.getenv("OPENAI_API_KEY", "sk-xxx")
    llm = LLM(api_key=openai_key, model="gpt-3.5-turbo", stream=False)  # 使用非流式便于调试
    
    # 初始化 MemoryManager
    memory_manager = MemoryManager()
    
    # 初始化 ToolManager 并注册工具
    tool_manager = ToolManager()
    tool_manager.register("search", lambda query, data: search_tool(query, data))
    tool_manager.register("add", add)
    tool_manager.register("terminate", terminate)
    
    # 创建 ToolCallingAgent
    agent = ToolCallingAgent(
        name="ToolCallingAgent",
        llm=llm,
        memory_manager=memory_manager,
        tool_manager=tool_manager,
        max_iterations=3  # 设置最大迭代次数
    )
    
    print("=== ToolCallingAgent 示例 ===")
    print("这是一个基于React框架的智能体，支持think-act模式")
    print("输入 'exit' 退出\n")
    
    # 示例数据
    sample_data = create_sample_data()
    
    # 示例对话
    examples = [
        "你好，请介绍一下你自己",
        "请搜索包含'Python'的信息",
        "计算 15 + 27 的结果",
        "请搜索编程语言相关的信息"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n--- 示例 {i} ---")
        print(f"用户: {example}")
        
        # 对于搜索工具，需要传入数据
        if "搜索" in example:
            # 临时修改search工具以包含数据
            original_search = tool_manager.tools["search"]
            tool_manager.tools["search"] = lambda query, data=sample_data: original_search(query, data)
        
        try:
            result = await agent.run(example)
            print(f"Agent: {result}")
            logger.info(f"示例{i}完成: {result}")
        except Exception as e:
            print(f"错误: {e}")
            logger.error(f"示例{i}失败: {e}")
    
    print("\n=== 交互模式 ===")
    print("现在你可以与Agent进行交互了！")
    
    while True:
        try:
            user_input = await asyncio.to_thread(input, "\n你: ")
            if user_input.strip().lower() in ['exit', 'quit', '退出']:
                print("再见！")
                break
                
            logger.info(f"用户输入: {user_input}")
            
            # 对于搜索请求，确保有数据
            if "搜索" in user_input:
                original_search = tool_manager.tools["search"]
                tool_manager.tools["search"] = lambda query, data=sample_data: original_search(query, data)
            
            result = await agent.run(user_input)
            print(f"Agent: {result}")
            logger.info(f"Agent回复: {result}")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"发生错误: {e}")
            logger.exception(f"交互错误: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 