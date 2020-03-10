#include "Fractal.hpp"

#include "common/Logging.hpp"
#include "common/Version.h"

#ifdef WIN32
#include <Windows.h>
#endif /* WIN32 */

#include <cstdio>
#include <exception>

namespace module {

/**
 * @brief Construct a new Fractal:: Fractal object
 *
 */
Fractal::Fractal() {
  for (size_t y = 0; y < SIZE; ++y) {
    for (size_t x = 0; x < SIZE; ++x) {
      // Fractal is -VIEW_MAX to VIEW_MAX
      math::Complex seed(x * VIEW_MAX * 2 / SIZE - VIEW_MAX,
                         y * VIEW_MAX * 2 / SIZE - VIEW_MAX);
      fractal.at(y).at(x) = countInterations(seed);
    }
  }
}

/**
 * @brief Count the number of iteration required for a seed to diverge
 *
 * @param seed complex number seed
 * @return uint8_t number of iterations, MAX_ITR if it did not diverge
 */
uint8_t Fractal::countInterations(math::Complex seed) {
  uint8_t count = 0;
  math::Complex value(0, 0);
  while (count < MAX_ITR && value.getMagnitude() < 1.0) {
    value = value * value + seed;
    ++count;
  }
  return count;
}

/**
 * @brief Print the fractal to the screen
 *
 */
void Fractal::print() {
  for (size_t y = 0; y < SIZE; ++y) {
    std::array<char, SIZE + 1> buf{""};
    buf.at(SIZE) = '\0';
    for (size_t x = 0; x < SIZE; ++x) {
      // Fractal is -1.5 to 1.5
      // NOLINTNEXTLINE (bug-prone-narrowing-conversions)
      buf.at(x) = (fractal.at(y).at(x) >> uint8_t{5}) + '0';
    }
    spdlog::info(buf.data());
  }
}

}  // namespace module

/**
 * @brief Main entry point for program
 *
 * @return int zero on success, non-zero on failure
 */
#ifdef WIN32
int WINAPI WinMain(HINSTANCE /* hInstance */,
                   HINSTANCE /* hPrevInstance */,
                   char* /* args */,
                   int /* nShowCmd */) {
#else  /* WIN32 */
int main(int argc, char* argv[]) {
#endif /* WIN32 */

  try {
    common::logging::configure("log.log", true);
  } catch (const std::exception& e) {
    puts(e.what());
  }

  spdlog::info(VERSION_STRING);

  module::Fractal fractal;
  fractal.print();
  std::this_thread::sleep_for(std::chrono::seconds(2));

  return 0;
}