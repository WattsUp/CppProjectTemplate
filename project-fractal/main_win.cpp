#include "Fractal.hpp"

#include "common/Logging.hpp"
#include "common/Version.h"

#include <Windows.h>

#include <cstdio>
#include <exception>

/**
 * @brief Main entry point for program
 *
 * @return int zero on success, non-zero on failure
 */
int WINAPI WinMain(HINSTANCE /* hInstance */,
                   HINSTANCE /* hPrevInstance */,
                   char* /* args */,
                   int /* nShowCmd */) {
  try {
    common::logging::configure("log.log", true);
  } catch (const std::exception& e) {
    puts(e.what());
  }

  spdlog::info(VERSION_STRING);

  fractal::Fractal fractal;
  fractal.print();
  std::this_thread::sleep_for(std::chrono::seconds(2));

  return 0;
}