#!/usr/bin/env python
# bfs2.py rev 15 Jan 2014 Stuart Ambler
# Third try at single pair shortest path algorithm via breadth first search.
# Copyright (c) 2014 Stuart Ambler.
# Distributed under the Boost License in the accompanying file LICENSE.

# Finds shortest path from root to target given edgelist, using breadth first
# search, adapted from bfs1, but moves from both ends to the middle, and uses
# ideas (primarily doing a whole level at a time) from http://
# networkx.lanl.gov/_modules/networkx/algorithms/shortest_paths/unweighted.htm .
# Unlike bfs0 and bfs1, bfs2 expects the edgelist to be a list of lists, indexed
# by node, rather than a dictionary indexed by node number and values lists.
# Returns (path_len, path), path given as list of nodes, or None if no path.

# When starting to write this, I added a note to use optimizations assuming the
# path is much smaller than 1/2 the size of the edgelist, but it looks like
# none occurred to me.

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
                    # Could just check in t_level nodes (see LaTeX proof
                    # of method), but in practice it didn't really seem to help.
                    if new_node in parent_t:
                        match_node = new_node
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
                    # Could just check in r_level nodes (see LaTeX proof
                    # of method), but in practice it didn't really seem to help.
                    if new_node in parent_r:
                        match_node = new_node
                        break
                if match_node is not None:
                    break

    if match_node is not None:
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
