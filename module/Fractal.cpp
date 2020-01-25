#include "Fractal.hpp"

#include "common/Logging.hpp"

#include <exception>

namespace module {

/**
 * @brief Construct a new Fractal:: Fractal object
 *
 */
Fractal::Fractal() {
  for (size_t y = 0; y < FRACTAL_SIZE; ++y) {
    for (size_t x = 0; x < FRACTAL_SIZE; ++x) {
      // Fractal is -1.5 to 1.5
      math::Complex seed(x * 3.0 / FRACTAL_SIZE - 1.5,
                         y * 3.0 / FRACTAL_SIZE - 1.5);
      fractal[y][x] = countInterations(seed);
    }
  }
}

/**
 * @brief Count the number of iteration required for a seed to diverge
 *
 * @param seed complex number seed
 * @return uint8_t number of iterations, 255 if it did not diverge
 */
uint8_t Fractal::countInterations(math::Complex seed) {
  uint8_t count = 0;
  while (count < 255 && seed.getMagnitude() < 1.0) {
    seed = seed * seed + math::Complex(0.1, 0.1);
    ++count;
  }
  return count;
}

/**
 * @brief Print the fractal to the screen
 *
 */
void Fractal::print() {
  for (size_t y = 0; y < FRACTAL_SIZE; ++y) {
    char buf[FRACTAL_SIZE + 1];
    buf[FRACTAL_SIZE] = '\0';
    for (size_t x = 0; x < FRACTAL_SIZE; ++x) {
      // Fractal is -1.5 to 1.5
      buf[x] = (fractal[y][x] >> 5) + '0';
    }
    SPDLOG_INFO(buf);
  }
}

}  // namespace module

/**
 * @brief Main entry point for program
 *
 * @return int zero on success, non-zero on failure
 */
int main() {
  try {
    common::logging::configure("log.log", true);
  } catch (const std::exception& e) {
    // printf(e.what());
  }

  module::Fractal fractal;
  fractal.print();

  return 0;
}