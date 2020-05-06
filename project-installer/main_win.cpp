#include <spdlog/spdlog.h>
#include <string>

/**
 * @brief Main entry point for program
 *
 * @param lpCmdLine command line string
 * @return int zero on success, non-zero on failure
 */
int WINAPI WinMain(HINSTANCE /* hInstance */,
                   HINSTANCE /* hPrevInstance */,
                   char* lpCmdLine,
                   int /* nShowCmd */) {
  spdlog::info("Installing with arguments: {}", lpCmdLine);
  return 0;
}