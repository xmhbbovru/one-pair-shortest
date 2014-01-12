#!/usr/bin/env python
# shortestpath.py rev 11 Jan 2013 Stuart Ambler
# Breadth first search methods for single pair shortest path, reads graphs,
# generates trees and random graphs, and tests.
# Copyright (c) 2014 Stuart Ambler.
# Distributed under the Boost License in the accompanying file LICENSE.

from __future__ import print_function

from collections import deque  # for bfs0,1,2
#import cProfile   # for testing; uses line_profiler now
import functools  # for testing
import getopt     # for testing
import itertools  # for testing
import math       # for testing and test data generation
import random     # for test data generation
import sys        # for testing
import timeit     # for testing

# Finds shortest path from root to target given edgelist, using breadth first
# search, adapted from Skiena The Algorithm Design Manual Second Edition,
# pp. 162-166.  Modified from my original version by swapping root and target
# if the latter has a smaller edgelist, for consistency with bfs1 and bfs2.
# Returns (path_len, path), path given as list of nodes, or None if no path.

def bfs0(root, target, edgelist):
    if (root == target):
        return (0, [root])
    if (not root in edgelist.keys()) or (not len(edgelist) > 0):
        return None

    if len(edgelist[root]) > len(edgelist[target]):
        (root, target) = (target, root)
 
    visited = dict()
    parent = dict()
    for node in edgelist.keys():
        visited[node] = False
        parent[node] = None

    queue = deque()
    queue.append(root)
    visited[root] = True
    prev = root

    done = False
    while (not done) and len(queue) > 0:
        curr = queue.popleft()
        for node in edgelist[curr]:
            if not visited[node]:
                visited[node] = True
                queue.append(node)
                parent[node] = curr
            # Could indent the following, saving time.  Done in bfs1.
            if node == target:
                done = True
                break
    if done:
        accum = [target]
        p = parent[target]
        while p is not None:
            accum.insert(0, p)
            p = parent[p]
        return (len(accum) - 1, accum)
    else:
        return None

# Finds shortest path from root to target given edgelist, using breadth first
# search, adapted from bfs0 (use parent dict in such a way as to avoid having
# visited dict, indent the if statement noted in bfs0, and start with whichever
# of root, target has the smaller edgelist.
# Returns (path_len, path), path given as list of nodes, or None if no path.

def bfs1(root, target, edgelist):
    if (root == target):
        return (0, [root])
    if (not root in edgelist.keys()) or (not len(edgelist) > 0):
        return None

    if len(edgelist[root]) > len(edgelist[target]):
        (root, target) = (target, root)
 
    parent = dict()
    for node in edgelist.keys():
        parent[node] = None

    queue = deque()
    queue.append(root)
    prev = root

    done = False
    while (not done) and len(queue) > 0:
        curr = queue.popleft()
        for node in edgelist[curr]:
            if (parent[node] is None) and (node != root):
                parent[node] = curr
                if node == target:
                    done = True
                    break
                queue.append(node)
    if done:
        accum = [target]
        p = parent[target]
        while p is not None:
            accum.insert(0, p)
            p = parent[p]
        return (len(accum) - 1, accum)
    else:
        return None

# Finds shortest path from root to target given edgelist, using breadth first
# search, adapted from bfs1, but moves from both ends to the middle, and uses
# ideas (primarily doing a whole level at a time) from http://
# networkx.lanl.gov/_modules/networkx/algorithms/shortest_paths/unweighted.htm .
# Unlike bfs0 and bfs1, bfs2 expects the edgelist to be a list of lists, indexed
# by node, rather than a dictionary indexed by node number and values lists.
# Returns (path_len, path), path given as list of nodes, or None if no path.

# When starting to write this, I added a note to use optimizations assuming the
# path is much smaller than 1/2 the size of the edgelist, but it looks like
# none occurred to me).

#@profile  # for line_profiler
def bfs2(root, target, edgelist):
    if (root == target):
        return (0, [root])
