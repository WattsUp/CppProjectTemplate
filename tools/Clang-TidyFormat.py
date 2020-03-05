#!/usr/bin/env python
""" A wrapper script for clang-format and clang-tidy that checks all source
files for formatting/static analysis and returns a list of files to fix.
Optionally checks only changed files. Optionally automatically fixes the
errors.
"""

import argparse
import multiprocessing
import os
import queue
import re
import subprocess
import sys
import threading
import traceback


def getFileList(git, pattern):
  """
  Get a list of all files (caring for gitignore) that match the regex pattern
  """
  files = []
  result = subprocess.Popen(
      [git, "ls-files", "--exclude-standard", "--modified", "--others", "--cached"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
  if result.communicate()[0] is not None:
    for filename in result.communicate()[0].split('\n'):
      if re.match(pattern, filename) and filename not in files:
        files.append(filename)
  return files


def getChangedFileList(git, pattern, indexOnly):
  """
  Get a list of all modified/added files (caring for gitignore) that match the regex pattern
  indexOnly will only check files added to the index (git add FILE)
  """
  files = []
  result = subprocess.Popen(
      [git, "diff-index", "--cached", "--name-only", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
  if result.communicate()[0] is not None:
    for filename in result.communicate()[0].split('\n'):
      if re.match(pattern, filename) and filename not in files:
        files.append(filename)

  if(indexOnly):
    return files

  result = subprocess.Popen(
      [git, "ls-files", "--exclude-standard", "--modified", "--others"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
  if result.communicate()[0] is not None:
    for filename in result.communicate()[0].split('\n'):
      if re.match(pattern, filename) and filename not in files:
        files.append(filename)
  return files


def runClang(clangFormat, clangTidy, buildPath, queue, lock, failedCommands,
             toFormatFiles, fix, quiet, formatting, tidying, headerFilter):
  while True:
    name = queue.get()

    if tidying:
      cmd = [clangTidy, "-p", buildPath, "-quiet", "-header-filter=" + headerFilter]
      if fix:
        cmd.append("-fix")
      cmd.append(name)

      try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
      except Exception:
        queue.task_done()
        failedCommands.append(' '.join(cmd))
        continue

      output, err = proc.communicate()
      if proc.returncode != 0:
        failedCommands.append(' '.join(cmd))
      with lock:
        if fix and not quiet:
          sys.stdout.write(' '.join(cmd) + '\n')
        else:
          sys.stdout.write(' '.join(cmd) + '\n' + output)
        if len(err) > 0:
          sys.stdout.flush()
          sys.stderr.write(err)

    if formatting:
      cmd = [clangFormat, "-style=file"]
      if fix:
        cmd.append("-i")
      else:
        cmd.append("-output-replacements-xml")
      cmd.append(name)

      try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
      except Exception:
        queue.task_done()
        failedCommands.append(' '.join(cmd))
        continue

      output, err = proc.communicate()
      if proc.returncode != 0:
        failedCommands.append(' '.join(cmd))
      with lock:
        if fix and not quiet:
          sys.stdout.write(' '.join(cmd) + '\n')
        else:
          if "<replacement " in output:
            toFormatFiles.append(name)
        if len(err) > 0:
          sys.stdout.flush()
          sys.stderr.write(err)
    queue.task_done()


def main():
  parser = argparse.ArgumentParser(description='Run clang-format against all or changed files,'
                                   ' and output which ones need formatting. Optionally, automatically fix formatting')
  parser.add_argument('--format', action='store_true', default=False,
                      help='check clang-format')
  parser.add_argument('--tidy', action='store_true', default=False,
                      help='check clang-tidy')
  parser.add_argument('--clang-format-binary', metavar='PATH',
                      default='clang-format',
                      help='path to clang-format binary')
  parser.add_argument('--clang-tidy-binary', metavar='PATH',
                      default='clang-tidy',
                      help='path to clang-tidy binary')
  parser.add_argument('--git-binary', metavar='PATH',
                      default='git',
                      help='path to git binary')
  parser.add_argument('--regex', metavar='PATTERN', default=r'.*\.(cpp|cc|c\+\+|cxx|c|h|hpp)$',
                      help='custom pattern selecting file paths to check '
                      '(case insensitive). Ignore third-party and lib files: '
                      '"^((?!(third-party|lib)).)*\\.(cpp|cc|c\\+\\+|cxx|c|h|hpp)$"')
  parser.add_argument('-j', type=int, default=0,
                      help='number of clang-format instances to be run in parallel.')
  parser.add_argument('-a', action='store_true', default=False,
                      help='check all user files, overrides --index')
  parser.add_argument('-p', metavar='PATH', default="./build/",
                      help='Path used to read a compile command database.')
  parser.add_argument('--index', action='store_true', default=False,
                      help='only check files added to the index')
  parser.add_argument('--fix', action='store_true', default=False,
                      help='apply formatting fixes')
  parser.add_argument('--quiet', action='store_true', default=False,
                      help='only output return codes and exceptions')

  argv = sys.argv[1:]
  args = parser.parse_args(argv)

  if not args.tidy and not args.format:
    parser.print_help()
    sys.exit(0)

  try:
    subprocess.check_call(
        [args.git_binary, '--version'], stdout=subprocess.DEVNULL)
  except BaseException:
    print(
        'Unable to run git. Is git binary correctly specified?',
        file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)

  if args.format:
    try:
      subprocess.check_call(
          [args.clang_format_binary, '--version'], stdout=subprocess.DEVNULL)
    except BaseException:
      print(
          'Unable to run clang format. Is clang-format binary correctly specified?', file=sys.stderr)
      traceback.print_exc()
      sys.exit(1)

  if args.tidy:
    try:
      subprocess.check_call(
          [args.clang_tidy_binary, '--version'], stdout=subprocess.DEVNULL)
    except BaseException:
      print(
          'Unable to run clang tidy. Is clang-tidy binary correctly specified?', file=sys.stderr)
      traceback.print_exc()
      sys.exit(1)

  files = []
  if args.a:
    files = getFileList(args.git_binary, re.compile(args.regex))
  else:
    files = getChangedFileList(
        args.git_binary, re.compile(args.regex), args.index)

  headerFilter = "$(project|common)"

  returnCode = 0
  maxTasks = args.j
  if maxTasks == 0:
    maxTasks = multiprocessing.cpu_count()

  try:
    taskQueue = queue.Queue(maxTasks)
    failedCommands = []
    toFormatFiles = []
    lock = threading.Lock()
    for _ in range(maxTasks):
      t = threading.Thread(target=runClang,
                           args=(args.clang_format_binary, args.clang_tidy_binary, args.p,
                                 taskQueue, lock, failedCommands, toFormatFiles, args.fix,
                                 args.quiet, args.format, args.tidy, headerFilter))
      t.daemon = True
      t.start()

    # Fill the queue with files.
    for name in files:
      taskQueue.put(name)

    # Wait for all threads to be done.
    taskQueue.join()
    if len(failedCommands):
      returnCode = 2
      print("Failed executing commands:")
      for cmd in failedCommands:
        print(cmd)

    if len(toFormatFiles):
      returnCode = 1
      if not args.quiet:
        print("Need to format:")
        for file in toFormatFiles:
          print(file)
    elif not args.quiet and args.format:
      print("No files need to be formatted")

  except KeyboardInterrupt:
    print('\nCtrl-C detected, goodbye.')
    os.kill(0, 9)

  sys.exit(returnCode)


if __name__ == "__main__":
  main()
