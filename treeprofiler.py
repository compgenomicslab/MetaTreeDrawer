#!/usr/bin/env python


from ete4.parser.newick import NewickError
from ete4 import Tree, PhyloTree
from ete4 import GTDBTaxa
from ete4 import NCBITaxa
from ete4.smartview import TreeStyle, NodeStyle, TreeLayout
from layouts import text_layouts, taxon_layouts, staple_layouts, heatmap_layouts, conditional_layouts

from argparse import ArgumentParser
import argparse
from collections import defaultdict
from collections import Counter
from scipy import stats
import colorsys
import random
import b64pickle
import itertools
import math
import numpy as np
import csv
import sys


__author__ = 'Ziqi DENG'
__license__ = "GPL v2"
__email__ = 'dengziqi1234@gmail.com'
__version__ = '0.0.1'
__date__ = '01-11-2022'
__description__ = ('A program for profiling metadata on target '
                    'tree and conduct summary analysis')


#colours_50 = ["#E41A1C","#C72A35","#AB3A4E","#8F4A68","#735B81","#566B9B","#3A7BB4","#3A85A8","#3D8D96","#419584","#449D72","#48A460","#4CAD4E","#56A354","#629363","#6E8371","#7A7380","#87638F","#93539D","#A25392","#B35A77","#C4625D","#D46A42","#E57227","#F67A0D","#FF8904","#FF9E0C","#FFB314","#FFC81D","#FFDD25","#FFF12D","#F9F432","#EBD930","#DCBD2E","#CDA12C","#BF862B","#B06A29","#A9572E","#B65E46","#C3655F","#D06C78","#DE7390","#EB7AA9","#F581BE","#E585B8","#D689B1","#C78DAB","#B791A5","#A8959F","#999999"]
paried_color = ["red", "darkblue", "lightgreen", "darkyellow", "violet", "mediumturquoise", "sienna", "lightCoral", "lightSkyBlue", "indigo", "tan", "coral", "olivedrab", "teal"]

