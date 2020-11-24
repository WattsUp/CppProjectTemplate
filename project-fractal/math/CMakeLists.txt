
set (SRCS
  "complex.cpp"
)

target_sources("fractal" PRIVATE ${SRCS})

set (TEST_SRCS
  "complex_test.cpp"
)

target_sources("gtester" PRIVATE ${TEST_SRCS} ${SRCS})