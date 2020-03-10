#ifndef _COMMON_LOGGING_H_
#define _COMMON_LOGGING_H_

#include <spdlog/spdlog.h>

namespace common {
namespace logging {

const size_t MAX_FILE_SIZE  = 5 * 1024 * 1024;  // 5MiB
const size_t MAX_FILE_COUNT = 3;

void configure(const char* filename, bool useConsole);

}  // namespace logging
}  // namespace common

#endif /* _COMMON_LOGGING_H_ */