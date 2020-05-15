#include "complex.hpp"

#include <cmath>

namespace fractal {
namespace math {

/**
 * @brief Construct a new Complex object
 *
 * @param r real component
 * @param i imaginary component
 */
Complex::Complex(double r, double i) : real(r), imag(i) {}

/**
 * @brief Get the real component
 *
 * @return double
 */
double Complex::getReal() const {
  return real;
}

/**
 * @brief Get the imaginary component
 *
 * @return double
 */
double Complex::getImag() const {
  return imag;
}

/**
 * @brief Get the magnitude of the complex number
 *
 * @return double
 */
double Complex::getMagnitude() const {
  return sqrt(real * real + imag * imag);
}

}  // namespace math
}  // namespace fractal