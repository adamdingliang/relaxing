#!/usr/bin/env python3

import os
import sys
import argparse


def main():
    """ Handles arguments and invokes the driver function.
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-v', '--verbose', help='enable verbose mode.', action='store_true')
    parser.add_argument('-d', '--debug', help='enable debug mode.', action='store_true')
    parser.add_argument('--dry-run', help='enable dry-run mode.', action='store_true')

    args = parser.parse_args()
    test()
    return


def test():
    for i in range(0, 5):
        print(i)


if __name__ == '__main__':
    main()
