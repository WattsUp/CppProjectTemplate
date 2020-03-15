
set (SRCS
  "Complex.cpp"
)

target_sources("fractal" PRIVATE ${SRCS})

set (TEST_SRCS
  "Complex_Test.cpp"
)

target_sources("test" PRIVATE ${TEST_SRCS} ${SRCS})