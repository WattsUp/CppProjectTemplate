set (SRCS
  "main.cpp"
)

set (SRCS_UNIX
)

set (SRCS_WIN
  "Installer_win32.cpp"
)

if (WIN32)
  list(APPEND SRCS "Installer_win32.rc")
  set_property(SOURCE "Installer_win32.rc" APPEND PROPERTY OBJECT_DEPENDS
    "Installer.ico"
    "${CMAKE_SOURCE_DIR}/common/Version.h"
    "Resources.h"
  )
  add_dependencies("installer" "archive")
endif()

target_sources("installer" PRIVATE ${SRCS} $<IF:$<BOOL:${WIN32}>, ${SRCS_WIN}, ${SRCS_UNIX}>)
