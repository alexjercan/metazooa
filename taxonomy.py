import argparse
import json
import re
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from graphviz import Digraph


def find_roots(graph: Dict[str, List[str]]) -> List[str]:
    all_nodes = set(graph.keys())
    children = {c for kids in graph.values() for c in kids}
    return list(all_nodes - children)


def parse_taxonomy_tree(lines: List[str]) -> Dict[str, List[str]]:
    """
    Parse an ASCII taxonomy tree into an adjacency list graph.
    Returns dict: {parent: [children]}
    """
    graph = defaultdict(list)
    stack: List[Tuple[int, str]] = []  # keeps (depth, node_name)
    for raw_line in lines:
        if not raw_line.strip():
            continue

        prefix_match = re.match(r"^([| +\\-]*)", raw_line)
        assert prefix_match is not None

        prefix = prefix_match.group(1)
        depth = prefix.count("|") + prefix.count(" ") // 2
        name = re.sub(r"^[| +\\-]*", "", raw_line).strip()
        while stack and stack[-1][0] >= depth:
            stack.pop()

        if stack:
            parent = stack[-1][1]
            if name == parent:
                name = f"{name}_child"
            graph[parent].append(name)

        if not name:
            continue

        if name not in graph:
            graph[name] = []

        stack.append((depth, name))

    metazoa_children = []
    for root in find_roots(graph):
        if root != "Metazoa":
            metazoa_children.append(root)

    graph["Metazoa"] = metazoa_children
    return dict(graph)


def build_nested(graph: Dict[str, List[str]], node: str, common_names: Dict[str, str]) -> Dict[str, Any] | str:
    children = graph[node]

    if not children:
        return common_names.get(node, node)

    return {
        child: build_nested(graph, child, common_names)
        for child in children
    }


def graph_to_nested(graph: Dict[str, List[str]], common_names: Dict[str, str]) -> Dict[str, Any]:
    roots = find_roots(graph)

    return {
        root: build_nested(graph, root, common_names)
        for root in roots
    }


def is_leaf(graph: Dict[str, List[str]], node: str) -> bool:
    return len(graph[node]) == 0


def graph_to_graphviz(graph: Dict[str, List[str]], common_names: Optional[Dict[str, str]] = None) -> Digraph:
    dot = Digraph()
    dot.attr(rankdir="TB")
    dot.attr(splines="ortho")
    dot.attr(nodesep="0.4")
    dot.attr(ranksep="0.6")

    for parent, children in graph.items():

        parent_label = parent
        if common_names and parent in common_names:
            parent_label = f"{parent}\n({common_names[parent]})"

        # Style leaf vs internal nodes
        if is_leaf(graph, parent):
            dot.node(parent, label=parent_label, shape="box")
        else:
            dot.node(parent, label=parent_label, shape="ellipse")

        for child in children:
            dot.edge(parent, child)

    return dot


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate taxonomy visualizations from tree data")
    parser.add_argument(
        "--tree-file",
        default="commontree.txt",
        help="Input taxonomy tree file (default: commontree.txt)",
    )
    parser.add_argument(
        "--names-file",
        default="name_map.json",
        help="Input common names mapping file (default: name_map.json)",
    )
    parser.add_argument(
        "--output-json",
        default="taxonomy-graph.json",
        help="Output nested JSON file (default: taxonomy-graph.json)",
    )
    parser.add_argument(
        "--output-svg",
        default="taxonomy_tree",
        help="Output SVG file name without extension (default: taxonomy_tree)",
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Skip generating JSON output",
    )
    parser.add_argument(
        "--no-svg",
        action="store_true",
        help="Skip generating SVG output",
    )

    args = parser.parse_args()

    with open(args.tree_file, "r") as f:
        lines = f.readlines()

    with open(args.names_file, "r") as f:
        common_names = json.load(f)

    graph = parse_taxonomy_tree(lines)

    if not args.no_json:
        nested = graph_to_nested(graph, common_names)
        with open(args.output_json, "w") as f:
            json.dump(nested, f)
        print(f"Wrote taxonomy graph to {args.output_json}")

    if not args.no_svg:
        dot = graph_to_graphviz(graph, common_names)
        dot.render(args.output_svg, format="svg", cleanup=True)
        print(f"Wrote taxonomy visualization to {args.output_svg}.svg")
