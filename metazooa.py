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
    """ Check if a node is a leaf in the graph """
    return len(graph[node]) == 0


def find_parent(graph: Dict[str, List[str]], child: str) -> Optional[str]:
    """ Find the parent of a given child node """

    for parent, children in graph.items():
        if child in children:
            return parent

    return None


def remove_node(graph: Dict[str, List[str]], node: str) -> None:
    """ Recursively remove a node and its descendants from the graph """

    children = graph.pop(node, [])

    for child in children:
        remove_node(graph, child)


def is_ancestor_of(graph: Dict[str, List[str]], ancestor: str, descendant: str) -> bool:
    """ Check if 'ancestor' is an ancestor of 'descendant' in the graph """

    parent = find_parent(graph, descendant)
    while parent is not None:
        if parent == ancestor:
            return True
        parent = find_parent(graph, parent)

    return False


def prune_graph(graph: Dict[str, List[str]], clade: str, species: str) -> Dict[str, List[str]]:
    """ Prune the graph to only include the specified clade, and removing all the related species. """

    # Remove all other branches except the clade
    new_graph = {}
    for k, v in graph.items():
        if is_ancestor_of(graph, clade, k) or k == clade:
            new_graph[k] = v

    graph = new_graph

    # Remove the species from the clade, by pruning up the tree
    # We remove the child clade that is a direct descendant of the clade that leads to the species
    node = species
    parent = find_parent(graph, node)
    if parent is None:
        return graph

    while parent != clade:
        node = parent
        parent = find_parent(graph, node)
        if parent is None:
            return graph

    remove_node(graph, node)
    children = graph.get(clade, [])
    if node in children:
        children.remove(node)
        graph[clade] = children

    return graph


def find_root(tree: Dict[str, List[str]]) -> str:
    """ Find the root of the tree """

    all_nodes = set(tree.keys())
    children = set(c for v in tree.values() for c in v)
    roots = all_nodes - children
    if len(roots) != 1:
        raise ValueError("Tree must have exactly one root")

    return next(iter(roots))


def build_parent_map(tree: Dict[str, List[str]]) -> Dict[str, str]:
    """ Build a map of child -> parent for the tree """

    parent = {}
    for p, children in tree.items():
        for c in children:
            parent[c] = p

    return parent


def lca(tree: Dict[str, List[str]], a: str, b: str) -> str:
    """ Find the lowest common ancestor of nodes a and b in the tree """

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
    Find the best leaf guess that minimizes the worst-case number of remaining candidates

    # Example:

    Mammals
    ├── Dogs: Husky, Corgi, Bulldog
    ├── Cats: Lion, Tiger, House Cat
    └── Primates: Chimp, Gorilla

    If I guess "Husky" (Same for Corgi, Bulldog, and basically same for the cats)
    - Husky vs other Dogs (Corgi, Bulldog) -> LCA is "Dogs" (2 candidates)
    - Husky vs Cats (Lion, Tiger, House Cat) -> LCA is "Mammals" (3 candidates)
    - Husky vs Primates (Chimp, Gorilla) -> LCA is "Mammals" (2 candidates)
    - Worst case: 5 animals (the 3 cats + 2 primates in the "Mammals" bucket)

    If I guess "Chimp" (or Gorilla) (a primate):
    - Chimp vs other Primates (Gorilla) -> LCA is "Primates" (1 candidate)
    - Chimp vs Dogs (Husky, Corgi, Bulldog) -> LCA is "Mammals" (3 candidates)
    - Chimp vs Cats (Lion, Tiger, House Cat) -> LCA is "Mammals" (3 candidates)
    - Worst case: 6 animals (the 3 dogs + 3 cats in the "Mammals" bucket)
    """

    # Find all the possible candidates (leaf nodes) in the tree
    candidates = [node for node in tree.keys() if is_leaf(tree, node)]

    best_guess = None
    best_worst_case = float("inf")

    # Simulate the guess for each candidate and calculate
    # the worst-case number of remaining candidates
    for guess in candidates:
        buckets: Dict[str, int] = defaultdict(int)

        # Count how many candidates would fall into each bucket
        # based on their LCA with the guess
        for leaf in candidates:
            clade = lca(tree, guess, leaf)
            buckets[clade] += 1

            if buckets[clade] >= best_worst_case:
                break

        # The worst-case number of remaining candidates is
        # the size of the largest bucket
        worst_case = max(buckets.values())
        if worst_case < best_worst_case:
            best_worst_case = worst_case
            best_guess = guess

    return best_guess


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--guess-clade",
        type=str,
        help="Get best guess species for a given clade",
    )
    parser.add_argument(
        "--without",
        type=str,
        help="Species to exclude from guessing, comma-separated",
    )

    args = parser.parse_args()

    clade = args.guess_clade
    except_species = args.without.split(",") if args.without else []

    with open("name_map.json", "r") as f:
        name_map = json.load(f)

    scientific_map = {v: k for k, v in name_map.items()}
    except_species = [scientific_map.get(s, s) for s in except_species]

    with open("commontree.txt", "r") as f:
        lines = f.readlines()

    graph = parse_taxonomy_tree(lines)

    tree = dict(graph)
    for s in except_species:
        tree = prune_graph(tree, clade, s)

    guess = best_leaf_guess(tree)

    if guess is None:
        print(f"No valid candidates found in clade {clade}")
        exit(1)

    named_guess = name_map.get(guess, guess)
    print(f"Best guess for clade {clade}: {named_guess} ({guess})")
