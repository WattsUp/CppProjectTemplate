#!/usr/bin/env python
## A script to check for all software dependencies (prompts for their
#  installation), modify top-level project name, modify targets, reset the git
#  repository to an initial commit, and tag the commit v0.0.0.

import Template

import argparse
import os
import re
import shutil
import subprocess
import sys
import traceback

## Check the required installations
#  If an installation does not pass check, terminate program
#  @param args to grab installation locations from
def checkInstallations(args):
  print("Checking cmake version")
  if not Template.checkSemver([args.cmake_binary, "--version"], "3.13.0"):
    print("Install cmake version 3.13+", file=sys.stderr)
    sys.exit(1)

  print("Checking git version")
  if not Template.checkSemver([args.git_binary, "--version"], "2.17.0"):
    print("Install git version 2.17+", file=sys.stderr)
    sys.exit(1)

  print("Checking git config")
  try:
    Template.call([args.git_binary, "config", "--global", "user.name"])
    Template.call([args.git_binary, "config", "--global", "user.email"])
  except Exception:
    print("No identity for git", file=sys.stderr)
    print("git config --global user.name \"Your name\"", file=sys.stderr)
    print("git config --global user.email \"you@example.com\"", file=sys.stderr)
    sys.exit(1)

  print("Checking clang-format version")
  if not Template.checkSemver(
          [args.clang_format_binary, "--version"], "7.0.0"):
    print("Install clang-format version 7.0+", file=sys.stderr)
    sys.exit(1)

  print("Checking clang-tidy version")
  if not Template.checkSemver([args.clang_tidy_binary, "--version"], "7.0.0"):
    print("Install clang-tidy version 7.0+", file=sys.stderr)
    sys.exit(1)

  print("Checking clang-apply-replacements version")
  if not Template.checkSemver(
          [args.clang_apply_replacements_binary, "--version"], "7.0.0"):
    print("Install clang-apply-replacements version 7.0+", file=sys.stderr)
    sys.exit(1)

  print("Checking doxygen version")
  if not Template.checkSemver([args.doxygen_binary, "--version"], "1.8.17"):
    print("Install doxygen version 1.8.17+", file=sys.stderr)
    sys.exit(1)

  if not args.skip_compiler:
    print("Checking working compiler exists")
    try:
      Template.call([args.cmake_binary, "-E", "make_directory", "__temp__"])
      Template.call([args.cmake_binary, "-E", "touch", "CMakeLists.txt"],
                    "__temp__")
      Template.call([args.cmake_binary, "--check-system-vars", "-Wno-dev", "."],
                    "__temp__")
      Template.call([args.cmake_binary, "-E", "remove_directory", "__temp__"])
    except Exception:
      print("Failed to check for a compiler", file=sys.stderr)
      traceback.print_exc()
      sys.exit(1)

  print("All software dependencies have been installed")

## Modify CMakeLists given new top level project name, and target names
def modifyCMakeLists():
  name = input("Enter top level project name: ").lower().strip()
  name = re.sub(r" ", "-", name)

  targetsRaw = input("Enter target names (separate multiple by comma, follow with"
                     " '(GUI)' to indicate target will have a GUI): test, ")
  targets = []
  targetsGUI = []
  for targetRaw in targetsRaw.lower().split(","):
    match = re.match(r"([\w\d ]*)(\(gui\))?", targetRaw).groups()
    target = re.sub(r" ", "-", match[0].strip())
    if target and (target not in targets) and (target not in targetsGUI):
      if match[1]:
        targetsGUI.append(target)
        print("Added GUI target \"{}\"".format(target))
      else:
        targets.append(target)
        print("Added console target \"{}\"".format(target))

  with open("CMakeLists.txt", "r", newline="\n") as file:
    filedata = file.read()
    file.close()

  # Replace top level project name
  filedata = re.sub(r"project\(.*?\)",
                    "project(\"{}\")".format(name), filedata)
  # Add targets to target list and subdirectory list
  targetList = "set (TARGETS_RAW\n  \"test\" # Unit tester common to all projects\n"
  subdirectories = "# Add each subdirectory\nadd_subdirectory(\"common\")\n"
  for target in targets:
    if target:
      targetList += "  \"{}\"\n".format(target)
      subdirectories += "add_subdirectory(\"project-{}\")\n".format(target)
  for target in targetsGUI:
    if target:
      targetList += "  \"{}(GUI)\"\n".format(target)
      subdirectories += "add_subdirectory(\"project-{}\")\n".format(target)
  targetList += ")"

  filedata = re.sub(r"set \(TARGETS_RAW\n(.*\n)*?\)", targetList, filedata)
  filedata = re.sub(
      r"# Add each subdirectory\n(add_subdirectory\(.*\"\)\n*)*",
      subdirectories + "\n",
      filedata)

  # Overwrite file
  with open("CMakeLists.txt", "w", newline="\n") as file:
    file.write(filedata)
    file.close()

  print("Modified ./CMakeLists.txt")

  # Remove existing project folders
  for f in os.listdir("."):
    if re.match(r"project-.*", f):
      shutil.rmtree(f, ignore_errors=True)

  for target in targets:
    folder = "project-" + target
    os.mkdir(folder)

    with open("tools/templates/CMakeLists.txt", "r", newline="\n") as file:
      data = file.read()
      file.close()
    data = re.sub(r"TARGET", target, data)
    data = re.sub(r"  \"main_.*\.cpp\"\n", "", data)
    path = os.path.join(folder, "CMakeLists.txt")
    with open(path, "w", newline="\n") as file:
      file.write(data)
      file.close()
    print("Created", path)

    path = os.path.join(folder, "main.cpp")
    shutil.copy("tools/templates/main_unix.cpp", path)
    print("Created", path)

  for target in targetsGUI:
    folder = "project-" + target
    os.mkdir(folder)

    with open("tools/templates/CMakeLists.txt", "r", newline="\n") as file:
      data = file.read()
      file.close()
    data = re.sub(r"TARGET", target, data)
    data = re.sub(r"  \"main\.cpp\"\n", "", data)
    path = os.path.join(folder, "CMakeLists.txt")
    with open(path, "w", newline="\n") as file:
      file.write(data)
      file.close()
    print("Created", path)

    path = os.path.join(folder, "main_unix.cpp")
    shutil.copy("tools/templates/main_unix.cpp", path)
    print("Created", path)
    path = os.path.join(folder, "main_win.cpp")
    shutil.copy("tools/templates/main_win.cpp", path)
    print("Created", path)

