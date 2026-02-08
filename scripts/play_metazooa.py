#!/usr/bin/env python3
"""Interactive Metazooa/Metaflora game - guess the species!"""

import argparse
import json
import random
from typing import Dict, List, Tuple

from helpers import (
    ensure_tree_file,
    get_all_leaves,
    json_tree_to_graph,
    lca,
    lowercase_tree,
)


def build_parent_map(graph: Dict[str, List[str]]) -> Dict[str, str]:
    """Build a map of child -> parent for the tree"""
    parent = {}
    for p, children in graph.items():
        for c in children:
            parent[c] = p
    return parent


def evaluate_guess(
    target: str, guess: str, graph: Dict[str, List[str]], parent_map: Dict[str, str]
) -> Tuple[bool, str]:
    """
    Evaluate a guess against the target species.

    Args:
        target: The correct species (scientific name)
        guess: The guessed species (scientific name)
        graph: The taxonomy graph
        parent_map: Mapping of child -> parent nodes

    Returns:
        (is_correct, clade_hint): Tuple of whether guess is correct and a helpful clade hint
    """
    if guess == target:
        return True, ""

    hint_clade = lca(graph, target, guess)
    return False, hint_clade


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Play Metazooa/Metaflora - Guess the species!"
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
        help="Game to play (metazooa or metaflora, default: metazooa)",
    )

    args = parser.parse_args()
    ensure_tree_file(args.tree_file, args.game.lower())

    # Load JSON tree
    try:
        with open(args.tree_file, "r") as f:
            json_tree = json.load(f)
    except FileNotFoundError:
        print(f"Error: {args.tree_file} not found")
        exit(1)

    # Make the json_tree case insensitive
    json_tree = lowercase_tree(json_tree)

    # Convert JSON tree to graph and build name map
    graph: Dict[str, List[str]] = {}
    name_map: Dict[str, str] = {}
    json_tree_to_graph(json_tree, graph, name_map)

    # Get all species (leaves)
    species = get_all_leaves(graph)

    if not species:
        print("Error: No species found in the tree!")
        exit(1)

    # Build parent map for hints
    parent_map = build_parent_map(graph)

    # Pick a random species
    target = random.choice(species)
    target_name = name_map.get(target, target)

    # Game intro
    game_display = "Metazooa" if args.game == "metazooa" else "Metaflora"
    print(f"\n🎮 Welcome to {game_display}!")
    print("=" * 50)
    print(f"I'm thinking of a {args.game.rstrip('a')}...")
    print("Can you guess what it is?")
    print("(Type 'hint' for a hint, 'quit' to exit)\n")

    guesses = 0
    max_guesses = 20

    while guesses < max_guesses:
        try:
            guess_input = input("Your guess: ").strip().lower()
        except EOFError:
            print("\nGame ended.")
            exit(0)

        if not guess_input:
            continue

        if guess_input == "quit":
            print(f"\nYou gave up! The answer was: {target_name} ({target})")
            exit(0)

        # Convert input to scientific name if needed
        scientific_guess = None
        if guess_input in graph:
            scientific_guess = guess_input
        else:
            # Try to find by common name
            for sci, common in name_map.items():
                if common == guess_input:
                    scientific_guess = sci
                    break

        if scientific_guess is None:
            print("I don't know that species. Try again!\n")
            continue

        guesses += 1

        # Evaluate the guess
        is_correct, hint = evaluate_guess(target, scientific_guess, graph, parent_map)

        if is_correct:
            print(f"\n🎉 Correct! It was {target_name}!")
            print(f"You got it in {guesses} {'guess' if guesses == 1 else 'guesses'}!")
            exit(0)

        print(f"❌ Wrong! Think about {hint}\n")

    print(f"\n😔 Game over! You didn't guess it in {max_guesses} tries.")
    print(f"The answer was: {target_name} ({target})")
