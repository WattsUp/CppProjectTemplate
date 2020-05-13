set (SRCS
  "main.cpp"
)

set (SRCS_UNIX
)

set (SRCS_WIN
)

if (WIN32)
  file(WRITE "archive.rc" "#ifndef ARCHIVE\n"
    "#define ARCHIVE 1\n"
    "#endif\n"
    "ARCHIVE RCDATA ${ARCHIVE_OUTPUT}.zip")
  list(APPEND SRCS "archive.rc")
  set_property(SOURCE "Fractal_win32.rc" APPEND PROPERTY OBJECT_DEPENDS
    "${ARCHIVE_OUTPUT}.zip"
  )
endif()

target_sources("installer" PRIVATE ${SRCS} $<IF:$<BOOL:${WIN32}>, ${SRCS_WIN}, ${SRCS_UNIX}>)


# # Add archive as a resource for self-extraction
# add_dependencies("installer" "archive")