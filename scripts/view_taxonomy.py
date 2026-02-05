#!/usr/bin/env python3
"""Generate taxonomy visualizations from JSON tree data."""

import argparse
import json
from typing import Any, Dict, List, Optional

from graphviz import Digraph


def json_to_graph(json_tree: Dict[str, Any]) -> Dict[str, List[str]]:
    """Convert nested JSON tree to adjacency list graph."""
    graph: Dict[str, List[str]] = {}

    def traverse(node: Dict[str, Any]) -> None:
        name = node.get("name", node.get("scientific", "Unknown"))
        graph[name] = []

        if "children" in node:
            for child in node["children"]:
                child_name = child.get("name", child.get("scientific", "Unknown"))
                graph[name].append(child_name)
                traverse(child)

    traverse(json_tree)
    return graph


def build_nested(
    node: Dict[str, Any], common_names: Optional[Dict[str, str]] = None
) -> Dict[str, Any] | str:
    """Convert JSON node to nested dictionary structure."""
    scientific = node.get("scientific", node.get("name", "Unknown"))
    common = node.get("name", scientific)

    if "children" not in node or not node["children"]:
        return f"{scientific} ({common})" if scientific != common else scientific

    return {
        child.get("scientific", child.get("name", "Unknown")): build_nested(child, common_names)
        for child in node["children"]
    }


def json_to_nested(json_tree: Dict[str, Any]) -> Dict[str, Any]:
    """Convert JSON tree to nested dictionary."""
    scientific = json_tree.get("scientific", json_tree.get("name", "Unknown"))
    return {scientific: build_nested(json_tree)}


def is_leaf(graph: Dict[str, List[str]], node: str) -> bool:
    """Check if a node is a leaf."""
    return len(graph.get(node, [])) == 0


def graph_to_graphviz(graph: Dict[str, List[str]]) -> Digraph:
    """Convert graph to Graphviz visualization."""
    dot = Digraph()
    dot.attr(rankdir="TB")
    dot.attr(splines="ortho")
    dot.attr(nodesep="0.4")
    dot.attr(ranksep="0.6")

    for parent, children in graph.items():
        # Style leaf vs internal nodes
        if is_leaf(graph, parent):
            dot.node(parent, label=parent, shape="box")
        else:
            dot.node(parent, label=parent, shape="ellipse")

        for child in children:
            dot.edge(parent, child)

    return dot


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate taxonomy visualizations from JSON tree data")
    parser.add_argument(
        "--tree-file",
        default="commontree.json",
        help="Input taxonomy tree file in JSON format (default: commontree.json)",
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

    try:
        with open(args.tree_file, "r") as f:
            json_tree = json.load(f)
    except FileNotFoundError:
        print(f"Error: {args.tree_file} not found")
        exit(1)

    graph = json_to_graph(json_tree)

    if not args.no_json:
        nested = json_to_nested(json_tree)
        with open(args.output_json, "w") as f:
            json.dump(nested, f, indent=2)
        print(f"Wrote taxonomy graph to {args.output_json}")

    if not args.no_svg:
        dot = graph_to_graphviz(graph)
        dot.render(args.output_svg, format="svg", cleanup=True)
        print(f"Wrote taxonomy visualization to {args.output_svg}.svg")
