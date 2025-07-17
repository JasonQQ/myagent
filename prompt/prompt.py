class PromptManager:
    def __init__(self):
        self.prompts = {}

    def add_prompt(self, name, template):
        self.prompts[name] = template

    def get_prompt(self, name):
        return self.prompts.get(name, "")
