#!/usr/bin/env python
# test.py rev 28 Jan 2014 Stuart Ambler
# Tests and times breadth first search algorithms bfs1,2 using graphs
# generated and read in by gendata functions.
# Copyright (c) 2014 Stuart Ambler.
# Distributed under the Boost License in the accompanying file LICENSE.

from __future__ import print_function

#import cProfile   # uses line_profiler now
import functools
import getopt
import itertools
import os
import random
import sys
import timeit

from bfs1    import *
from bfs2    import *
from bfserr  import *
from gendata import *

invalid_input_exit_code = 2

# Transforms data as needed for input to bfs1,2 since the first one uses
# an edgelist dict with meaningful or given node numbers, but the second
# uses an edgelist list with contiguous node numbers starting at 0 as indices.

def bfs_input_helper(contig, root, target, el, el_name, el_arr, el_nd_nr_2_ix):
    if contig:
        return (el_nd_nr_2_ix[root], el_nd_nr_2_ix[target], el_arr,
                el_name + '_arr')
    else:
        return (root, target, el, el_name)

# Transforms data output from bfs1,2 since the first one returns paths
# with meaningful or given node numbers, but the second returns a path
# with node numbers that are list indices.

def bfs_output_helper(contig, output, el_nd_ix_2_nr):
    if contig:
        if output is None:
            return None
        pathlen = output[0]
        path    = output[1]
        return (pathlen, [el_nd_ix_2_nr[node] for node in path])
    else:
        return(output)

# Used to check that output from bfs1,2 is the same or with reversed path

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

global_bfs_output = (0,[0])  # used for communication from timeit function calls

# Test that the example graph is written, read, and processed correctly.

def test_example(bfs_func_list, bfs_contig, errors, verbose,
                 cause_error_kludge=False):
    print('testing example graph')
    nr_bfs = len(bfs_func_list)

    tmp_filename = write_edgelist_of_pairs(example_edgelist_of_pairs())
    example_el = read_edgelist(tmp_filename)
    os.remove(tmp_filename)
    correctly_read_example = correctly_read_example_edgelist_of_pairs()
    if correctly_read_example != example_el or cause_error_kludge:
        errors.append('test_example read_edgelist problem')
        print('  error, example edgelist of pairs expected: ',
              correctly_read_example)
        print('    as read, ', example_el)
        return

    (example_el, example_el_arr, example_el_nd_ix_2_nr,
     example_el_nd_nr_2_ix) = make_contiguous_edgelist(example_el)
    correct_example_el_output = example_shortest_paths()

    nodelist = sorted(example_el.keys())
    bfs_problem = False
    for i in range(1, nr_bfs):
        contig = bfs_contig[i]
        for x in itertools.combinations(nodelist, 2):
            (root, target, e, name) = bfs_input_helper(contig, x[0], x[1],
                                                       example_el,
                                                       'example_el',
                                                       example_el_arr,
                                                       example_el_nd_nr_2_ix)
            bfsi_output = bfs_output_helper(contig, bfs_func_list[i](root,
                                                                     target,e),
                                            example_el_nd_ix_2_nr)
            if not output_eq_or_rev(bfsi_output,
                                    correct_example_el_output[(root, target)]):
                bfs_problem = True  # assume example shortest paths unique
                print('  error, {0}({1}, {2}, example_el)'.format(
                        *((bfs_func_list[i].__name__,) + x)))
                print('    expected', correct_example_el_output[(root, target)])
                print('    actual', bfsi_output)
    if bfs_problem:
        errors.append('test_example bfs problem')

# Test and time with edgelist from file.
                
