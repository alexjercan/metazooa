#!/bin/bash
# Script to get all the species names Metazooa uses.
# Change filenames/locations/numbers as needed.

# This hits the Metazooa practice game page as a new user 2000 times and writes the answer to a file. I figured this was more than enough to get all 255 species.
for i in {1..100}
do
    uv run --active python species.py >> metazooa-species.txt
	echo -ne "  Species grabbed: $i\r"
done

# This sorts the file, strips out duplicates, and puts the results in a new file.
sort -u metazooa-species.txt > metazooa-species-sorted.txt
echo "  Unique species: $(wc -l metazooa-species-sorted.txt)"

# Now you can upload the file to the NCBI Taxonomy page <https://www.ncbi.nlm.nih.gov/Taxonomy/CommonTree/wwwcmt.cgi> to generate a phylogenetic tree.