def read_args():
    """
    Parse the input parameters
    Return the parsed arguments.
    """
    parser = ArgumentParser(description=
        "treeprofiler.py (ver. "+__version__+
        " of "+__date__+")." + __description__+ " Authors: "+
        __author__+" ("+__email__+")",
        formatter_class=argparse.RawTextHelpFormatter)

    # input parameters group
    group = parser.add_argument_group(title='input parameters',
        description="Input parameters")
    group.add_argument('-t', '--tree',
        type=str,
        required=False,
        help="Input tree, .nw file, customized tree input")
    group.add_argument('-d', '--metadata',
        type=str,
        required=False,
        help="<metadata.csv> .csv, .tsv. mandatory input")
    group.add_argument('--annotated_tree',
        default=False,
        action='store_true',
        required=False,
        help="inputtree already annotated by treeprofileer")
    group.add_argument('--no_colnames',
        default=False,
        action='store_true',
        required=False,
        help="metadata table doesn't contain columns name")
    group.add_argument('--text_column',
        type=str,
        required=False,
        help="<col1,col2> names, column index or index range of columns which need to be read as categorical data")
    group.add_argument('--num_column',
        type=str,
        required=False,
        help="<col1,col2> names, column index or index range of columns which need to be read as numerical data")
    group.add_argument('--bool_column',
        type=str,
        required=False,
        help="<col1,col2> names, column index or index range of columns which need to be read as boolean data")
    group.add_argument('--text_column_idx',
        type=str,
        required=False,
        help="1,2,3 or [1-5] index of columns which need to be read as categorical data")
    group.add_argument('--num_column_idx',
        type=str,
        required=False,
        help="1,2,3 or [1-5] index columns which need to be read as numerical data")
    group.add_argument('--bool_column_idx',
        type=str,
        required=False,
        help="1,2,3 or [1-5] index columns which need to be read as boolean data")
    group.add_argument('--taxatree',
        type=str,
        required=False,
        help="<kingdom|phylum|class|order|family|genus|species|subspecies> reference tree from taxonomic database")
    group.add_argument('--taxadb',
        type=str,
        default='GTDB',
        required=False,
        help="<NCBI|GTDB> for taxonomic profiling or fetch taxatree default [GTDB]")    
    group.add_argument('--taxon_column',
        type=str,
        required=False,
        help="<col1> name of columns which need to be read as taxon data")
    group.add_argument('--taxon_delimiter',
        type=str,
        default=';',
        required=False,
        help="delimiter of taxa columns. default [;]")
    group.add_argument('--taxonomic_profile',
        default=False,
        action='store_true',
        required=False,
        help="Determine if you need taxonomic profile on tree")

    group = parser.add_argument_group(title='Analysis arguments',
        description="Analysis parameters")
    group.add_argument('--num_stat',
        default='all',
        type=str,
        required=False,
        help="statistic calculation to perform for numerical data in internal nodes, [all, sum, avg, max, min, std] ")  
    group.add_argument('--internal_plot_measure',
        default='avg',
        type=str,
        required=False,
        help="statistic measures to be shown in numerical layout for internal nodes, [default: avg]")  

    group.add_argument('--counter_stat',
        default='raw',
        type=str,
        required=False,
        help="statistic calculation to perform for categorical data in internal nodes, raw count or in percentage [raw, relative] ")  
    
    group.add_argument('--rank_limit',
        type=str,
        required=False,
        help="TAXONOMIC_LEVEL prune annotate tree by rank limit")
    group.add_argument('--pruned_by', 
        type=str,
        required=False,
        action='append',
        help='target tree pruned by customized conditions')
    group.add_argument('--collapsed_by', 
        type=str,
        required=False,
        action='append',
        help='target tree collapsed by customized conditions')
    group.add_argument('--highlighted_by', 
        type=str,
        required=False,
        action='append',
        help='target tree highlighted by customized conditions')
    
    group = parser.add_argument_group(title='basic treelayout arguments',
        description="treelayout parameters")
    group.add_argument('--drawer',
        type=str,
        required=False,
        help="Circular or Rectangular")
    group.add_argument('--collapse_level',
        type=str,
        required=False,
        help="default collapse level, default is 10") 
    group.add_argument('--ultrametric',
        default=False,
        action='store_true',
        required=False,
        help="ultrametric tree")

    group = parser.add_argument_group(title='Plot arguments',
        description="Plot parameters")
    group.add_argument('--BinaryLayout',
        type=str,
        required=False,
        help="<col1,col2> names, column index or index range of columns which need to be plot as BinaryLayout")
    group.add_argument('--RevBinaryLayout',
        type=str,
        required=False,
        help="<col1,col2> names, column index or index range of columns which need to be plot as RevBinaryLayout")

    group.add_argument('--ColorbranchLayout',
        type=str,
        required=False,
        help="<col1,col2> names, column index or index range of columns which need to be plot as Textlayouts")
    group.add_argument('--LabelLayout',
        type=str,
        required=False,
        help="<col1,col2> names, column index or index range of columns which need to be plot as LabelLayout")
    group.add_argument('--RectangularLayout',
        type=str,
        required=False,
        help="<col1,col2> names, column index or index range of columns which need to be plot as RectangularLayout")
    
    
    group.add_argument('--HeatmapLayout',
        type=str,
        required=False,
        help="<col1,col2> names, column index or index range of columns which need to be read as HeatmapLayout")
    group.add_argument('--BarplotLayout',
        type=str,
        required=False,
        help="<col1,col2> names, column index or index range of columns which need to be read as BarplotLayouts")
    
    
    group.add_argument('--TaxonLayout',
        type=str,
        required=False,
        help="<col1,col2> names, column index or index range of columns which need to be read as TaxonLayouts")

    group = parser.add_argument_group(title='Output arguments',
        description="Output parameters")
    group.add_argument('--interactive',
        default=False,
        action='store_true',
        help="run interactive session")
    group.add_argument('--port',
        type=str,
        default=5000,
        help="run interactive session on custom port")
    group.add_argument('--plot',
        type=str,
        required=False,
        help="output as pdf")
    group.add_argument('-o', '--outtree',
        type=str,
        required=False,
        help="output annotated tree")
    group.add_argument('--outtsv',
        type=str,
        required=False,
        help="output annotated tsv file")


    args = parser.parse_args()
    return args

