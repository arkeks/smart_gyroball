# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "/home/seradya/esp/esp-idf/components/bootloader/subproject"
  "/home/seradya/Documents/Programming/smart_gyroball/build/bootloader"
  "/home/seradya/Documents/Programming/smart_gyroball/build/bootloader-prefix"
  "/home/seradya/Documents/Programming/smart_gyroball/build/bootloader-prefix/tmp"
  "/home/seradya/Documents/Programming/smart_gyroball/build/bootloader-prefix/src/bootloader-stamp"
  "/home/seradya/Documents/Programming/smart_gyroball/build/bootloader-prefix/src"
  "/home/seradya/Documents/Programming/smart_gyroball/build/bootloader-prefix/src/bootloader-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/home/seradya/Documents/Programming/smart_gyroball/build/bootloader-prefix/src/bootloader-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/home/seradya/Documents/Programming/smart_gyroball/build/bootloader-prefix/src/bootloader-stamp${cfgdir}") # cfgdir has leading slash
endif()