#    # These checks may not be needed
#    nr_nodes = len(edgelist)
#    if (nr_nodes <= 0
#        or root < 0 or root >= nr_nodes
#        or target < 0 or target >= nr_nodes):
#        return None

    if len(edgelist[root]) > len(edgelist[target]):
        (root, target) = (target, root)
 
    parent_r = { root:None }
    parent_t = { target:None }
    r_level_nodes = [root]
    t_level_nodes = [target]

    match_node = None

    # Process a whole level for r or t, before possibly switching.
    while (match_node is None) and r_level_nodes and t_level_nodes:
        if len(r_level_nodes) <= len(t_level_nodes):
            level_nodes = r_level_nodes
            r_level_nodes = []
            for node in level_nodes:
                for new_node in edgelist[node]:
                    if new_node not in parent_r:
                        parent_r[new_node] = node
                        r_level_nodes.append(new_node)
                        parent_r[new_node] = node
                    if node in parent_t:
                        match_node = node
                        break
                if match_node is not None:
                    break
        else:
            level_nodes = t_level_nodes
            t_level_nodes = []
            for node in level_nodes:
                for new_node in edgelist[node]:
                    if new_node not in parent_t:
                        parent_t[new_node] = node
                        t_level_nodes.append(new_node)
                        parent_t[new_node] = node
                    if node in parent_r:
                        match_node = node
                        break
                if match_node is not None:
                    break

    if match_node is not None:
        accum_r = [match_node]
        p = parent_r[match_node]
        while p is not None:
            accum_r.insert(0, p)
            p = parent_r[p]

        accum_t = []
        p = parent_t[match_node]
        while p is not None:
            accum_t.insert(0, p)
            p = parent_t[p]
        accum_t.reverse()

        accum = accum_r if accum_t is None else accum_r + accum_t
        return (len(accum) - 1, accum)
    else:
        return None

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

# Transforms data as needed for input to bfs0,1,2, since the first two
# use an edgelist dict with meaningful or given node numbers, but the
# third uses an edgelist list with contiguous node numbers starting at 0
# as indices.

def bfs_input_helper(i, root, target, el, el_name, el_arr, elndnr2ix):
    if i < 2:
        return (root, target, el, el_name)
    else:
        return (elndnr2ix[root], elndnr2ix[target], el_arr,
                el_name + '_arr')

# Transforms data output from bfs0,1,2, since the first two return
# paths with meaningful or given node numbers, but the third returns
# a path with node numbers that are list indices.

def bfs_output_helper(i, output, elndix2nr):
    if i < 2:
        return(output)
    else:
        if output is None:
            return None
        pathlen = output[0]
        path    = output[1]
        return (pathlen, [elndix2nr[node] for node in path])

# Used to check that output from bfs0,1,2 is the same or with reversed path

def output_eq_or_rev(output1, output2):
    if output1 == output2:
        return True
    elif output1 is None or output2 is None:
        return False
    else:
        (pathlen1, path1) = output1
        (pathlen2, path2) = output2
        revpath1 = list(path1)
        revpath1.reverse()
        return pathlen1 == pathlen2 and (path1 == path2 or revpath1 == path2)

""" If the verbose flag is set, the test of read_edgelist working correctly,
and the display for manual checking of selected paths computed by bfs0,  assume
the following content of edgelist.txt (order unimportant):
2	1
1	2
3	2
	3
4	3
5	3
3	4
5	4
3	5
4	5
6	1
1	6
7	6
6	7
9	8
8	9

i.e. the edges of the graph

1--2--3--4  8--9
|      \ |
6--7    \5
"""

def usage():
    print(
"""
Usage: python shortestpath.py [-d <degree>] [-m <max_depth>]
                              [-r <nr_reps_random>]
                              [-n <nr_nodes_random>] [-f <fraction_edges>]
                              [-v]
long versions [--degree=<degree>] [--max_depth <max_depth>]
              [--nr_reps_random=<nr_reps_random>]
              [--nr_nodes_random=<nr_nodes_random>]
              [--fraction_edges=<fraction_edges>]
              [--verbose]
""")

