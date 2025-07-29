# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "/home/arkeks/Software/esp/esp-idf-v5.4.1/esp-idf/components/bootloader/subproject"
  "/home/arkeks/projects/esp-bsp/components/lcd/esp_lcd_gc9a01/test_apps/build/bootloader"
  "/home/arkeks/projects/esp-bsp/components/lcd/esp_lcd_gc9a01/test_apps/build/bootloader-prefix"
  "/home/arkeks/projects/esp-bsp/components/lcd/esp_lcd_gc9a01/test_apps/build/bootloader-prefix/tmp"
  "/home/arkeks/projects/esp-bsp/components/lcd/esp_lcd_gc9a01/test_apps/build/bootloader-prefix/src/bootloader-stamp"
  "/home/arkeks/projects/esp-bsp/components/lcd/esp_lcd_gc9a01/test_apps/build/bootloader-prefix/src"
  "/home/arkeks/projects/esp-bsp/components/lcd/esp_lcd_gc9a01/test_apps/build/bootloader-prefix/src/bootloader-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/home/arkeks/projects/esp-bsp/components/lcd/esp_lcd_gc9a01/test_apps/build/bootloader-prefix/src/bootloader-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/home/arkeks/projects/esp-bsp/components/lcd/esp_lcd_gc9a01/test_apps/build/bootloader-prefix/src/bootloader-stamp${cfgdir}") # cfgdir has leading slash
endif()
