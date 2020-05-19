add_subdirectory(math)

set (SRCS
  "fractal.cpp"
)

if (WIN32)
  list(APPEND SRCS "fractal_win32.rc")
  set_property(SOURCE "fractal_win32.rc" APPEND PROPERTY OBJECT_DEPENDS
    "fractal.ico"
    "${CMAKE_SOURCE_DIR}/common/version.h"
  )
endif()

set (SRCS_UNIX
  "main_unix.cpp"
)

set (SRCS_WIN
  "main_win.cpp"
)

target_sources("fractal" PRIVATE ${SRCS} $<IF:$<BOOL:${WIN32}>, ${SRCS_WIN}, ${SRCS_UNIX}>)