def test_file(edge_filename, bfs_func_list, bfs_contig, errors, verbose):
    if not edge_filename:
        return

    print('testing and timing all pairs', edge_filename)
    nr_bfs = len(bfs_func_list)

    el = read_edgelist(edge_filename)
    (el, el_arr, el_nd_ix_2_nr,
     el_nd_nr_2_ix) = make_contiguous_edgelist(el)

    # Test that the various methods agree on all pairs for graph from file.

    nodelist = sorted(el.keys())
    bfs_problem = False
    for i in range(1, nr_bfs):
        contig = bfs_contig[i]
        for x in itertools.combinations(nodelist, 2):
            (root, target, e, name) = bfs_input_helper(contig, x[0], x[1], el,
                                                       'el', el_arr,
                                                       el_nd_nr_2_ix)
            bfsi_output = bfs_output_helper(contig, bfs_func_list[i](root,
                                                                     target,e),
                                            el_nd_ix_2_nr)
            bfs1_output = bfs1(x[0], x[1], el)
            if verbose:
                print('  ', root, target, 'bfs1', bfs1_output)
            if not output_eq_or_rev(bfs1_output, bfsi_output):
                if ((bfs1_output is None) or (bfsi_output is None)
                    or (bfs1_output[0] != bfsi_output[0])):
                    bfs_problem = True
                if not verbose:
                    print('  ', root, target, 'bfs1', bfs1_output)
                print('  Inconsistent with')
                print('  ', root, target,
                      bfs_func_list[i].__name__, bfsi_output)
    if bfs_problem:
        errors.append('test_file bfs problem')
                    
    # Total times for each of various methods for all pairs for graph.

    for i in range(0, nr_bfs):
        contig = bfs_contig[i]
        t = 0
        for x in itertools.combinations(nodelist, 2):
            (root, target, e, name) = bfs_input_helper(contig, x[0], x[1], el,
                                                       'el', el_arr,
                                                       el_nd_nr_2_ix)
            test_str = ('{0}.{1}({2}, {3}, {4})'
                        + '').format(bfs_func_list[i].__module__,
                                     bfs_func_list[i].__name__,
                                     root, target, name)
            setup_str = ('import {0}; import gendata; import test; '
                         + 'el = gendata.read_edgelist('
                         + '"edgelist.txt"); (el, el_arr, el_nd_ix_2_nr, '
                         + 'el_nd_nr_2_ix) = '
                         + 'gendata.make_contiguous_edgelist(el); '
                         + '(root, target, e, name) = '
                         + 'test.bfs_input_helper({1}, '
                         + '{2}, {3}, el, "el", '
                         + 'el_arr, el_nd_nr_2_ix)'
                         ).format(bfs_func_list[i].__module__, contig,
                                  x[0], x[1])
            t = t + timeit.timeit(test_str, setup=setup_str, number=1)
        print('  {0} {1}'.format(bfs_func_list[i].__name__, t))

# Generate and time with tree graph.

def test_tree(degree, max_depth, bfs_func_list, bfs_contig, errors, verbose):
    print('generating tree graph')
    nr_bfs = len(bfs_func_list)

    (eltree, eltree_arr,
     eltree_nd_ix_2_nr, eltree_nd_nr_2_ix) = construct_tree_edgelist(
        degree, max_depth)
    nr_digits_per_level = int(math.ceil(math.log10(degree)))
    rightfill = '0' * (nr_digits_per_level - 1)
    eltree_root_nr   = int((rightfill + '1') * (max_depth + 1))
    eltree_target_nr = int((rightfill + '1') * (max_depth - 1)
                            + (rightfill + '2') + (rightfill + '1'))

    # Order makes a difference in timing; putting node with smaller edgelist
    # as root has been faster, though the bfs functions now check for that.

    nr_nodes = len(eltree.keys())
    nr_edges = 0
    for an_el in eltree_arr:
        nr_edges += len(an_el)
    nr_edges /= 2
    tree_condition_equal_sign = '==' if nr_nodes == nr_edges + 1 else "!="
    print(('timing degree {0}, max_depth {1}, nr nodes {2} '
           '{3} nr edges + 1').format(degree, max_depth, len(eltree.keys()),
                                      tree_condition_equal_sign))

    # Times for the various methods for tree graph.

    for i in range(0, nr_bfs):
        contig = bfs_contig[i]
        (root, target, e, name) = bfs_input_helper(contig, eltree_root_nr,
                                                   eltree_target_nr,
                                                   eltree, 'eltree',
                                                   eltree_arr,
                                                   eltree_nd_nr_2_ix)
        if verbose:
            test_str = ('output = {0}.{1}'
                        + '({2}, {3}, {4}); print('
                        + 'test.bfs_output_helper({5}, '
                        + 'output, eltree_nd_ix_2_nr))'
                        + ' ').format(bfs_func_list[i].__module__,
                                      bfs_func_list[i].__name__,
                                     root, target, name, contig)
        else:
            test_str = ('output = {0}.{1}'
                        + '({2}, {3}, {4})'
                        + '').format(bfs_func_list[i].__module__,
                                     bfs_func_list[i].__name__,
                                     root, target, name)
        setup_str = ('import {0}; import gendata; import test; '
                     + '(eltree, eltree_arr, eltree_nd_ix_2_nr, '
                     + 'eltree_nd_nr_2_ix) = '
                     + 'gendata.construct_tree_edgelist'
                     + '({1}, {2})'
                     + '').format(bfs_func_list[i].__module__,
                                  degree, max_depth)
        t = timeit.timeit(test_str, setup=setup_str, number=1)
        print('  {0} {1} {2} {3}'.format(bfs_func_list[i].__name__,
                                         eltree_root_nr, eltree_target_nr, t))

