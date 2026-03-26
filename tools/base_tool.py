class BaseTool:
    name = ""
    description = ""

    def run(self, **kwargs):
        raise NotImplementedError("Each tool must implement the run() method")

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
