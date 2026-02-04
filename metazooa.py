import argparse
import json
import re
from collections import defaultdict, deque
from typing import List, Tuple, Dict, Set, Optional, Any

import requests
from bs4 import BeautifulSoup
from graphviz import Digraph
from rich.progress import track


def get_species() -> Tuple[List[str], List[str]]:
    url = "https://metazooa.com/play/practice"
    response = requests.get(url)
    response.raise_for_status()

    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    script = soup.find("script", type="application/json")
    if script and script.string:
        data = json.loads(script.string)
        species_list = data["v"][0][0]["speciesList"]
        scientific_names = []
        names = []
        for species in species_list:
            scientific_names.append(species["scientific"])
            names.append(species["name"])

        return scientific_names, names

    return [], []


def species_main() -> None:
    name_map = {}

    for _ in track(range(100), description="Getting species..."):
        species, names = get_species()
        for s, name in zip(species, names):
            name_map[s] = name

    with open("metazooa-species-sorted.txt", "w") as f:
        names = sorted(name_map.keys())
        for s in names:
            f.write(s + "\n")

    with open("name_map.json", "w") as f:
        json.dump(name_map, f)


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


def taxonomy_main():
    with open("commontree.txt", "r") as f:
        lines = f.readlines()

    with open("name_map.json", "r") as f:
        common_names = json.load(f)

    graph = parse_taxonomy_tree(lines)

    nested = graph_to_nested(graph, common_names)
    with open("taxonomy-graph.json", "w") as f:
        json.dump(nested, f)

    dot = graph_to_graphviz(graph, common_names)
    dot.render("taxonomy_tree", format="svg")


def find_parent(graph: Dict[str, List[str]], child: str) -> Optional[str]:
    for parent, children in graph.items():
        if child in children:
            return parent

    return None


def remove_node(graph: Dict[str, List[str]], node: str) -> None:
    children = graph.pop(node, [])

    for child in children:
        remove_node(graph, child)


def is_ancestor_of(graph: Dict[str, List[str]], ancestor: str, descendant: str) -> bool:
    parent = find_parent(graph, descendant)
    while parent is not None:
        if parent == ancestor:
            return True
        parent = find_parent(graph, parent)

    return False


def prune_graph(graph: Dict[str, List[str]], clade: str, species: str) -> Dict[str, List[str]]:
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
    all_nodes = set(tree.keys())
    children = set(c for v in tree.values() for c in v)
    roots = all_nodes - children
    if len(roots) != 1:
        raise ValueError("Tree must have exactly one root")

    return next(iter(roots))


def build_parent_map(tree: Dict[str, List[str]]) -> Dict[str, str]:
    parent = {}
    for p, children in tree.items():
        for c in children:
            parent[c] = p
    return parent


def lca(tree: Dict[str, List[str]], a: str, b: str) -> str:
    parent = build_parent_map(tree)

    ancestors = set()
    x = a
    while x in parent:
        ancestors.add(x)
        x = parent[x]
    ancestors.add(x)  # root

    y = b
    while y not in ancestors:
        y = parent[y]

    return y


def best_leaf_guess(tree: Dict[str, List[str]]) -> Optional[str]:
    candidates = [node for node in tree.keys() if is_leaf(tree, node)]

    best_guess = None
    best_worst_case = float("inf")

    for guess in candidates:
        buckets: Dict[str, int] = defaultdict(int)

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


def guess_main(clade: str, except_species: List[str]) -> None:
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
        return

    named_guess = name_map.get(guess, guess)
    print(f"Best guess for clade {clade}: {named_guess} ({guess})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--species",
        action="store_true",
        help="Get species from Metazooa",
    )
    parser.add_argument(
        "--taxonomy",
        action="store_true",
        help="Parse taxonomy tree from commontree.txt",
    )
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

    if args.species:
        species_main()

    if args.taxonomy:
        taxonomy_main()

    if args.guess_clade:
        except_species = args.without.split(",") if args.without else []
        guess_main(args.guess_clade, except_species)
