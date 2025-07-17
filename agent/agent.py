from pydantic import BaseModel
from agent.llm import LLM
from agent.memory_manager import MemoryManager
from agent.tool_manager import ToolManager
from typing import Any
import asyncio

class BaseAgent(BaseModel):
    name: str
    llm: LLM
    memory_manager: MemoryManager
    tool_manager: ToolManager

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