def parse_csv(input_file, delimiter='\t', no_colnames=False):
    metadata = {}
    columns = defaultdict(list)
    with open(input_file, 'r') as f:
        if no_colnames:
            fields_len = len(next(f).split(delimiter))
            headers = ['col'+str(i) for i in range(fields_len)]
            reader = csv.DictReader(f, delimiter=delimiter, fieldnames=headers)
        else:
            reader = csv.DictReader(f, delimiter=delimiter)
            headers = reader.fieldnames
        node_header, node_props = headers[0], headers[1:]
        
        for row in reader:
            nodename = row[node_header]
            del row[node_header]
            metadata[nodename] = dict(row)
            for (k,v) in row.items(): # go over each column name and value 
                columns[k].append(v) # append the value into the appropriate list
                                    # based on column name k

    return metadata, node_props, columns

def parse_csv_to_column(metadata):
    columns = defaultdict(list) # each value in each column is appended to a list
    with open(metadata) as f:
        reader = csv.DictReader(f, delimiter="\t") # read rows into a dictionary format
        for row in reader: # read a row as {column1: value1, column2: value2,...}
            for (k,v) in row.items(): # go over each column name and value 
                columns[k].append(v) # append the value into the appropriate list
                                    # based on column name k
    return columns

def ete4_parse(newick):
    try:
        tree = Tree(newick)
    except NewickError:
        try:
            tree = Tree(newick, format=1)            
        except NewickError:
            tree = Tree(newick, format=1, quoted_node_names=True)

    # Correct 0-dist trees
    has_dist = False
    for n in tree.traverse(): 
        if n.dist > 0: 
            has_dist = True
            break
    if not has_dist: 
        for n in tree.iter_descendants(): 
            n.dist = 1

    return tree

def load_metadata_to_tree(tree, metadata_dict, taxon_column=None, taxon_delimiter=';'):
    name2leaf = {}
    for leaf in tree.iter_leaves():
        name2leaf[leaf.name] = leaf

    for node, props in metadata_dict.items():
        
        #hits = tree.get_leaves_by_name(node)
        #hits = tree.search_nodes(name=node) # including internal nodes
        if node in name2leaf.keys():
            target_node = name2leaf[node]
            for key,value in props.items():
                if key == taxon_column:
                    taxon_prop = value.split(taxon_delimiter)[-1]
                    target_node.add_prop(key, taxon_prop)
                else:
                    target_node.add_prop(key, value)
        else:
            pass
        
        # if hits:
            
        #     target_node = hits[0]
        #     for key,value in props.items():
        #         if key == taxon_column:
        #             taxon_prop = value.split(taxon_delimiter)[-1]
        #             target_node.add_prop(key, taxon_prop)
        #         else:
        #             target_node.add_prop(key, value)
        # elif len(hits)>1:
        #     print('repeat')
        #     break
        # else:
        #     pass
    return tree

# def merge_annotations(nodes, target_props, dtype='str'):
#     internal_props = {}

#     for target_prop in target_props:
#         if dtype == 'str':
#             prop_list = children_prop_array(nodes, target_prop)
#             internal_props[add_suffix(target_prop, 'counter')] = '||'.join([add_suffix(key, value, '--') for key, value in dict(Counter(prop_list)).items()])
            
#         elif dtype == 'num':
#             prop_array = np.array(children_prop_array(nodes, target_prop),dtype=np.float64)
#             n, (smin, smax), sm, sv, ss, sk = stats.describe(prop_array)

#             internal_props[add_suffix(target_prop, 'sum')] = np.sum(prop_array)
#             internal_props[add_suffix(target_prop, 'min')] = smin
#             internal_props[add_suffix(target_prop, 'max')] = smax
#             internal_props[add_suffix(target_prop, 'avg')] = sm
#             if math.isnan(sv) == False:
#                 internal_props[add_suffix(target_prop, 'std')] = sv
#             else:
#                 internal_props[add_suffix(target_prop, 'std')] = 0

#     return internal_props
def merge_text_annotations(nodes, target_props, counter_stat='raw'):
    internal_props = {}
    for target_prop in target_props:
        if counter_stat == 'raw':
            prop_list = children_prop_array(nodes, target_prop)
            internal_props[add_suffix(target_prop, 'counter')] = '||'.join([add_suffix(str(key), value, '--') for key, value in dict(Counter(prop_list)).items()])

        elif counter_stat == 'relative':
            prop_list = children_prop_array(nodes, target_prop)
            counter_line = []
            #print(dict(Counter(prop_list)))
            total = sum(dict(Counter(prop_list)).values())
            #print(total)
            for key, value in dict(Counter(prop_list)).items():
                #print(key, value)
                rel_val = '{0:.2f}'.format(float(value)/total)
                counter_line.append(add_suffix(key, rel_val, '--'))
            internal_props[add_suffix(target_prop, 'counter')] = '||'.join(counter_line)
            #internal_props[add_suffix(target_prop, 'counter')] = '||'.join([add_suffix(key, value, '--') for key, value in dict(Counter(prop_list)).items()])

        else:
            print('Invalid stat method')
            break
    
    return internal_props