def get_cmdline_options(argv, degree, max_depth,
                        nr_reps_random, nr_nodes_random, fraction_edges,
                        verbose):
    invalid_input_exit_code = 2

    if isinstance(argv, str):
        argv = argv.split(' ')
    try:
        (opts, args) = getopt.getopt(argv, 'd:m:r:n:f:v',
                                     ['degree=', 'max_depth=',
                                      'nr_reps_random=',
                                      'nr_nodes_random=',
                                      'fraction_edges=',
                                      'verbose'])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(invalid_input_exit_code)

    for (opt, arg) in opts:
        if opt in ('-d', '--degree'):
            try:
                arg_degree = int(arg)
                if arg_degree >= 2:
                    degree = arg_degree
                else:
                    print('degree must be an integer at least 2')
                    usage()
                    sys.exit(2)
            except ValueError:
                print('degree must be an integer at least 2')
                usage()
                sys.exit(invalid_input_exit_code)
        elif opt in ('-m', '--max_depth'):
            try:
                arg_max_depth = int(arg)
                if arg_max_depth >= 2:
                    max_depth = arg_max_depth
                else:
                    print('max_depth must be an integer at least 2')
                    usage()
                    sys.exit(invalid_input_exit_code)
            except ValueError:
                print('max_depth must be an integer at least 2')
                usage()
                sys.exit(invalid_input_exit_code)
        elif opt in ('-r', '--nr_reps_random'):
            try:
                arg_nr_reps_random = int(arg)
                nr_reps_random = arg_nr_reps_random
            except ValueError:
                print('nr_reps_random must be an integer')
                usage()
                sys.exit(invalid_input_exit_code)
        elif opt in ('-n', '--nr_nodes_random'):
            try:
                arg_nr_nodes_random = int(arg)
                if arg_nr_nodes_random >= 2:
                    nr_nodes_random = arg_nr_nodes_random
                else:
                    print('nr_nodes_random must be an integer at least 2')
                    usage()
                    sys.exit(invalid_input_exit_code)
            except ValueError:
                print('nr_nodes_random must be an integer at least 2')
                usage()
                sys.exit(invalid_input_exit_code)
        elif opt in ('-f', '--fraction_edges'):
            try:
                arg_fraction_edges = float(arg)
                if arg_fraction_edges > 0.0 and arg_fraction_edges < 1.0:
                    fraction_edges = arg_fraction_edges
                else:
                    print('fraction_edges must be between '
                          + '0.0 and 1.0 exclusive')
                    usage()
                    sys.exit(invalid_input_exit_code)
            except ValueError:
                print('fraction_edges must be between 0.0 and 1.0 exclusive')
                usage()
                sys.exit(invalid_input_exit_code)
        elif opt in ('-v', '--verbose'):
            verbose = True

    return (degree, max_depth, nr_reps_random, nr_nodes_random, fraction_edges,
            verbose)

global_bfs_output = (0,[0])  # used for communication from timeit function calls

