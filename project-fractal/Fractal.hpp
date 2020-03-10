#ifndef _FRACTAL_FRACTAL_H_
#define _FRACTAL_FRACTAL_H_

#include "math/Complex.hpp"

#include <array>
#include <cstdint>

namespace fractal {

class Fractal {
 public:
  Fractal();

  void print();

 private:
  uint8_t countInterations(math::Complex seed);

  static constexpr size_t SIZE     = 32;
  static constexpr double VIEW_MAX = 1.0;
  static constexpr uint8_t MAX_ITR = 255;

  std::array<std::array<uint8_t, SIZE>, SIZE> fractal{{}};
};

}  // namespace fractal

#endif /* _FRACTAL_FRACTAL_H_ */