# def merge_bool_annotations(nodes, target_props, counter_stat='raw'):
#     internal_props = {}
#     for target_prop in target_props:
#         if counter_stat == 'raw':
#             prop_list = children_prop_array(nodes, target_prop)
#             counter_line = []
#             for key, value in dict(Counter(prop_list)).items():
#                 counter_line.append(add_suffix(key, value, '--'))
            
#             internal_props[add_suffix(target_prop, 'counter')] = '||'.join(counter_line)
#             # internal_props[add_suffix(target_prop, 'counter')] = '||'.join([add_suffix(str(key), value, '--') for key, value in dict(Counter(prop_list)).items()])

#         # elif counter_stat == 'relative':
#         #     prop_list = children_prop_array(nodes, target_prop)
#         #     internal_props[add_suffix(target_prop, 'counter')] = '||'.join([add_suffix(key, value, '--') for key, value in dict(Counter(prop_list)).items()])

#         else:
#             print('Invalid stat method')
#             break
    
#     return internal_props

def merge_num_annotations(nodes, target_props, num_stat='all'):
    internal_props = {}
    for target_prop in target_props:
        prop_array = np.array(children_prop_array(nodes, target_prop),dtype=np.float64)
        n, (smin, smax), sm, sv, ss, sk = stats.describe(prop_array)

        if num_stat == 'all':
            internal_props[add_suffix(target_prop, 'avg')] = sm
            internal_props[add_suffix(target_prop, 'sum')] = np.sum(prop_array)
            internal_props[add_suffix(target_prop, 'max')] = smax
            internal_props[add_suffix(target_prop, 'min')] = smin
            if math.isnan(sv) == False:
                internal_props[add_suffix(target_prop, 'std')] = sv
            else:
                internal_props[add_suffix(target_prop, 'std')] = 0
        
        elif num_stat == 'avg':
            internal_props[add_suffix(target_prop, 'avg')] = sm
        elif num_stat == 'sum':
            internal_props[add_suffix(target_prop, 'sum')] = np.sum(prop_array)
        elif num_stat == 'max':
            internal_props[add_suffix(target_prop, 'max')] = smax
        elif num_stat == 'min':
            internal_props[add_suffix(target_prop, 'min')] = smin
        elif num_stat == 'std':
            if math.isnan(sv) == False:
                internal_props[add_suffix(target_prop, 'std')] = sv
            else:
                internal_props[add_suffix(target_prop, 'std')] = 0
        else:
            print('Invalid stat method')
            break
    return internal_props

def add_suffix(name, suffix, delimiter='_'):
    return str(name) + delimiter + str(suffix)

def children_prop_array(nodes, prop):
    array = [n.props.get(prop) for n in nodes if n.props.get(prop)] 
    return array

def annotate_taxa(tree, db="GTDB", taxid_attr="name", sp_delimiter='.', sp_field=0):
    global rank2values
    # def return_spcode(leaf):
    #     try:
    #         return leaf.name.split(sp_delimiter)[sp_field]
    #     except IndexError:
    #         return leaf.name

    if db == "GTDB":
        gtdb = GTDBTaxa()
        gtdb.annotate_tree(tree,  taxid_attr=taxid_attr)
    elif db == "NCBI":
        ncbi = NCBITaxa()
        # extract sp codes from leaf names
        #tree.set_species_naming_function(return_spcode)
        ncbi.annotate_tree(tree, taxid_attr=taxid_attr)

    # tree.annotate_gtdb_taxa(taxid_attr='name')
    # assign internal node as sci_name
    rank2values = defaultdict(list)
    for n in tree.traverse():
        if n.props.get('rank'):
            rank2values[n.props.get('rank')].append(n.props.get('sci_name',''))
        
        if n.name:
            pass
        else:
            n.name = n.props.get("sci_name", "")
    #print(rank2values)
    return tree, rank2values

