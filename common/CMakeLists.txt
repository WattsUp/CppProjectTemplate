set (SRCS
  "Logging.cpp"
)

target_sources("fractal" PRIVATE ${SRCS})

set (TEST_SRCS
  "TestMain.cpp"
  "Logging_Test.cpp"
)

target_sources("test" PRIVATE ${TEST_SRCS} ${SRCS})