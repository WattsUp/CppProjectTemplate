#include "Installer.h"

#include "Resources.h"
#include "common/Logging.hpp"
#include "miniz.h"

#include <Windows.h>
#include <fstream>

namespace installer {

/**
 * @brief Extract the archive to the install folder
 *
 * @param path to save the extracted contents to
 * @return bool true when extraction was successful
 */
bool extractArchive(char* path) {
  HRSRC res    = ::FindResource(NULL, MAKEINTRESOURCE(RES_ARCHIVE), RT_RCDATA);
  HGLOBAL data = ::LoadResource(NULL, res);
  void* pData  = ::LockResource(data);
  size_t size  = ::SizeofResource(NULL, res);

  spdlog::info("Extracting archive to {}", path);
  if (_mkdir(path) && errno != EEXIST) {
    spdlog::error("Failed to make directory {}: {}", path, errno);
    return false;
  }

  mz_zip_archive zip;
  memset(&zip, 0, sizeof(zip));
  if (!mz_zip_reader_init_mem(&zip, pData, size, 0)) {
    spdlog::error("Failed opening archive");
    return false;
  }

  spdlog::debug("Archive contains {} files", mz_zip_reader_get_num_files(&zip));

  for (mz_uint i = 0; i < mz_zip_reader_get_num_files(&zip); i++) {
    mz_zip_archive_file_stat stat;
    if (!mz_zip_reader_file_stat(&zip, i, &stat)) {
      spdlog::error("Failed getting file {}'s statistics", i);
      mz_zip_reader_end(&zip);
      return false;
    }
    spdlog::debug("\"{}\" {}B => {}B", stat.m_filename, stat.m_comp_size,
                  stat.m_uncomp_size);

    if (mz_zip_reader_is_file_a_directory(&zip, i)) {
      std::string filePath = std::string{path} + "/" + stat.m_filename;
      if (_mkdir(filePath.c_str()) && errno != EEXIST) {
        spdlog::error("Failed to make directory {}: {}", path, errno);
        return false;
      }
    } else {
      std::string filePath = std::string{path} + "/" + stat.m_filename;
      if (!mz_zip_reader_extract_to_file(&zip, i, filePath.c_str(), 0)) {
        spdlog::error("Failed writing file {} to {}", i, filePath.c_str());
        mz_zip_reader_end(&zip);
        return false;
      }
    }
  }

  mz_zip_reader_end(&zip);

  return true;
}  // namespace installer

void install() {
  if (!extractArchive("temp")) {
    spdlog::error("Error occurred whilst extracting archive");
  }
}

}  // namespace installer