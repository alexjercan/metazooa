# Metazooa

This is an attempt to create a solver for the metazooa game.

### Quickstart

1. Species
Create a list of all the species in the game using

```console
uv run --active python scripts/get_species.py
```

This will create a file `metazooa-species-sorted.txt` that contains a list of
all the animals with the scientific names.

2. Phylogenetic Tree
Now you can upload the file to the NCBI Taxonomy page
<https://www.ncbi.nlm.nih.gov/Taxonomy/CommonTree/wwwcmt.cgi> to generate a
phylogenetic tree.

- Select "Browse..." and upload the file `metazooa-species-sorted.txt`.
- Select "Choose" and you will get a tree.
- Select "Save as" and save the tree in text tree format.

Or you can do it automatically using the `generate_tree.py` script:

```console
uv run --active python scripts/generate_tree.py
```

3. Visualization

You can generate an svg graph of the tree using the `taxonomy.py` script:

```console
uv run --active python scripts/view_taxonomy.py
```

4. Solve the puzzle

You can use the `metazooa.py` script to solve the puzzle:

```console
uv run --active python metazooa.py --clade Metazoa
```

This will give you the best possible guess for the puzzle. Then you can attempt
that guess and repeat the process until you find the correct answer.

```console
uv run --active python metazooa.py --clade [CLADE] --without '[ANIMAL1],[ANIMAL2],...'
```

5. (Optional) Web Page

```console
python3 -m http.server
```

Then you can open `http://localhost:8000` in your browser and use the web page
to solve the puzzle.

### Example

The heuristic is to guess the animal that has the least number of candidates in
the worst case scenario. For example, if we have the following tree:

Mammals
├── Dogs: Husky, Corgi, Bulldog
├── Cats: Lion, Tiger, House Cat
└── Primates: Chimp, Gorilla

If I guess "Husky" (Same for Corgi, Bulldog, and basically same for the cats)
- Husky vs other Dogs (Corgi, Bulldog) -> LCA is "Dogs" (2 candidates)
- Husky vs Cats (Lion, Tiger, House Cat) -> LCA is "Mammals" (3 candidates)
- Husky vs Primates (Chimp, Gorilla) -> LCA is "Mammals" (2 candidates)
- Worst case: 5 animals (the 3 cats + 2 primates in the "Mammals" bucket)

If I guess "Chimp" (or Gorilla) (a primate):
- Chimp vs other Primates (Gorilla) -> LCA is "Primates" (1 candidate)
- Chimp vs Dogs (Husky, Corgi, Bulldog) -> LCA is "Mammals" (3 candidates)
- Chimp vs Cats (Lion, Tiger, House Cat) -> LCA is "Mammals" (3 candidates)
- Worst case: 6 animals (the 3 dogs + 3 cats in the "Mammals" bucket)

Then the best guess is to guess either one of the dogs or the cats, which will
give us a worst case of 5 candidates, instead of guessing a primate which will
give us a worst case of 6 candidates.


