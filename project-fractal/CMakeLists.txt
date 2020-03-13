add_subdirectory(math)

set (SRCS
  "Fractal.cpp"
)

target_sources("fractal" PRIVATE ${SRCS})