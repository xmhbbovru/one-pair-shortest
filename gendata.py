#!/usr/bin/env python
# gendata.py rev 11 Jan 2014 Stuart Ambler
# Generate or read graphs for testings; generates trees or random graphs.
# Copyright (c) 2014 Stuart Ambler.
# Distributed under the Boost License in the accompanying file LICENSE.

import math
import random

# Assumes one edge per line, a pair of integer node numbers separated by
# whitespace, that contains both ordered pairs for each undirected edge.
# Returns a dict with keys the node numbers found in the input, and values
# the edgelists (list of node numbers) for them.

def read_edgelist(filename):
    infile = open(filename, 'r')
    lines = infile.readlines()
    infile.close()
    edgelist = dict()
    for line in lines:
        tokens = line.split()
        from_node = int(tokens[0])
        to_node = int(tokens[1])
        curr_list = edgelist.get(from_node)
        if curr_list:
            curr_list.append(to_node)
        else:
            edgelist[from_node] = [to_node]
    return edgelist

# Given edgelist dict with 'meaningful' edge numbers as keys, creates an
# edgelist list with contiguous edge numbers starting at 0, a list to translate
# from contiguous to meaningful edge numbers, and a dict to translate backwards.

def make_contiguous_edgelist(edgelist):
    nr_nodes = len(edgelist.keys())
    edgelist_array = [None] * nr_nodes
    node_ix_to_nr = [None] * nr_nodes
    node_nr_to_ix = {}
    i = 0
    for node in edgelist.keys():
        node_ix_to_nr[i] = node
        node_nr_to_ix[node] = i
        i = i + 1
    i = 0
    for (node, el) in edgelist.items():
        edgelist_array[i] = [node_nr_to_ix[edge_node] for edge_node in el]
        i = i + 1
    return (edgelist, edgelist_array, node_ix_to_nr, node_nr_to_ix)

# Constructs a given depth of the tree, adding to the list nodelist and
# dict edgelist.

def construct_tree_level(degree, max_depth, curr_depth, nodelist, edgelist):
    nr_digits_per_level = int(math.ceil(math.log10(degree)))
    depth_factor = 10**(curr_depth * nr_digits_per_level)
    for n in nodelist:  # node is tuple (node_nr, depth)
        if n[1] + 1 == curr_depth:
            # root has no parent so needs one more child
            nr_children = degree - 1 if curr_depth > 1 else degree
            for i in range(0, nr_children):
                node_nr = n[0]
                new_node_nr = node_nr + (i + 1) * depth_factor
                new_node = (new_node_nr, curr_depth)
                nodelist.append(new_node)

                old_list = edgelist.get(node_nr)
                if old_list:
                    old_list.append(new_node_nr)
                else:
                    edgelist[node_nr] = [new_node_nr]

                new_list = edgelist.get(new_node_nr)
                if new_list:
                    new_list.append(node_nr)
                else:
                    edgelist[new_node_nr] = [node_nr]

# degree must be at least 2.  The degree of the leaves will be 1.
# Returns per make_contiguous_edgelist, an edgelist dict with 'meaningful' edge
# numbers as keys, as well as an edgelist list with contiguous edge numbers
# starting at 0, a list to translate from contiguous to meaningful edge numbers,
# and a dict to translate backwards.

def construct_tree_edgelist(degree, max_depth):
    nodelist   = [(1, 0)]
    edgelist   = {}
    for depth in range(1, max_depth + 1):
        construct_tree_level(degree, max_depth, depth, nodelist, edgelist)
    return make_contiguous_edgelist(edgelist)

# nr_nodes must be at least 2 and fraction_edges between 0 and 1 inclusive
# (edge cases of 0.0 and 1.0 not tested).
# fraction_edges is the desired fraction of the possible
# (nr_nodes) * (nr_nodes - 1) / 2 edges.

def construct_random_graph(nr_nodes, fraction_edges):
    nodelist = range(0, nr_nodes)
    desired_nr_edges = int(round(fraction_edges * nr_nodes * (nr_nodes - 1)))
    edgelist = {}
    nr_edges = 0

    while (nr_edges < desired_nr_edges):
        from_node = random.randint(0, nr_nodes - 1)
        to_node = random.randint(0, nr_nodes - 1)

        from_list = edgelist.get(from_node)
        to_list = edgelist.get(to_node)
        if from_list:
            if to_node not in from_list:  # our logic implies also the reverse
                from_list.append(to_node)
                if to_list:
                    to_list.append(from_node)
                else:
                    edgelist[to_node] = [from_node]
                nr_edges = nr_edges + 2
        else:
            edgelist[from_node] = [to_node]
            if to_list:
                to_list.append(from_node)
            else:
                edgelist[to_node] = [from_node]
            nr_edges = nr_edges + 2

    return make_contiguous_edgelist(edgelist)
