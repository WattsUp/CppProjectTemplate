
set (SRCS
  "Complex.cpp"
)

target_sources("Fractal" PRIVATE ${SRCS})

set (TEST_SRCS
  "Complex_Test.cpp"
)

target_sources("Test" PRIVATE ${TEST_SRCS} ${SRCS})