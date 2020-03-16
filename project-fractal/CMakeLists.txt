add_subdirectory(math)

set (SRCS
  "Fractal.cpp"
)

if (WIN32)
  list(APPEND SRCS "Fractal_win32.rc")
  set_property(SOURCE "Fractal_win32.rc" APPEND PROPERTY OBJECT_DEPENDS
    "${CMAKE_SOURCE_DIR}/bin/wattsup314.ico"
    "${CMAKE_SOURCE_DIR}/common/Version.h"
  )
  target_compile_definitions("fractal" PRIVATE
    "RC_VERSION_1=${${PROJECT_NAME}_VERSION_MAJOR}"
    "RC_VERSION_2=${${PROJECT_NAME}_VERSION_MINOR}"
    "RC_VERSION_3=${${PROJECT_NAME}_VERSION_PATCH}"
    "RC_VERSION_4=${${PROJECT_NAME}_VERSION_AHEAD}"
    "RC_VERSION=\"${${PROJECT_NAME}_VERSION_STRING_FULL}\""
  )
endif()

target_sources("fractal" PRIVATE ${SRCS})