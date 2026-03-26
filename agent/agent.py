import json
import os

from agent.openrouter_client import OpenRouterClient
from config import DEFAULT_MODEL, MAX_TOOL_ITERATIONS, SYSTEM_PROMPT_PATH


class Agent:
    def __init__(self, tools, prompt_vars=None, verbose=False):
        self.verbose = verbose
        self.client = OpenRouterClient(model=os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL))
        self.tools = tools
        self.tool_schemas = [tool.to_schema() for tool in self.tools]
        self.tool_map = {tool.name: tool for tool in self.tools}
        self.messages = []
        self._load_system_prompt(prompt_vars or {})

    def _load_system_prompt(self, prompt_vars):
        if os.path.exists(SYSTEM_PROMPT_PATH):
            with open(SYSTEM_PROMPT_PATH) as f:
                system_prompt = f.read().strip()
            if prompt_vars:
                system_prompt = system_prompt.format(**prompt_vars)
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
        hints = [h for tool in self.tools for h in [tool.pending_hint()] if h]
        content = user_input + "\n\n" + "\n".join(hints) if hints else user_input

        for tool in self.tools:
            tool.reset()

        self.messages.append({"role": "user", "content": content})

        for iteration in range(MAX_TOOL_ITERATIONS):
            if self.verbose:
                print(f"[verbose] Iteration {iteration + 1}, messages: {len(self.messages)}")

            active_tools = [s for tool, s in zip(self.tools, self.tool_schemas) if not tool.disabled]
            message = self.client.complete(self.messages, tools=active_tools or None)
            self.messages.append(message)

            tool_calls = message.get("tool_calls")

            if not tool_calls:
                print(f"Agent: {message.get('content', '')}")
                return

            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])

                tool = self.tool_map.get(tool_name)

                if self.verbose:
                    info = tool.verbose_info(tool_args) if tool else ""
                    print(f"[verbose] Calling tool: {tool_name} {info}")
                if tool:
                    result = tool.run(**tool_args)
                else:
                    result = {"error": f"Tool '{tool_name}' not found."}

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result),
                })

                if tool:
                    fallback = tool.should_fallback()
                    if fallback:
                        print(fallback)
                        return

        for tool in self.tools:
            fallback = tool.should_fallback()
            if fallback:
                print(fallback)
                return
