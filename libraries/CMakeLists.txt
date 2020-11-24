set ( LIBRARY_INCLUDES
  "miniz"
)

target_sources("installer-win" PRIVATE "miniz/miniz.c")

find_package(spdlog CONFIG REQUIRED)
find_package(fmt CONFIG REQUIRED)

find_package(GTest CONFIG REQUIRED)
target_link_libraries("gtester" PRIVATE GTest::gtest)

foreach(target ${TARGETS})
  target_include_directories(${target} SYSTEM PRIVATE ${LIBRARY_INCLUDES})
  target_link_libraries(${target} PRIVATE spdlog::spdlog_header_only)
  if (WIN32 AND (NOT BUILD_SHARED_LIBS OR ${target} STREQUAL "installer-win"))
    # Self extracting Windows installer always use static linking
    target_link_libraries(${target} PRIVATE fmt::fmt-header-only)
  endif()
endforeach()