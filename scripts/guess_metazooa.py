#!/usr/bin/env python3
"""Find the best species guess using minmax or entropy-based strategies."""

import argparse
import json
import math
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


def compute_entropy(candidates: List[str]) -> float:
    """Compute Shannon entropy of a uniform distribution over candidates."""
    if len(candidates) <= 1:
        return 0.0
    return math.log2(len(candidates))


def best_leaf_guess_minmax(tree: Dict[str, List[str]]) -> List[str]:
    candidates = get_all_leaves(tree)

    best_worst_case = float("inf")
    best_guesses: List[str] = []

    for guess in candidates:
        buckets: Dict[str, int] = defaultdict(int)

        for target in candidates:
            clade = lca(tree, guess, target)
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


def best_leaf_guess_entropy(tree: Dict[str, List[str]]) -> List[str]:
    """
    Find the best leaf guess that minimizes expected entropy after feedback.

    Uses information theory: for each candidate guess, compute the expected entropy
    after receiving LCA feedback. Pick the guess with the highest information gain
    (largest reduction in entropy).
    """
    candidates = get_all_leaves(tree)
    initial_entropy = compute_entropy(candidates)

    if initial_entropy == 0:
        return candidates

    best_info_gain = -1.0
    best_guesses: List[str] = []

    for guess in candidates:
        # Group candidates by their LCA with this guess
        feedback_groups: Dict[str, int] = defaultdict(int)

        for leaf in candidates:
            clade = lca(tree, guess, leaf)
            feedback_groups[clade] += 1

        # Compute expected entropy after receiving feedback
        expected_entropy_after = 0.0
        total_candidates = len(candidates)

        for _, group_size in feedback_groups.items():
            probability = group_size / total_candidates
            # Entropy of the group (assuming uniform distribution within group)
            group_entropy = compute_entropy([""] * group_size)  # Simplified: use group size
            expected_entropy_after += probability * group_entropy

        information_gain = initial_entropy - expected_entropy_after

        if information_gain > best_info_gain:
            best_info_gain = information_gain
            best_guesses = [guess]
        elif abs(information_gain - best_info_gain) < 1e-9:  # Float comparison tolerance
            best_guesses.append(guess)

    return best_guesses


def best_leaf_guess_hybrid(tree: Dict[str, List[str]], entropy_weight: float = 0.5) -> List[str]:
    """
    Find the best leaf guess using a hybrid approach combining minmax and entropy.

    Args:
        tree: The taxonomy graph
        entropy_weight: Weight for entropy score (0-1).
                       0 = pure minmax, 1 = pure entropy, 0.5 = balanced

    Returns:
        List of equally good guesses according to hybrid scoring
    """
    candidates = get_all_leaves(tree)
    initial_entropy = compute_entropy(candidates)

    if initial_entropy == 0:
        return candidates

    scores = {}

    for guess in candidates:
        # Minmax: worst-case group size
        feedback_groups_minmax: Dict[str, int] = defaultdict(int)
        for leaf in candidates:
            clade = lca(tree, guess, leaf)
            feedback_groups_minmax[clade] += 1

        worst_case = max(feedback_groups_minmax.values())
        minmax_score = -worst_case  # Negative because we want to minimize

        # Entropy: information gain
        feedback_groups_entropy: Dict[str, int] = defaultdict(int)
        for leaf in candidates:
            clade = lca(tree, guess, leaf)
            feedback_groups_entropy[clade] += 1

        expected_entropy_after = 0.0
        total_candidates = len(candidates)
        for _, group_size in feedback_groups_entropy.items():
            probability = group_size / total_candidates
            group_entropy = compute_entropy([""] * group_size)
            expected_entropy_after += probability * group_entropy

        information_gain = initial_entropy - expected_entropy_after
        entropy_score = information_gain

        # Hybrid score: weighted combination
        # Normalize scores to 0-1 range first
        scores[guess] = {
            "minmax": minmax_score,
            "entropy": entropy_score,
            "worst_case": worst_case,
            "info_gain": information_gain,
        }

    # Normalize and combine
    minmax_scores = [s["minmax"] for s in scores.values()]
    entropy_scores = [s["entropy"] for s in scores.values()]

    minmax_min, minmax_max = min(minmax_scores), max(minmax_scores)
    entropy_min, entropy_max = min(entropy_scores), max(entropy_scores)

    # Avoid division by zero
    minmax_range = minmax_max - minmax_min if minmax_max > minmax_min else 1
    entropy_range = entropy_max - entropy_min if entropy_max > entropy_min else 1

    best_hybrid_score = -float("inf")
    best_guesses: List[str] = []

    for guess, score_dict in scores.items():
        minmax_norm = (score_dict["minmax"] - minmax_min) / minmax_range
        entropy_norm = (score_dict["entropy"] - entropy_min) / entropy_range

        hybrid_score = (
            entropy_weight * entropy_norm + (1 - entropy_weight) * minmax_norm
        )

        if hybrid_score > best_hybrid_score:
            best_hybrid_score = hybrid_score
            best_guesses = [guess]
        elif abs(hybrid_score - best_hybrid_score) < 1e-9:
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


def guess_metazooa(
    tree: Dict[str, List[str]],
    clade: str,
    except_species: List[str],
    strategy: str = "minmax",
    entropy_weight: float = 0.5,
) -> Tuple[str, List[str]]:
    """
    Find the best guess for a species in the given clade, excluding certain species.

    Args:
        tree: The taxonomy graph
        clade: The clade to search in
        except_species: Species to exclude
        strategy: "minmax", "entropy", or "hybrid"
        entropy_weight: Weight for hybrid strategy (only used if strategy="hybrid")

    Returns:
        (best_guess, all_equally_good_guesses)
    """
    pruned_tree = prune_graph(dict(tree), clade, except_species)

    if strategy == "minmax":
        guesses = best_leaf_guess_minmax(pruned_tree)
    elif strategy == "entropy":
        guesses = best_leaf_guess_entropy(pruned_tree)
    elif strategy == "hybrid":
        guesses = best_leaf_guess_hybrid(pruned_tree, entropy_weight)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

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
    parser.add_argument(
        "--strategy",
        default="minmax",
        choices=["minmax", "entropy", "hybrid"],
        help="Strategy to use: minmax (worst-case), entropy (average-case), or hybrid (default: minmax)",
    )
    parser.add_argument(
        "--entropy-weight",
        type=float,
        default=0.5,
        help="Weight for entropy in hybrid strategy, 0-1 (default: 0.5)",
    )

    args = parser.parse_args()
    ensure_tree_file(args.tree_file, args.game.lower())

    graph, name_map = prepare_tree(args.tree_file)
    clade = args.clade.lower()
    without = [s.strip().lower() for s in args.without.split(",") if s.strip()]

    scientific_map = {v: k for k, v in name_map.items()}
    except_species = [scientific_map.get(s, s) for s in without]

    guess, guesses = guess_metazooa(
        graph, clade, except_species, args.strategy, args.entropy_weight
    )
    named_guess = name_map.get(guess, guess)
    print(f"Best guess for clade {args.clade} ({args.strategy}): {named_guess} ({guess})")
    print(
        f"Other equally good guesses: {[name_map.get(g, g) for g in guesses if g != guess]}"
    )
