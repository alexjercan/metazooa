import argparse
import json
import re
from collections import defaultdict
from typing import Dict, List, Optional, Tuple


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
    stack: List[Tuple[int, str]] = []
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


def is_leaf(graph: Dict[str, List[str]], node: str) -> bool:
    """Check if a node is a leaf in the graph"""
    return len(graph[node]) == 0


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


def best_leaf_guess(tree: Dict[str, List[str]]) -> Optional[str]:
    """
    Find the best leaf guess that minimizes the worst-case number of remaining candidates.

    Uses a minimax strategy: for each candidate guess, simulate what happens if you
    get feedback about the LCA (lowest common ancestor) between your guess and the
    actual answer. Pick the guess where the largest group of possibilities is smallest.
    """
    candidates = [node for node in tree.keys() if is_leaf(tree, node)]

    best_guess = None
    best_worst_case = float("inf")

    for guess in candidates:
        buckets: Dict[str, int] = defaultdict(int)

        # Count how many candidates would fall into each bucket based on their LCA
        for leaf in candidates:
            clade = lca(tree, guess, leaf)
            buckets[clade] += 1

            if buckets[clade] >= best_worst_case:
                break

        worst_case = max(buckets.values())
        if worst_case < best_worst_case:
            best_worst_case = worst_case
            best_guess = guess

    return best_guess


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find the best species guess for a given clade with optional exclusions"
    )
    parser.add_argument(
        "--clade",
        required=True,
        help="Clade to guess a species from",
    )
    parser.add_argument(
        "--without",
        default="",
        help="Species to exclude from guessing (comma-separated common names)",
    )
    parser.add_argument(
        "--tree-file",
        default="commontree.txt",
        help="Taxonomy tree file (default: commontree.txt)",
    )
    parser.add_argument(
        "--names-file",
        default="name_map.json",
        help="Species name mapping file (default: name_map.json)",
    )

    args = parser.parse_args()

    with open(args.names_file, "r") as f:
        name_map = json.load(f)

    scientific_map = {v: k for k, v in name_map.items()}
    except_species = [scientific_map.get(s, s) for s in args.without.split(",") if s.strip()]

    with open(args.tree_file, "r") as f:
        lines = f.readlines()

    graph = parse_taxonomy_tree(lines)
    tree = prune_graph(dict(graph), args.clade, except_species)

    guess = best_leaf_guess(tree)

    if guess is None:
        print(f"No valid candidates found in clade {args.clade}")
        exit(1)

    named_guess = name_map.get(guess, guess)
    print(f"Best guess for clade {args.clade}: {named_guess} ({guess})")