def main(argv):
    global global_bfs_output

    degree          = 3  # must be at least 2
    max_depth       = 7  # must be at least 2
    nr_reps_random  = 0  # because potentially time-consuming
    nr_nodes_random = 10000
    fraction_edges  = 0.005
    verbose         = False
    (degree, max_depth, nr_reps_random, nr_nodes_random, fraction_edges,
     verbose) = get_cmdline_options(argv, degree, max_depth, nr_reps_random,
                                    nr_nodes_random, fraction_edges, verbose)
    nr_bfs = 3
    bfs_func_list = [bfs0, bfs1, bfs2]

    correct_el = {1: [2, 6], 2: [1, 3], 3: [2, 4, 5], 4: [3, 5],
                  5: [3, 4], 6: [1, 7], 7: [6], 8: [9], 9: [8]}
    el = read_edgelist('edgelist.txt')
    (el, el_arr, el_ndix2nr, el_ndnr2ix) = make_contiguous_edgelist(el)

    if verbose:
        print(el, 'read ok' if el == correct_el else 'not read ok')
        print('manually check:')
        print('1 1', bfs0(1, 1, el))
        print('1 2', bfs0(1, 2, el))
        print('1 3', bfs0(1, 3, el))
        print('1 4', bfs0(1, 4, el))
        print('1 5', bfs0(1, 5, el))
        print('1 6', bfs0(1, 6, el))
        print('1 8', bfs0(1, 8, el))
        print('2 3', bfs0(2, 3, el))
        print('2 4', bfs0(2, 4, el))
        print('2 5', bfs0(2, 5, el))
        print('8 9', bfs0(8, 9, el))
        print()
        print('1 1', bfs0(1, 1, el))
        print('2 1', bfs0(2, 1, el))
        print('3 1', bfs0(3, 1, el))
        print('4 1', bfs0(4, 1, el))
        print('5 1', bfs0(5, 1, el))
        print('6 1', bfs0(6, 1, el))
        print('7 1', bfs0(7, 1, el))
        print('8 1', bfs0(8, 1, el))
        print('3 2', bfs0(3, 2, el))
        print('4 2', bfs0(4, 2, el))
        print('5 2', bfs0(5, 2, el))
        print('9 8', bfs0(9, 8, el))
        print()

    # Generate tree graph.

    (eltree, eltree_arr,
     eltree_ndix2nr, eltree_ndnr2ix) = construct_tree_edgelist(degree,
                                                               max_depth)
    eltree_root_nr   = int('1' * (max_depth - 1) + '11')
    eltree_target_nr = int('1' * (max_depth - 1) + '21')

    # Order makes a difference in timing; putting node with smaller edgelist
    # as root has been faster.
    # (eltree_root_nr, eltree_target_nr) = (eltree_target_nr, eltree_root_nr)

    print(('generated tree graph degree {0}, max_depth {1}, '
           + 'nr nodes {2} = nr edges + 1').format(degree, max_depth,
                                                   len(eltree.keys())))

    # Test that the various methods agree on all pairs for graph from file.

    nodelist = sorted(el.keys())
    for i in range(1, nr_bfs):
        for x in itertools.combinations(nodelist, 2):
            (root, target, e, name) = bfs_input_helper(i, x[0], x[1], el,
                                                       'el', el_arr, el_ndnr2ix)
            bfsi_output = bfs_output_helper(i,
                                            bfs_func_list[i](root, target, e),
                                            el_ndix2nr)
            bfs0_output = bfs0(x[0], x[1], el)
            if not output_eq_or_rev(bfs0_output, bfsi_output):
                print('Inconsistency bfs{0},bfs0({1}, {2}, el)'.format(*((i,)
                                                                         + x)))
                print(bfsi_output)
                print(bfs0_output)

    # Total times for each of various methods for all pairs for graph from file.

    for i in range(0, nr_bfs):
        t = 0
        for x in itertools.combinations(nodelist, 2):
            (root, target, e, name) = bfs_input_helper(i, x[0], x[1], el,
                                                       'el', el_arr, el_ndnr2ix)
            test_str = 'shortestpath.bfs{0}({1}, {2}, {3})'.format(i, root,
                                                                   target,
                                                                   name)
            setup_str = ('import shortestpath; el = shortestpath.read_edgelist('
                         + '"edgelist.txt"); (el, el_arr, el_ndix2nr, '
                         + 'el_ndnr2ix) = '
                         + 'shortestpath.make_contiguous_edgelist(el); '
                         + '(root, target, e, name) = '
                         + 'shortestpath.bfs_input_helper({0}, '
                         + '{1}, {2}, el, "el", '
                         + 'el_arr, el_ndnr2ix)').format(i, x[0], x[1])
            t = t + timeit.timeit(test_str, setup=setup_str, number=1)
        print('timeit file all pairs bfs{0} {1}'.format(i, t))

    # Times for the various methods for tree graph constructed above.

    for i in range(0, nr_bfs):
        (root, target, e, name) = bfs_input_helper(i, eltree_root_nr,
                                                   eltree_target_nr,
                                                   eltree, 'eltree', eltree_arr,
                                                   eltree_ndnr2ix)
        if verbose:
            test_str = ('output = shortestpath.bfs{0}'
                        + '({1}, {2}, {3}); print('
                        + 'shortestpath.bfs_output_helper({0}, '
                        + 'output, eltree_ndix2nr))').format(i, root, target,
                                                            name)
        else:
            test_str = ('output = shortestpath.bfs{0}'
                        + '({1}, {2}, {3})').format(i, root, target, name)
        setup_str = ('import shortestpath; '
                     + '(eltree, eltree_arr, eltree_ndix2nr, eltree_ndnr2ix) = '
                     + 'shortestpath.construct_tree_edgelist'
                     + '({0}, {1})').format(degree, max_depth)
        t = timeit.timeit(test_str, setup=setup_str, number=1)
        print(('timeit tree degree {0} depth {1} bfs{2} {3} {4} {5}'
               + '').format(degree, max_depth, i,
                            eltree_root_nr, eltree_target_nr, t))

    # Generate random graphs, choose nodes at random, time the various methods.
    # Because of the time to generate, put the bfs method loop inside the
    # generation rep loop.

    ran_t = [0.0] * nr_bfs       # used to store total for all reps
    ran_pathlen = [0] * nr_bfs   # used to store total for all reps
    ran_output  = [(0, [0])] * nr_bfs # used to store result from current rep
    tot_act_nr_nodes = 0
    tot_act_nr_edges = 0
    tot_nr_no_paths  = 0

    for rep_nr in range(0, nr_reps_random):  # nr_reps_random <= 0 ignored
        (ran, ran_arr,
         ran_ndix2nr, ran_ndnr2ix) = construct_random_graph(nr_nodes_random,
                                                            fraction_edges)
        act_nr_nodes = len(ran_arr)
        tot_act_nr_nodes = tot_act_nr_nodes + act_nr_nodes
        for a_nodes_edges in ran_arr:
            tot_act_nr_edges = tot_act_nr_edges + len(a_nodes_edges)

        ran_root_ix = None
        ran_target_ix = None
        while ((ran_root_ix is None) or (ran_target_ix is None)
               or (ran_root_ix == ran_target_ix)):
            ran_root_ix = random.randint(0, act_nr_nodes)
            ran_target_ix = random.randint(0, act_nr_nodes)
        ran_root_nr = ran_ndix2nr[ran_root_ix]
        ran_target_nr = ran_ndix2nr[ran_target_ix]

        for i in range(0, nr_bfs):
            (root, target, e, name) = bfs_input_helper(i, ran_root_nr,
                                                       ran_target_nr,
                                                       ran, 'ran',
                                                       ran_arr,
                                                       ran_ndnr2ix)
            def f():
                global global_bfs_output
                global_bfs_output = bfs_output_helper(i,
                                                      bfs_func_list[i](root,
                                                                       target,
                                                                       e),
                                                      ran_ndix2nr)
            ran_t[i] = ran_t[i] + timeit.timeit(f, number=1)
            if global_bfs_output is None:
                tot_nr_no_paths = tot_nr_no_paths + 1
            else:
                ran_pathlen[i] = ran_pathlen[i] + global_bfs_output[0]
            ran_output[i] = global_bfs_output
            if not output_eq_or_rev(ran_output[i], ran_output[0]):
                print('Inconsistency random graph bfs{0},bfs0)'.format(i))
                print(ran_output[i])
                print(ran_output[0])

    # Display random graphs timing.

    if nr_reps_random > 0:  # nr_reps_random <= 0 ignored
        for i in range(0, nr_bfs):
            print('bfs{0} random, nr nodes {1}, fraction edges {2}'.format(i,
                      tot_act_nr_nodes / float(nr_reps_random), fraction_edges))
            # prints the number of undirected edges
            print(('     nr edges {0}, nr reps {1}, mean path length {2}'
                   + '').format(0.5 * tot_act_nr_edges / float(nr_reps_random),
                                nr_reps_random,
                                ran_pathlen[i] / float(nr_reps_random)))
            if verbose:
                print('     output', ran_output[i])
            print('     mean time {0}'.format(ran_t[i] / float(nr_reps_random)))
    
if __name__ == '__main__':
    main (sys.argv[1:])

""" From interactive python prompt:
"""
