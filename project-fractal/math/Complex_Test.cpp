#include "Complex.hpp"
#include <cmath>

#include <gtest/gtest.h>

class ComplexTest : public ::testing::Test {
 protected:
  module::math::Complex a{3.0, -4.0};
  module::math::Complex b{-15.0, 2.0};
  module::math::Complex c{-37.0, 66.0};

  virtual void SetUp(){};

  virtual void TearDown(){};
};

// NOLINTNEXTLINE
TEST_F(ComplexTest, Add) {
  module::math::Complex result = a + b;
  EXPECT_DOUBLE_EQ(result.getReal(), -12.0);
  EXPECT_DOUBLE_EQ(result.getImag(), -2.0);
}

// NOLINTNEXTLINE
TEST_F(ComplexTest, Subtract) {
  module::math::Complex result = a - b;
  EXPECT_DOUBLE_EQ(result.getReal(), 18.0);
  EXPECT_DOUBLE_EQ(result.getImag(), -6.0);
}

// NOLINTNEXTLINE
TEST_F(ComplexTest, Multiply) {
  module::math::Complex result = a * b;
  EXPECT_DOUBLE_EQ(result.getReal(), -37.0);
  EXPECT_DOUBLE_EQ(result.getImag(), 66.0);
}

// NOLINTNEXTLINE
TEST_F(ComplexTest, Divide) {
  module::math::Complex result = c / a;
  EXPECT_DOUBLE_EQ(result.getReal(), -15.0);
  EXPECT_DOUBLE_EQ(result.getImag(), 2.0);
}

// NOLINTNEXTLINE
TEST_F(ComplexTest, DivideByZero) {
  module::math::Complex result = c / module::math::Complex{0.0, 0.0};
  EXPECT_TRUE(isnan(result.getReal()));
  EXPECT_TRUE(isnan(result.getImag()));
}

// NOLINTNEXTLINE
TEST_F(ComplexTest, Magnitude) {
  EXPECT_DOUBLE_EQ(a.getMagnitude(), 5.0);
}