# Generate random graphs, choose nodes at random, test and time.

def test_random(nr_reps_random, nr_nodes_random, fraction_edges,
                bfs_func_list, bfs_contig, errors, verbose):
    if not (nr_reps_random > 0):
        return

    print('generating, testing, and timing random graphs')
    nr_bfs = len(bfs_func_list)

    ran_t = [0.0] * nr_bfs       # used to store total for all reps
    ran_pathlen = [0] * nr_bfs   # used to store total for all reps
    ran_output  = [(0, [0])] * nr_bfs # used to store result from current rep
    tot_act_nr_nodes = 0
    tot_act_nr_edges = 0
    tot_nr_no_paths  = 0
    bfs_problem      = False

    # Because of the time to generate, put the bfs method loop inside the
    # generation rep loop.

    for rep_nr in range(0, nr_reps_random):  # nr_reps_random <= 0 ignored
        (ran, ran_arr,
         ran_nd_ix_2_nr, ran_nd_nr_2_ix) = construct_random_graph(
            nr_nodes_random, fraction_edges)
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
            ran_root_nr = ran_nd_ix_2_nr[ran_root_ix]
            ran_target_nr = ran_nd_ix_2_nr[ran_target_ix]

        for i in range(0, nr_bfs):
            contig = bfs_contig[i]
            (root, target, e, name) = bfs_input_helper(contig, ran_root_nr,
                                                       ran_target_nr,
                                                       ran, 'ran', ran_arr,
                                                       ran_nd_nr_2_ix)
            def f():
                global global_bfs_output
                global_bfs_output = bfs_output_helper(
                    contig, bfs_func_list[i](root, target, e), ran_nd_ix_2_nr)
            ran_t[i] = ran_t[i] + timeit.timeit(f, number=1)
            if global_bfs_output is None:
                tot_nr_no_paths = tot_nr_no_paths + 1
            else:
                ran_pathlen[i] = ran_pathlen[i] + global_bfs_output[0]
                ran_output[i] = global_bfs_output
                if not output_eq_or_rev(ran_output[0], ran_output[i]):
                    if ((ran_output[0] is None) or (ran_output[i] is None)
                        or (ran_output[0][0] != ran_output[i][0])):
                        bfs_problem = True
                    print(('  Inconsistency random graph {0}, {1}'
                           + '').format(bfs_func_list[0].__name__,
                                        bfs_func_list[i].__name__))
                    print('  ', ran_output[0])
                    print('  ', ran_output[i])
    if bfs_problem:
        errors.append('test_random bfs problem')

    # Display random graphs timing.

    if nr_reps_random > 0:  # nr_reps_random <= 0 ignored
        print('nr nodes {0}, fraction edges {1}, nr edges {2}'.format(
                tot_act_nr_nodes / float(nr_reps_random),
                fraction_edges,
                0.5 * tot_act_nr_edges / float(nr_reps_random)))
        # prints the number of undirected edges
        print(('nr reps {0}, mean path length {1}, no path (all reps, bfs) {2}'
               + '').format(nr_reps_random,
                            ran_pathlen[i] / float(nr_reps_random),
                            tot_nr_no_paths))
        for i in range(0, nr_bfs):
            if verbose:
                print('  {0} output'.format(bfs_func_list[i].__name__,),
                      ran_output[i])
            print(('  {0} mean time {1}'
                   + '').format(bfs_func_list[i].__name__,
                                ran_t[i] / float(nr_reps_random)))
    
