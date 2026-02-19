#!/usr/bin/env python3
"""Batch test script to evaluate initial guess performance within a clade."""

import argparse
import os
import random
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
from typing import Dict, List

from guess_metazooa import guess_metazooa, prepare_tree
from helpers import (
    ensure_tree_file,
    get_all_leaves,
    is_ancestor_of,
    prune_graph,
)
from play_metazooa import build_parent_map, evaluate_guess
from rich.progress import Progress


def get_clade_species(graph: Dict[str, List[str]], clade: str) -> List[str]:
    """
    Get all leaf species that belong to a given clade.

    Args:
        graph: The taxonomy graph
        clade: The clade to get species from

    Returns:
        List of all species (leaves) in the clade
    """
    species = []
    visited = set()

    def traverse(node: str):
        if node in visited:
            return
        visited.add(node)

        children = graph.get(node, [])
        if not children:  # It's a leaf
            species.append(node)
        else:
            for child in children:
                traverse(child)

    traverse(clade)
    return species


def is_node_in_clade(graph: Dict[str, List[str]], node: str, clade: str) -> bool:
    """Check if a node is in the clade"""
    return is_ancestor_of(graph, clade, node) or node == clade


def run_single_game(args):
    initial_guess, target, graph, strategy = args
    return count_guesses_to_target(initial_guess, target, graph, strategy)


def count_guesses_to_target(
    initial_guess: str,
    target: str,
    graph: Dict[str, List[str]],
    strategy: str = "minmax",
) -> int:
    """
    Count how many guesses it takes to find the target species starting from initial_guess.
    Uses the same game logic as play_metazooa with evaluate_guess and prune_graph.

    Args:
        initial_guess: The first species to guess
        target: The target species to find
        graph: The taxonomy graph
        strategy: The guessing strategy to use ("minmax" or "entropy")

    Returns:
        Number of guesses it took to find the target

    Raises:
        AssertionError: If target is unreachable (algorithm failed to find it)
    """
    remaining_graph = deepcopy(graph)
    parent_map = build_parent_map(remaining_graph)
    num_guesses = 0
    current_guess = initial_guess

    while num_guesses < 100:
        num_guesses += 1

        # Evaluate the guess
        is_correct, hint = evaluate_guess(target, current_guess, remaining_graph, parent_map)

        if is_correct:
            return num_guesses

        # Prune the graph to remove the wrong guess and its branch
        remaining_graph = prune_graph(remaining_graph, hint, [current_guess])

        # Rebuild parent map with remaining species
        parent_map = build_parent_map(remaining_graph)

        # Find the next best guess
        _, guesses = guess_metazooa(remaining_graph, hint, [], strategy=strategy)
        if not guesses:
            # Target is unreachable - algorithm failed
            raise AssertionError(f"CRITICAL: Target '{target}' became unreachable! Initial guess was '{initial_guess}'. Algorithm failed to find the target.")

        # Use random choice like in guess_metazooa.py
        current_guess = random.choice(guesses)

    # Should never reach here if algorithm works correctly
    raise AssertionError(f"CRITICAL: Max guesses (100) exceeded for target '{target}' with initial guess '{initial_guess}'")


def batch_test_clade(
    initial_guess: str,
    clade: str,
    graph: Dict[str, List[str]],
    name_map: Dict[str, str],
    strategy: str = "minmax",
    num_tests: int = 1000,
    progress: Progress = None,
) -> tuple[int, float]:
    """
    Test an initial guess by playing many random games within a clade.

    Args:
        initial_guess: The initial guess to test
        clade: The clade to test within
        graph: The taxonomy graph (already pruned to clade)
        name_map: The species name mapping
        strategy: The guessing strategy to use ("minmax" or "entropy")
        num_tests: Number of games to play (default: 1000)

    Returns:
        (total_guesses, average_guesses): Total guesses and average per game
    """
    clade_species = get_clade_species(graph, clade)

    if not clade_species:
        raise ValueError(f"No species found in clade '{clade}'")

    tasks = [
        (initial_guess, random.choice(clade_species), graph, strategy)
        for _ in range(num_tests)
    ]

    total_guesses = 0
    failed_games = []

    if progress is not None:
        task_id = progress.add_task(f"Testing {format_guess(initial_guess, name_map)}...", total=num_tests, transient=True)

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(run_single_game, t) for t in tasks]

        for i, future in enumerate(as_completed(futures)):
            try:
                total_guesses += future.result()
            except AssertionError as e:
                failed_games.append((i, tasks[i][1], str(e)))

            if progress is not None:
                progress.update(task_id, advance=1)

        progress.remove_task(task_id)

    if failed_games:
        print("\n❌ CRITICAL ERRORS DETECTED:")
        print("=" * 60)
        for test_num, target_species, error_msg in failed_games:
            target_name = name_map.get(target_species, target_species)
            print(f"Test #{test_num}: {target_name} ({target_species})")
            print(f"  Error: {error_msg}")
        print("=" * 60)
        raise RuntimeError(f"Algorithm failed in {len(failed_games)} out of {num_tests} tests!")

    average_guesses = total_guesses / num_tests
    return total_guesses, average_guesses


