#ifndef _FRACTAL_FRACTAL_H_
#define _FRACTAL_FRACTAL_H_

#include "math/complex.hpp"

#include <array>
#include <cstdint>

namespace fractal {

/**
 * @brief Fractal generation class
 * Creates an array of iteration counts. Runs a fractal formula on the
 * corresponding coordinate and calculates the number of iterations to converge
 * or diverge. Displays this information as a 2D graph.
 *
 */
class Fractal {
 public:
  Fractal();

  void print();

 private:
  uint8_t countInterations(math::Complex seed);

  static constexpr size_t SIZE     = 32;   ///< Number of grid points
  static constexpr double VIEW_MAX = 1.0;  ///< Bounds of grid coordinates
  static constexpr uint8_t MAX_ITR = 255;  ///< Maximum iterations to converge

  /// 2D array of grid points to count iterations of the fractal formula
  std::array<std::array<uint8_t, SIZE>, SIZE> fractal{{}};
};

}  // namespace fractal

#endif /* _FRACTAL_FRACTAL_H_ */