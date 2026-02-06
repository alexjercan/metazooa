#!/usr/bin/env python3
"""Find the best species guess for a given clade using minimax strategy."""

import argparse
import json
import os
import random
from collections import defaultdict
from typing import Dict, List, Optional


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


def best_leaf_guess(tree: Dict[str, List[str]]) -> List[str]:
    """
    Find the best leaf guess that minimizes the worst-case number of remaining candidates.

    Uses a minimax strategy: for each candidate guess, simulate what happens if you
    get feedback about the LCA (lowest common ancestor) between your guess and the
    actual answer. Pick the guess where the largest group of possibilities is smallest.
    """
    candidates = [node for node in tree.keys() if is_leaf(tree, node)]

    best_worst_case = float("inf")
    best_guesses: List[str] = []

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
            best_guesses = []

        if worst_case == best_worst_case:
            best_guesses.append(guess)

    return best_guesses


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
        default="commontree.json",
        help="Taxonomy tree file in JSON format (default: commontree.json)",
    )
    parser.add_argument(
        "--game",
        default="metazooa",
        help="Game to use for species data (metazooa or metaflora, default: metazooa)",
    )

    args = parser.parse_args()

    # Check if we have the required files
    if os.path.isfile(args.tree_file) is False:
        game = args.game.lower()
        if game == "metazooa":
            url = "https://metazooa.com/play/practice"
        elif game == "metaflora":
            url = "https://flora.metazooa.com/play/practice"
        else:
            print(f"Error: Invalid game '{args.game}', must be 'metazooa' or 'metaflora'")
            exit(1)

        print(f"Error: {args.tree_file} not found, downloading...")
        os.system(f"python3 scripts/get_species.py --requests 100 --mapping-file name_map.json --url {url}")
        os.system(f"python3 scripts/generate_tree.py --names-file name_map.json --output {args.tree_file}")

    # Load JSON tree
    try:
        with open(args.tree_file, "r") as f:
            json_tree = json.load(f)
    except FileNotFoundError:
        print(f"Error: {args.tree_file} not found")
        exit(1)

    # Convert JSON tree to graph and build name map
    graph: Dict[str, List[str]] = {}
    name_map: Dict[str, str] = {}
    json_tree_to_graph(json_tree, graph, name_map)

    # Convert common names to scientific names for exclusions
    scientific_map = {v: k for k, v in name_map.items()}
    except_species = [scientific_map.get(s, s) for s in args.without.split(",") if s.strip()]

    # Prune and guess
    tree = prune_graph(dict(graph), args.clade, except_species)
    guesses = best_leaf_guess(tree)

    if not guesses:
        print(f"No valid candidates found in clade {args.clade}")
        exit(1)

    guess = random.choice(guesses)
    named_guess = name_map.get(guess, guess)
    print(f"Best guess for clade {args.clade}: {named_guess} ({guess})")
    print(f"Other equally good guesses: {[name_map.get(g, g) for g in guesses if g != guess]}")
