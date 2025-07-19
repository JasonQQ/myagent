#!/usr/bin/env python3
"""
简单的ToolCallingAgent测试程序
使用模拟LLM验证React功能
"""

import asyncio
from agent import ToolCallingAgent
from agent.llm import LLM
from agent.memory_manager import MemoryManager
from agent.tool_manager import ToolManager
from tool import search_tool, add, terminate
from logger import get_logger

logger = get_logger()

class SimpleMockLLM(LLM):
    """简单的模拟LLM，严格按照THINK/ACT格式响应"""
    
    def __init__(self, model: str = "mock-gpt-3.5-turbo", stream: bool = False):
        super().__init__(api_key="mock-key", model=model, stream=stream)
    
    async def chat(self, messages, stream=None, **kwargs):
        """严格按照THINK/ACT格式响应"""
        if stream is None:
            stream = self.stream
            
        # 获取最后一条用户消息
        last_user_message = ""
        for message in reversed(messages):
            if message.get("role") == "user":
                last_user_message = message.get("content", "")
                break
        
        print(f"DEBUG: 用户消息 = '{last_user_message}'")
        
        # 检查是否有工具执行结果
        if "工具执行结果" in last_user_message:
            # 基于工具结果生成最终回复
            if "Python" in last_user_message:
                return "我已经找到了包含'Python'的信息：Python是一种编程语言。这是一个非常流行的编程语言。"
            elif "add" in last_user_message:
                return "计算完成！15 + 27 = 42。"
            else:
                return "工具执行完成，我已经为您处理了请求。"
        
        # 根据用户消息生成响应
        if "你好" in last_user_message or "介绍" in last_user_message or "是谁" in last_user_message:
            return "你好！我是ToolCallingAgent，一个基于React框架的智能助手。"
        
        elif "Python" in last_user_message and "搜索" in last_user_message:
            return "THINK: 用户想要搜索包含'Python'的信息，我需要使用search工具来查找相关内容。\nACT: search Python"
        
        elif "编程语言" in last_user_message and "搜索" in last_user_message:
            return "THINK: 用户想要搜索编程语言相关的信息，我需要使用search工具来查找相关内容。\nACT: search 编程语言"
        
        elif "计算" in last_user_message or "加" in last_user_message:
            return "THINK: 用户要求进行计算，我需要使用add工具来完成数学运算。\nACT: add 15 27"
        
        elif "工具" in last_user_message and "不存在" in last_user_message:
            return "THINK: 用户想要使用一个不存在的工具，我应该告知用户这个工具不存在。\nACT: nonexistent_tool"
        
        else:
            return "我理解您的需求。如果您需要搜索信息、进行计算或使用其他工具，请告诉我具体的要求。"

async def test_tool_calling_agent():
    """测试ToolCallingAgent的React功能"""
    
    print("=== ToolCallingAgent React功能测试 ===")
    print("使用模拟LLM，严格按照THINK/ACT格式\n")
    
    # 初始化组件
    mock_llm = SimpleMockLLM()
    memory_manager = MemoryManager()
    tool_manager = ToolManager()
    
    # 注册工具
    tool_manager.register("search", lambda query, data: search_tool(query, data))
    tool_manager.register("add", add)
    tool_manager.register("terminate", terminate)
    
    # 创建 ToolCallingAgent
    agent = ToolCallingAgent(
        name="TestAgent",
        llm=mock_llm,
        memory_manager=memory_manager,
        tool_manager=tool_manager,
        max_iterations=3
    )
    
    # 示例数据
    sample_data = [
        "Python是一种编程语言",
        "JavaScript是前端开发语言", 
        "Java是企业级开发语言",
        "C++是系统编程语言"
    ]
    
    # 测试用例
    test_cases = [
        "你好，请介绍一下你自己",
        "请搜索包含'Python'的信息",
        "计算 15 + 27 的结果",
        "请搜索编程语言相关的信息"
    ]
    
    for i, user_input in enumerate(test_cases, 1):
        print(f"\n--- 测试 {i} ---")
        print(f"用户: {user_input}")
        
        # 对于搜索工具，需要传入数据
        if "搜索" in user_input:
            original_search = tool_manager.tools["search"]
            tool_manager.tools["search"] = lambda query, data=sample_data: original_search(query, data)
        
        try:
            result = await agent.run(user_input)
            print(f"Agent: {result}")
            print("✅ 测试通过")
            logger.info(f"测试{i}完成: {result}")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            logger.error(f"测试{i}失败: {e}")
    
    print("\n=== 测试完成 ===")
    print("所有测试用例执行完毕。")

if __name__ == "__main__":
    asyncio.run(test_tool_calling_agent()) 