class BaseTool:
    name = ""
    description = ""
    disabled = False

    def run(self, **kwargs):
        raise NotImplementedError("Each tool must implement the run() method")

    def reset(self):
        pass

    def should_fallback(self):
        return None

    def pending_hint(self):
        return None

    def verbose_info(self, tool_args):
        return ""

    def to_schema(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters(),
            },
        }

    def parameters(self):
        return {"type": "object", "properties": {}, "required": []}
