#ifndef _MODULE_MATH_COMPLEX_H_
#define _MODULE_MATH_COMPLEX_H_

namespace module {
namespace math {

class Complex {
 private:
  double real;
  double imag;

 public:
  Complex(double r = 0.0, double i = 0.0);

  double getReal() const;
  double getImag() const;
  double getMagnitude() const;

  friend Complex operator+(const Complex& left, const Complex& right) {
    return Complex(left.real + right.real, left.imag + right.imag);
  }

  friend Complex operator-(const Complex& left, const Complex& right) {
    return Complex(left.real - right.real, left.imag - right.imag);
  }

  friend Complex operator*(const Complex& left, const Complex& right) {
    return Complex(left.real * right.real - left.imag * right.imag,
                   left.imag * right.real + left.real * right.imag);
  }

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
}  // namespace module

#endif /* _MODULE_MATH_COMPLEX_H_ */