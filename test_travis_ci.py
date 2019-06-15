#!/usr/bin/env python3
"""
"""

import os
import unittest
from travis_ci.travis_ci import test


class TestSomething(unittest.TestCase):
    def setUp(self):
        pass

    def test_travis_ci(self):
        test()
        return

    def tearDown(self):
        pass


if __name__ == '__main__':
    print(os.getcwd())
    unittest.main()

