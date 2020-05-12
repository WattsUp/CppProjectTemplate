set (SRCS
  "main.cpp"
)

set (SRCS_UNIX
)

set (SRCS_WIN
)

target_sources("installer" PRIVATE ${SRCS} $<IF:$<BOOL:${WIN32}>, ${SRCS_WIN}, ${SRCS_UNIX}>)