#!/usr/bin/env python3
"""Information theory analysis for optimal starting guess selection."""

import argparse
import math
import time
from typing import Dict, List

from guess_metazooa import prepare_tree
from helpers import (
    ensure_tree_file,
    lca,
    prune_graph,
)
from rich.progress import Progress


def get_clade_species(graph: Dict[str, List[str]], clade: str) -> List[str]:
    """Get all leaf species in a clade."""
    species = []
    visited = set()

    def traverse(node: str):
        if node in visited:
            return
        visited.add(node)
        children = graph.get(node, [])
        if not children:
            species.append(node)
        else:
            for child in children:
                traverse(child)

    traverse(clade)
    return species


def get_clade_nodes(graph: Dict[str, List[str]], clade: str) -> List[str]:
    """Get all nodes (internal and leaves) in a clade."""
    nodes = []
    visited = set()

    def traverse(node: str):
        if node in visited:
            return
        visited.add(node)
        nodes.append(node)
        children = graph.get(node, [])
        for child in children:
            traverse(child)

    traverse(clade)
    return nodes


def compute_entropy(candidates: List[str]) -> float:
    """Compute Shannon entropy of a uniform distribution over candidates."""
    if len(candidates) <= 1:
        return 0.0
    return math.log2(len(candidates))


def compute_information_gain(
    initial_guess: str,
    clade: str,
    graph: Dict[str, List[str]],
) -> tuple[float, float]:
    """
    Compute the information gain from making an initial guess.

    Args:
        initial_guess: The species to guess
        clade: The clade (all possible targets)
        graph: The taxonomy graph

    Returns:
        (information_gain, expected_entropy_after_guess)
    """
    candidates = get_clade_species(graph, clade)
    initial_entropy = compute_entropy(candidates)

    if initial_entropy == 0:
        return 0.0, 0.0

    # For each candidate target, compute what LCA feedback we'd get
    feedback_groups: Dict[str, int] = {}

    for target in candidates:
        feedback_clade = lca(graph, initial_guess, target)
        feedback_groups[feedback_clade] = feedback_groups.get(feedback_clade, 0) + 1

    # Compute expected entropy after receiving feedback
    expected_entropy_after = 0.0
    total_candidates = len(candidates)

    for group_clade, group_size in feedback_groups.items():
        probability = group_size / total_candidates
        # Get remaining candidates in this group
        group_candidates = get_clade_species(graph, group_clade)
        group_entropy = compute_entropy(group_candidates)
        expected_entropy_after += probability * group_entropy

    information_gain = initial_entropy - expected_entropy_after

    return information_gain, expected_entropy_after


def expected_guesses_lower_bound(
    information_gain: float, initial_entropy: float
) -> float:
    """
    Compute a lower bound on expected guesses using information gain.

    This assumes optimal play where we gain `information_gain` bits per guess.
    Lower bound: ceil(initial_entropy / information_gain)
    """
    if information_gain <= 0:
        return float("inf")
    return initial_entropy / information_gain


def format_guess(scientific_name: str, name_map: Dict[str, str]) -> str:
    """Format a guess with both scientific and common name."""
    common_name = name_map.get(scientific_name, scientific_name)
    if common_name != scientific_name:
        return f"{common_name} ({scientific_name})"
    return scientific_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Information theory analysis of starting guesses"
    )
    parser.add_argument(
        "--initial-guess",
        help="Compute analysis for a specific initial guess",
    )
    parser.add_argument(
        "--clade",
        default="metazoa",
        help="Clade to analyze (default: metazoa)",
    )
    parser.add_argument(
        "--tree-file",
        default="commontree.json",
        help="Taxonomy tree file (default: commontree.json)",
    )
    parser.add_argument(
        "--game",
        default="metazooa",
        choices=["metazooa", "metaflora"],
        help="Game (default: metazooa)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Show top N guesses (default: 10)",
    )

    args = parser.parse_args()
    ensure_tree_file(args.tree_file, args.game.lower())

    full_graph, name_map = prepare_tree(args.tree_file)

    # Find the clade
    clade_input = args.clade.lower()
    clade = None
    if clade_input in full_graph:
        clade = clade_input
    else:
        for sci, common in name_map.items():
            if common == clade_input:
                clade = sci
                break

    if clade is None:
        print(f"Error: Clade '{args.clade}' not found")
        exit(1)

    # Prune the graph to only include the clade (it's known)
    graph = prune_graph(full_graph, clade, [])

    initial_time = time.time()

    candidates = get_clade_species(graph, clade)
    initial_entropy = compute_entropy(candidates)

    print("📊 Information Theory Analysis")
    print(f"Clade: {format_guess(clade, name_map)}")
    print(f"Number of species: {len(candidates)}")
    print(f"Initial entropy: {initial_entropy:.4f} bits")
    print(f"Theoretical minimum guesses: {initial_entropy:.4f}")
    print("=" * 80)

    if args.initial_guess:
        initial_guess_input = args.initial_guess.lower()
        initial_guess = None
        if initial_guess_input in graph:
            initial_guess = initial_guess_input
        else:
            for sci, common in name_map.items():
                if common == initial_guess_input:
                    initial_guess = sci
                    break

        if initial_guess is None:
            print(f"Error: Initial guess '{args.initial_guess}' not found")
            exit(1)

        info_gain, exp_entropy_after = compute_information_gain(initial_guess, clade, graph)
        exp_guesses = expected_guesses_lower_bound(info_gain, initial_entropy)

        print(f"📈 Analysis for: {format_guess(initial_guess, name_map)}")
        print(f"Information gain: {info_gain:.4f} bits")
        print(f"Expected entropy after guess: {exp_entropy_after:.4f} bits")
        print(f"Expected guesses (lower bound): {exp_guesses:.4f}")
        print("=" * 80 + "\n")

    else:
        print(f"\n🔍 Analyzing all {len(candidates)} candidates...")
        print("=" * 80)

        results = []

        with Progress() as progress:
            task_id = progress.add_task("Testing candidates...", total=len(candidates))

            for guess in candidates:
                info_gain, exp_entropy_after = compute_information_gain(guess, clade, graph)
                exp_guesses = expected_guesses_lower_bound(info_gain, initial_entropy)
                results.append((guess, info_gain, exp_entropy_after, exp_guesses))

                progress.update(task_id, advance=1)

        results.sort(key=lambda x: x[3])

        print(f"🏆 Top {args.top_n} starting guesses:")
        print("=" * 80)
        print(
            f"{'Rank':<5} {'Species':<40} {'Info Gain':<12} {'Expected Guesses':<18}"
        )
        print("=" * 80)

        for rank, (species, info_gain, _, exp_guesses) in enumerate(
            results[: args.top_n], 1
        ):
            species_name = format_guess(species, name_map)
            print(
                f"{rank:<5} {species_name:<40} {info_gain:<12.4f} {exp_guesses:<18.4f}"
            )

        print("=" * 80)
        best_species, best_info_gain, _, best_exp_guesses = results[0]
        print(f"\n✨ Best starting guess: {format_guess(best_species, name_map)}")
        print(f"   Information gain: {best_info_gain:.4f} bits")
        print(f"   Expected guesses: {best_exp_guesses:.4f}\n")

    total_time = time.time() - initial_time
    print(f"⏱️  Total testing time: {total_time:.2f} seconds")
