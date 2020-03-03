#!/usr/bin/env python
""" A wrapper script for clang-format that checks all source files for
formatting and returns a list of files. Optionally executes on changed files
only (git integration). Optionally automatically fixes the formatting errors.
"""

import argparse
import glob
import re
import sys


def getFileList(pattern):
    files = []
    # "git ls-files --exclude-standard --modified --others --cached"
    for filename in glob.iglob('**/*', recursive=True):
        if re.match(pattern, filename):
            files.append(filename)
    return files

def getChangedFileList(pattern):
    files = []
    # "git diff-index --cached --name-only HEAD"
    # "git ls-files --exclude-standard --modified --others"
    return files


def main():
    parser = argparse.ArgumentParser(description='Run clang-format against all or changed files,'
                                     ' and output which ones need formatting. Optionally, automatically fix formatting')
    parser.add_argument('--clang-format-binary', metavar='PATH',
                        default='clang-format',
                        help='path to clang-format binary')
    parser.add_argument('--git-binary', metavar='PATH',
                        default='git',
                        help='path to git binary')
    parser.add_argument('--regex', metavar='PATTERN', default=r'.*\.(cpp|cc|c\+\+|cxx|c|h|hpp)$',
                        help='custom pattern selecting file paths to check '
                        '(case insensitive)')
    parser.add_argument('-j', type=int, default=4,
                        help='number of clang-format instances to be run in parallel.')
    parser.add_argument('-a', action='store_true', default=False,
                        help='check all user files (not set: only changed files)')
    parser.add_argument('--fix', action='store_true', default=False,
                        help='apply suggested fixes')

    argv = sys.argv[1:]
    args = parser.parse_args(argv)
    print(args)
    if args.a:
        for filename in getFileList(re.compile(args.regex)):
            print(filename)
    else:
        for filename in getChangedFileList(re.compile(args.regex)):
            print(filename)


if __name__ == "__main__":
    main()
