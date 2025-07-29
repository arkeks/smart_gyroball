# The following four lines of boilerplate have to be in your project's CMakeLists
# in this exact order for cmake to work correctly
cmake_minimum_required(VERSION 3.16)


include($ENV{IDF_PATH}/tools/cmake/project.cmake)
list(APPEND EXTRA_COMPONENT_DIRS 
components/lvgl
components/esp_lcd_gc9a01
components/esp_lvgl_port
components/fonts
components/img
)
project(Lab4_1)
