#include "esp_log.h"
#include "driver/spi_master.h"
#include "esp_lcd_gc9a01.h"
#include "driver/gpio.h"
#include "lvgl.h"

// SPI and GPIO Configuration (confirm with your hardware)
#define LCD_SPI_HOST        (SPI2_HOST)
#define LCD_PIN_NUM_MOSI    (GPIO_NUM_15) // SDA on schematic
#define LCD_PIN_NUM_SCLK    (GPIO_NUM_14) // SCL on schematic
#define LCD_PIN_NUM_CS      (GPIO_NUM_5)  // CS on schematic
#define LCD_PIN_NUM_DC      (GPIO_NUM_27) // DC on schematic
#define LCD_PIN_NUM_RST     (GPIO_NUM_33) // RES on schematic
#define LCD_PIN_NUM_BL      (GPIO_NUM_32) // BL on schematic

// LCD
#define LCD_WIDTH_RES  (240)
#define LCD_HEIGHT_RES (240)
#define LCD_BPP        (16)

// LVGL
#define MAX_TRANSF_SIZE (LCD_HEIGHT_RES * 80 * LCD_BPP / 8) // TODO: find out proper value (this is taken from example)
#define RENDER_BUF_SIZE (LCD_WIDTH_RES*LCD_HEIGHT_RES*LV_COLOR_FORMAT_GET_SIZE(LV_COLOR_FORMAT_RGB565))