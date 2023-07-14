#!/bin/bash

# Annotate tree with NCBI taxonomic annotation
treeprofiler annotate \
--tree spongilla_example.nw \
--input_type newick \
--metadata spongilla_example.tsv \
--taxonomic_profile \
--taxadb NCBI \
--taxon_column name \
--taxon_delimiter . \
--taxa_field 0  \
--outdir ./

# Visualize tree with colored taxonclade
treeprofiler plot \
--tree spongilla_example_annotated.nw \
--input_type newick \
--taxonclade_layout