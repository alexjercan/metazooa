"""Helper functions for working with the tree graph structure."""

import os
from typing import Dict, List, Optional


def ensure_tree_file(tree_path: str, game: str) -> None:
    """Ensure the tree file exists, if not, download and generate it."""
    if os.path.isfile(tree_path):
        return

    if game == "metazooa":
        url = "https://metazooa.com/play/practice"
    elif game == "metaflora":
        url = "https://flora.metazooa.com/play/practice"
    else:
        print(f"Error: Invalid game '{game}', must be 'metazooa' or 'metaflora'")
        exit(1)

    print(f"Error: {tree_path} not found, downloading...")
    os.system(
        f"python3 scripts/get_species.py --requests 100 --mapping-file name_map.json --url {url}"
    )
    os.system(
        f"python3 scripts/generate_tree.py --names-file name_map.json --output {tree_path}"
    )


def is_leaf(graph: Dict[str, List[str]], node: str) -> bool:
    """Check if a node is a leaf in the graph"""
    return len(graph[node]) == 0


def get_all_leaves(graph: Dict[str, List[str]]) -> List[str]:
    """Get all leaf nodes (species) from the graph"""
    return [node for node in graph.keys() if is_leaf(graph, node)]


def find_parent(graph: Dict[str, List[str]], child: str) -> Optional[str]:
    """Find the parent of a given child node"""
    for parent, children in graph.items():
        if child in children:
            return parent
    return None


def remove_node(graph: Dict[str, List[str]], node: str) -> None:
    """Recursively remove a node and its descendants from the graph"""
    children = graph.pop(node, [])
    for child in children:
        remove_node(graph, child)


def is_ancestor_of(graph: Dict[str, List[str]], ancestor: str, descendant: str) -> bool:
    """Check if 'ancestor' is an ancestor of 'descendant' in the graph"""
    parent = find_parent(graph, descendant)
    while parent is not None:
        if parent == ancestor:
            return True
        parent = find_parent(graph, parent)
    return False


def lowercase_tree(node: Dict) -> Dict:
    node["scientific"] = node["scientific"].lower()
    if "name" in node:
        node["name"] = node["name"].lower()
    if "children" in node:
        node["children"] = [lowercase_tree(child) for child in node["children"]]
    return node


def prune_graph(graph: Dict[str, List[str]], clade: str, species: List[str]) -> Dict[str, List[str]]:
    """Prune the graph to only include the specified clade, removing related species"""
    # Remove all other branches except the clade
    new_graph = {}
    for k, v in graph.items():
        if is_ancestor_of(graph, clade, k) or k == clade:
            new_graph[k] = v

    graph = new_graph

    # Remove the species from the clade
    for node in species:
        parent = find_parent(graph, node)
        if parent is None:
            continue

        while parent != clade:
            node = parent
            parent = find_parent(graph, node)
            if parent is None:
                break

        remove_node(graph, node)
        children = graph.get(clade, [])
        if node in children:
            children.remove(node)
            graph[clade] = children

    return graph


def json_tree_to_graph(json_node: Dict, graph: Dict[str, List[str]], name_map: Dict[str, str]) -> None:
    """Convert JSON tree structure to adjacency list graph."""
    scientific = json_node.get("scientific", "")

    if scientific not in graph:
        graph[scientific] = []

    if "children" in json_node:
        for child in json_node["children"]:
            child_scientific = child.get("scientific", "")
            graph[scientific].append(child_scientific)
            json_tree_to_graph(child, graph, name_map)

            # Update name map with both scientific and common names
            if child_scientific and "name" in child:
                name_map[child_scientific] = child["name"]

    # Store the common name
    if scientific and "name" in json_node:
        name_map[scientific] = json_node["name"]


def build_parent_map(tree: Dict[str, List[str]]) -> Dict[str, str]:
    """Build a map of child -> parent for the tree"""
    parent = {}
    for p, children in tree.items():
        for c in children:
            parent[c] = p
    return parent


def lca(tree: Dict[str, List[str]], a: str, b: str) -> str:
    """Find the lowest common ancestor of nodes a and b in the tree"""
    parent = build_parent_map(tree)

    # Find all ancestors of a
    ancestors = set()
    x = a
    while x in parent:
        ancestors.add(x)
        x = parent[x]
    ancestors.add(x)  # root

    # Iterate up from b until we find a common ancestor
    y = b
    while y not in ancestors:
        y = parent[y]

    return y
