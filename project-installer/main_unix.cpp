#include <spdlog/spdlog.h>
#include <string>

/**
 * @brief Main entry point for program
 *
 * @param argc count of arguments
 * @param argv array of arguments
 * @return int zero on success, non-zero on failure
 */
int main(int argc, char* argv[]) {
  std::string argsString;
  for (int i = 0; i < argc; ++i) {
    argsString += *(argv + i);
    argsString += " ";
  }
  const char* lpCmdLine = argsString.c_str();
  spdlog::info("Installing with arguments: {}", lpCmdLine);
  return 0;
}