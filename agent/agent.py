import os

from agent.openrouter_client import OpenRouterClient

DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o")


class Agent:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.client = OpenRouterClient(model=DEFAULT_MODEL)
        self.messages = []
        self._load_system_prompt()

    def _load_system_prompt(self):
        prompt_path = os.path.join("prompts", "system.md")
        if os.path.exists(prompt_path):
            with open(prompt_path) as f:
                system_prompt = f.read().strip()
            self.messages.append({"role": "system", "content": system_prompt})

    def run(self, task=None):
        if task:
            self._step(task)
        else:
            self._loop()

    def _loop(self):
        print("Agent started. Type 'exit' to quit.")
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ("exit", "quit"):
                break
            if not user_input:
                continue
            self._step(user_input)

    def _step(self, user_input):
        self.messages.append({"role": "user", "content": user_input})

        if self.verbose:
            print(f"[verbose] Sending {len(self.messages)} messages to model")

        response = self.client.complete(self.messages)
        self.messages.append({"role": "assistant", "content": response})

        print(f"Agent: {response}")
