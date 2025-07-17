class ToolManager:
    def __init__(self):
        self.tools = {}

    def register(self, name, tool):
        self.tools[name] = tool

    def get(self, name):
        return self.tools.get(name)

    def run(self, name, *args, **kwargs):
        tool = self.get(name)
        if tool:
            return tool(*args, **kwargs)
        raise ValueError(f"Tool {name} not found")