def format_guess(scientific_name: str, name_map: Dict[str, str]) -> str:
    """Format a guess with both scientific and common name."""
    common_name = name_map.get(scientific_name, scientific_name)
    if common_name != scientific_name:
        return f"{common_name} ({scientific_name})"
    return scientific_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Batch test an initial guess across random targets in a clade"
    )
    parser.add_argument(
        "--initial-guess",
        help="Initial guess to test (common or scientific name). If not provided, tests all available candidates",
    )
    parser.add_argument(
        "--clade",
        default="metazoa",
        help="Clade to test within (default: metazoa)",
    )
    parser.add_argument(
        "--tree-file",
        default="commontree.json",
        help="Taxonomy tree file in JSON format (default: commontree.json)",
    )
    parser.add_argument(
        "--game",
        default="metazooa",
        choices=["metazooa", "metaflora"],
        help="Game to test (metazooa or metaflora, default: metazooa)",
    )
    parser.add_argument(
        "--strategy",
        default="minmax",
        choices=["minmax", "entropy"],
        help="Strategy to use: minmax (worst-case), entropy (average-case) (default: minmax)",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=1000,
        help="Number of random games to play (default: 1000)",
    )

    args = parser.parse_args()
    print(f"🔬 Starting batch test for clade '{args.clade}' with initial guess '{args.initial_guess or 'ALL CANDIDATES'}' ({args.batch} games each)")

    ensure_tree_file(args.tree_file, args.game.lower())

    full_graph, name_map = prepare_tree(args.tree_file)

    # Find the clade
    clade_input = args.clade.lower()
    clade = None
    if clade_input in full_graph:
        clade = clade_input
    else:
        # Try to find by common name
        for sci, common in name_map.items():
            if common == clade_input:
                clade = sci
                break

    if clade is None:
        print(f"Error: Clade '{args.clade}' not found")
        exit(1)

    # Prune the graph to only include the clade (it's known)
    graph = prune_graph(full_graph, clade, [])

    print(f"📍 Testing within clade: {format_guess(clade, name_map)}")

    initial_time = time.time()

    # If initial guess is provided, test it
    if args.initial_guess:
        initial_guess_input = args.initial_guess.lower()
        initial_guess = None
        if initial_guess_input in graph:
            initial_guess = initial_guess_input
        else:
            # Try to find by common name
            for sci, common in name_map.items():
                if common == initial_guess_input:
                    initial_guess = sci
                    break

        if initial_guess is None:
            print(f"Error: Initial guess '{args.initial_guess}' not found in clade '{args.clade}'")
            exit(1)

        # Validate that initial guess is in the clade
        assert is_node_in_clade(graph, initial_guess, clade), \
            f"Error: Initial guess '{format_guess(initial_guess, name_map)}' is not in clade '{format_guess(clade, name_map)}'"

        # Run batch test for single initial guess
        print(f"📊 Batch Testing: {format_guess(initial_guess, name_map)}")
        print(f"Games: {args.batch}")
        print("=" * 60)

        try:
            total_guesses, average_guesses = batch_test_clade(initial_guess, clade, graph, name_map, args.strategy, args.batch)

            print(f"✓ All {args.batch} games completed successfully!")
            print(f"Total guesses: {total_guesses}")
            print(f"Average guesses per game: {average_guesses:.2f}")
            print("=" * 60 + "\n")
        except (RuntimeError, ValueError) as e:
            print(f"\n❌ {e}")
            exit(1)
    else:
        # Find the best initial guess for this clade
        print(f"🔍 Finding best initial guess for clade: {format_guess(clade, name_map)}")
        print(f"Games per candidate: {args.batch}")
        print("=" * 60)

        # The animals that we are going to compare
        initial_guesses = get_all_leaves(graph)

        if not initial_guesses:
            print(f"Error: No species found in clade '{args.clade}' to test as initial guesses")
            exit(1)

        print(f"Will test {len(initial_guesses)} candidates\n")

        results = []

        with Progress() as progress:
            task_id = progress.add_task("Testing candidates...", total=len(initial_guesses))

            for initial_guess in initial_guesses:
                try:
                    total_guesses, average_guesses = batch_test_clade(initial_guess, clade, graph, name_map, args.strategy, args.batch, progress)
                    results.append((initial_guess, total_guesses, average_guesses))
                    print(f"✓ {format_guess(initial_guess, name_map):<40} {average_guesses:>6.2f} avg")
                except (RuntimeError, ValueError) as e:
                    print(f"⚠️  Skipping {format_guess(initial_guess, name_map)}: {str(e)[:60]}...")
                    continue

                progress.update(task_id, advance=1)

        if not results:
            print("Error: Could not test any candidates")
            exit(1)

        # Sort by average guesses (lower is better)
        results.sort(key=lambda x: x[2])

        print("\n" + "=" * 60)
        print("🏆 RESULTS (sorted by average guesses):")
        print("=" * 60)

        for rank, (species, _, average) in enumerate(results, 1):
            marker = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f" {rank}."
            print(f"{marker} {format_guess(species, name_map):<40} {average:>6.2f} avg")

        best_species, best_total, best_average = results[0]
        print("=" * 60)
        print(f"\n✨ Best initial guess: {format_guess(best_species, name_map)}")
        print(f"   Average guesses per game: {best_average:.2f}\n")

    total_time = time.time() - initial_time
    print(f"⏱️  Total testing time: {total_time:.2f} seconds")
