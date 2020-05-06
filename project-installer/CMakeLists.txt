set (SRCS
)

set (SRCS_UNIX
  "main_unix.cpp"
)

set (SRCS_WIN
  "main_win.cpp"
)

target_sources("installer" PRIVATE ${SRCS} $<IF:${WIN32}, ${SRCS_WIN}, ${SRCS_UNIX}>)