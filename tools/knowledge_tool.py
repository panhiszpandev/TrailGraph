import os

from config import ANSWER_THRESHOLD, EXPLORATION_THRESHOLD
from tools.base_tool import BaseTool

KNOWLEDGE_DIR = "knowledge"


def parse_node_file(filepath):
    summary = ""
    parent = ""
    children = []
    related = []
    key_points = []
    content_lines = []
    in_content = False

    with open(filepath) as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("summary:"):
                summary = line.replace("summary:", "").strip()
            elif line.startswith("parent:"):
                parent = line.replace("parent:", "").strip()
            elif line.startswith("children:"):
                raw = line.replace("children:", "").strip().strip("[]")
                children = [x.strip() for x in raw.split(",") if x.strip()]
            elif line.startswith("related:"):
                raw = line.replace("related:", "").strip().strip("[]")
                related = [x.strip() for x in raw.split(",") if x.strip()]
            elif line.startswith("key_points:"):
                raw = line.replace("key_points:", "").strip().strip("[]")
                key_points = [x.strip().strip('"') for x in raw.split(",") if x.strip()]
            elif line == "## Content":
                in_content = True
            elif in_content:
                content_lines.append(line)

    content = "\n".join(content_lines).strip()
    return summary, parent, children, related, key_points, content


def build_parents_chain(node_path):
    parents = []
    current = node_path

    while True:
        filepath = os.path.join(KNOWLEDGE_DIR, current)
        if not os.path.exists(filepath):
            break
        summary, parent, _, _, _, _ = parse_node_file(filepath)
        if not parent:
            break
        parent_filepath = os.path.join(KNOWLEDGE_DIR, parent)
        if not os.path.exists(parent_filepath):
            break
        parent_summary, _, _, _, _, _ = parse_node_file(parent_filepath)
        parents.append({"name": parent, "summary": parent_summary})
        current = parent

    return parents


def build_node_info(node_path, view):
    filepath = os.path.join(KNOWLEDGE_DIR, node_path)

    if not os.path.exists(filepath):
        return None

    summary, _, children, related, key_points, content = parse_node_file(filepath)

    node_name = os.path.basename(node_path)

    current_node = {"name": node_name, "summary": summary}

    if view == "focused":
        current_node["content"] = content
    else:
        current_node["key_points"] = key_points

    children_info = []
    for child_path in children:
        child_filepath = os.path.join(KNOWLEDGE_DIR, child_path)
        if os.path.exists(child_filepath):
            child_summary, _, _, _, _, _ = parse_node_file(child_filepath)
            children_info.append({"name": child_path, "summary": child_summary})

    related_info = []
    for rel_path in related:
        rel_filepath = os.path.join(KNOWLEDGE_DIR, rel_path)
        if os.path.exists(rel_filepath):
            rel_summary, _, _, _, _, _ = parse_node_file(rel_filepath)
            related_info.append({"name": rel_path, "summary": rel_summary})

    parents_info = build_parents_chain(node_path)

    return {
        "current_node": current_node,
        "parents": parents_info,
        "children": children_info,
        "related": related_info,
    }


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

    def reset(self):
        self.visited = []
        self.hop_count = 0

    def run(self, node, view="exploration", score=0, reason=""):
        if node in self.visited:
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

        result = build_node_info(node, view)
        if result is None:
            return {"error": f"Node '{node}' not found in knowledge base."}

        result["metadata"] = {
            "hop_count": self.hop_count,
            "visited": self.visited,
        }

        return result

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
