add_subdirectory(math)

set (SRCS
  "Fractal.cpp"
)

target_sources("Fractal" PRIVATE ${SRCS})