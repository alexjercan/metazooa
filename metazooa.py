import argparse
import json
import re
from collections import defaultdict
from typing import List, Tuple, Dict, Set, Optional

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


def build_nested(graph, node, common_names):
    children = graph[node]

    if not children:
        return common_names.get(node, node)

    return {
        child: build_nested(graph, child, common_names)
        for child in children
    }


def graph_to_nested(graph, common_names):
    roots = find_roots(graph)
    return {
        root: build_nested(graph, root, common_names)
        for root in roots
    }


def is_leaf(graph, node):
    return len(graph[node]) == 0


def graph_to_graphviz(graph, common_names=None):
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

    exit(0)
    dot = graph_to_graphviz(graph, common_names)
    dot.render("taxonomy_tree", format="svg")


def find_roots(graph):
    all_nodes = set(graph.keys())
    children = {c for kids in graph.values() for c in kids}
    return list(all_nodes - children)


def parse_taxonomy_tree(lines):
    """
    Parse an ASCII taxonomy tree into an adjacency list graph.
    Returns dict: {parent: [children]}
    """
    graph = defaultdict(list)
    stack = []  # keeps (depth, node_name)

    for raw_line in lines:
        if not raw_line.strip():
            continue

        # Count indentation depth based on leading tree characters
        prefix_match = re.match(r"^([| +\\-]*)", raw_line)
        prefix = prefix_match.group(1)

        # Each 2 characters roughly represent one depth level
        depth = prefix.count("|") + prefix.count(" ") // 2

        # Extract node name (remove tree drawing chars)
        name = re.sub(r"^[| +\\-]*", "", raw_line).strip()

        # Adjust stack to current depth
        while stack and stack[-1][0] >= depth:
            stack.pop()

        # Add edge from parent -> child
        if stack:
            parent = stack[-1][1]

            # Make child unique if needed
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


def get_all_species_in_clade(node: str, graph: Dict[str, List[str]],
                             excluded: Set[str]) -> Set[str]:
    """
    Get all leaf nodes (species) in the subtree rooted at `node`,
    excluding any nodes in the `excluded` set.
    """
    # If this node is excluded, return empty set
    if node in excluded:
        return set()

    # If this node has no children, it's a leaf (species)
    if not graph[node]:
        return {node}

    # Recursively get all species from children
    species = set()
    for child in graph[node]:
        species.update(get_all_species_in_clade(child, graph, excluded))

    return species


def get_best_guess(clade: str, graph: Dict[str, List[str]], except_species: List[str]) -> Optional[str]:
    """
    Find the best guess within the given clade.

    Strategy: Find the child subtree with the most species (excluding
    those already guessed). This maximizes information gain.
    """
    excluded = set(except_species)

    # Get all possible species in the current clade
    all_in_clade = get_all_species_in_clade(clade, graph, excluded)

    # If no species left, we're stuck (shouldn't happen in normal play)
    if not all_in_clade:
        return None

    # If only one species left, that must be it
    if len(all_in_clade) == 1:
        return list(all_in_clade)[0]

    # Find the child with the largest valid subtree
    best_child = None
    best_count = 0

    for child in graph[clade]:
        child_species = get_all_species_in_clade(child, graph, excluded)
        count = len(child_species)

        # We want a child that has at least one valid species
        if count > best_count:
            best_count = count
            best_child = child

    # If we found a good child subtree, recurse into it
    if best_child is not None:
        return get_best_guess(best_child, graph, except_species)

    # Fallback: just pick any child that hasn't been excluded
    for child in graph[clade]:
        if child not in excluded:
            return child

    return None


def guess_main(clade: str, except_species: List[str]) -> None:
    """
    Main function to determine the best guess.

    Args:
        clade: The current clade we're narrowed down to (e.g., "Metazoa", "Aves")
        except_species: List of species we've already guessed (and were wrong)
    """
    with open("name_map.json", "r") as f:
        name_map = json.load(f)

    scientific_map = {v: k for k, v in name_map.items()}
    except_species = [scientific_map.get(s, s) for s in except_species]

    with open("commontree.txt", "r") as f:
        lines = f.readlines()

    graph = parse_taxonomy_tree(lines)

    guess = get_best_guess(clade, graph, except_species)

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
