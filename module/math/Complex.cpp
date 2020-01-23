#include "Complex.hpp"

namespace module {
namespace math {

/**
 * @brief Construct a new Complex:: Complex object
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
double Complex::getReal() const { return real; }

/**
 * @brief Get the imaginary component
 *
 * @return double
 */
double Complex::getImag() const { return imag; }

} // namespace math
} // namespace module