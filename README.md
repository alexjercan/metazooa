# Metazooa

This is an attempt to create a solver for the metazooa game.

### Quickstart

1. Species
Create a list of all the species in the game using

```console
uv run --active python species.py
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

3. Visualization

You can generate an svg graph of the tree using the `taxonomy.py` script:

```console
uv run --active python taxonomy.py
```

3. Solve the puzzle

You can use the `metazooa.py` script to solve the puzzle:

```console
uv run --active python metazooa.py --clade Metazoa
```

This will give you the best possible guess for the puzzle. Then you can attempt
that guess and repeat the process until you find the correct answer.

```console
uv run --active python metazooa.py --clade [CLADE] --without '[ANIMAL1], [ANIMAL2], ...'
```

