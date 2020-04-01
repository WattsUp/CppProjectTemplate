#ifndef _FRACTAL_MATH_COMPLEX_H_
#define _FRACTAL_MATH_COMPLEX_H_

namespace fractal {
namespace math {

/**
 * @brief Complex number class with real and imaginary components
 *
 * Holds two floting point numbers for real and imaginary components of a
 * complex number. Allows arithmetic expressions to be evaluated with complex
 * numbers.
 *
 */
class Complex {
 private:
  double real;  ///< Real component
  double imag;  ///< Imaginary component

 public:
  explicit Complex(double r = 0.0, double i = 0.0);

  double getReal() const;
  double getImag() const;
  double getMagnitude() const;

  /**
   * @brief Addition operator
   * Sums the real and imaginary components separately
   *
   * @param left hand side
   * @param right hand side
   * @return Complex result
   */
  friend Complex operator+(const Complex& left, const Complex& right) {
    return Complex(left.real + right.real, left.imag + right.imag);
  }

  /**
   * @brief Subtraction operator
   * Subtracts the real and imaginary componets separately
   *
   * @param left hand side
   * @param right hand side
   * @return Complex result
   */
  friend Complex operator-(const Complex& left, const Complex& right) {
    return Complex(left.real - right.real, left.imag - right.imag);
  }

  /**
   * @brief Multiplication operator
   * Multiplies the complex numbers together following imaginary number
   * convention \f$(a+bi)(c+di)=(a*c-b*d)+(a*d+b*c)i\f$
   *
   * @param left hand side
   * @param right hand side
   * @return Complex result
   */
  friend Complex operator*(const Complex& left, const Complex& right) {
    return Complex(left.real * right.real - left.imag * right.imag,
                   left.imag * right.real + left.real * right.imag);
  }

  /**
   * @brief Division operator
   * Multiplies the complex numbers together following imaginary number
   * convention \f$\frac{a+bi}{c+di}=\frac{(a+bi)*(c-di)}{c^2+d^2}\f$
   *
   * @param left hand side (quotient)
   * @param right hand side (divisor)
   * @return Complex result
   */
  friend Complex operator/(const Complex& left, const Complex& right) {
    // Denominator = right * conj(right)
    double denominator = right.real * right.real + right.imag * right.imag;
    // Numerator = left * conj(right)
    return Complex(
        (left.real * right.real + left.imag * right.imag) / denominator,
        (left.imag * right.real - left.real * right.imag) / denominator);
  }
};

}  // namespace math
}  // namespace fractal

#endif /* _FRACTAL_MATH_COMPLEX_H_ */