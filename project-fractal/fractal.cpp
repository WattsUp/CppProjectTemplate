#include "fractal.hpp"

#include "common/logging.hpp"

namespace fractal {

/**
 * @brief Construct a new Fractal object
 *
 */
Fractal::Fractal() {
  for (size_t y = 0; y < SIZE; ++y) {
    for (size_t x = 0; x < SIZE; ++x) {
      // Fractal is -VIEW_MAX to VIEW_MAX
      math::Complex seed(
          static_cast<double>(x) * VIEW_MAX * 2 / SIZE - VIEW_MAX,
          static_cast<double>(y) * VIEW_MAX * 2 / SIZE - VIEW_MAX);
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
    /// Using the Mandelbrot set formula \f$z_{n+1}=z_n^2+c\f$
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
      buf.at(x) = static_cast<char>((fractal.at(y).at(x) >> uint8_t{5}) + '0');
    }
    spdlog::info(buf.data());
  }
}

}  // namespace fractal