# Print usage with default values.

def usage(d_edge_filename, d_degree, d_max_depth,
          d_nr_reps_random, d_nr_nodes_random, d_fraction_edges):
    print(
        """
Usage: python test.py [-e <edge_file>]
                      [-d <degree>]
                      [-m <max_depth>]
                      [-r <nr_reps_random>]
                      [-n <nr_nodes_random>]
                      [-f <fraction_edges>]
                      [-v] [-h]
  long versions:      [--edge_file <edge_file>]
                      [--degree <degree>]
                      [--max_depth <max_depth>]
                      [--nr_reps_random <nr_reps_random>]
                      [--nr_nodes_random <nr_nodes_random>]
                      [--fraction_edges <fraction_edges>]
                      [--verbose] [--help]
  defaults: python test.py -e {0} -d {1} -m {2} -r {3} -n {4} -f {5}
  If -h is present, just print this info.
""".format(d_edge_filename, d_degree, d_max_depth,
           d_nr_reps_random, d_nr_nodes_random, d_fraction_edges))

# Exits (doesn't return) if error or help requested.

def get_cmdline_options(argv, edge_filename, degree, max_depth,
                        nr_reps_random, nr_nodes_random, fraction_edges,
                        verbose):
    # save default values
    d_edge_filename   = edge_filename
    d_degree          = degree
    d_max_depth       = max_depth
    d_nr_reps_random  = nr_reps_random
    d_nr_nodes_random = nr_nodes_random
    d_fraction_edges  = fraction_edges

    global invalid_input_exit_code

    if isinstance(argv, str):
        argv = argv.split(' ')
    try:
        (opts, args) = getopt.getopt(argv, 'e:d:m:r:n:f:vh',
                                     ['edge_file', 'degree=', 'max_depth=',
                                      'nr_reps_random=',
                                      'nr_nodes_random=',
                                      'fraction_edges=',
                                      'verbose', 'help'])
    except getopt.GetoptError as err:
        print(str(err))
        usage(d_edge_filename, d_degree, d_max_depth,
              d_nr_reps_random, d_nr_nodes_random, d_fraction_edges)
        sys.exit(invalid_input_exit_code)

    for (opt, arg) in opts:
        if opt in ('-e', '--edge_file'):
            edge_filename = arg
        elif opt in ('-d', '--degree'):
            try:
                arg_degree = int(arg)
                if arg_degree >= 2:
                    degree = arg_degree
                else:
                    print('degree must be an integer at least 2')
                    usage(d_edge_filename, d_degree, d_max_depth,
                          d_nr_reps_random, d_nr_nodes_random, d_fraction_edges)
                    sys.exit(invalid_input_exit_code)
            except ValueError:
                print('degree must be an integer at least 2')
                usage(d_edge_filename, d_degree, d_max_depth,
                      d_nr_reps_random, d_nr_nodes_random, d_fraction_edges)
                sys.exit(invalid_input_exit_code)
        elif opt in ('-m', '--max_depth'):
            try:
                arg_max_depth = int(arg)
                if arg_max_depth >= 2:
                    max_depth = arg_max_depth
                else:
                    print('max_depth must be an integer at least 2')
                    usage(d_edge_filename, d_degree, d_max_depth,
                          d_nr_reps_random, d_nr_nodes_random, d_fraction_edges)
                    sys.exit(invalid_input_exit_code)
            except ValueError:
                print('max_depth must be an integer at least 2')
                usage(d_edge_filename, d_degree, d_max_depth,
                      d_nr_reps_random, d_nr_nodes_random, d_fraction_edges)
                sys.exit(invalid_input_exit_code)
        elif opt in ('-r', '--nr_reps_random'):
            try:
                arg_nr_reps_random = int(arg)
                nr_reps_random = arg_nr_reps_random
            except ValueError:
                print('nr_reps_random must be an integer')
                usage(d_edge_filename, d_degree, d_max_depth,
                      d_nr_reps_random, d_nr_nodes_random, d_fraction_edges)
                sys.exit(invalid_input_exit_code)
        elif opt in ('-n', '--nr_nodes_random'):
            try:
                arg_nr_nodes_random = int(arg)
                if arg_nr_nodes_random >= 2:
                    nr_nodes_random = arg_nr_nodes_random
                else:
                    print('nr_nodes_random must be an integer at least 2')
                    usage(d_edge_filename, d_degree, d_max_depth,
                          d_nr_reps_random, d_nr_nodes_random, d_fraction_edges)
                    sys.exit(invalid_input_exit_code)
            except ValueError:
                print('nr_nodes_random must be an integer at least 2')
                usage(d_edge_filename, d_degree, d_max_depth,
                      d_nr_reps_random, d_nr_nodes_random, d_fraction_edges)
                sys.exit(invalid_input_exit_code)
        elif opt in ('-f', '--fraction_edges'):
            try:
                arg_fraction_edges = float(arg)
                if arg_fraction_edges > 0.0 and arg_fraction_edges < 1.0:
                    fraction_edges = arg_fraction_edges
                else:
                    print('fraction_edges must be between '
                          + '0.0 and 1.0 exclusive')
                    usage(d_edge_filename, d_degree, d_max_depth,
                          d_nr_reps_random, d_nr_nodes_random, d_fraction_edges)
                    sys.exit(invalid_input_exit_code)
            except ValueError:
                print('fraction_edges must be between 0.0 and 1.0 exclusive')
                usage(d_edge_filename, d_degree, d_max_depth,
                      d_nr_reps_random, d_nr_nodes_random, d_fraction_edges)
                sys.exit(invalid_input_exit_code)
        elif opt in ('-v', '--verbose'):
            verbose = True
        elif opt in ('-h', '--help'):
            usage(d_edge_filename, d_degree, d_max_depth,
                  d_nr_reps_random, d_nr_nodes_random, d_fraction_edges)
            sys.exit(0)

    return (edge_filename, degree, max_depth, nr_reps_random, nr_nodes_random,
            fraction_edges, verbose)

