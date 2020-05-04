#!/usr/bin/env python
## A wrapper script for clang-format and clang-tidy that checks all source
#  files for formatting/static analysis and returns a list of files to fix.
#  Optionally checks only changed files. Optionally automatically fixes the
#  errors.

import Template

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

## Get a list of all files (caring for gitignore) that match the regex pattern
#  @param git executable
#  @param pattern regex to match file name to
#  @return list of absolute file paths to process
def getFileList(git, pattern):
  files = []
  cmd = [git, "ls-files", "--exclude-standard",
         "--modified", "--others", "--cached"]
  result = subprocess.check_output(cmd, universal_newlines=True).strip()
  for filename in result.split("\n"):
    filename = Template.makeAbsolute(filename, os.getcwd())
    if re.match(pattern, filename) and filename not in files:
      files.append(filename)
  return files

## Get a list of all modified/added files (caring for gitignore) that match the
#  regex pattern
#  @param git executable
#  @param pattern regex to match file name to
#  @param indexOnly true will only check files added to the index (git add FILE)
#  @return list of absolute file paths to process
def getChangedFileList(git, pattern, indexOnly):
  files = []
  cmd = [git, "diff-index", "--cached", "--name-only", "HEAD"]
  result = subprocess.check_output(cmd, universal_newlines=True).strip()
  for filename in result.split("\n"):
    filename = Template.makeAbsolute(filename, os.getcwd())
    if re.match(pattern, filename) and filename not in files:
      files.append(filename)

  if(indexOnly):
    return files

  cmd = [git, "ls-files", "--exclude-standard", "--modified", "--others"]
  result = subprocess.check_output(cmd, universal_newlines=True).strip()
  for filename in result.split("\n"):
    filename = Template.makeAbsolute(filename, os.getcwd())
    if re.match(pattern, filename) and filename not in files:
      files.append(filename)
  return files

## Create argument menu and parse from command arguments
#  @return object of arguments
def getArguments():
  parser = argparse.ArgumentParser(description="Run clang-format and/or clang-tidy against all or changed files,"
                                   " and output which ones need fixing. Optionally, automatically fix")
  parser.add_argument("--format", action="store_true", default=False,
                      help="check clang-format")
  parser.add_argument("--tidy", action="store_true", default=False,
                      help="check clang-tidy")
  parser.add_argument("--clang-format-binary", metavar="PATH", default="clang-format",
                      help="path to clang-format binary")
  parser.add_argument("--clang-tidy-binary", metavar="PATH", default="clang-tidy",
                      help="path to clang-tidy binary")
  parser.add_argument("--clang-apply-replacements-binary", metavar="PATH", default="clang-apply-replacements",
                      help="path to clang-apply-replacements binary")
  parser.add_argument("--git-binary", metavar="PATH", default="git",
                      help="path to git binary")
  parser.add_argument("--regex", metavar="PATTERN", default=r"^((?!test).)*\.(cpp|cc|c\+\+|cxx|c|h|hpp)$",
                      help="custom pattern selecting file paths to check "
                      "(case insensitive). Ignore third-party and lib files: "
                      "\"^((?!(third-party|lib)).)*\\.(cpp|cc|c\\+\\+|cxx|c|h|hpp)$\"")
  parser.add_argument("-j", type=int, default=multiprocessing.cpu_count(),
                      help="number of clang-format instances to be run in parallel.")
  parser.add_argument("-a", action="store_true", default=False,
                      help="check all user files, overrides --index")
  parser.add_argument("-p", metavar="PATH", default="./build/",
                      help="Path used to read a compile command database.")
  parser.add_argument("--index", action="store_true", default=False,
                      help="only check files added to the index")
  parser.add_argument("--fix", action="store_true", default=False,
                      help="apply formatting fixes")
  parser.add_argument("--quiet", action="store_true", default=False,
                      help="only output errors")
  parser.add_argument("-v", action="store_true", default=False,
                      help="output commands being run")

  argv = sys.argv[1:]
  args = parser.parse_args(argv)

  if not args.tidy and not args.format:
    print("Need --tidy and/or --format flag")
    parser.print_help()
    sys.exit(1)

  if args.tidy:
    args.p = Template.findInParent("compile_commands.json", args.p)

  if args.v:
    args.quiet = False

  checkInstallations(args)

  return args

