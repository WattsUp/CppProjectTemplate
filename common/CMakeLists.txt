set (SRCS
  "Logging.cpp"
)

foreach(target ${TARGETS})
  target_sources(${target} PRIVATE ${SRCS})
endforeach()

set (TEST_SRCS
  "TestMain.cpp"
  "Logging_Test.cpp"
)

target_sources("test" PRIVATE ${TEST_SRCS})