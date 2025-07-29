cmake_minimum_required(VERSION 3.28)
idf_component_register(
    SRCS "Sakana.c"
    INCLUDE_DIRS "."
    REQUIRES lvgl
)