# Additional clean files
cmake_minimum_required(VERSION 3.16)

if("${CONFIG}" STREQUAL "" OR "${CONFIG}" STREQUAL "")
  file(REMOVE_RECURSE
  [[C:\_data\github\mLabCuriosity\fw\mLabCuriosity\out\mLabCuriosity]]
  )
endif()