def taxatree_prune(tree, rank_limit='subspecies'):
    rank_limit = rank_limit.lower()

    ex = False
    while not ex:
        ex = True
        for n in tree.iter_leaves():
            if n.props.get('rank') != rank_limit:
                n.detach()
                ex = False
    return tree

from utils import to_code, call
def conditional_prune(tree, conditions_input, prop2type):
    conditional_output = []
    for line in conditions_input:
        single_one = to_code(line)
        conditional_output.append(single_one)

    ex = False
    while not ex:
        ex = True
        for n in tree.traverse():
            final_call = False
            for or_condition in conditional_output:
                for condition in or_condition:
                    op = condition[1]
                    if op == 'in':
                        value = condition[0]
                        prop = condition[2]
                    else:
                        prop = condition[0]
                        value = condition[2]
                    datatype = prop2type[prop]
                    final_call = call(n, prop, datatype, op, value)
                    if final_call == False:
                        break
                    else:
                        continue
                if final_call:
                    n.detach()
                    ex = False
                else:
                    pass
    return tree

def tree2table(tree, internal_node=True, props=[], outfile='tree2table.csv'):
    node2leaves = {}
    leaf2annotations = {}
    with open(outfile, 'w', newline='') as csvfile:
        fieldnames = props
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t', extrasaction='ignore')
        writer.writeheader()
        for node in tree.traverse():
            if internal_node:
                output_row = dict(node.props)
                for k, prop in output_row.items():
                    if type(prop) == list:
                        output_row[k] = '|'.join(str(v) for v in prop)
                writer.writerow(output_row)
            else:
                if node.is_leaf():
                    output_row = dict(node.props)
                    for k, prop in output_row.items():
                        if type(prop) == list:
                            output_row[k] = '|'.join(str(v) for v in prop)
                    writer.writerow(output_row)
                else:
                    pass

    return 

def get_layouts(argv_input, layout_name, level, internal_rep):
    props = []
    layouts = []
    
    # identify range [1-5], index 1,2,3 and column names
    for i in argv_input.split(','):
        if i[0] == '[' and i[-1] == ']':
            column_start, column_end = get_range(i)
            for j in range(column_start, column_end+1):
                props.append(node_props[j-1])
        else:
            try:
                i = int(i)
                props.append(node_props[i-1])
            except ValueError:
                props.append(i)

    # load layout for each prop
    for idx, prop in enumerate(props):
        if layout_name in ['binary', 'revbinary']:
            prop_colour_dict = {} # key = value, value = colour id
            if columns:
                prop_values = list(set(columns[prop]))
            else:
                prop_values = list(set(children_prop_array(annotated_tree, prop)))
            nvals = len(prop_values)
            for i in range(0, nvals):
                prop_colour_dict[prop_values[i]] = paried_color[i]
            
            color = random_color(h=None)
            #color = random_color(h=None)
            if layout_name == 'binary':
                layout = conditional_layouts.LayoutBinary(prop+'_'+layout_name, level, color, prop_colour_dict, prop, reverse=False)
                #layout = TreeLayout(name=prop+'_'+layout_name, ns=conditional_layouts.boolean_layout(prop, level, color, prop_colour_dict, internal_rep))

            elif layout_name == 'revbinary':
                layout = conditional_layouts.LayoutBinary(prop+'_'+layout_name, level, color, prop_colour_dict, prop, reverse=True)

        # numerical layouts
        elif layout_name == 'heatmap':
            layout =  staple_layouts.LayoutHeatmap(prop+'_'+layout_name, level, internal_rep, prop)
        
        elif layout_name == 'barplot':
            layout =  staple_layouts.LayoutBarplot(name=prop+'_'+layout_name, prop=prop, \
                                    color_prop=paried_color[level], size_prop=prop, 
                                    column=level, internal_rep=internal_rep
                                    )
        
        # categorical layouts
        elif layout_name in ['label','rectangular', 'colorbranch']:
            colour_dict = {} # key = value, value = colour id
            if columns:
                prop_values = list(set(columns[prop]))
            else:
                prop_values = list(set(children_prop_array(annotated_tree, prop)))
            nvals = len(prop_values)

            for i in range(0, nvals):
                if nvals <= 14:
                    colour_dict[prop_values[i]] = paried_color[i]
                else:
                    colour_dict[prop_values[i]] = random_color(h=None)
            
            if layout_name == 'label':
                layout = text_layouts.LayoutText(prop+'_'+layout_name, level, colour_dict, text_prop = prop)
                #layout = TreeLayout(name=prop+'_'+layout_name, ns=text_layouts.text_layout(prop, level, colour_dict, internal_rep))
            
            elif layout_name == 'rectangular':
                layout = text_layouts.LayoutRect(prop+'_'+layout_name, level, colour_dict, text_prop = prop)
            
            elif layout_name == 'colorbranch':
                layout = text_layouts.LayoutColorbranch(prop+'_'+layout_name, level, colour_dict, text_prop = prop)

        
        layouts.append(layout)
        level += 1
    return layouts, level

