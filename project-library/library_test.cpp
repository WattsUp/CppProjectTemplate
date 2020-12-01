#include "library/library.h"

#include <gtest/gtest.h>

TEST(Library, libraryAdd) {
  EXPECT_EQ(uint32_t{123}, libraryAdd(uint32_t{120}, uint32_t{3}));
}