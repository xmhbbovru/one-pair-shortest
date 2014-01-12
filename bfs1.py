#!/usr/bin/env python
# bfs1.py rev 11 Jan 2014 Stuart Ambler
# Second try at single pair shortest path algorithm via bread first search.
# Copyright (c) 2014 Stuart Ambler.
# Distributed under the Boost License in the accompanying file LICENSE.

from collections import deque

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
