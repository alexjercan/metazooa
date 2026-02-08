#!/usr/bin/env python3
"""Find the best species guess for a given clade using minimax strategy."""

import argparse
import json
import random
from collections import defaultdict
from typing import Dict, List, Tuple

from helpers import (
    ensure_tree_file,
    get_all_leaves,
    json_tree_to_graph,
    lca,
    lowercase_tree,
    prune_graph,
)


def best_leaf_guess(tree: Dict[str, List[str]]) -> List[str]:
    """
    Find the best leaf guess that minimizes the worst-case number of remaining candidates.

    Uses a minimax strategy: for each candidate guess, simulate what happens if you
    get feedback about the LCA (lowest common ancestor) between your guess and the
    actual answer. Pick the guess where the largest group of possibilities is smallest.
    """
    candidates = get_all_leaves(tree)

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


def prepare_tree(tree_path: str) -> Tuple[Dict[str, List[str]], Dict[str, str]]:
    """Load and prepare the tree from a JSON file."""
    try:
        with open(tree_path, "r") as f:
            json_tree = json.load(f)
    except FileNotFoundError:
        print(f"Error: {tree_path} not found")
        exit(1)

    # Make the json_tree case insensitive for clade matching
    json_tree = lowercase_tree(json_tree)

    graph: Dict[str, List[str]] = {}
    name_map: Dict[str, str] = {}
    json_tree_to_graph(json_tree, graph, name_map)

    return graph, name_map


def guess_metazooa(tree: Dict[str, List[str]], clade: str, except_species: List[str]) -> Tuple[str, List[str]]:
    """Find the best guess for a species in the given clade, excluding certain species."""
    pruned_tree = prune_graph(dict(tree), clade, except_species)
    guesses = best_leaf_guess(pruned_tree)

    if not guesses:
        raise ValueError(f"No valid candidates found in clade {clade}")

    guess = random.choice(guesses)
    return guess, guesses


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
    ensure_tree_file(args.tree_file, args.game.lower())

    graph, name_map = prepare_tree(args.tree_file)
    clade = args.clade.lower()
    without = [s.strip().lower() for s in args.without.split(",") if s.strip()]

    scientific_map = {v: k for k, v in name_map.items()}
    except_species = [scientific_map.get(s, s) for s in without]

    guess, guesses = guess_metazooa(graph, clade, except_species)
    named_guess = name_map.get(guess, guess)
    print(f"Best guess for clade {args.clade}: {named_guess} ({guess})")
    print(
        f"Other equally good guesses: {[name_map.get(g, g) for g in guesses if g != guess]}"
    )
