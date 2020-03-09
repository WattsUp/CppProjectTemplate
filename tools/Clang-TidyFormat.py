#!/usr/bin/env python
""" A wrapper script for clang-format and clang-tidy that checks all source
files for formatting/static analysis and returns a list of files to fix.
Optionally checks only changed files. Optionally automatically fixes the
errors.
"""

import argparse
import json
import multiprocessing
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import traceback


def makeAbsolute(f, directory):
  if os.path.isabs(f):
    return os.path.abspath(f)
  return os.path.normpath(os.path.join(directory, f))


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


def runTidy(clangTidy, queue, lock, failedCommands,
            buildPath, headerFilter, tmpdir, quiet):
  while True:
    name = queue.get()

    cmd = [
        clangTidy,
        "-p",
        buildPath,
        "-header-filter=" + headerFilter]
    if tmpdir is not None:
      cmd.append('-export-fixes')
      # Get a temporary file. We immediately close the handle so clang-tidy can
      # overwrite it.
      (handle, tmpfile) = tempfile.mkstemp(suffix='.yaml', dir=tmpdir)
      os.close(handle)
      cmd.append(tmpfile)
    cmd.append(name)

    try:
      proc = subprocess.Popen(
          cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except Exception:
      queue.task_done()
      failedCommands.append(' '.join(cmd))
      continue

    output = proc.communicate()[0]
    if proc.returncode != 0:
      failedCommands.append(' '.join(cmd))
    with lock:
      if not quiet:
        sys.stdout.write(' '.join(cmd) + '\n' + output)
    queue.task_done()


def runFormat(clangFormat, queue, lock, failedCommands,
              toFormatFiles, fix, quiet):
  while True:
    name = queue.get()

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


def findCompilationDatabase(path):
  """Adjusts the directory until a compilation database is found."""
  result = './'
  while not os.path.isfile(os.path.join(result, path)):
    if os.path.realpath(result) == '/':
      print('Error: could not find compilation database.')
      sys.exit(1)
    result += '../'
  return os.path.realpath(result)


def main():
  parser = argparse.ArgumentParser(description='Run clang-format and/or clang-tidy against all or changed files,'
                                   ' and output which ones need fixing. Optionally, automatically fix')
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
  parser.add_argument('--clang-apply-replacements-binary', metavar='PATH',
                      default='clang-apply-replacements',
                      help='path to clang-tidy binary')
  parser.add_argument('--git-binary', metavar='PATH',
                      default='git',
                      help='path to git binary')
  parser.add_argument('--regex', metavar='PATTERN', default=r'.*\.(cpp|cc|c\+\+|cxx|c|h|hpp)$',
                      help='custom pattern selecting file paths to check '
                      '(case insensitive). Ignore third-party and lib files: '
                      '"^((?!(third-party|lib)).)*\\.(cpp|cc|c\\+\\+|cxx|c|h|hpp)$"')
  parser.add_argument('--header-filter', metavar='PATTERN', default="^[a-zA-Z]",
                      help='custom header filter passed to clang-tidy. Default ^[a-zA-Z]'
                      ' checks all user files, ignoreing libraries (..\\libraries\\.*)')
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
    print("Need --tidy and/or --format flag")
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

  returnCode = 0
  maxTasks = args.j
  if maxTasks == 0:
    maxTasks = multiprocessing.cpu_count()

  database = json.load(open(os.path.join(args.p, "compile_commands.json")))
  compileCommandFiles = [makeAbsolute(entry['file'], entry['directory'])
                         for entry in database]

  tmpdir = None
  if args.fix:
    try:
      subprocess.check_call(
          [args.clang_apply_replacements_binary, '--version'], stdout=subprocess.DEVNULL)
    except BaseException:
      print(
          'Unable to run clang apply replacements. Is clang-apply-replacements binary'
          ' correctly specified?', file=sys.stderr)
      traceback.print_exc()
      if tmpdir:
        shutil.rmtree(tmpdir)
      sys.exit(1)
    tmpdir = tempfile.mkdtemp()

  try:
    if args.tidy:
      taskQueue = queue.Queue(maxTasks)
      failedCommands = []
      lock = threading.Lock()
      for _ in range(maxTasks):
        t = threading.Thread(target=runTidy,
                             args=(args.clang_tidy_binary, taskQueue, lock, failedCommands,
                                   args.p, args.header_filter, tmpdir, args.quiet))
        t.daemon = True
        t.start()

      # Fill the queue with files.
      for name in files:
        if os.path.abspath(name) in compileCommandFiles:
          taskQueue.put(name)

      # Wait for all threads to be done.
      taskQueue.join()
      if len(failedCommands):
        returnCode = 2
        print("Failed executing commands:")
        for cmd in failedCommands:
          print(cmd)
    
    if args.fix:
      if not args.quiet:
        print("Applying tidy fixes...")

      try:
        cmd = [args.clang_apply_replacements_binary]
        cmd.append("-format")
        cmd.append("-style=file")
        cmd.append(tmpdir)
        subprocess.call(cmd)
      except:
        print('Error applying fixes.\n', file=sys.stderr)
        traceback.print_exc()
        returnCode=1

    if args.format:
      taskQueue = queue.Queue(maxTasks)
      failedCommands = []
      toFormatFiles = []
      lock = threading.Lock()
      for _ in range(maxTasks):
        t = threading.Thread(target=runFormat,
                             args=(args.clang_format_binary, taskQueue, lock, failedCommands,
                                   toFormatFiles, args.fix, args.quiet))
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
    if tmpdir:
      shutil.rmtree(tmpdir)
    os.kill(0, 9)

  if tmpdir:
    shutil.rmtree(tmpdir)
  sys.exit(returnCode)


if __name__ == "__main__":
  main()
