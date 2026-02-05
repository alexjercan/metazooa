import argparse
import json
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape species data from metazooa.com")
    parser.add_argument(
        "--requests",
        type=int,
        default=100,
        help="Number of requests to make (default: 100)",
    )
    parser.add_argument(
        "--species-file",
        default="metazooa-species-sorted.txt",
        help="Output file for sorted species list (default: metazooa-species-sorted.txt)",
    )
    parser.add_argument(
        "--mapping-file",
        default="name_map.json",
        help="Output file for name mapping (default: name_map.json)",
    )

    args = parser.parse_args()

    name_map = {}

    for _ in track(range(args.requests), description="Getting species..."):
        species, names = get_species()
        for s, name in zip(species, names):
            name_map[s] = name

    with open(args.species_file, "w") as f:
        for s in sorted(name_map.keys()):
            f.write(s + "\n")

    with open(args.mapping_file, "w") as f:
        json.dump(name_map, f)

    print(f"Wrote {len(name_map)} species to {args.species_file} and {args.mapping_file}")
