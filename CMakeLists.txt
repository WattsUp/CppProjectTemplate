cmake_minimum_required(VERSION 3.13)

# Must use GNUInstallDirs to install libraries into correct
# locations on all platforms.
include(GNUInstallDirs)

# Default to CMAKE_BUILD_TYPE = Release unless overridden on command line
if( DEFINED CMAKE_BUILD_TYPE )
    set( CMAKE_BUILD_TYPE ${CMAKE_BUILD_TYPE} CACHE STRING "Set to either \"Release\" or \"Debug\"" )
else()
    set( CMAKE_BUILD_TYPE Release CACHE STRING "Set to either \"Release\" or \"Debug\"" )
endif()

project("project-template" DESCRIPTION "A template repository for C++ projects")

# Global setting: Use C++14
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Generate compile commands for clang-tidy
set(CMAKE_EXPORT_COMPILE_COMMANDS on)

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

set (TARGETS_RAW
  "test(console)"      # Unit tester common to all projects
  "fractal"            # Main executable
  "installer(console)" # Used to install the software onto the user's computer, setup environment, etc.
)

foreach(TARGET_RAW ${TARGETS_RAW})
  string(REPLACE "(console)" "" TARGET ${TARGET_RAW})
  list(APPEND TARGETS ${TARGET})
endforeach()

# Remove existing /W0-4 flag before adding the desired one
string(REGEX REPLACE " /W[0-4]" "" CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")
string(REGEX REPLACE " /W[0-4]" "" CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")

# Set compiler options for warnings (treat as errors)
add_compile_options(
  $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:-Werror>
  $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:-Wall>
  $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:-Wextra>
  $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:-Wconversion>
  $<$<CXX_COMPILER_ID:MSVC>:/WX>
  $<$<CXX_COMPILER_ID:MSVC>:/W4>)

# Add the suffix "d" to debug builds
set(CMAKE_DEBUG_POSTFIX "d")

# Update semantic version from git tag
set(VERSION_FILE "${CMAKE_SOURCE_DIR}/common/Version.h")
set(VERSION_DEPENDENCY "${VERSION_FILE}.notgenerated")
find_package(Python3 COMPONENTS Interpreter)
add_custom_command(
  OUTPUT "${VERSION_DEPENDENCY}"
  BYPRODUCTS "${VERSION_FILE}"
  COMMAND "${Python3_EXECUTABLE}"
    "${CMAKE_SOURCE_DIR}/tools/CreateVersionFromGitTag.py"
    --output "${VERSION_FILE}"
    --quiet
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  COMMENT "Generating version file"
)

foreach(TARGET ${TARGETS_RAW})
  string(REPLACE "(console)" "" TARGET_NAME ${TARGET})
  # Create the executable target
  if(!WIN32)
    # Looks for int main(int argc, char* argv[])
    add_executable(${TARGET_NAME})
  elseif(${TARGET} MATCHES "\(console\)")
    # Looks for int main(int argc, char* argv[])
    add_executable(${TARGET_NAME})
    target_compile_definitions(${TARGET_NAME} PUBLIC WIN_CONSOLE)
  else()
    # Looks for int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, char* args, int nShowCmd)
    add_executable(${TARGET_NAME} WIN32)
  endif()

  # Add the root as an include directory: i.e. #include "common/Logging.hpp" from any level
  target_include_directories(${TARGET_NAME} PRIVATE ${CMAKE_SOURCE_DIR})

  # Set debug flag when building debug release, add a suffix to output files
  target_compile_definitions(${TARGET_NAME} PUBLIC "$<$<CONFIG:DEBUG>:DEBUG>")
  set_target_properties(${TARGET_NAME} PROPERTIES DEBUG_POSTFIX ${CMAKE_DEBUG_POSTFIX})

  # Make the version file a dependency so it always gets updated
  target_sources(${TARGET_NAME} PRIVATE "${VERSION_DEPENDENCY}")
endforeach()

# Generate doxygen when building release type builds
if(CMAKE_BUILD_TYPE STREQUAL "Release")
  find_package(Doxygen)
  add_custom_target(
    doc ALL
    COMMAND "${Python3_EXECUTABLE}"
      "${CMAKE_SOURCE_DIR}/tools/UpdateDoxygen.py"
      --doxygen-binary "${DOXYGEN_EXECUTABLE}"
      --doxygen-output "${CMAKE_SOURCE_DIR}/docs/project.doxyfile"
      --project-name "${PROJECT_NAME}"
      --project-brief "${PROJECT_DESCRIPTION}"
      --quiet
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Generating API documentation with Doxygen"
    DEPENDS "${VERSION_DEPENDENCY}"
  )
endif()

# Add support for Mingw RC compiler
if(WIN32)
  enable_language(RC)
  include(CMakeDetermineRCCompiler)

  if(MINGW)
    set(CMAKE_RC_COMPILER_INIT windres)
    set(CMAKE_RC_COMPILE_OBJECT "<CMAKE_RC_COMPILER> <FLAGS> -O coff <DEFINES> -I${CMAKE_CURRENT_BINARY_DIR} -i <SOURCE> -o <OBJECT>")
  endif()
endif()

# CMake targets cannot have spaces, to have spaces in the output, uncomment and adjust the following
#set_target_properties(installer PROPERTIES OUTPUT_NAME "installer with spaces")

# Add libraries first to setup library include directives
add_subdirectory("libraries")

# Include public interface (for a library)
include_directories("include")

# Add each subdirectory
add_subdirectory("common")
add_subdirectory("project-fractal")
add_subdirectory("project-installer")

target_link_libraries("test" gtest)