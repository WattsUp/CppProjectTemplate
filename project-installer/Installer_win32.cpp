#include "Installer.h"

#include "Resources.h"
#include "common/Logging.hpp"

#include <Windows.h>
#include <fstream>

namespace installer {

/**
 * @brief Extract the archive to the install folder
 *
 * @param path to save the extracted contents to
 */
void extractArchive(char* path) {
  HRSRC res    = ::FindResource(NULL, MAKEINTRESOURCE(RES_ARCHIVE), RT_RCDATA);
  HGLOBAL data = ::LoadResource(NULL, res);
  void* pData  = ::LockResource(data);
  size_t size  = ::SizeofResource(NULL, res);

  wchar_t tempPath[128];
  if (!GetTempPath(128, tempPath)) {
    spdlog::error("Failed to get temporary path: {}", ::GetLastError());
    return;
  }
  std::wstring archivePath = std::wstring(tempPath) + L"archive.zip";

  spdlog::info(L"Saving archive to {}", archivePath);
  std::ofstream file(archivePath, std::ios::out | std::ios::binary);
  file.write((char*)pData, size);
  file.close();

  spdlog::info("Extracting archive to {}", path);
  std::this_thread::sleep_for(std::chrono::seconds(10));

  if (!::DeleteFile(archivePath.c_str())) {
    spdlog::error("Failed to delete archive: {}", ::GetLastError());
    return;
  }
}

void install() {
  extractArchive(".");
}

}  // namespace installer