## Check the required installations
#  If an installation does not pass check, terminate program
#  @param args to grab installation locations from
def checkInstallations(args):
  if args.v:
    print("Checking git version")
  if not Template.checkSemver([args.git_binary, "--version"], "2.17.0"):
    print("Install git version 2.17+")
    sys.exit(1)

  if args.format:
    if args.v:
      print("Checking clang-format version")
    if not Template.checkSemver([args.clang_format_binary, "--version"], "7.0.0"):
      print("Install clang-format version 7.0+")
      sys.exit(1)

  if args.tidy:
    if args.v:
      print("Checking clang-tidy version")
    if not Template.checkSemver([args.clang_tidy_binary, "--version"], "7.0.0"):
      print("Install clang-tidy version 7.0+")
      sys.exit(1)

    if args.fix:
      if args.v:
        print("Checking clang-apply-replacements version")
      if not Template.checkSemver([args.clang_apply_replacements_binary, "--version"], "7.0.0"):
        print("Install clang-apply-replacements version 7.0+")
        sys.exit(1)

## Thread to run clang-tidy
#  @param clangTidy executable
#  @param queue of files
#  @param lock of stdout
#  @param failedCommands list of commands that encountered an exception
#  @param compilationDatabase to pass to clang-tidy to check compilation
#  @param tmpdir location to export list of fixes to
#  @param quiet true will only print errors
#  @param verbose true will print commands
def runTidy(clangTidy, queue, lock, failedCommands,
            compilationDatabase, tmpdir, quiet, verbose):
  while True:
    name = queue.get()

    cmd = [clangTidy, "-p", compilationDatabase, "-quiet"]
    if tmpdir:
      cmd.append("-export-fixes")
      # Get a temporary file. We immediately close the handle so clang-tidy can
      # overwrite it.
      (handle, tmpfile) = tempfile.mkstemp(suffix=".yaml", dir=tmpdir)
      os.close(handle)
      cmd.append(tmpfile)
    cmd.append(name)

    if verbose:
      with lock:
        print(" ". join(cmd))
    try:
      proc = subprocess.Popen(
          cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except Exception:
      queue.task_done()
      failedCommands.append(" ".join(cmd))
      continue

    output, err = proc.communicate()
    if proc.returncode != 0:
      failedCommands.append(" ".join(cmd))
    with lock:
      if not quiet or len(output) > 0:
        print("Tidying", name)
        print(output, flush=True)
      if "warnings generated" not in err or verbose:
        print(err, flush=True)
    queue.task_done()

## Tidy files in parallel
#  @param clangTidy executable
#  @param compilationDatabase
#  @param tmpdir temporary directory to export changes to
#  @param maxTasks number of parallel tasks to execute
#  @param files list of files to process
#  @param quiet true will only print errors
#  @param verbose true will print commands
def tidyFiles(clangTidy, compilationDatabase, tmpdir, maxTasks, files, quiet, verbose):
  with open(compilationDatabase, "r") as file:
    database = json.load(file)
  compileCommandFiles = [Template.makeAbsolute(entry["file"], entry["directory"])
                         for entry in database]

  taskQueue = queue.Queue(maxTasks)
  failedCommands = []
  lock = threading.Lock()
  for _ in range(maxTasks):
    t = threading.Thread(target=runTidy,
                         args=(clangTidy, taskQueue, lock, failedCommands,
                               compilationDatabase, tmpdir, quiet, verbose))
    t.daemon = True
    t.start()

  # Fill the queue with files.
  for name in files:
    if name in compileCommandFiles:
      taskQueue.put(name)

  # Wait for all threads to be done.
  taskQueue.join()
  if len(failedCommands) != 0:
    print("Failed executing commands:")
    for cmd in failedCommands:
      print(cmd)

## Apply changes exported from clang-tidy
#  @param applyReplacements executable
#  @param tmpdir directory where tidy replacements were exported
#  @param quiet true will only print errors
def fixTidyFiles(applyReplacements, tmpdir, quiet):
  if not quiet:
    print("Applying tidy fixes...")

  try:
    cmd = [applyReplacements, "-format", "-style=file", tmpdir]
    Template.call(cmd)
  except Exception:
    print("Error applying fixes.\n", file=sys.stderr)
    traceback.print_exc()

## Thread to run clang-format
#  @param clangFormat executable
#  @param queue of files
#  @param lock of stdout
#  @param failedCommands list of commands that encountered an exception
#  @param toFormatFiles list of files that need to be formatted
#  @param fix true will automatically apply formatting fixes
#  @param quiet true will only print errors
#  @param verbose true will print commands
def runFormat(clangFormat, queue, lock, failedCommands,
              toFormatFiles, fix, quiet, verbose):
  while True:
    name = queue.get()

    cmd = [clangFormat, "-style=file"]
    if fix:
      cmd.append("-i")
    else:
      cmd.append("-output-replacements-xml")
    cmd.append(name)

    if verbose:
      with lock:
        print(" ". join(cmd))
    try:
      proc = subprocess.Popen(
          cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except Exception:
      queue.task_done()
      failedCommands.append(" ".join(cmd))
      continue

    output, err = proc.communicate()
    if proc.returncode != 0:
      failedCommands.append(" ".join(cmd))
    with lock:
      if not quiet:
        if fix:
          print("Formatted", name, flush=True)
        else:
          print("Checked formatting of", name, flush=True)
      if "<replacement " in output:
        toFormatFiles.append(name)
      if len(err) > 0:
        print(err, file=sys.stderr, flush=True)
    queue.task_done()

## Format files in parallel
#  @param clangFormat executable
#  @param fix true will automatically apply formatting fixes
#  @param quiet true will only print errors
#  @param verbose true will print commands
#  @param maxTasks number of parallel tasks to execute
#  @param files list of files to process
def formatFiles(clangFormat, fix, quiet, verbose, maxTasks, files):
  taskQueue = queue.Queue(maxTasks)
  failedCommands = []
  toFormatFiles = []
  lock = threading.Lock()
  for _ in range(maxTasks):
    t = threading.Thread(target=runFormat,
                         args=(clangFormat, taskQueue, lock, failedCommands,
                               toFormatFiles, fix, quiet, verbose))
    t.daemon = True
    t.start()

  # Fill the queue with files.
  for name in files:
    taskQueue.put(name)

  # Wait for all threads to be done.
  taskQueue.join()
  if len(failedCommands) != 0:
    print("Failed executing commands:")
    for cmd in failedCommands:
      print(cmd)

  if len(toFormatFiles) != 0:
    print("Need to format:")
    for file in toFormatFiles:
      print(file)
  elif not quiet and not fix:
    print("No files need to be formatted")

## Main function
def main():
  args = getArguments()

  files = []
  if args.a:
    files = getFileList(args.git_binary, re.compile(args.regex, re.IGNORECASE))
  else:
    files = getChangedFileList(
        args.git_binary, re.compile(args.regex, re.IGNORECASE), args.index)

  tmpdir = None
  if args.tidy and args.fix:
    tmpdir = tempfile.mkdtemp()

  try:
    if args.tidy:
      tidyFiles(args.clang_tidy_binary, args.p, tmpdir,
                args.j, files, args.quiet, args.v)

    if tmpdir:
      fixTidyFiles(args.clang_apply_replacements_binary, tmpdir, args.quiet)

    if args.format:
      formatFiles(args.clang_format_binary, args.fix,
                  args.quiet, args.v, args.j, files)

  except KeyboardInterrupt:
    print("\nCtrl-C detected, goodbye.")
    if tmpdir:
      shutil.rmtree(tmpdir)
    os.kill(0, 9)

  if tmpdir:
    shutil.rmtree(tmpdir)


if __name__ == "__main__":
  main()
