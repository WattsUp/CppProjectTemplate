set ( LIBRARY_INCLUDES
  "spdlog/include"
)

foreach(target ${TARGETS})
  target_include_directories(${target} SYSTEM PRIVATE ${LIBRARY_INCLUDES})
endforeach()

set(gtest_force_shared_crt ON)
add_subdirectory("googletest")
target_include_directories("Test" SYSTEM PRIVATE "googletest/googletest/include")