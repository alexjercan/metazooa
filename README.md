# Metazooa

This is an attempt to create a solver for the metazooa game.

### Quickstart

1. Species
Create a list of all the species in the game using

```console
uv run --active python metazooa.py --species
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

TODO: maybe we can automate this step in the future.

