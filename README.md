README.md rev. 28 January 2014 by Stuart Ambler.
Copyright (c) 2014 Stuart Ambler.
Distributed under the Boost License in the accompanying file LICENSE.

# Two Single Pair Shortest Path Algorithms for Unweighted Undirected Graphs

- bfs1.py         unidirectional breadth first search
- bfs2.py         bidirectional bfs, going from both ends toward the middle
- bfserr.py       methods that return errors, for testing the test framework
- edgelist.txt    contains the edgelist of a graph used by tests that find
                  shortest paths between all node pairs in it
- gendata.py      generates test data: a small example, trees, and random
                  graphs
- rununittest.py  runs unit tests (mostly test.test with various arguments)
                  and gets coverage; using nose
- test.py         tests and times the algorithms

Tested with python 2.7.5+, coverage 3.6; and python 3.3.2+, coverage 3.7.1.
To test,

- python -m test                   to choose test.test arguments
- python -m rununittest            to run suite of tests
- python -m coverage html          to format coverage results of the suite
- (rm -r htmlcov before running coverage again)
- (rm .coverage  before switch between 2.7 and 3.3)

References used include Skiena's The Algorithm Design Manual Second Edition,
pages 162-166, and <http://networkx.lanl.gov/_modules/networkx/algorithms/shortest_paths/unweighted.html>.
