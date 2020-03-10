set (SRCS
  "Logging.cpp"
)

target_sources("Fractal" PRIVATE ${SRCS})

set (TEST_SRCS
  "TestMain.cpp"
  "Logging_Test.cpp"
)

target_sources("Test" PRIVATE ${TEST_SRCS} ${SRCS})