def test(argv,
         example_err=False, file_err=False, tree_err=False, ran_err=False):
    global global_bfs_output

    edge_filename   = ''
    degree          = 3  # must be at least 2
    max_depth       = 7  # must be at least 2
    nr_reps_random  = 0  # because potentially time-consuming
    nr_nodes_random = 10000
    fraction_edges  = 0.005
    verbose         = False
    (edge_filename, degree, max_depth, nr_reps_random, nr_nodes_random,
     fraction_edges, verbose) = get_cmdline_options(argv,
                                                    edge_filename,
                                                    degree,
                                                    max_depth,
                                                    nr_reps_random,
                                                    nr_nodes_random,
                                                    fraction_edges,
                                                    verbose)
    bfs_func_list = [bfs1, bfs2]
    bfserr_func_ix = 1
    bfs_func_list_save = list(bfs_func_list)
    bfs_contig = [False, False]
    errors = []

    if example_err:
        bfs_func_list[bfserr_func_ix] = bfserr_node
    test_example(bfs_func_list, bfs_contig, errors, verbose)
    if example_err:
        bfs_func_list[bfserr_func_ix] = bfs_func_list_save[bfserr_func_ix]

    if file_err:
        bfs_func_list[bfserr_func_ix] = bfserr_none
    test_file(edge_filename,
              bfs_func_list, bfs_contig, errors, verbose)
    if file_err:
        bfs_func_list[bfserr_func_ix] = bfs_func_list_save[bfserr_func_ix]

    if tree_err:
        bfs_func_list[bfserr_func_ix] = bfserr_none
    test_tree(degree, max_depth,
              bfs_func_list, bfs_contig, errors, verbose)  # it doesn't test...
    if tree_err:
        bfs_func_list[bfserr_func_ix] = bfs_func_list_save[bfserr_func_ix]

    if ran_err:
        bfs_func_list[bfserr_func_ix] = bfserr_len
    test_random(nr_reps_random, nr_nodes_random, fraction_edges,
                bfs_func_list, bfs_contig, errors, verbose)
    if ran_err:
        bfs_func_list[bfserr_func_ix] = bfs_func_list_save[bfserr_func_ix]

    if errors:
        print(errors)
    return errors

def main(argv):
    return test(argv)

if __name__ == '__main__':
    main(sys.argv[1:])

""" From interactive python prompt:
"""
