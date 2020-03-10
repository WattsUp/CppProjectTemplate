#
# This cmake fractal sets the project version and partial version
# variables by analysing the git tag and commit history. It expects git
# tags defined with semantic versioning 2.0.0 (http://semver.org/).
#
# The fractal expects the PROJECT_NAME variable to be set. The project 
# version will be updated using information fetched from the
# most recent git tag and commit
#
# Once done, this fractal will define the following variables:
#
# ${PROJECT_NAME}_VERSION_STRING - Version string without metadata
# such as "v2.0.0" or "v1.2.41-beta.1". This should correspond to the
# most recent git tag.
# ${PROJECT_NAME}_VERSION_STRING_FULL - Version string with metadata
# such as "v2.0.0+3.a23fbc" or "v1.3.1-alpha.2+~4.9c4fd1"
# ${PROJECT_NAME}_VERSION - Same as ${PROJECT_NAME}_VERSION_STRING,
# without the preceding 'v', e.g. "2.0.0" or "1.2.41-beta.1"
# ${PROJECT_NAME}_VERSION_MAJOR - Major version integer (e.g. 2 in v2.3.1-RC.2+~21.ef12c8)
# ${PROJECT_NAME}_VERSION_MINOR - Minor version integer (e.g. 3 in v2.3.1-RC.2+~21.ef12c8)
# ${PROJECT_NAME}_VERSION_PATCH - Patch version integer (e.g. 1 in v2.3.1-RC.2+~21.ef12c8)
# ${PROJECT_NAME}_VERSION_TWEAK - Tweak version string (e.g. "RC.2" in v2.3.1-RC.2+~21.ef12c8)
# ${PROJECT_NAME}_VERSION_AHEAD - How many commits ahead of last tag (e.g. 21 in v2.3.1-RC.2+~21.ef12c8)
# ${PROJECT_NAME}_MODIFIED - If the reposistory has been modified since last commit (e.g. ~ in v2.3.1-RC.2+~21.ef12c8)
# ${PROJECT_NAME}_VERSION_GIT_SHA - The git sha1 of the most recent commit (e.g. the "ef12c8" in v2.3.1-RC.2+~21.ef12c8)
#
# This fractal is public domain, use it as it fits you best.
#
# Author: Nuno Fachada (modified by Bradley Davis)

# Get last tag from git
execute_process(COMMAND ${GIT_EXECUTABLE} describe --abbrev=0 --tags
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  OUTPUT_VARIABLE ${PROJECT_NAME}_VERSION_STRING
  OUTPUT_STRIP_TRAILING_WHITESPACE)

#How many commits since last tag
execute_process(COMMAND ${GIT_EXECUTABLE} rev-list ${${PROJECT_NAME}_VERSION_STRING}..HEAD --count
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  OUTPUT_VARIABLE ${PROJECT_NAME}_VERSION_AHEAD
  OUTPUT_STRIP_TRAILING_WHITESPACE)

# Get current commit SHA from git
execute_process(COMMAND ${GIT_EXECUTABLE} rev-parse --short HEAD
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  OUTPUT_VARIABLE ${PROJECT_NAME}_VERSION_GIT_SHA
  OUTPUT_STRIP_TRAILING_WHITESPACE)

# Check if repository contains any modifications
execute_process(COMMAND ${GIT_EXECUTABLE} diff-index --quiet --cached HEAD
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  RESULT_VARIABLE ${PROJECT_NAME}_MODIFIED)
if(${PROJECT_NAME}_MODIFIED EQUAL 0)
  execute_process(COMMAND ${GIT_EXECUTABLE} diff-files --quiet
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    RESULT_VARIABLE ${PROJECT_NAME}_MODIFIED)
endif()
if(${PROJECT_NAME}_MODIFIED EQUAL 0)
  execute_process(COMMAND ${GIT_EXECUTABLE} ls-files --others --exclude-standard
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    OUTPUT_VARIABLE REPO_NEW_FILES
    OUTPUT_STRIP_TRAILING_WHITESPACE)
  if(REPO_NEW_FILES)
    set(${PROJECT_NAME}_MODIFIED 1)
  endif()
endif()

# Get partial versions into a list
string(REGEX MATCHALL "-.*$|[0-9]+" ${PROJECT_NAME}_PARTIAL_VERSION_LIST
  ${${PROJECT_NAME}_VERSION_STRING})

# Set the version numbers
list(GET ${PROJECT_NAME}_PARTIAL_VERSION_LIST
  0 ${PROJECT_NAME}_VERSION_MAJOR)
list(GET ${PROJECT_NAME}_PARTIAL_VERSION_LIST
  1 ${PROJECT_NAME}_VERSION_MINOR)
list(GET ${PROJECT_NAME}_PARTIAL_VERSION_LIST
  2 ${PROJECT_NAME}_VERSION_PATCH)

# The tweak part is optional, so check if the list contains it
list(LENGTH ${PROJECT_NAME}_PARTIAL_VERSION_LIST
  ${PROJECT_NAME}_PARTIAL_VERSION_LIST_LEN)
if (${PROJECT_NAME}_PARTIAL_VERSION_LIST_LEN GREATER 3)
  list(GET ${PROJECT_NAME}_PARTIAL_VERSION_LIST 3 ${PROJECT_NAME}_VERSION_TWEAK)
  string(SUBSTRING ${${PROJECT_NAME}_VERSION_TWEAK} 1 -1 ${PROJECT_NAME}_VERSION_TWEAK)
endif()

# Unset the list
unset(${PROJECT_NAME}_PARTIAL_VERSION_LIST)

# Set full project version string
if(${PROJECT_NAME}_MODIFIED)
  set(${PROJECT_NAME}_VERSION_STRING_FULL
    ${${PROJECT_NAME}_VERSION_STRING}+~${${PROJECT_NAME}_VERSION_AHEAD}.${${PROJECT_NAME}_VERSION_GIT_SHA})
else()
set(${PROJECT_NAME}_VERSION_STRING_FULL
  ${${PROJECT_NAME}_VERSION_STRING}+${${PROJECT_NAME}_VERSION_AHEAD}.${${PROJECT_NAME}_VERSION_GIT_SHA})
endif()