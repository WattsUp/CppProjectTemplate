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

## Prompt the user to enter targets and their configurations
#  @return list of targets (list: name string, gui boolean, archive boolean)
def getTargets():
  targets = []
  more = True
  print("----\nEnter target name: test")
  print("Will test have a GUI? (Y/n): n")
  print("Will test be released publicly? (Not a test utility) (Y/n): n")
  more = input(
      "Do you have more targets to add? (Y/n): ").lower().strip() == "y"
  while more:
    name = input("----\nEnter target name: ").lower().strip().replace(" ", "-")
    gui = input("Will {} have a GUI? (Y/n): ".format(name)
                ).lower().strip() == "y"
    archive = input(
        "Will {} be released publicly? (Not a test utility) (Y/n): ".format(name)).lower().strip() == "y"
    targets.append([name, gui, archive])
    more = input(
        "Do you have more targets to add? (Y/n): ").lower().strip() == "y"
  return targets


## Modify CMakeLists given new top level project name, and target names
def modifyCMakeLists():
  name = input("Enter top level project name: ").lower().strip()
  name = re.sub(r" ", "-", name)

  targets = getTargets()

  with open("CMakeLists.txt", "r", newline="\n") as file:
    filedata = file.read()
    file.close()

  # Replace top level project name
  filedata = re.sub(r"project\(.*?\)",
                    "project(\"{}\")".format(name), filedata)
  # Add targets to target list and subdirectory list
  targetList = "set (TARGETS\n  \"test\" # Unit tester common to all projects\n"
  targetConfigList = "set (TARGET_CONFIGS\n  \"\" # test\n"
  subdirectories = "# Add each subdirectory\nadd_subdirectory(\"common\")\n"
  for target in targets:
    targetList += "  \"{}\"\n".format(target[0])
    targetConfigList += "  \""
    if target[1]:
      targetConfigList += "GUI"
    if target[2]:
      targetConfigList += "Archive"
    targetConfigList += "\" # {}\n".format(target[0])
    subdirectories += "add_subdirectory(\"project-{}\")\n".format(target[0])
  targetList += ")"
  targetConfigList += ")"

  filedata = re.sub(r"set \(TARGETS\n(.*\n)*?\)", targetList, filedata)
  filedata = re.sub(r"set \(TARGET_CONFIGS\n(.*\n)*?\)",
                    targetConfigList, filedata)
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
    folder = "project-" + target[0]
    os.mkdir(folder)

    with open("tools/templates/CMakeLists.txt", "r", newline="\n") as file:
      data = file.read()
      file.close()
    data = re.sub(r"TARGET", target[0], data)
    if target[1]:
      data = re.sub(r"  \"main\.cpp\"\n", "", data)
    else:
      data = re.sub(r"  \"main_.*\.cpp\"\n", "", data)

    path = os.path.join(folder, "CMakeLists.txt")
    with open(path, "w", newline="\n") as file:
      file.write(data)
      file.close()
    print("Created", path)

    if (target[1]):
      path = os.path.join(folder, "main_unix.cpp")
      shutil.copy("tools/templates/main_unix.cpp", path)
      print("Created", path)
      path = os.path.join(folder, "main_win.cpp")
      shutil.copy("tools/templates/main_win.cpp", path)
      print("Created", path)
    else:
      path = os.path.join(folder, "main.cpp")
      shutil.copy("tools/templates/main_unix.cpp", path)
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

    shutil.rmtree("libraries", ignore_errors=True)
    os.mkdir("libraries")
    path = "libraries/CMakeLists.txt"
    shutil.copy("tools/templates/CMakeListsLibraries.txt", path)
    print("Created", path)

    for submodule in submodules.split("\n"):
      # Get the URL and local path of each submodule
      matches = re.search(r"^(submodule\..*\.)path (.*)$", submodule)
      path = matches[2]
      cmd = [git, "config", "-f", ".gitmodules", "--get", matches[1] + "url"]
      url = subprocess.check_output(cmd, universal_newlines=True).strip()

      Template.call([git, "submodule", "add", url, path])
      print("Added {} to {}".format(url, path))

    Template.call([git, "add", "."])

    Template.call([git, "commit", "-m", "Initial commit"])
    Template.call([git, "tag", "-a", "v0.0.0", "-m", "Initial release"])
    print("----\nCommitted master and tagged v0.0.0, need to push to remote")

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
  parser.add_argument("--cmake", metavar="PATH", default="cmake",
                      help="path to cmake binary")
  parser.add_argument("--clang-format", metavar="PATH", default="clang-format",
                      help="path to clang-format binary")
  parser.add_argument("--clang-tidy", metavar="PATH", default="clang-tidy",
                      help="path to clang-tidy binary")
  parser.add_argument("--clang-apply-replacements", metavar="PATH", default="clang-apply-replacements",
                      help="path to clang-apply-replacements binary")
  parser.add_argument("--git", metavar="PATH", default="git",
                      help="path to git binary")
  parser.add_argument("--doxygen", metavar="PATH", default="doxygen",
                      help="path to doxygen binary")
  parser.add_argument("--skip-compiler", action="store_true", default=False,
                      help="do not check that cmake can find a compiler")
  parser.add_argument("--software-check-only", action="store_true", default=False,
                      help="only check the installation and setup of required software")
  parser.add_argument("--documentation-branch", default='gh-pages',
                      help="branch to create for documentation website")

  argv = sys.argv[1:]
  args = parser.parse_args(argv)

  Template.checkInstallations(
      args.git,
      True,
      args.clang_format,
      args.clang_tidy,
      args.clang_apply_replacements,
      args.doxygen,
      args.cmake,
      not args.skip_compiler,
      False)
  print("All software dependencies have been installed")
  if args.software_check_only:
    return
  print("----------")
  modifyCMakeLists()
  print("----------")
  resetGit(args.git, args.documentation_branch)


if __name__ == "__main__":
  main()
