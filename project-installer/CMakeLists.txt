set (SRCS
)

set (SRCS_UNIX
  "main_unix.cpp"
)

set (SRCS_WIN
  "main_win.cpp"
)

target_sources("installer" PRIVATE ${SRCS} $<IF:$<BOOL:${WIN32}>, ${SRCS_WIN}, ${SRCS_UNIX}>)