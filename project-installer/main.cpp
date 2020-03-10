#include <spdlog/spdlog.h>

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
#endif /* WIN32 */
  spdlog::info("Installing with arguments: {}", lpCmdLine);
  return 0;
}