def get_range(input_range):
    column_range = input_range[input_range.find("[")+1:input_range.find("]")]
    column_start, column_end = [int(i) for i in column_range.split('-')]
    #column_list_idx = [i for i in range(column_start, column_end+1)]
    return column_start, column_end

def random_color(h=None):
    """Generates a random color in RGB format."""
    if not h:
        h = random.random()
    s = 0.5
    l = 0.5
    return _hls2hex(h, l, s)
 
def _hls2hex(h, l, s):
    return '#%02x%02x%02x' %tuple(map(lambda x: int(x*255),
                                    colorsys.hls_to_rgb(h, l, s)))

def main():
    import time
    global annotated_tree, node_props, columns
    args = read_args()

    layouts = []
    level = 2 # level 1 is the leaf name

    # parse csv to metadata table
    start = time.time()
    
    if args.metadata:
        if args.no_colnames:
            metadata_dict, node_props, columns = parse_csv(args.metadata, no_colnames=args.no_colnames)
        else:
            metadata_dict, node_props, columns = parse_csv(args.metadata)
    else:
        columns = {}
    #code goes here
    end = time.time()
    print('Time for parse_csv to run: ', end - start)
    
    # parse tree
    if args.tree:
        tree = ete4_parse(args.tree)
    elif args.taxa and args.taxadb:
        tree = ''

    if args.text_column:
        text_column = args.text_column.split(',')
    else:
        text_column = []

    if args.num_column:
        num_column = args.num_column.split(',')
    else:
        num_column = []
    
    if args.bool_column:
        bool_column = args.bool_column.split(',')
    else:
        bool_column = []

    if args.text_column_idx:
        text_column_idx = []
        for i in args.text_column_idx.split(','):
            if i[0] == '[' and i[-1] == ']':
                text_column_start, text_column_end = get_range(i)
                for j in range(text_column_start, text_column_start+1):
                    text_column_idx.append(j)
            else:
                text_column_idx.append(int(i))

        text_column = [node_props[index-1] for index in text_column_idx]

    if args.num_column_idx:
        num_column_idx = []
        for i in args.num_column_idx.split(','):
            if i[0] == '[' and i[-1] == ']':
                num_column_start, num_column_end = get_range(i)
                for j in range(num_column_start, num_column_start+1):
                    num_column_idx.append(j)
            else:
                num_column_idx.append(int(i))

        num_column = [node_props[index-1] for index in num_column_idx]

    if args.bool_column_idx:
        bool_column_idx = []
        for i in args.bool_column_idx.split(','):
            if i[0] == '[' and i[-1] == ']':
                bool_column_start, bool_column_end = get_range(i)
                for j in range(bool_column_start, bool_column_end+1):
                    bool_column_idx.append(j)
            else:
                bool_column_idx.append(int(i))

        bool_column_idx = [node_props[index-1] for index in bool_column_idx]

    # load annotations to leaves
    start = time.time()
    
    taxon_column = []
    if not args.annotated_tree:
        if args.taxon_column:
            taxon_column.append(args.taxon_column)
            annotated_tree = load_metadata_to_tree(tree, metadata_dict, args.taxon_column, args.taxon_delimiter)
        else:
            annotated_tree = load_metadata_to_tree(tree, metadata_dict)
    else:
        annotated_tree = tree

    end = time.time()
    print('Time for load_metadata_to_tree to run: ', end - start)
    rest_column = []
    #rest_column = list(set(node_props) - set(text_column) - set(num_column) - set(bool_column))
    
    # stat method
    if args.counter_stat:
        counter_stat = args.counter_stat

    if args.num_stat:
        num_stat = args.num_stat

    # merge annotations
    start = time.time()
    if not args.annotated_tree:
        node2leaves = annotated_tree.get_cached_content()
        count = 0
        for node in annotated_tree.traverse("postorder"):
            internal_props = {}
            if node.is_leaf():
                pass
            else:
                
                if text_column:
                    internal_props_text = merge_text_annotations(node2leaves[node], text_column, counter_stat=counter_stat)
                    internal_props.update(internal_props_text)

                if num_column:
                    internal_props_num = merge_num_annotations(node2leaves[node], num_column, num_stat=num_stat)
                    internal_props.update(internal_props_num)

                if bool_column:
                    internal_props_bool = merge_text_annotations(node2leaves[node], bool_column, counter_stat=counter_stat)
                    internal_props.update(internal_props_bool)

                if rest_column:
                    internal_props_rest = merge_text_annotations(node2leaves[node], rest_column, counter_stat=counter_stat)
                    internal_props.update(internal_props_rest)
                
                #internal_props = {**internal_props_text, **internal_props_num, **internal_props_rest}
                #print(internal_props.items())
                for key,value in internal_props.items():
                    node.add_prop(key, value)
    else:
        pass
    end = time.time()
    print('Time for merge annotations to run: ', end - start)
    
    prop2type = {'name':'str'} # start with leaf name
    for prop in text_column+bool_column+rest_column:
        prop2type[prop] = 'str'
        prop2type[prop+'_counter'] = 'str'
    for prop in num_column:
        prop2type[prop] = 'num'
        prop2type[prop+'_avg'] = 'num'
        prop2type[prop+'_sum'] = 'num'
        prop2type[prop+'_max'] = 'num'
        prop2type[prop+'_min'] = 'num'
        prop2type[prop+'_std'] = 'num'

    # taxa annotations
    start = time.time()
    if args.taxonomic_profile:
        if not args.taxadb:
            print('Please specify which taxa db using --taxadb <GTDB|NCBI>')
        else:
            if args.taxon_column:
                annotated_tree, rank2values = annotate_taxa(annotated_tree, db=args.taxadb, taxid_attr=args.taxon_column, sp_delimiter=args.taxon_delimiter)
            else:
                annotated_tree, rank2values = annotate_taxa(annotated_tree, db=args.taxadb, taxid_attr="name")
        # if args.taxon_column:
        #     annotated_tree = annotate_taxa(annotated_tree, taxid_attr=taxon_column)
        # else:
        #     annotated_tree = annotate_taxa(annotated_tree, taxid_attr="name")
    else:
        rank2values = {}
    end = time.time()
    print('Time for annotate_taxa to run: ', end - start)
    ### Anslysis settings###

    # prune tree by rank
    if args.rank_limit:
        annotated_tree= taxatree_prune(annotated_tree, rank_limit=args.rank_limit)

    # collapse tree by condition 
    if args.pruned_by: # need to be wrap with quotes
        condition_strings = args.pruned_by
        annotated_tree= conditional_prune(annotated_tree, condition_strings, prop2type)

        

    # collapse tree by condition 
    if args.collapsed_by: # need to be wrap with quotes
        condition_strings = args.collapsed_by
        for condition in condition_strings:
            c_layout = TreeLayout(name=condition, \
                                    ns=conditional_layouts.collapsed_by_layout(condition, prop2type = prop2type, level=level))
            layouts.append(c_layout)

    # label node by condition
    if args.highlighted_by: # need to be wrap with quotes
        condition_strings = args.highlighted_by
        for condition in condition_strings:
            s_layout = TreeLayout(name=condition, \
                                    ns=conditional_layouts.highlight_layout(condition, prop2type = prop2type, level=level))
            layouts.append(s_layout)
        
    #### Layouts settings ####
    # Taxa layouts
    if args.TaxonLayout:
        taxa_layouts = [
            #taxon_layouts.TaxaRectangular(name='Taxa')
        ]
        
        taxon_prop = args.TaxonLayout

        if not rank2values:
            rank2values = defaultdict(list)
            for n in tree.traverse():
                if n.props.get('rank'):
                    rank2values[n.props.get('rank')].append(n.props.get('sci_name',''))
                
        else:
            pass

        for rank, value in rank2values.items():
            colour_dict = {} 
            nvals = len(value)
            for i in range(0, nvals):
                if nvals <= 14:
                    colour_dict[value[i]] = paried_color[i]
                else:
                    colour_dict[value[i]] = random_color(h=None)

            layout = taxon_layouts.TaxaClade(name='TaxaClade_'+rank, level=level, rank = rank, colour_dict=colour_dict)
            taxa_layouts.append(layout)

        # taxa_layouts = [
            # TreeLayout(name='level1_kingdom', ns=taxon_layouts.collapse_kingdom()),
            # TreeLayout(name='level2_phylum', ns=taxon_layouts.collapse_phylum()),
            # TreeLayout(name='level3_class', ns=taxon_layouts.collapse_class()),
            # TreeLayout(name='level4_order', ns=taxon_layouts.collapse_order()),
            # TreeLayout(name='level5_family', ns=taxon_layouts.collapse_family()),
            # TreeLayout(name='level6_genus', ns=taxon_layouts.collapse_genus()),
            # TreeLayout(name='level7_species', ns=taxon_layouts.collapse_species()),
        # ]


        layouts = layouts + taxa_layouts
        level += 1

    # numerical
    if args.num_stat != 'all':
        internal_num_rep = args.num_stat
    else:
        internal_num_rep = args.internal_plot_measure

    if args.HeatmapLayout:
        heatmap_layouts, level = get_layouts(args.HeatmapLayout, 'heatmap', level, internal_num_rep)
        layouts.extend(heatmap_layouts)

    if args.BarplotLayout:
        barplot_layouts, level = get_layouts(args.BarplotLayout, 'barplot', level, internal_num_rep)
        layouts.extend(barplot_layouts)

    # boolean 
    
    # categorical
    if args.ColorbranchLayout:
        colorbranch_layouts, level = get_layouts(args.ColorbranchLayout, 'colorbranch', level, 'counter')
        layouts.extend(colorbranch_layouts)

    if args.RectangularLayout:
        rectangular_layouts, level = get_layouts(args.RectangularLayout, 'rectangular', level, 'counter')
        layouts.extend(rectangular_layouts)
        
    if args.LabelLayout:
        label_layouts, level = get_layouts(args.LabelLayout, 'label', level, 'counter')
        layouts.extend(label_layouts)

    if args.BinaryLayout:
        label_layouts, level = get_layouts(args.BinaryLayout, 'binary', level, 'counter')
        layouts.extend(label_layouts)

    if args.RevBinaryLayout:
        label_layouts, level = get_layouts(args.RevBinaryLayout, 'revbinary', level, 'counter')
        layouts.extend(label_layouts)

    
    #### Output #####
    if args.outtree:
        annotated_tree.write(outfile=args.outtree, properties = [], format=1)
    if args.interactive:
        annotated_tree.explore(tree_name='example',layouts=layouts, port=args.port)
        
    
    return annotated_tree

