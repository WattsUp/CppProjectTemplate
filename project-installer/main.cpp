#include "common/Logging.hpp"
#include "common/Version.h"

#include "Installer.h"

#include <cstdio>
#include <exception>

/**
 * @brief Main entry point for program
 *
 * @param argc count of arguments
 * @param argv array of arguments
 * @return int zero on success, non-zero on failure
 */
int main(int argc, char* argv[]) {
  try {
#if DEBUG
    spdlog::info(VERSION_STRING_FULL);
    spdlog::set_level(spdlog::level::debug);
#else  /* DEBUG */
    spdlog::info(VERSION_STRING);
#endif /* DEBUG */

    for (int i = 0; i < argc; ++i) {
      // NOLINTNEXTLINE (cppcoreguidelines-pro-bounds-pointer-arithmetic)
      spdlog::info("Argument: {}", argv[i]);
    }
  } catch (std::exception& e) {
    // Catch exceptions from spdlog
    puts(e.what());
  }

  installer::install();

  return 0;
}