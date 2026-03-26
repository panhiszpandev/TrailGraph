import json
import os

from agent.openrouter_client import OpenRouterClient
from tools.knowledge_tool import GetKnowledgeContext

DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
MAX_TOOL_ITERATIONS = 10
EXPLORATION_THRESHOLD = 60
ANSWER_THRESHOLD = 85
MAX_HOPS = 5


class Agent:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.client = OpenRouterClient(model=DEFAULT_MODEL)
        self.tools = [GetKnowledgeContext()]
        self.tool_schemas = [tool.to_schema() for tool in self.tools]
        self.tool_map = {tool.name: tool for tool in self.tools}
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
        for tool in self.tools:
            tool.reset()

        self.messages.append({"role": "user", "content": user_input})

        best_node = None
        best_score = 0

        for iteration in range(MAX_TOOL_ITERATIONS):
            if self.verbose:
                print(f"[verbose] Iteration {iteration + 1}, messages: {len(self.messages)}")

            message = self.client.complete(self.messages, tools=self.tool_schemas)
            self.messages.append(message)

            tool_calls = message.get("tool_calls")

            if not tool_calls:
                print(f"Agent: {message.get('content', '')}")
                return

            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])
                score = tool_args.get("score", 0)
                node = tool_args.get("node", "")

                if self.verbose:
                    print(f"[verbose] Calling tool: {tool_name} | node: {node} | score: {score}")

                if score > best_score:
                    best_score = score
                    best_node = node

                tool = self.tool_map.get(tool_name)
                if tool:
                    hop_count = tool.hop_count
                    result = tool.run(**tool_args)
                else:
                    result = {"error": f"Tool '{tool_name}' not found."}
                    hop_count = 0

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result),
                })

                if score < EXPLORATION_THRESHOLD and hop_count > 0:
                    self._fallback(best_node, best_score)
                    return

                if hop_count >= MAX_HOPS:
                    self._fallback(best_node, best_score)
                    return

        self._fallback(best_node, best_score)

    def _fallback(self, best_node, best_score):
        node_name = os.path.basename(best_node) if best_node else "unknown"
        print(
            f"\n[agent] Could not find a confident match. "
            f"The closest I found was: {node_name} ({best_score}/100).\n"
            f"Was that what you meant, or could you clarify your question?"
        )
