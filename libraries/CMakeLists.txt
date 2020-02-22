set ( LIBRARY_INCLUDES
  "spdlog/include"
)

foreach(target ${TARGETS})
  target_include_directories(${target} SYSTEM PRIVATE ${LIBRARY_INCLUDES})
endforeach()