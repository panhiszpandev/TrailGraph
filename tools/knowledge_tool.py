import os

from tools.base_tool import BaseTool

KNOWLEDGE_DIR = "knowledge"


def parse_node_file(filepath):
    summary = ""
    children = []
    related = []
    content_lines = []
    in_content = False

    with open(filepath) as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("summary:"):
                summary = line.replace("summary:", "").strip()
            elif line.startswith("children:"):
                raw = line.replace("children:", "").strip().strip("[]")
                children = [x.strip() for x in raw.split(",") if x.strip()]
            elif line.startswith("related:"):
                raw = line.replace("related:", "").strip().strip("[]")
                related = [x.strip() for x in raw.split(",") if x.strip()]
            elif line == "## Content":
                in_content = True
            elif in_content:
                content_lines.append(line)

    content = "\n".join(content_lines).strip()
    return summary, children, related, content


def find_parent(node_path):
    parts = node_path.replace("\\", "/").split("/")
    if len(parts) == 1:
        return None

    subdir = parts[0]
    entry_points_dir = os.path.join(KNOWLEDGE_DIR, "entry_points")

    for filename in os.listdir(entry_points_dir):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(entry_points_dir, filename)
        _, children, _, _ = parse_node_file(filepath)
        node_name = "/".join(parts)
        if any(node_name in c or subdir.lower() in c.lower() for c in children):
            summary, _, _, _ = parse_node_file(filepath)
            return {"name": f"entry_points/{filename}", "summary": summary}

    return None


def build_node_info(node_path, view):
    filepath = os.path.join(KNOWLEDGE_DIR, node_path)

    if not os.path.exists(filepath):
        return None

    summary, children, related, content = parse_node_file(filepath)

    node_name = os.path.basename(node_path)

    current_node = {"name": node_name, "summary": summary}

    if view == "focused":
        current_node["content"] = content
    else:
        excerpt = content[:300] + "..." if len(content) > 300 else content
        current_node["content_excerpt"] = excerpt

    children_info = []
    for child_path in children:
        child_filepath = os.path.join(KNOWLEDGE_DIR, child_path)
        if os.path.exists(child_filepath):
            child_summary, _, _, _ = parse_node_file(child_filepath)
            children_info.append({"name": child_path, "summary": child_summary})

    related_info = []
    for rel_path in related:
        rel_filepath = os.path.join(KNOWLEDGE_DIR, rel_path)
        if os.path.exists(rel_filepath):
            rel_summary, _, _, _ = parse_node_file(rel_filepath)
            related_info.append({"name": rel_path, "summary": rel_summary})

    parent = find_parent(node_path)
    parents_info = [parent] if parent else []

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
        "Use view='exploration' to see children and related nodes. "
        "Use view='focused' to get the full content of the node."
    )

    def run(self, node, view="exploration"):
        result = build_node_info(node, view)
        if result is None:
            return {"error": f"Node '{node}' not found in knowledge base."}
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
                    "description": "Use 'exploration' to see children and related nodes. Use 'focused' to get full content.",
                },
            },
            "required": ["node"],
        }
