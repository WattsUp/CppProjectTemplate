cmake_minimum_required(VERSION 3.0.0)

# Must use GNUInstallDirs to install libraries into correct
# locations on all platforms.
include(GNUInstallDirs)

# Default to CMAKE_BUILD_TYPE = Release unless overridden on command line
if( DEFINED CMAKE_BUILD_TYPE )
    set( CMAKE_BUILD_TYPE ${CMAKE_BUILD_TYPE} CACHE STRING "Set to either \"Release\" or \"Debug\"" )
else()
    set( CMAKE_BUILD_TYPE Release CACHE STRING "Set to either \"Release\" or \"Debug\"" )
endif()

project(ProjectTemplate)

# Global setting: Use C++14
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if( WIN32 )
    # define UNICODE and_UNICODE definition on Windows
    # Both definitions are required
    add_definitions(-DUNICODE -D_UNICODE)
endif()

#================================================
# Let CMake look in these directories for nested
# 'CMakeLists.txt' files to process
#================================================

add_subdirectory(libraries)

add_subdirectory(common)
# add_subdirectory(include)
add_subdirectory(module)
# add_subdirectory(tools)