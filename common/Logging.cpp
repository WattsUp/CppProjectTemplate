#include "Logging.hpp"

#include <spdlog/sinks/rotating_file_sink.h>
#include <spdlog/spdlog.h>
#include <vector>

namespace common {
namespace logging {

/**
 * @brief Configure logging with a file, optional console, or neither
 *
 * @param filename of the log file, nullptr for no logging to file
 * @param showConsole will open a console output window if true
 */
void configure(const char* filename, bool showConsole) {
  std::vector<spdlog::sink_ptr> sinks;

  // if (showConsole) {
  //   // Create a console, remove its close button, redirect stdout to it
  //   if (AllocConsole()) {
  //     HWND hwnd = GetConsoleWindow();
  //     if (hwnd) {
  //       HMENU hMenu = GetSystemMenu(hwnd, FALSE);
  //       if (hMenu)
  //         DeleteMenu(hMenu, SC_CLOSE, MF_BYCOMMAND);
  //     }
  //     freopen_s((FILE**)stdout, "CONOUT$", "w", stdout);
  //   } else
  //     throw std::exception("Log console initialization failed");
  //   sinks.emplace_back(
  //       std::make_shared<spdlog::sinks::wincolor_stdout_sink_mt>());
  // }

  // Create a file sink
  if (filename) {
    sinks.emplace_back(std::make_shared<spdlog::sinks::rotating_file_sink_mt>(
        filename, MAX_FILE_SIZE, MAX_FILE_COUNT));
  }

  std::shared_ptr<spdlog::logger> logger =
      std::make_shared<spdlog::logger>("", begin(sinks), end(sinks));
  spdlog::set_default_logger(logger);
#ifdef DEBUG
  spdlog::set_level(spdlog::level::debug);
#endif

  spdlog::set_pattern("[%P:%t:%m%d/%H:%M:%S.%e][%=8l][%g(%#)] %v");
}
}  // namespace logging
}  // namespace common