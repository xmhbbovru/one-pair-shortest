README.md rev. 12 January 2014 by Stuart Ambler.
Copyright (c) 2014 Stuart Ambler.
Distributed under the Boost License in the accompanying file LICENSE.

# Single Pair Shortest Path Algorithms for Unweighted Undirected Graphs

- bfs0.py         is close to my first attempt.
- bfs1.py         is slightly optimized.
- bfs2.py         is bidirectional, going from both ends toward the middle.
- bfs3.py         like bfs2 but matches a whole level at once
- gendata.py      generates test data, trees and random graphs.
- test.py         tests the algorithms.
- shortestpath.py contains all the above .py files in one file, slightly changed
                  for execution from one file
- edgelist.txt is the edgelist of a graph used by some of the tests.

Tested with python 2.7.5 and 3.3.2.

References used include Skiena's The Algorithm Design Manual Second Edition,
pages 162-166, and <http://networkx.lanl.gov/_modules/networkx/algorithms/shortest_paths/unweighted.html>.
