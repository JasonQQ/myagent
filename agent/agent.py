from pydantic import BaseModel, Field
from agent.llm import LLM
from agent.memory_manager import MemoryManager
from agent.tool_manager import ToolManager
from typing import Any, Dict, List, Optional
import asyncio
import json
import re

class BaseAgent(BaseModel):
    name: str = Field(
        description="Agent的名称标识",
        min_length=1,
        max_length=100
    )
    llm: LLM = Field(
        description="语言模型实例，用于处理对话和生成回复"
    )
    memory_manager: MemoryManager = Field(
        description="记忆管理器，用于存储和管理对话历史"
    )
    tool_manager: ToolManager = Field(
        description="工具管理器，用于注册和调用各种工具"
    )

    model_config = {
        "arbitrary_types_allowed": True
    }

    async def run(self, prompt: str) -> Any:
        self.memory_manager.add({"role": "user", "content": prompt})
        if prompt.startswith("tool:"):
            try:
                parts = prompt[5:].strip().split()
                tool_name = parts[0]
                args = [int(x) if x.isdigit() else x for x in parts[1:]]
                # 工具一般为同步，这里用to_thread包裹
                result = await asyncio.to_thread(self.tool_manager.run, tool_name, *args)
                self.memory_manager.add({"role": "agent", "content": str(result)})
                return result
            except Exception as e:
                return f"工具调用失败: {e}"
        messages = self.memory_manager.get_all()
        try:
            reply = await self.llm.chat(messages)
            self.memory_manager.add({"role": "agent", "content": reply})
            return reply
        except Exception as e:
            return f"LLM调用失败: {e}"


class ToolCallingAgent(BaseAgent):
    """基于React框架的工具调用智能体
    
    特点：
    - 实现think-act模式
    - 支持工具调用
    - 支持基本对话功能
    - 可扩展的智能体基座
    """
    
    system_prompt: str = Field(
        default="""你是一个智能助手，具备以下能力：
1. 思考问题并制定解决方案
2. 调用工具来完成任务
3. 与用户进行自然对话

当需要调用工具时，请按照以下格式：
THINK: 你的思考过程
ACT: 工具名称 参数1 参数2 ...

可用的工具有：
{tools}

请根据用户的需求，先思考，然后决定是否需要调用工具或直接回复。""",
        description="系统提示词，定义智能体的行为和能力"
    )
    
    max_iterations: int = Field(
        default=5,
        description="最大迭代次数，防止无限循环",
        ge=1,
        le=20
    )

    def __init__(self, **data):
        super().__init__(**data)
        # 初始化时添加系统提示词到记忆
        if not self.memory_manager.memory:
            self.memory_manager.add({"role": "system", "content": self._get_system_prompt()})

    def _get_system_prompt(self) -> str:
        """获取包含可用工具信息的系统提示词"""
        tools_info = []
        for tool_name in self.tool_manager.tools.keys():
            tools_info.append(f"- {tool_name}")
        
        tools_str = "\n".join(tools_info) if tools_info else "暂无可用工具"
        return self.system_prompt.format(tools=tools_str)

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """解析LLM的响应，提取THINK和ACT部分"""
        think_match = re.search(r'THINK:\s*(.*?)(?=ACT:|$)', response, re.DOTALL | re.IGNORECASE)
        act_match = re.search(r'ACT:\s*(.*?)(?=THINK:|$)', response, re.DOTALL | re.IGNORECASE)
        
        think = think_match.group(1).strip() if think_match else ""
        act = act_match.group(1).strip() if act_match else ""
        
        return {
            "think": think,
            "act": act,
            "is_tool_call": bool(act)
        }

    def _extract_tool_call(self, act_text: str) -> Optional[Dict[str, Any]]:
        """从ACT文本中提取工具调用信息"""
        if not act_text:
            return None
            
        parts = act_text.strip().split()
        if not parts:
            return None
            
        tool_name = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        return {
            "tool_name": tool_name,
            "args": args
        }

    async def _execute_tool_call(self, tool_call: Dict[str, Any]) -> str:
        """执行工具调用"""
        try:
            tool_name = tool_call["tool_name"]
            args = tool_call["args"]
            
            # 检查工具是否存在
            if tool_name not in self.tool_manager.tools:
                return f"错误：工具 '{tool_name}' 不存在"
            
            # 执行工具调用
            result = await asyncio.to_thread(
                self.tool_manager.run, 
                tool_name, 
                *args
            )
            
            return f"工具 '{tool_name}' 执行结果: {result}"
            
        except Exception as e:
            return f"工具调用失败: {str(e)}"

    async def run(self, prompt: str) -> Any:
        """运行智能体，实现React框架的think-act模式"""
        # 添加用户输入到记忆
        self.memory_manager.add({"role": "user", "content": prompt})
        
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # 获取当前对话历史
            messages = self.memory_manager.get_all()
            
            try:
                # 调用LLM进行思考
                response = await self.llm.chat(messages)
                
                # 解析响应
                parsed = self._parse_llm_response(response)
                
                # 添加思考过程到记忆
                if parsed["think"]:
                    self.memory_manager.add({
                        "role": "assistant", 
                        "content": f"THINK: {parsed['think']}"
                    })
                
                # 如果没有工具调用，直接返回回复
                if not parsed["is_tool_call"]:
                    # 提取纯文本回复（去除THINK/ACT标记）
                    clean_response = response
                    if parsed["think"]:
                        clean_response = response.replace(f"THINK: {parsed['think']}", "").strip()
                    if parsed["act"]:
                        clean_response = clean_response.replace(f"ACT: {parsed['act']}", "").strip()
                    
                    self.memory_manager.add({"role": "assistant", "content": clean_response})
                    return clean_response
                
                # 执行工具调用
                tool_call = self._extract_tool_call(parsed["act"])
                if tool_call:
                    tool_result = await self._execute_tool_call(tool_call)
                    
                    # 添加工具调用和结果到记忆
                    self.memory_manager.add({
                        "role": "assistant", 
                        "content": f"ACT: {parsed['act']}"
                    })
                    self.memory_manager.add({
                        "role": "user", 
                        "content": f"工具执行结果: {tool_result}"
                    })
                    
                    # 如果这是最后一次迭代，返回工具结果
                    if iteration >= self.max_iterations:
                        return tool_result
                    
                    # 继续下一轮迭代，让LLM基于工具结果继续思考
                    continue
                
                # 如果解析失败，直接返回原始响应
                self.memory_manager.add({"role": "assistant", "content": response})
                return response
                
            except Exception as e:
                error_msg = f"LLM调用失败: {str(e)}"
                self.memory_manager.add({"role": "assistant", "content": error_msg})
                return error_msg
        
        # 达到最大迭代次数
        return f"达到最大迭代次数({self.max_iterations})，停止执行"

    def add_tool(self, name: str, tool_func):
        """添加工具到工具管理器"""
        self.tool_manager.register(name, tool_func)
        # 更新系统提示词
        self._update_system_prompt()

    def _update_system_prompt(self):
        """更新系统提示词中的工具列表"""
        # 找到并更新系统消息
        for i, message in enumerate(self.memory_manager.memory):
            if message.get("role") == "system":
                self.memory_manager.memory[i]["content"] = self._get_system_prompt()
                break
