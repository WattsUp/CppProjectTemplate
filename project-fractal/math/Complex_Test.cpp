#include "Complex.hpp"
#include <cmath>

#include <gtest/gtest.h>

class ComplexTest : public ::testing::Test {
 protected:
  fractal::math::Complex a{3.0, -4.0};   
  fractal::math::Complex b{-15.0, 2.0}; 
  fractal::math::Complex c{-37.0, 66.0};

  virtual void SetUp(){};

  virtual void TearDown(){};
};

TEST_F(ComplexTest, Add) {
  fractal::math::Complex result = a + b;
  EXPECT_DOUBLE_EQ(result.getReal(), -12.0);
  EXPECT_DOUBLE_EQ(result.getImag(), -2.0);
}

TEST_F(ComplexTest, Subtract) {
  fractal::math::Complex result = a - b;
  EXPECT_DOUBLE_EQ(result.getReal(), 18.0);
  EXPECT_DOUBLE_EQ(result.getImag(), -6.0);
}

TEST_F(ComplexTest, Multiply) {
  fractal::math::Complex result = a * b;
  EXPECT_DOUBLE_EQ(result.getReal(), -37.0);
  EXPECT_DOUBLE_EQ(result.getImag(), 66.0);
}

TEST_F(ComplexTest, Divide) {
  fractal::math::Complex result = c / a;
  EXPECT_DOUBLE_EQ(result.getReal(), -15.0);
  EXPECT_DOUBLE_EQ(result.getImag(), 2.0);
}

TEST_F(ComplexTest, DivideByZero) {
  fractal::math::Complex result = c / fractal::math::Complex{0.0, 0.0};
  EXPECT_TRUE(std::isnan(result.getReal()));
  EXPECT_TRUE(std::isnan(result.getImag()));
}

TEST_F(ComplexTest, Magnitude) {
  EXPECT_DOUBLE_EQ(a.getMagnitude(), 5.0);
}