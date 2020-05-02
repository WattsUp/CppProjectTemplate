#!/usr/bin/env python
## A script to fetch the latest version tag from git then append how far ahead
#  the current repository is. Outputs to a version file.

import Template

import argparse
import re
import subprocess
import sys
import traceback
from os import path

## Check the required installations
#  If an installation does not pass check, terminate program
#  @param args to grab installation locations from
def checkInstallations(args):
  if not args.quiet:
    print("Checking git version")
  if not Template.checkSemver([args.git_binary, "--version"], "2.17.0"):
    print("Install git version 2.17+")
    sys.exit(1)

## Get the version information from the git tags and repository state
#  @param git executable
#  @return Template.Version object
def getVersion(git):
  # Most recent tag
  cmd = [git, "describe", "--abbrev=0", "--tags"]
  string = subprocess.check_output(
      cmd, universal_newlines=True).strip()

  # Number of commits since last tag
  cmd = [git, "rev-list", string + "..HEAD", "--count"]
  ahead = subprocess.check_output(
      cmd, universal_newlines=True).strip()

  # Current commit SHA
  cmd = [git, "rev-parse", "--short", "HEAD"]
  gitSHA = subprocess.check_output(
      cmd, universal_newlines=True).strip()

  # Check if repository contains any modifications
  modified = False
  cmd = [git, "diff-index", "--quiet", "--cached", "HEAD"]
  if subprocess.call(cmd):
    modified = True
  else:
    cmd = [git, "diff-files", "--quiet"]
    if subprocess.call(cmd):
      modified = True
    else:
      cmd = [git, "ls-files", "--others", "--exclude-standard"]
      if subprocess.check_output(cmd, universal_newlines=True).strip():
        modified = True

  return Template.Version(string, ahead, modified, gitSHA)

## Main function
def main():
  # Create an arg parser menu and grab the values from the command arguments
  parser = argparse.ArgumentParser(description="Fetch the latest version tag "
                                   "from git then append how far ahead the "
                                   "current repository is. Optionally outputs "
                                   "to a version file.")
  parser.add_argument("--git-binary", metavar="PATH",
                      default="git",
                      help="path to git binary")
  parser.add_argument("--output", metavar="PATH",
                      help="output file to write version info, default stdout")
  parser.add_argument('--quiet', action='store_true', default=False,
                      help='only output return codes and errors')

  argv = sys.argv[1:]
  args = parser.parse_args(argv)

  checkInstallations(args)

  try:
    version = getVersion(args.git_binary)
  except Exception:
    print("Exception getting version from git tags")
    traceback.print_exc()
    sys.exit(1)

  data = f"""#ifndef _COMMON_VERSION_H_
#define _COMMON_VERSION_H_

#ifndef VERSION_DEFINES
const constexpr char* VERSION_STRING_FULL = "{version.fullStr()}";
const constexpr char* VERSION_STRING      = "{version.string}";
const constexpr size_t VERSION_MAJOR      = {version.major};
const constexpr size_t VERSION_MINOR      = {version.minor};
const constexpr size_t VERSION_PATCH      = {version.patch};
const constexpr char* VERSION_TWEAK       = "{version.tweak}";
const constexpr size_t VERSION_AHEAD      = {version.ahead};
const constexpr size_t VERSION_MODIFIED   = {int(version.modified)};
const constexpr char* VERSION_GIT_SHA     = "{version.gitSHA}";
#else /* VERSION_DEFINES */
#define VERSION_STRING_FULL "{version.fullStr()}"
#define VERSION_STRING "{version.string}"
#define VERSION_MAJOR {version.major}
#define VERSION_MINOR {version.minor}
#define VERSION_PATCH {version.patch}
#define VERSION_TWEAK "{version.tweak}"
#define VERSION_AHEAD {version.ahead}
#define VERSION_MODIFIED {int(version.modified)}
#define VERSION_GIT_SHA "{version.gitSHA}"
#endif /* VERSION_DEFINES */

#endif /* _COMMON_VERSION_H_ */
"""

  # Write to output file if given a path and existing file has different content
  if args.output:
    if path.isfile(args.output):
      with open(args.output, "r", newline="\n") as file:
        if file.read() == data:
          if not args.quiet:
            print("Version file unchanged: ", args.output)
          sys.exit(0)
    with open(args.output, "w", newline="\n") as file:
      file.write(data)
      if not args.quiet:
        print("Wrote version file to", args.output)
  else:
    print(data)


if __name__ == "__main__":
  main()
