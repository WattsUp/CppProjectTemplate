#!/usr/bin/env python
""" Shared functions the template tools use
"""
from dataclasses import dataclass
import subprocess
import re
import sys
if sys.version_info[0] != 3 or sys.version_info[1] < 7:
  print("This script requires Python version >=3.7")
  sys.exit(1)


class Version:
  string = ""
  major = 0
  minor = 0
  patch = 0
  tweak = ""
  ahead = 0
  modified = False
  gitSHA = ""

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

  def __str__(self):
    return self.string

  def fullStr(self):
    if self.modified:
      return "{}+~{}.{}".format(self.string, self.ahead, self.gitSHA)
    else:
      return "{}+{}.{}".format(self.string, self.ahead, self.gitSHA)

  def __ge__(self, other):
    if self.major < other.major:
      return False
    if self.minor < other.minor:
      return False
    if self.patch < other.patch:
      return False
    return True


def checkSemver(cmd, minimum):
  try:
    output = subprocess.check_output(
        cmd, universal_newlines=True)
  except BaseException:
    print(
        "Unable to run {:}. Is command correctly specified?".format(cmd[0]), file=sys.stderr)
    sys.exit(1)

  version = Version(re.sub(r".*(\d+).(\d+).(\d+).*",
                           r"\1.\2.\3", output, flags=re.S))
  return version >= Version(minimum)
