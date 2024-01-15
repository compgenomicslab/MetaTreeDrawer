#!/usr/bin/env python3
try:
    from distutils.util import strtobool
except ImportError:
    from treeprofiler.src.utils import strtobool
    
from treeprofiler.src.utils import add_suffix

# Lineage specificity analysis
# Function to calculate precision, sensitivity, and F1 score
def calculate_metrics(node, total_with_trait, prop):
    if not node.is_leaf:
        clade_with_trait = sum(1 for child in node.leaves() if bool(strtobool(child.props.get(prop))))
        clade_total = len([leave for leave in node.leaves()])
        precision = clade_with_trait / clade_total if clade_total else 0
        sensitivity = clade_with_trait / total_with_trait if total_with_trait else 0
        f1 = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) else 0
        return precision, sensitivity, f1
    return 0, 0, 0

# Total number of nodes with the trait
def get_total_trait(tree, prop):
    return sum(1 for node in tree.leaves() if bool(strtobool(node.props.get(prop))))

###### start lineage specificity analysis ######
def run_lsa(tree, props, precision_cutoff=0.95, sensitivity_threshold=0.95):
    best_node = None
    best_f1 = -1
    for prop in props:
        total_with_trait = get_total_trait(tree, prop)
        # Calculating metrics for each clade
        for node in tree.traverse("postorder"):
            if not node.is_leaf:
                #node.add_prop(trait=int(node.name[-1]) if node.is_leaf else 0)
                precision, sensitivity, f1 = calculate_metrics(node, total_with_trait, prop)
                node.add_prop(add_suffix(prop, "prec"), precision)
                node.add_prop(add_suffix(prop, "sens"), sensitivity)
                node.add_prop(add_suffix(prop, "f1"), f1)
                #node.add_prop(precision=precision, sensitivity=sensitivity, f1_score=f1)
                print(f"Node: {node.name} , Precision: {precision}, Sensitivity: {sensitivity}, F1 Score: {f1}")

                # Check if the node meets the lineage-specific criteria
                if precision >= precision_cutoff and sensitivity >= sensitivity_threshold and f1 > best_f1:
                    best_f1 = f1
                    best_node = node
        if best_node:
            print(f"Best node: for feature {prop}: {best_node}")
    #return tree, best_node

# #### find lineage-specific clades ####
# def find_lineage_specific_root(tree):
#     best_node = None
#     best_f1 = -1
#     for node in tree.traverse("postorder"):
#         if not node.is_leaf:
#             precision, sensitivity, f1 = calculate_metrics(node, total_with_trait)
#             node.add_props(precision=precision, sensitivity=sensitivity, f1_score=f1)
            
#             # Check if the node meets the lineage-specific criteria
#             if precision >= 0.5 and sensitivity >= 0.5 and f1 > best_f1:
#                 best_f1 = f1
#                 best_node = node
#     return best_node
