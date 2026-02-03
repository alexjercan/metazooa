import json

import requests
from bs4 import BeautifulSoup


def get_species():
    url = "https://metazooa.com/play/practice"
    response = requests.get(url)
    response.raise_for_status()

    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    script = soup.find("script", type="application/json")
    if script and script.string:
        data = json.loads(script.string)
        species_list = data["v"][0][0]["speciesList"]
        names = []
        for species in species_list:
            names.append(species["scientific"])

        return names

    return []


if __name__ == "__main__":
    species = get_species()
    for s in species:
        print(s)
