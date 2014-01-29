#!/usr/bin/env python
# rununittest.py rev 28 Jan 2014 Stuart Ambler
# Uses unittest to test a number of command-line argument combinations
# of test.py, plus a few other tests.
# Copyright (c) 2014 Stuart Ambler.
# Distributed under the Boost License in the accompanying file LICENSE.

from __future__ import print_function
import sys
import unittest

class TestTest(unittest.TestCase):
    """ unittest derivative for test frameworks.
    """
    def setUp(self):
        pass
    def tearDown(self):
        pass    
    def test_overall(self):
        """ Test via test frameworks.
        """
        import bfs1
        import bfs2
        import bfserr
        import test
        self.assertEqual([], test.main(''))
        self.assertEqual([], test.main('-v'))
        self.assertEqual([], test.main('-e edgelist.txt'))
        self.assertEqual([], test.main('-e edgelist.txt -v'))
        self.assertEqual([], test.main('-d 5 -m 7'))
        self.assertEqual([], test.main('-d 5 -m 7 -v'))
        self.assertEqual([], test.main('-r 1 -n 8000 -f 0.001'))
        self.assertEqual([], test.main('-r 1 -n 8000 -f 0.001 -v'))
        self.assertEqual([], test.main('-r 1 -n 1000 -f 0.001'))
        self.assertNotEqual([], test.test('',                example_err=True))
        self.assertNotEqual([], test.test('-e edgelist.txt', file_err=True))
        self.assertEqual([], test.test('', tree_err=True))  # it doesn't test
        self.assertNotEqual([], test.test('-r 1',            ran_err=True))
        self.assertRaisesRegexp(SystemExit, '0',
                                test.main, '-h')
        self.assertRaisesRegexp(SystemExit, str(test.invalid_input_exit_code),
                                test.main, '--invalid_option')
        self.assertRaisesRegexp(SystemExit, str(test.invalid_input_exit_code),
                                test.main, '-d a')
        self.assertRaisesRegexp(SystemExit, str(test.invalid_input_exit_code),
                                test.main, '-d -1')
        self.assertRaisesRegexp(SystemExit, str(test.invalid_input_exit_code),
                                test.main, '-m a')
        self.assertRaisesRegexp(SystemExit, str(test.invalid_input_exit_code),
                                test.main, '-m -1')
        self.assertRaisesRegexp(SystemExit, str(test.invalid_input_exit_code),
                                test.main, '-r a')
        self.assertRaisesRegexp(SystemExit, str(test.invalid_input_exit_code),
                                test.main, '-n a')
        self.assertRaisesRegexp(SystemExit, str(test.invalid_input_exit_code),
                                test.main, '-n -1')
        self.assertRaisesRegexp(SystemExit, str(test.invalid_input_exit_code),
                                test.main, '-f a')
        self.assertRaisesRegexp(SystemExit, str(test.invalid_input_exit_code),
                                test.main, '-f -1')

        self.assertEqual((0, [1]), bfs1.bfs1(1, 1, dict()))
        self.assertEqual((0, [1]), bfs2.bfs2(1, 1, dict()))
        self.assertIsNone(bfserr.bfserr_none(1, 1, dict()))
        self.assertNotEqual(0, bfserr.bfserr_len(1, 1, dict())[0])
        self.assertEqual(0, bfserr.bfserr_len(0, 1, dict())[0])
        self.assertNotEqual([1], bfserr.bfserr_node(1, 1, dict())[1])

        self.assertIsNone(bfs1.bfs1(0, 1, dict()))
        self.assertIsNone(bfserr.bfserr_none(0, 1, dict()))
        self.assertIsNone(bfserr.bfserr_node(0, 1, dict()))

        self.assertEqual((1, 0, [], 'el_arr'),
                         test.bfs_input_helper(True, 3, 4, [], 'el', [],
                                               {4:0, 3:1}))
        self.assertIsNone(test.bfs_output_helper(True, None, dict()))
        self.assertEqual((1, [3, 4]), test.bfs_output_helper(True,
                                                             (1, [1, 0]),
                                                             {0:4, 1:3}))

        self.assertNotEqual([], test.test_example([], [], [], False, True))

def main():
    """ 
    Args:    none
    Returns: exit code
    Usage:   python -m rununittest
    """
    # Can use unittest or nose; nose here, which allows --with-coverage.
    import nose
    return nose.run(argv=[sys.argv[0], "-s", "--with-coverage", "rununittest"])

if __name__ == "__main__":
    main ()
