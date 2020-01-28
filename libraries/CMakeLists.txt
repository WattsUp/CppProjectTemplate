set ( LIBRARY_INCLUDES
  "spdlog/include"
)

foreach(target ${TARGETS})
  target_include_directories(${target} PRIVATE ${LIBRARY_INCLUDES})
endforeach()