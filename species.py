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
