#!/usr/bin/env python
## Shared functions the template tools use
import sys
if sys.version_info[0] != 3 or sys.version_info[1] < 6:
  print("This script requires Python version >=3.6")
  sys.exit(1)

import os
import re
import subprocess
import stat

## Semantic versioning object with string parsing
class Version:
  string = ""
  major = 0
  minor = 0
  patch = 0
  tweak = ""
  ahead = 0
  modified = False
  gitSHA = ""

  ## Initialization of Version object
  #  @param self object pointer
  #  @param string of version: "[major].[minor].[patch](-tweak)"
  #  @param ahead number of commits ahead of version string
  #  @param modified state of the repository
  #  @param gitSHA of current repository state
  def __init__(self, string, ahead=0, modified=False, gitSHA=""):
    self.string = string
    self.ahead = ahead
    self.modified = modified
    self.gitSHA = gitSHA

    versionList = re.findall(r"-.*$|[0-9]+", string)
    self.major = versionList[0]
    self.minor = versionList[1]
    self.patch = versionList[2]
    if len(versionList) == 4:
      self.tweak = versionList[3][1:]
    else:
      self.tweak = ""

  ## String representation of Version
  #  @param self object pointer
  #  @return version string "[major].[minor].[patch](-tweak)"
  def __str__(self):
    return self.string

  ## Full string representation of Version
  #  @param self object pointer
  #  @return full version string "[major].[minor].[patch](-tweak)+[modified][ahead].[gitSHA]"
  def fullStr(self):
    if self.modified:
      return "{}+~{}.{}".format(self.string, self.ahead, self.gitSHA)
    else:
      return "{}+{}.{}".format(self.string, self.ahead, self.gitSHA)

  ## Greater than or equal to comparison
  #  @param self object pointer
  #  @param other object pointer
  #  @return true if self's version is higher than other's, false otherwise
  def __ge__(self, other):
    if self.major < other.major:
      return False
    if self.minor < other.minor:
      return False
    if self.patch < other.patch:
      return False
    return True

## Run a command, read its output for semantic version, compare to a minimum
#  @param cmd command to run, i.e. ["git", "--version"]
#  @param minimum semantic version string to compare to
#  @return true if outputted version is greater or equal to the minimum,
#    false otherwise (including exception occurred whilst executing command)
def checkSemver(cmd, minimum):
  try:
    output = subprocess.check_output(
        cmd, universal_newlines=True)
  except BaseException:
    sys.stderr.write(
        "Unable to run {:}. Is command correctly specified?\n".format(cmd[0]))
    return False

  version = Version(re.sub(r".*(\d+).(\d+).(\d+).*",
                           r"\1.\2.\3", output, flags=re.S))
  return version >= Version(minimum)

## Run a command in a directory (optional), redirect stdout to DEVNULL
#  @param cmd command to run, i.e. ["git", "--version"]
#  @param cwd directory to run command in
#  @return return code of the command
def call(cmd, cwd="."):
  return subprocess.check_call(cmd, cwd=cwd, stdout=subprocess.DEVNULL)

## Modify a path for write access, usually called on error of func
#  @param func object pointer
#  @param path to update permissions
#  @param excinfo
def chmodWrite(func, path, excinfo):
  os.chmod(path, stat.S_IWRITE)
  func(path)

## Make a path absolute
#  @param f path to check
#  @param directory path is relative to
#  @return absolute path of f
def makeAbsolute(f, directory):
  if os.path.isabs(f):
    return os.path.abspath(f)
  return os.path.normpath(os.path.join(directory, f))

## Find the file, checks parent folders until root
#  @param file to find
#  @return absolute path of file
def findInParent(file, directory):
  while not os.path.isfile(os.path.join(directory, file)):
    if os.path.normpath(directory) == "/":
      print("Error: could not file:", file)
      sys.exit(1)
    directory += "../"
  return makeAbsolute(file, directory)