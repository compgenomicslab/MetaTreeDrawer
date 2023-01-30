# MetaTreeProfiler Tutorial
## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Mapping metadata into tree](#mapping-metadata-into-tree) 
    1. [Simple mapping metadata into leaf nodes](#simple-mapping-metadata-into-leaf-nodes)
    2. [Mapping Categorical data](#mapping-categorical-data)
    3. [Mapping Boolean data](#mapping-boolean-data)
    4. [Mapping Numerical data](#mapping-numerical-data)
    5. [Mapping metadata without column names](#mapping-metadata-without-column-names)
    6. [Taxonomic profiling](#taxonomic-profiling)
        1. [Basic usage on GTDB](#basic-usage-on-GTDB)
        2. [Basic usage on NCBI](#basic-usage-on-NCBI)
4. [Visualizing annotated tree with layouts](#visualizing-annotated-tree-with-layouts)
    1. [Layouts for categorical data](#layouts-for-categorical-data)
    2. [Layouts for boolean data](#layouts-for-boolean-data)
    3. [Layouts for numerical data](#layouts-for-numerical-data)
    4. [Visualizing annotated internal nodes](#visualizing-annotated-internal-nodes)
    5. [Layouts for Taxonomic data](#layouts-for-taxonomic-data)
5. [Conditional query in annotated tree](#conditional-query-in-annotated-tree)
    1. [Basic Query](#basic-query)
    2. [Query in internal nodes](#query-in-internal-nodes)
    3. [AND and OR conditions](#and-and-or-conditions)
    4. [conditional pruning based on taxonomic level](#conditional-pruning-based-on-taxonomic-level)

## Introduction
MetaTreeProfiler is command-line tool for profiling metadata table into phylogenetic tree with descriptive analysis and output visualization

## Installation
MetaTreeProfiler requires to install ete4 toolkit
```
# install ete4 dependencies Cython
conda install -c anaconda cython
pip install Flask
pip install Flask-RESTful Flask-HTTPAuth Flask-Compress Flask-Cors
conda install six numpy scipy

# install ete4
git clone https://github.com/etetoolkit/ete.git
cd ete/
git branch checkout ete4
pip install -e .
```

Install MetaTreeProfiler
```
# install selenium via pip 
pip install selenium
# or conda
conda install -c conda-forge selenium 

# install MetaTreeProfiler
git clone https://github.com/dengzq1234/MetaTreeDrawer
cd MetaTreeDrawer/
# add treeprofiler to path
export PATH=$PATH:$(pwd)
```

### Input files
MetaTreeProfiler takes following file types as input 

| Input    |      Filetype  | 
|----------|-------------   |
| Tree     |      Newick    | 
| Metadata |      TSV       |

### Basic usage
MetaTreeProfiler has two main subcommand:
 - annotate
 - plot

The first one `annotate` is used to annotate your input tree and corresponding metadata, MetaTreeProfiler will map all the metadata into corresponding tree node. In this step, annotated tree will be generated in newick and ete format

```
treeprofiler.py annotate --tree tree.nw --metadata metadata.tsv --outdir ./
```

The second subcommand `plot` is used to visualize tree with associated metadata. By default, treeprofiler will launch an interactive session at localhost for user to explore input tree.

```
treeprofiler.py plot --tree tree_annotated.nw --tree_type newick 
```
or

```
treeprofiler.py plot --tree tree_annotated.ete --tree_type ete 
```


# Using MetaTreeProfiler
In this Tutorial we will use MetaTreeProfiler and demostrate basic usage with data in examples/


```
cd examples/
ls 
basic_example1.nw   basic_example1.tsv
gtdb_example1.nw    gtdb_example1.tsv        
progenome3.nw   progenome3.tsv 
spongilla_example.nw  spongilla_example.tsv
progenome3_annotated.nw  spongilla_annotated.nw 
```

## `annotate`, Mapping metadata into tree 
### **Simple mapping metadata into leaf nodes** 
treeprofiler will start local server which metadata will be mapped to corresponding leaf nodes
```
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --outdir ./examples/
```

Annotated tree will be generated in newick and ete format, alongside with a config file where describes datatype of each properties

### Mapping metadata into tree and profile tree internal nodes annotations and analysis
At the above example, we only mapped metadata to leaf nodes, in this example, we will also profile **internal nodes** annotation and analysis of their children nodes.

### Mapping Categorical data
For categorical dataset, each internal node will count the selected feature of its children nodes as counter, as shown as ```<feature_name>_counter``` in internal node. To label categorical feature metadata, using following arguments

```
# label categorical data by column name(s) in metadata (for multiple columns, seperate by ","), using --text_prop <header>
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --text_prop random_type --outdir ./examples/

# label categorical data by column index, using --text_prop_idx <idx>
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --text_prop_idx 6 --outdir ./examples/

# label column index by range, "[star_idx-end_idx]"
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --text_prop_idx [1-6] --outdir ./examples/
```

Categorical data will be process as counter in each internal node. Users can choose either counter is raw or relative count by using `--counter_stat`
| internal_node properties  |      statistic method  | 
|----------|-------------   |
| `<feature name>`_counter  |      raw, relative    | 

```
# raw count, example internal_node shown as: ```random_type_counter: medium--3||high--2```
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --text_prop random_type --counter_stat raw --outdir ./examples/

# relative count, example internal_node shown as: ```random_type_counter: medium--0.60||high--0.40```
 internal_node example shown as, random_type_counter: medium--3||high--2
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --text_prop random_type --counter_stat relative --outdir ./examples/
```


### Mapping Boolean data
For Boolean dataset, each internal node will count the selected feature(s) of its children nodes as counter as categorical, as shown as `_counter` of suffix feature name(s) of internal node. To label Boolean feature metadata, using following arguments


```
# label boolean data by column name(s) in metadata (for multiple columns, seperate by ","), using --bool_prop <header>
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --bool_prop bool_type,bool_type2 --outdir ./examples/

# label boolean data by column index, using --bool_prop_idx <idx>
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --bool_prop_idx 7,8 --outdir ./examples/

# label column index by range, "[star_idx-end_idx]"
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --bool_prop_idx [7-8] --outdir ./examples/
```

Boolean counter stats follows rule as categorical data
 

### Mapping Numerical data
For numerical dataset, each internal node will perform folwing descriptive statistic analysis of all of its children node of selected feature(s)

| internal_node properties  |      statistic method  | 
|----------|-------------   |
| `<feature name>`_avg      |      average    | 
| `<feature name>`_sum      |      sum    | 
| `<feature name>`_max      |      maximum    | 
| `<feature name>`_min      |      minimum    | 
| `<feature name>`_std      |      standard deviation    | 

To label numerical data
```
# label numerical data by column name(s) in metadata (for multiple columns, seperate by ","), using --num_prop <header>
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --num_prop sample1,sample2,sample3,sample4,sample5 --outdir ./examples/

# label numerical data by column index, using --num_prop_idx <idx>
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --num_prop_idx 1,2,3,4,5 --outdir ./examples/ 

# label column index by range, "[star_idx-end_idx]"
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --num_prop_idx [1-5]  --outdir ./examples/
```

By default, numerical feature will be calculated all the descriptive statistic, but users can choose specific one to be calculated by using `--num_stat [all, sum, avg, max, min, std] `

--num_stat NUM_STAT   statistic calculation to perform for numerical data in internal nodes, [all, sum, avg, max, min, std] 
```
# by default
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --num_prop sample1 --num_stat all --outdir ./examples/ 

# only average calculation
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --num_prop sample1 --num_stat avg --outdir ./examples/ 
```
### Mapping metadata without column names
if metadata doesn't contain column names, please add `--no_colnames` as flag. MetaTreeProfiler will automatically assign feature name by index order

### Taxonomic profiling
If input metadada containcs taxon data, MetaTreeProfiler allows users to process taxonomic annotation with either GTDB or NCBI database.

- `--taxadb`, `NCBI` or `GTDB`, choose the Taxonomic Database for annotation
- `--taxon_column`, choose the column in metadata which representa taxon
- `--taxonomic_profile`, activate taxonomic annotation
- `--taxon_delimiter`, delimiter of taxa columns. default `.`
- `--taxa_field`, field of taxa name after delimiter. default `0`

#### Basic usage on GTDB 
Here we demonstrate with `examples/gtdb_example1.nw` and `examples/gtdb_example1.tsv`
```
# in case of gtdb_example1.tsv
python treeprofiler.py annotate --tree examples/gtdb_example1.nw --metadata examples/gtdb_example1.tsv --taxonomic_profile --taxon_column 0 --taxadb GTDB --outdir ./examples/
```

#### Basic usage on NCBI
For instance of `examples/spongilla_example.nw` and `examples/spongilla_example.tsv`, it contains accession ID such as `83887.comp22273_c0_seq2_m.43352`, hence using `--` 
```
python treeprofiler.py annotate --tree examples/spongilla_example.nw --metadata examples/spongilla_example.tsv --taxonomic_profile --taxon_column name --taxon_delimiter .  --taxa_field 0 --taxadb NCBI 
--outdir ./examples/
```

## `plot`, visualizing annotated tree with layouts
MetaTreeProfiler provides a several of layout options for visualize features in metadata along with tree, depends on their datatype

### Layouts for categorical data
Users can add the following flag to activate layouts for categorical data
```
--ColorbranchLayout COLORBRANCHLAYOUT
                            <col1,col2> names, column index or index range of columns which need to be plot as Textlayouts
--LabelLayout LABELLAYOUT
                        <col1,col2> names, column index or index range of columns which need to be plot as LabelLayout
--RectangularLayout RECTANGULARLAYOUT
                        <col1,col2> names, column index or index range of columns which need to be plot as RectangularLayout
```

example
```
## annotate tree first
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --text_prop random_type --outdir ./examples/

## target column "random_type" in examples/basic_example1.tsv
# List random_type feature as text in aligned panel using LabelLayout
python treeprofiler.py plot --tree examples/basic_example1_annotated.nw --LabelLayout random_type 

# Label random_type feature on branch with different colors in aligned panel  using --ColorbranchLayout
ppython treeprofiler.py plot --tree examples/basic_example1_annotated.nw  --ColorbranchLayout random_type 

# Label random_type feature with retangular block in aligned panel using --RectangularLayout
python treeprofiler.py plot --tree examples/basic_example1_annotated.nw  --RectangularLayout random_type 
```
### Layouts for boolean data
Users can add the following flag to activate layouts for Boolean data
```
--BinaryLayout BINARYLAYOUT
                        <col1,col2> names, column index or index range of columns which need to be plot as BinaryLayout, label shown only positive value
--RevBinaryLayout REVBINARYLAYOUT
                        <col1,col2> names, column index or index range of columns which need to be plot as RevBinaryLayout, label shown only negative value
```

```
## annotate tree first
# multiple columns seperated by ','
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --bool_prop bool_type,bool_type2 --outdir ./examples/

## target column "bool_type", "bool_type2" in examples/basic_example1.tsv
# List postive bool_type feature in aligned panel using BinaryLayout
python treeprofiler.py plot --tree examples/basic_example1_annotated.nw  --BinaryLayout bool_type

# List negative bool_type feature in aligned panel using BinaryLayout
python treeprofiler.py plot --tree examples/basic_example1_annotated.nw  --RevBinaryLayout bool_type2

# multiple columns seperated by ','
python treeprofiler.py plot --tree examples/basic_example1_annotated.nw  --BinaryLayout bool_type,bool_type2  
```

### Layouts for Numerical data
Users can add the following flag to activate layouts for Numerical data
```
--HeatmapLayout HEATMAPLAYOUT
                        <col1,col2> names, column index or index range of columns which need to be read as HeatmapLayout
--BarplotLayout BARPLOTLAYOUT
                        <col1,col2> names, column index or index range of columns which need to be read as BarplotLayouts
```
```
## annotate tree first
# multiple columns seperated by ','
python treeprofiler.py annotate --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --num_prop_idx [1-5] --outdir ./examples/

## target column 'sample[1-5]' feature in examples/basic_example1.tsv
# visualize sample1 feature in Barplot
python treeprofiler.py plot --tree examples/basic_example1_annotated.nw  --BarplotLayout sample1,sample2,sample3,sample4,sample5

# visualize sample1-sample5 in Heatmap
#python treeprofiler.py plot --tree examples/basic_example1.nw --metadata #examples/basic_example1.tsv --HeatmapLayout [1-5]  
```

### Visualizing annotated internal nodes
If internal nodes are annotated, MetaTreeProfiler is also able to visualize annotated features automatically when layouts are activated

#### Internal nodes of categorical and boolean data
As internal nodes of categorical and boolean data are annotated as counter, hence when activating layouts of categorical or boolean data, it generate pipechart of counter summary at the top of each internal node

#### Internal nodes of numerical data
Internal nodes of numerical data are process descriptive statistic analysis by default, hence when users collapse any branch, BarplotLayout or HeatmapLayout will demonstrate representative value, `avg` by default. representative value can be changed by using `--internal_plot_measure`

example
```
# select max instead of avg as internal node ploting representative
python treeprofiler.py plot --tree examples/basic_example1_annotated.nw  --HeatmapLayout sample1,sample2,sample3,sample4,sample5 --internal_plot_measure max 
```

### Layouts for Taxonomic data
Activate Taxonomic layout using `--TaxonLayout`


## Conditional query in annotated tree
MetaTreeProfiler allows users to perform conditional processs based on differet circumstances

- `--collapsed_by`, collapse tree branches whose nodes if the conditions, mainly on internal nodes
- `--highlighted_by`, select tree nodes which fit the conditions
- `--pruned_by`, prune the annotated tree by conditions, and remove the branches or clades which don't fit the condition.
- `--rank_limit`, prune the taxonomic annotated tree based on rank of classification.

### Query Syntax
#### Basic Query
All the conditional query shared the same syntax, a standard query consists the following 

```
--pruned_by|collapsed_by|highlighted_by "<left_value> <operator> <right_value>"
```
* left value, the property of leaf node or internal node
* operators
    *  `=`
    * `!=`
    * `>` 
    * `>=`
    * `<`
    * `<=`
    * `contains`
* right value, custom value for the condition

Example 
```
# select tree node whose name contains `FALPE` character
...--highlighted_by "name contains FALPE"

# select tree node whose sample1 feature > 0.50
...--highlighted_by "sample1 > 0.50"
```

#### Query in internal nodes
Query in internal nodes' properties is also available, in this case, `left_value` of query will be the internal node property, remember to add the proper suffixes such as `_avg`, `_max`,etc, for the numerical data or `_counter` for categorical and boolean data. 

Example
```
# select tree internal node where sample1_avg feature > 0.50
python treeprofiler.py --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --num_prop_idx [1-5] --HeatmapLayout [1-5] --collapsed_by "sample1_avg < 0.50" 
```

Syntax for internal node counter data
```
# collapse tree internal nodes, where `low` relative counter < 0.30 in random_type_counter property
python treeprofiler.py --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --text_prop random_type --counter_stat relative  --collapsed_by "random_type_counter:low < 0.30" 
```

#### AND and OR conditions
The syntax for the AND condition and OR condition in MetaTreeProfiler is:

AND condition will be under one argument, syntax seperated by `,`, such as 
```
# select tree  node where sample1 feature > 0.50 AND sample2 < 0.2
python treeprofiler.py --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --num_prop_idx [1-5] --HeatmapLayout [1-5]--highlighted_by "sample1>0.50,sample2<0.2" 
```

OR condition will be used more than one arguments
```
# select tree node where sample1 feature > 0.50 OR sample2 < 0.2
python treeprofiler.py --tree examples/basic_example1.nw --metadata examples/basic_example1.tsv --num_prop_idx [1-5] --HeatmapLayout [1-5] --highlighted_by "sample1>0.50" --highlighted_by "sample2<0.2" 
```

### conditional limit based on taxonomic level
Prune taxonomic annotated tree based on following taxonomic rank level,
`kingdom`, `phylum`, `class`, `order`, `family`, `genus`, `species`, `subspecies` 
```
# prune tree by family
python treeprofiler.py --tree examples/gtdb_example1.nw --metadata examples/gtdb_example1.tsv --taxonomic_profile --rank_limit family --TaxonLayout  
```

## Explore progenome data
We store progenome v3 data in examples/ directory for exploration,

A glance of metadata
```
head -2 examples/progenome3.tsv
name    GC      GCA     aquatic_habitat host_associated size    soil_habitat    GCF
2486577.SAMN10347832.GCA_004210275.1    40.8    GCA_004210275.1 0       1       1375759 0       RS_GCF_004210275.1
2759495.SAMN15595193.GCA_014116815.1    34.3    GCA_014116815.1                 1928597         GB_GCA_014116815.1
```

Here we will conduct the profiling with one command line
```
python treeprofiler.py --tree examples/progenome3.nw --metadata examples/progenome3.tsv --taxonomic_profile --taxadb NCBI --taxon_delimiter . --taxa_field 0 --num_prop GC,size --bool_prop aquatic_habitat,host_associated,soil_habitat --BarplotLayout GC,size --TaxonLayout --BinaryLayout aquatic_habitat,host_associated,soil_habitat  
```