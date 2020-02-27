cmake_minimum_required(VERSION 3.11)

# Must use GNUInstallDirs to install libraries into correct
# locations on all platforms.
include(GNUInstallDirs)

# Default to CMAKE_BUILD_TYPE = Release unless overridden on command line
if( DEFINED CMAKE_BUILD_TYPE )
    set( CMAKE_BUILD_TYPE ${CMAKE_BUILD_TYPE} CACHE STRING "Set to either \"Release\" or \"Debug\"" )
else()
    set( CMAKE_BUILD_TYPE Release CACHE STRING "Set to either \"Release\" or \"Debug\"" )
endif()

project("Project Template")

# Global setting: Use C++14
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Update semantic version from git tag
set(GIT_EXECUTABLE "git")
include("tools/GetVersionFromGitTag.cmake")
# Write common/Version.h
file(WRITE ${CMAKE_SOURCE_DIR}/common/Version.h
  "#define VERSION_STRING_FULL \"" ${${PROJECT_NAME}_VERSION_STRING_FULL} "\"\n"
  "#define VERSION_STRING \"" ${${PROJECT_NAME}_VERSION_STRING} "\"\n"
  "#define VERSION_MAJOR " ${${PROJECT_NAME}_VERSION_MAJOR} "\n"
  "#define VERSION_MINOR " ${${PROJECT_NAME}_VERSION_MINOR} "\n"
  "#define VERSION_PATCH " ${${PROJECT_NAME}_VERSION_PATCH} "\n"
  "#define VERSION_TWEAK \"" ${${PROJECT_NAME}_VERSION_TWEAK} "\"\n"
  "#define VERSION_AHEAD " ${${PROJECT_NAME}_VERSION_AHEAD} "\n"
  "#define VERSION_MODIFIED " ${${PROJECT_NAME}_MODIFIED} "\n"
  "#define VERSION_GIT_SHA \"" ${${PROJECT_NAME}_VERSION_GIT_SHA} "\"\n"
)

if( WIN32 )
    # define UNICODE and_UNICODE definition on Windows
    # Both definitions are required
    add_definitions(-DUNICODE -D_UNICODE)
endif()

# Allow target_sources to use relative paths
cmake_policy(SET CMP0076 NEW)

# Output binaries to ./bin
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_DEBUG "${CMAKE_SOURCE_DIR}/bin")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}/bin")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_DEBUG "${CMAKE_SOURCE_DIR}/bin")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}/bin")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_SOURCE_DIR}/bin")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}/bin")

set (TARGETS
  "Fractal"   # Main executable
  "Installer" # Used to install the software onto the user's computer, setup environment, etc.
)

# Remove existing /W0-4 flag before adding the desired one
string(REGEX REPLACE " /W[0-4]" "" CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")
string(REGEX REPLACE " /W[0-4]" "" CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")

# Set compiler options for warnings (treat as errors)
add_compile_options(
  $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:-Werror>
  $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:-Wall>
  $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:-Wextra>
  $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:-Wconversion>
  $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:-Wsign-conversion>
  $<$<CXX_COMPILER_ID:MSVC>:/WX>
  $<$<CXX_COMPILER_ID:MSVC>:/W4>)

foreach(target ${TARGETS})
  # Create the executable target
  if( WIN32 )
    add_executable(${target} WIN32)
  else()
    add_executable(${target})
  endif()

  # Add the root as an include directory: i.e. #include "common/Logging.hpp" from any level
  target_include_directories(${target} PRIVATE ${CMAKE_SOURCE_DIR})
endforeach()

# CMake targets cannot have spaces, to have spaces in the output, uncomment and adjust the following
#set_target_properties(Installer PROPERTIES OUTPUT_NAME "Installer with spaces")

# Add libraries first to setup library include directives
add_subdirectory("libraries")

# Include public interface (for a library)
include_directories("include")

# Add each subdirectory
add_subdirectory("common")
add_subdirectory("tools")
add_subdirectory("project-installer")
add_subdirectory("project-fractal")