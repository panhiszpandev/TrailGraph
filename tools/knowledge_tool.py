import os

from config import ANSWER_THRESHOLD, EXPLORATION_THRESHOLD, MAX_HOPS
from graph.parser import build_node_info
from tools.base_tool import BaseTool


class GetKnowledgeContext(BaseTool):
    name = "get_knowledge_context"
    description = (
        "Retrieves the content and local graph view of a knowledge base node. "
        "Always provide a score (0-100) reflecting how relevant this node is to the user question, and a reason. "
        "Use view='exploration' to navigate the graph. "
        f"Use view='focused' to get full content when score >= {ANSWER_THRESHOLD}."
    )

    def __init__(self):
        self.visited = []
        self.hop_count = 0
        self.best_node = None
        self.best_score = 0
        self.last_score = 0
        self.last_error = False
        self.dead_end = False

    def reset(self):
        self.visited = []
        self.hop_count = 0
        self.best_node = None
        self.best_score = 0
        self.last_score = 0
        self.last_error = False
        self.dead_end = False
        self.disabled = False

    def run(self, node, view="exploration", score=0, reason=""):
        self.last_score = score
        self.last_error = False
        if score > self.best_score:
            self.best_score = score
            self.best_node = node

        if score >= ANSWER_THRESHOLD:
            view = "focused"

        if node in self.visited and view != "focused":
            return {
                "already_visited": True,
                "node": node,
                "suggestion": "This node was already visited. Consider exploring other candidates.",
                "metadata": {
                    "hop_count": self.hop_count,
                    "visited": self.visited,
                },
            }

        self.visited.append(node)
        self.hop_count += 1

        if view == "focused":
            self.disabled = True

        result = build_node_info(node, view)
        if result is None:
            self.last_error = True
            return {"error": f"Node '{node}' not found in knowledge base."}

        result["metadata"] = {
            "hop_count": self.hop_count,
            "visited": self.visited,
        }

        if view == "exploration" and not result.get("children") and not result.get("related"):
            self.dead_end = True

        return result

    def should_fallback(self):
        if self.hop_count == 0 or self.disabled:
            return None
        if self.dead_end or self.last_error or self.best_score < EXPLORATION_THRESHOLD or self.hop_count >= MAX_HOPS:
            node_name = os.path.basename(self.best_node) if self.best_node else "unknown"
            return (
                f"\n[agent] Could not find a confident match. "
                f"The closest I found was: {node_name} ({self.best_score}/100).\n"
                f"Was that what you meant, or could you clarify your question?"
            )
        return None

    def pending_hint(self):
        if self.best_node:
            return (
                f"[hint: if the user is confirming the previous suggestion, "
                f"retrieve the focused content of '{self.best_node}' and answer. "
                f"Otherwise treat it as a new question.]"
            )
        return None

    def verbose_info(self, tool_args):
        return f"| node: {tool_args.get('node', '')} | score: {tool_args.get('score', '')}"

    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "node": {
                    "type": "string",
                    "description": "Path to the knowledge node relative to the knowledge/ directory, e.g. 'entry_points/CRM.md' or 'sales/Lead_qualification.md'",
                },
                "view": {
                    "type": "string",
                    "enum": ["exploration", "focused"],
                    "description": f"Use 'exploration' to navigate. Use 'focused' when score >= {ANSWER_THRESHOLD} to get full content.",
                },
                "score": {
                    "type": "integer",
                    "description": f"Relevance score 0-100 for this node relative to the user question. 0-{EXPLORATION_THRESHOLD - 1}: low, {EXPLORATION_THRESHOLD}-{ANSWER_THRESHOLD - 1}: medium, {ANSWER_THRESHOLD}-100: high.",
                },
                "reason": {
                    "type": "string",
                    "description": "Brief explanation of why this score was assigned.",
                },
            },
            "required": ["node", "score", "reason"],
        }
