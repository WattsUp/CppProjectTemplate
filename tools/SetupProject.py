#!/usr/bin/env python
import argparse
import sys
import subprocess
import traceback
import re

if sys.version_info[0] != 3 or sys.version_info[1] < 6:
  print("This script requires Python version >=3.6")
  sys.exit(1)


def checkSemver(cmd, major, minor, patch):
  semverRegex = r"(\d+).(\d+).(\d+)"

  try:
    output = subprocess.check_output(
        cmd, universal_newlines=True)
  except BaseException:
    print(
        "Unable to run {:}. Is command correctly specified?".format(cmd[0]), file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)

  matches = re.findall(semverRegex, output)
  if len(matches) != 1:
    print("Failed to get semantic version from", cmd[0], matches)
    sys.exit(1)

  if int(matches[0][0]) < major:
    return False

  if int(matches[0][1]) < minor:
    return False

  if int(matches[0][2]) < patch:
    return False

  return True


def checkInstallations(args):

  print("Checking cmake version")
  if not checkSemver([args.cmake_binary, "--version"], 3, 11, 0):
    print("Install cmake version 3.11+")
    sys.exit(1)

  print("Checking git version")
  if not checkSemver([args.git_binary, "--version"], 2, 17, 0):
    print("Install git version 2.17+")
    sys.exit(1)

  print("Checking clang-format version")
  if not checkSemver([args.clang_format_binary, "--version"], 7, 0, 0):
    print("Install clang-format version 7.0+")
    sys.exit(1)

  print("Checking clang-tidy version")
  if not checkSemver([args.clang_tidy_binary, "--version"], 7, 0, 0):
    print("Install clang-tidy version 7.0+")
    sys.exit(1)

  print("Checking clang-apply-replacements version")
  if not checkSemver(
    [args.clang_apply_replacements_binary, "--version"], 7, 0, 0):
    print("Install clang-apply-replacements version 7.0+")
    sys.exit(1)

  print("Checking working compiler exists")
  try:
    subprocess.check_call([args.cmake_binary,
                           "-E",
                           "make_directory",
                           "__temp__"],
                          stdout=subprocess.DEVNULL)
    subprocess.check_call([args.cmake_binary,
                           "-E",
                           "touch",
                           "CMakeLists.txt"],
                          cwd="__temp__",
                          stdout=subprocess.DEVNULL)
    subprocess.check_call([args.cmake_binary,
                           "--check-system-vars",
                           "-Wno-dev",
                           "."],
                          cwd="__temp__",
                          stdout=subprocess.DEVNULL)
    subprocess.check_call([args.cmake_binary,
                           "-E",
                           "remove_directory",
                           "__temp__"],
                          stdout=subprocess.DEVNULL)
  except Exception:
    print("Failed to check for a compiler")
    traceback.print_exc()
    sys.exit(1)

  print("All software dependencies have been installed")


def renameProject():
  print("Enter top level project name")


def modifyTargets():
  print("Enter target names")


def resetGit():
  # set -e
  # rm -rf .git
  # git init

  # git config -f .gitmodules --get-regexp "^submodule\..*\.path$" > tempfile

  # while read -u 3 path_key path
  # do
  #     url_key=$(echo $path_key | sed "s/\.path/.url/")
  #     url=$(git config -f .gitmodules --get "$url_key")

  #     read -p "Are you sure you want to delete $path and re-initialize as a new submodule? " yn
  #     case $yn in
  #         [Yy]* ) rm -rf $path; git submodule add $url $path; echo "$path has been initialized";;
  #         [Nn]* ) exit;;
  #         * ) echo "Please answer yes or no.";;
  #     esac

  # done 3<tempfile

  # rm tempfile
  print("Git reset")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Check for all software dependencies "
                                   "(prompts for their installation), modify top-level "
                                   "project name, modify targets, reset the git repository "
                                   "to an initial commit, and tag the commit v0.0.0.")
  parser.add_argument("--cmake-binary", metavar="PATH",
                      default="cmake",
                      help="path to cmake binary")
  parser.add_argument("--clang-format-binary", metavar="PATH",
                      default="clang-format",
                      help="path to clang-format binary")
  parser.add_argument("--clang-tidy-binary", metavar="PATH",
                      default="clang-tidy",
                      help="path to clang-tidy binary")
  parser.add_argument("--clang-apply-replacements-binary", metavar="PATH",
                      default="clang-apply-replacements",
                      help="path to clang-apply-replacements binary")
  parser.add_argument("--git-binary", metavar="PATH",
                      default="git",
                      help="path to git binary")
  parser.add_argument("--keep-setup-script", action="store_true", default=False,
                      help="do not add this script to .gitignore")

  argv = sys.argv[1:]
  args = parser.parse_args(argv)

  checkInstallations(args)
  print("----------")
  renameProject()
  print("----------")
  modifyTargets()
  print("----------")
  resetGit()
