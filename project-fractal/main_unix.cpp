#include "fractal.hpp"

#include "common/logging.hpp"
#include "common/version.h"

#include <cstdio>
#include <exception>

/**
 * @brief Main entry point for program
 *
 * @return int zero on success, non-zero on failure
 */
int main(int /* argc */, char* /* argv */[]) {
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