## Reset the git repository: remove current repo, initialize a new one, update
#  submodules, commit, tag
#  @param git executable
#  @param documentation branch to create documentation website
def resetGit(git, documentation):
  try:
    if os.path.exists(".git"):
      shutil.rmtree(".git", onerror=Template.chmodWrite)
    Template.call([git, "init"])
    print("Created new git repository")

    # Get list of previous submodules and add them to the fresh repository
    cmd = [git, "config", "-f", ".gitmodules",
           "--get-regexp", "^submodule\\..*\\.path$"]
    submodules = subprocess.check_output(cmd, universal_newlines=True).strip()

    for submodule in submodules.split("\n"):
      # Get the URL and local path of each submodule
      matches = re.search(r"^(submodule\..*\.)path (.*)$", submodule)
      path = matches[2]
      cmd = [git, "config", "-f", ".gitmodules", "--get", matches[1] + "url"]
      url = subprocess.check_output(cmd, universal_newlines=True).strip()

      shutil.rmtree(path, ignore_errors=True)
      Template.call([git, "submodule", "add", url, path])
      print("Added {} to {}".format(url, path))

    Template.call([git, "add", "."])

    Template.call([git, "commit", "-m", "Initial commit"])
    Template.call([git, "tag", "-a", "v0.0.0", "-m", "Initial release"])
    print("Committed master and tagged v0.0.0, need to push to remote")

    # Create orphaned documentation branch
    Template.call([git, "checkout", "--orphan", documentation, "--quiet"])
    Template.call([git, "reset", "."])

    # Move template files to top level
    for f in os.listdir("docs/templates/"):
      shutil.copy(
          Template.makeAbsolute(
              "docs/templates/" + f,
              os.getcwd()),
          os.path.join(os.getcwd(), f))

    # Add template files, commit
    Template.call([git, "add",
                   ".gitattributes", ".gitignore", ".nojekyll", "index.html"])
    Template.call([git, "commit", "-m", "Initial commit"])
    print("Committed documentation branch, need to push to remote")

    # Remove all other files
    Template.call([git, "clean", "-fd"])
    if os.path.exists("docs"):
      shutil.rmtree("docs", onerror=Template.chmodWrite)
    Template.call([git, "checkout", "master", "--quiet"])

    print("Make sure to push with 'git push --tags'")

  except Exception:
    print("Failed to reset git repository", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)

## Main function
def main():
  parser = argparse.ArgumentParser(description="Check for all software dependencies "
                                   "(prompts for their installation), modify top-level "
                                   "project name, modify targets, reset the git repository "
                                   "to an initial commit, and tag the commit v0.0.0.")
  parser.add_argument("--cmake-binary", metavar="PATH", default="cmake",
                      help="path to cmake binary")
  parser.add_argument("--clang-format-binary", metavar="PATH", default="clang-format",
                      help="path to clang-format binary")
  parser.add_argument("--clang-tidy-binary", metavar="PATH", default="clang-tidy",
                      help="path to clang-tidy binary")
  parser.add_argument("--clang-apply-replacements-binary", metavar="PATH", default="clang-apply-replacements",
                      help="path to clang-apply-replacements binary")
  parser.add_argument("--git-binary", metavar="PATH", default="git",
                      help="path to git binary")
  parser.add_argument("--doxygen-binary", metavar="PATH", default="doxygen",
                      help="path to doxygen binary")
  parser.add_argument("--skip-compiler", action="store_true", default=False,
                      help="do not check that cmake can find a compiler")
  parser.add_argument("--software-check-only", action="store_true", default=False,
                      help="only check the installation and setup of required software")
  parser.add_argument("--documentation-branch", default='gh-pages',
                      help="branch to create for documentation website")

  argv = sys.argv[1:]
  args = parser.parse_args(argv)

  checkInstallations(args)
  if args.software_check_only:
    return
  print("----------")
  modifyCMakeLists()
  print("----------")
  resetGit(args.git_binary, args.documentation_branch)


if __name__ == "__main__":
  main()
