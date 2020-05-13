set (SRCS
  "main.cpp"
)

set (SRCS_UNIX
)

set (SRCS_WIN
  "Installer_win32.cpp"
  "miniz.c"
)

if (WIN32)
  file(WRITE "archive.rc" "#include \"Resources.h\"\n"
    "\n"
    "#ifndef RES_ARCHIVE\n"
    "#define RES_ARCHIVE 1\n"
    "#endif\n"
    "RES_ARCHIVE RCDATA ${ARCHIVE_OUTPUT}.zip")
  list(APPEND SRCS "archive.rc" "installer_win32.rc")
  set_property(SOURCE "archive.rc" APPEND PROPERTY OBJECT_DEPENDS
    "${ARCHIVE_OUTPUT}.zip"
    "Resources.h"
  )
  set_property(SOURCE "installer_win32.rc" APPEND PROPERTY OBJECT_DEPENDS
    "installer.ico"
    "${CMAKE_SOURCE_DIR}/common/Version.h"
  )
endif()

target_sources("installer" PRIVATE ${SRCS} $<IF:$<BOOL:${WIN32}>, ${SRCS_WIN}, ${SRCS_UNIX}>)
