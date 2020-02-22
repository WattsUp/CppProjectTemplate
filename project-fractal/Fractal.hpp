#ifndef _MODULE_FRACTAL_H_
#define _MODULE_FRACTAL_H_

#include "math/Complex.hpp"

#include <stdint.h>

namespace module {

class Fractal {
 public:
  Fractal();

  void print();

 private:
  uint8_t countInterations(math::Complex seed);

  static const size_t FRACTAL_SIZE = 32;

  uint8_t fractal[FRACTAL_SIZE][FRACTAL_SIZE];
};

}  // namespace module

#endif /* _MODULE_FRACTAL_H_ */