#include <spdlog/spdlog.h>
#include <string>

/**
 * @brief Main entry point for program
 *
 * @return int zero on success, non-zero on failure
 */
#ifdef WIN32
int WINAPI WinMain(HINSTANCE /* hInstance */,
                   HINSTANCE /* hPrevInstance */,
                   char* lpCmdLine,
                   int /* nShowCmd */) {
#else  /* WIN32 */
int main(int argc, char* argv[]) {
  std::string argsString = "";
  for (int i = 0; i < argc; ++i)
    argsString = argsString + argv[i] + " ";
  const char* lpCmdLine = argsString.c_str();
#endif /* WIN32 */
  spdlog::info("Installing with arguments: {}", lpCmdLine);
  return 0;
}