if __name__ == '__main__':
    main()

#output_tree = main()


# # # write to pickle
# with open(OUTPUTTREE+'.ete', 'w') as f:
#     f.write(b64pickle.dumps(output_tree, encoder='pickle', pack=False))

# # read from pickle
# with open(OUTPUTTREE+'.ete', 'r') as f:
#     file_content = f.read()
#     print(b64pickle.loads(file_content, encoder='pickle', unpack=False))

# write to newick tree
#output_tree.write(outfile=OUTPUTTREE, properties=[], format=1)

# write to tsv file
# fieldnames = [
#     'name', 'support', 'dist',  'leaves', 'sample1_sum', 'sample1_min', 'sample1_max', 'sample1_mean', 'sample1_variance', 'sample2_sum', 'sample2_min', 'sample2_max', 'sample2_mean', 'sample2_variance', 'sample3_sum', 'sample3_min', 'sample3_max', 'sample3_mean', 'sample3_variance', 'sample4_sum', 'sample4_min', 'sample4_max', 'sample4_mean', 'sample4_variance', 'sample5_sum', 'sample5_min', 'sample5_max', 'sample5_mean', 'sample5_variance', 'random_type_counter', 'taxid', 'sci_name', 'common_name', 'lineage', 'rank', 'named_lineage', 'nleaves', 'sample1', 'sample2', 'sample3', 'sample4','sample5','random_type' 
# ]
# tree2table(output_tree, internal_node=True, props=fieldnames)


# interactive explore
#output_tree.explore(tree_name='example',layouts=[], port=5000)