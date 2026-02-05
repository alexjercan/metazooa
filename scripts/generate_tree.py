#!/usr/bin/env python3
"""Generate a phylogenetic tree from a list of species using ete4 and NCBI taxonomy."""

import argparse
import json
import sys

from ete4 import NCBITaxa


def species_to_ncbi_ids(species_list, ncbi):
    """Convert species scientific names to NCBI taxonomy IDs."""
    taxids = []
    failed = []

    for species in species_list:
        species = species.strip()
        if not species:
            continue

        try:
            matches = ncbi.get_name_translator([species])
            if species in matches:
                taxids.extend(matches[species])
            else:
                failed.append(species)
        except Exception as e:
            print(f"Warning: Could not find '{species}': {e}", file=sys.stderr)
            failed.append(species)

    if failed:
        print(
            f"Warning: Could not find {len(failed)} species: {', '.join(failed[:5])}",
            file=sys.stderr,
        )

    return taxids


def build_tree_json(tree_node, ncbi, name_map):
    """Recursively build tree as nested JSON structure from ETE tree node."""
    name = ncbi.get_taxid_translator([tree_node.taxid])[tree_node.taxid]
    common_name = name_map.get(name, name)

    # Get taxid from the node
    taxid = 0
    if hasattr(tree_node, "taxid"):
        taxid = int(tree_node.taxid)

    node = {"scientific": name, "name": common_name, "taxid": taxid}

    # Recursively process children
    if hasattr(tree_node, "children") and tree_node.children:
        node["children"] = [build_tree_json(child, ncbi, name_map) for child in tree_node.children]

    return node


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate phylogenetic tree from species list")
    parser.add_argument(
        "--names-file",
        default="name_map.json",
        help="Input species name mapping file (default: name_map.json)",
    )
    parser.add_argument(
        "--output",
        default="commontree.json",
        help="Output tree file (default: commontree.json)",
    )

    args = parser.parse_args()

    print(
        "Initializing NCBI taxonomy database (this may take a moment on first run)...",
        file=sys.stderr,
    )
    ncbi = NCBITaxa()

    print("Reading species list...", file=sys.stderr)

    # Read species from name_map.json
    try:
        with open(args.names_file, "r") as f:
            name_map = json.load(f)
        species_list = list(name_map.keys())  # Use scientific names
    except FileNotFoundError:
        print(
            f"Error: {args.names_file} not found. Run fetch_species.py first.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Found {len(species_list)} species", file=sys.stderr)

    print("Converting species names to NCBI taxonomy IDs...", file=sys.stderr)
    taxids = species_to_ncbi_ids(species_list, ncbi)

    if not taxids:
        print("Error: Could not find any species in NCBI taxonomy", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully matched {len(taxids)} species", file=sys.stderr)

    print("Building taxonomy tree...", file=sys.stderr)

    tree = ncbi.get_topology(taxids)

    print(f"Tree root: {tree.name}", file=sys.stderr)

    tree_json = build_tree_json(tree, ncbi, name_map)

    with open(args.output, "w") as f:
        json.dump(tree_json, f, indent=2)

    print(f"✓ Saved taxonomy tree to {args.output}", file=sys.stderr)
