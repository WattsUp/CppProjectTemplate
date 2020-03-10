# C++ Project Template #
A template repository designed for medium to large C++ projects with multiple subprojects/executables.
Includes
* CMake build system
* Automatic semantic versioning
* [spdlog](https://github.com/gabime/spdlog) logging library
* [Google Test](https://github.com/google/googletest) framework
* Clang-format and clang-tidy
* Multiple target executables for main program, installer, auto-updater, tester, etc.
* Doxygen documentation

## Prerequisites ##
* Modern C/C++ compiler
* [CMake 3.11+](https://cmake.org/download/) installed
* [Clang tools](http://releases.llvm.org/download.html) namely clang-format and clang-tidy
* [Python >3.6](https://www.python.org/downloads/) for tools

**Recommended IDE** is [VSCode](https://code.visualstudio.com/) with the following extensions
* [C/C++](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools) language support
* [Clang-Format](https://marketplace.visualstudio.com/items?itemName=xaver.clang-format) integration
* [CMake](https://marketplace.visualstudio.com/items?itemName=twxs.cmake) language support
* [CMake Tools](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cmake-tools)
* [Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker)
* [Doxygen Documentation Generator](https://marketplace.visualstudio.com/items?itemName=cschlosser.doxdocgen)

## Building ##
### Git Clone ###
Clone the repository and its submodules
```bash
> mkdir workspace
> cd workspace
> git clone https://github.com/WattsUp/CppProjectTemplate myProject
> cd myProject
> git submodule init && git submodule update
```

### Manually Building ###
Configure the project with default compiler and compile
```bash
> cmake . -B build
> cmake --build build
```

### Building in VSCode ###
1. Open the project folder in VSCode with the recommended extensions
2. Open the CMake Tools tab
3. Select `Configure All Projects`, select appropriate compiler
4. Click `Build All Projects`

## Folder Structure ##
* `bin`       Binary folder, output directory for executables, add runtime resources here (icons, etc.)
* `common`    Common code shared amongst projects: logging, utilities, etc.
* `include`   Public include folder for libraries
* `libraries` Third party libraries usually included as a `git submodule`
* `tools`     Helper code such as check coding conventions script

### Projects ###
* `project-installer` Installer executable which sets up directories, variables, etc.
* `project-fractal`   Application to draw a fractal to the console

## Adapting ##
1. Clone the repository and initialize its submodules, see [Git Clone](#git-clone)
2. Change `project("ProjectTemplate")` to `project("[Top level project name]")` in `./CMakeLists.txt`
3. Modify/create folders for each sub project, see [Folder Structure](#folder-structure)
4. Modify/create target names in all `CMakeLists.txt`:
```CMake
set (TARGETS
  "[Target name 1]" # [Optional comment]
  "[Target name 2]" # [Optional comment]
)
```
and
```CMake
target_sources("[Target name 1]" PRIVATE ${SRCS})
```
**Note:** Target names cannot have spaces in CMake. To have spaces in the output files uncomment the following in `./CMakeLists.txt` and duplicate as needed:
```CMake
set_target_properties([TargetNoSpaces] PROPERTIES OUTPUT_NAME "Target With Spaces")
```
5. Add the appropriate subdirectories to `./CMakeLists.txt`
```CMake
# Add each subdirectory
add_subdirectory("common")
add_subdirectory("tools")
add_subdirectory("project-installer")
add_subdirectory("project-fractal")
```
6. CMake and build everything, see [Building](#building)
7. Write software
