#!/usr/bin/env python
# gendata.py rev 28 Jan 2014 Stuart Ambler
# Generate or read graphs for testings; generates trees or random graphs.
# Copyright (c) 2014 Stuart Ambler.
# Distributed under the Boost License in the accompanying file LICENSE.

import math
import random
import tempfile

# Returns as a list of pairs, the edges of the graph
#
# 1--2--3--4  8--9
# |      \ |
# 6--7    \5

def example_edgelist_of_pairs():
    return [(2, 1),
            (1, 2),
            (3, 2),
            (2, 3),
            (4, 3),
            (5, 3),
            (3, 4),
            (5, 4),
            (3, 5),
            (4, 5),
            (6, 1),
            (1, 6),
            (7, 6),
            (6, 7),
            (9, 8),
            (8, 9)]

# Returns data for checking the results of finding shortest paths in the data
# from example_edgelist_lines, a dict with keys pairs of nodes and values pairs
# of shortest path lengths and shortest paths.

def example_shortest_paths():
    half = {(1, 2):(1, [1, 2]),
            (1, 3):(2, [1, 2, 3]),
            (1, 4):(3, [1, 2, 3, 4]),
            (1, 5):(3, [1, 2, 3, 5]),
            (1, 6):(1, [1, 6]),
            (1, 7):(2, [1, 6, 7]),
            (1, 8):None,
            (1, 9):None,

            (2, 3):(1, [2, 3]),
            (2, 4):(2, [2, 3, 4]),
            (2, 5):(2, [2, 3, 5]),
            (2, 6):(2, [2, 1, 6]),
            (2, 7):(3, [2, 1, 6, 7]),
            (2, 8):None,
            (2, 9):None,

            (3, 4):(1, [3, 4]),
            (3, 5):(1, [3, 5]),
            (3, 6):(3, [3, 2, 1, 6]),
            (3, 7):(4, [3, 2, 1, 6, 7]),
            (3, 8):None,
            (3, 9):None,

            (4, 5):(1, [4, 5]),
            (4, 6):(4, [4, 3, 2, 1, 6]),
            (4, 7):(5, [4, 3, 2, 1, 6, 7]),
            (4, 8):None,
            (4, 9):None,

            (5, 6):(4, [5, 3, 2, 1, 6]),
            (5, 7):(5, [5, 3, 2, 1, 6, 7]),
            (5, 8):None,
            (5, 9):None,

            (6, 7):(1, [6, 7]),
            (6, 8):None,
            (6, 9):None,

            (7, 8):None,
            (7, 9):None,

            (8, 9):(1, [8, 9])}

    retval = dict(half)
    for p in half.keys():
        rev_p = (p[1], p[0])
        if half[p] is None:
            retval[rev_p] = None
        else:
            retval[rev_p] = (half[p][0], [x for x in reversed(half[p][1])])
    return retval

# Creates test data for read_edgelist.

def write_edgelist_of_pairs(elp):
    f = tempfile.NamedTemporaryFile(mode='w', delete=False)
    f.writelines(['{0} {1}\n'.format(*pair) for pair in elp])
    f.close()
    return f.name

# For checking the results of read_edgelist of the file created by
# write_edgelist_of_pairs given data from example_edgelist_of_pairs.

def correctly_read_example_edgelist_of_pairs():
    return {1: [2, 6], 2: [1, 3], 3: [2, 4, 5], 4: [3, 5],
            5: [3, 4], 6: [1, 7], 7: [6], 8: [9], 9: [8]}

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
    new_nodelist = []
    for n in nodelist:  # node is tuple (node_nr, depth)
        if n[1] + 1 == curr_depth:
            # root has no parent so needs one more child
            nr_children = degree - 1 if curr_depth > 1 else degree
            for i in range(0, nr_children):
                node_nr = n[0]
                new_node_nr = node_nr + (i + 1) * depth_factor
                new_node = (new_node_nr, curr_depth)
                new_nodelist.append(new_node)

                old_list = edgelist.get(node_nr)
                if old_list:
                    old_list.append(new_node_nr)
                else:
                    edgelist[node_nr] = [new_node_nr]

                # Used to have the following, but coverage said the first
                # condition never occurred.  If the rest of the logic here and
                # in callers is ok, could just use what's after else.
                # However, probably little cost.

                new_list = edgelist.get(new_node_nr)
                if new_list:
                    new_list.append(node_nr)
                else:
                    edgelist[new_node_nr] = [node_nr]

    nodelist += new_nodelist

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
