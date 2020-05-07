#!/usr/bin/env python
## A script to update the webpage folder with doxygen generated documentation

import Template
import CreateVersionFromGitTag as VersionTag

import argparse
import re
import subprocess
import sys
import traceback

## Check the required installations
#  If an installation does not pass check, terminate program
#  @param args to grab installation locations from
def checkInstallations(args):
  if not args.quiet:
    print("Checking git version")
  if not Template.checkSemver([args.git_binary, "--version"], "2.17.0"):
    print("Install git version 2.17+", file=sys.stderr)
    sys.exit(1)

  if not args.quiet:
    print("Checking doxygen version")
  if not Template.checkSemver([args.doxygen_binary, "--version"], "1.8.17"):
    print("Install doxygen version 1.8.17+", file=sys.stderr)
    sys.exit(1)

## Checks current branch is the default branch, up to date with remote,
#  unmodified, and tagged
#  @param git executable
#  @return true when current branch meets criteria, false otherwise
def checkCurrentBranchStatus(git, quiet):
  status = True

  # Fetch remote
  Template.call([git, "fetch"])

  # Get name of default branch
  cmd = [git, "symbolic-ref", "refs/remotes/origin/HEAD"]
  default = subprocess.check_output(cmd, universal_newlines=True).strip()
  default = re.match(r"refs/remotes/origin/(.*)", default).group(1)

  # Get branch status compared to remote
  cmd = [git, "branch", "-vv"]
  string = subprocess.check_output(cmd, universal_newlines=True).strip()
  match = re.search(
      r"^\* ([^\s]*) *[^\s]* *\[origin/([^\s:]*):? ?((ahead|behind) .*)?\]",
      string,
      flags=re.M)
  if not match:
    print("Current branch does not have a remote", file=sys.stderr)
    status = False
  else:
    groups = match.groups()
    if groups[1] != default:
      print("Current branch is not default (origin/{})".format(default),
            file=sys.stderr)
      status = False

    if groups[2]:
      print("Current branch is {} of its remote".format(groups[2]),
            file=sys.stderr)
      status = False

  version = VersionTag.getVersion(git)
  if version.modified:
    print("Repository is modified", file=sys.stderr)
    status = False

  if version.ahead:
    print("Repository is {} commits ahead of a tag".format(version.ahead),
          file=sys.stderr)
    status = False

  return status

## Main function
def main():
  # Create an arg parser menu and grab the values from the command arguments
  parser = argparse.ArgumentParser(description="Update the webpage folder with"
                                   " doxygen generated documentation")
  parser.add_argument("--git-binary", metavar="PATH", default="git",
                      help="path to git binary")
  parser.add_argument("--doxygen-binary", metavar="PATH", default="doxygen",
                      help="path to doxygen binary")
  parser.add_argument("--quiet", action="store_true", default=False,
                      help="only output return codes and errors")
  parser.add_argument("-f", action="store_true", default=False,
                      help="ignore current branch status check: default "
                      "branch, up to date with remote, unmodified, and tagged")

  argv = sys.argv[1:]
  args = parser.parse_args(argv)

  checkInstallations(args)

  try:
    if not checkCurrentBranchStatus(args.git_binary, args.quiet):
      if not args.f:
        print("Current repository is not updated default branch", file=sys.stderr)
        sys.exit(1)
  except Exception:
    print("Exception fetching remote", file=sys.stderr)
    traceback.print_exc()


if __name__ == "__main__":
  main()
