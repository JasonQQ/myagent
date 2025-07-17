from pydantic import BaseModel

class MemoryManager(BaseModel):
    memory: list = []

    def add(self, item):
        self.memory.append(item)

    def get_all(self):
        return self.memory

    def clear(self):
        self.memory = []
