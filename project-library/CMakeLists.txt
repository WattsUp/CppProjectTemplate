set (SRCS
  "library.cpp"
)

set (SRCS_UNIX
)

set (SRCS_WIN
)

target_sources("library" PRIVATE ${SRCS} $<IF:$<BOOL:${WIN32}>, ${SRCS_WIN}, ${SRCS_UNIX}>)

set (TEST_SRCS
  "library_test.cpp"
)

target_sources("gtester" PRIVATE ${TEST_SRCS} ${SRCS})