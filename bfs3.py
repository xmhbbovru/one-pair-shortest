#!/usr/bin/env python
# bfs3.py rev 12 Jan 2014 Stuart Ambler
# Fourth try at single pair shortest path algorithm via breadth first search.
# It was usually slower than the third and seemed to offer no advantage.
# Copyright (c) 2014 Stuart Ambler.
# Distributed under the Boost License in the accompanying file LICENSE.

import numpy

# Returns a matching node, if any, from the two lists of nodes (integers).
# numbers.  However, bfs3 using this implementation of find_match, turned
# out slower in a few tests, than bfs2.  Perhaps it would be different in C.
# The scratch argument is just for compatibility with the other implementation.
    
#def find_match(list1, list2, scratch):
#    # This will sort the lists in place; ok with intended use.
#    list1.sort()
#    list2.sort()
#    len1 = len(list1)
#    len2 = len(list2)
#    i1 = 0
#    i2 = 0
#    while (i1 < len1) and (i2 < len2):
#        curr1 = list1[i1]
#        curr2 = list2[i2]
#        if curr1 == curr2:
#            return curr1
#        elif curr1 < curr2:
#            i1 = i1 + 1
#        else:
#            i2 = i2 + 1
#    return None

# Another find_match implementation, which takes extra memory and might cause
# memory cache problems (or might not).  A previous version of this
# implementation was the reason for switchin in bfs2 from edgelist as dictionary
# to edgelist as array indexed by node numbers.  This was usually slower than
# bfs2 until using numpy here.  find_match expects scratch to be a numpy array,
# and expects values of list1 and list2 to be in the range 0..len(scratch)-1.

def find_match(list1, list2, scratch):
    if len(list1) < len(list2):
        (list1, list2) = (list2, list1)
    match_node = None
    for node in list2:
        scratch[node] = True
    for node in list1:
        if scratch[node]:
            match_node = node
            break
    for node in list2:
        scratch[node] = False
    return match_node

# Finds shortest path from root to target given edgelist, using breadth first
# search, adapted from bfs2 using ideas from a previous version of bfs2.  The
# difference is doing all the matching for a level at one time, rather than as
# the nodes in it are encountered.
# Returns (path_len, path), path given as list of nodes, or None if no path.

#@profile  # for line_profiler
def bfs3(root, target, edgelist):
    if (root == target):
        return (0, [root])
    nr_nodes = len(edgelist)
    if (nr_nodes <= 0
        or root < 0 or root >= nr_nodes
        or target < 0 or target >= nr_nodes):
        return None

    scratch = numpy.zeros(nr_nodes, dtype=bool)

    if len(edgelist[root]) > len(edgelist[target]):
        (root, target) = (target, root)
 
    parent_r = { root:None }
    parent_t = { target:None }
    r_level_nodes = [root]
    t_level_nodes = [target]

    match_node = None

    # Process a whole level for r or t, before possibly switching.
    while r_level_nodes and t_level_nodes:
        if len(r_level_nodes) <= len(t_level_nodes):
            level_nodes = r_level_nodes
            r_level_nodes = []
            for node in level_nodes:
                for new_node in edgelist[node]:
                    if new_node not in parent_r:
                        parent_r[new_node] = node
                        r_level_nodes.append(new_node)
                        parent_r[new_node] = node
            match_node = find_match(r_level_nodes, parent_t.keys(), scratch)
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
            match_node = find_match(t_level_nodes, parent_r.keys(), scratch)
            if match_node is not None:
                break
 
    if match_node != None:
        accum_r = [match_node]
        p = parent_r[match_node]
        while p is not None:
            accum_r.append(p)
            p = parent_r[p]
        accum_r.reverse()

        accum_t = []
        p = parent_t[match_node]
        while p is not None:
            accum_t.append(p)
            p = parent_t[p]

        accum = accum_r if accum_t is None else accum_r + accum_t
        return (len(accum) - 1, accum)
    else:
        return None
