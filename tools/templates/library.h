#ifndef _LIBRARY_H_
#define _LIBRARY_H_

#ifdef _MSC_VER
#if LIBRARY_CREATE_SHARED_LIBRARY
#define LIBRARY_API __declspec(dllexport)
#elif LIBRARY_LINKED_AS_SHARED_LIBRARY
#define LIBRARY_API __declspec(dllimport)
#endif
#elif __GNUC__ >= 4 || defined(__clang__)
#define LIBRARY_API __attribute__((visibility("default")))
#endif /* _MSC_VER */

#ifndef LIBRARY_API
#define LIBRARY_API
#endif /* LIBRARY_API */

/* stdint.h is not available on older MSVC */
#if defined(_MSC_VER) && (_MSC_VER < 1600) && (!defined(_STDINT)) && \
    (!defined(_STDINT_H))
typedef unsigned __int8 uint8_t;
typedef unsigned __int16 uint16_t;
typedef unsigned __int32 uint32_t;
#else
#include <stdint.h>
#endif

/**
 * @brief Add two numbers using the library
 *
 * @param a
 * @param b
 * @return uint32_t a + b
 */
uint32_t LIBRARY_API libraryAdd(uint32_t a, uint32_t b);

#endif /* _LIBRARY_H_ */