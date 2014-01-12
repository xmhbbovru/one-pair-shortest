#!/usr/bin/env python
# bfs0.py rev 11 Jan 2014 Stuart Ambler
# First try at single pair shortest path algorithm via bread first search.
# Copyright (c) 2014 Stuart Ambler.
# Distributed under the Boost License in the accompanying file LICENSE.

from collections import deque

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
