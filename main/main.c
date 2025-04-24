
#include "hardware_cfg.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_heap_caps.h"
#include "esp_lvgl_port.h"

static lv_display_t *display_obj;
// static uint8_t *render_buf[RENDER_BUF_SIZE];

LV_IMAGE_DECLARE(clown);
// LV_IMAGE_DECLARE(clown_rgb8);

// void flush_cb(lv_display_t * display)
// {
//     lv_display_flush_ready(display);
// }

void lv_example_get_started_1(void)
{
    /*Change the active screen's background color*/
    lv_obj_set_style_bg_color(lv_screen_active(), lv_color_hex(0x003a57), LV_PART_MAIN);

    /*Create a white label, set its text and align it to the center*/
    lv_obj_t * label = lv_label_create(lv_screen_active());
    lv_label_set_text(label, "Hello world");
    lv_obj_set_style_text_color(lv_screen_active(), lv_color_hex(0xffffff), LV_PART_MAIN);
    lv_obj_align(label, LV_ALIGN_CENTER, 0, 0);
}

void app_main(void)
{
    //-----------------PHYSICAL LCD INIT-------------------
    // SPI initialization
    const spi_bus_config_t buscfg = GC9A01_PANEL_BUS_SPI_CONFIG(LCD_PIN_NUM_SCLK, LCD_PIN_NUM_MOSI, MAX_TRANSF_SIZE);
    spi_bus_initialize(LCD_SPI_HOST, &buscfg, SPI_DMA_CH_AUTO);

    // LCD I/O initialization (attaching to SPI)
    esp_lcd_panel_io_handle_t io_handle = NULL;
    const esp_lcd_panel_io_spi_config_t io_config = GC9A01_PANEL_IO_SPI_CONFIG(LCD_PIN_NUM_CS, LCD_PIN_NUM_DC,
        NULL, NULL); // TODO: ensure that flush_cb is appropriate for this
    ESP_ERROR_CHECK(esp_lcd_new_panel_io_spi((esp_lcd_spi_bus_handle_t)LCD_SPI_HOST, &io_config, &io_handle));

    esp_lcd_panel_handle_t lcd_panel_handle = NULL;
    const esp_lcd_panel_dev_config_t lcd_panel_config = {
        .reset_gpio_num = LCD_PIN_NUM_RST,
#if ESP_IDF_VERSION < ESP_IDF_VERSION_VAL(5, 0, 0)
        .color_space = ESP_LCD_COLOR_SPACE_BGR,
#else
        .rgb_endian = LCD_RGB_ENDIAN_BGR,
#endif
        .bits_per_pixel = LCD_BPP,
    };

    // NOTE: display panel is the physical hardware displaying the pixels
    // gc9a01 panel driver init (install)
    ESP_ERROR_CHECK(esp_lcd_new_panel_gc9a01(io_handle, &lcd_panel_config, &lcd_panel_handle));
    ESP_ERROR_CHECK(esp_lcd_panel_reset(lcd_panel_handle));
    ESP_ERROR_CHECK(esp_lcd_panel_init(lcd_panel_handle));
    ESP_ERROR_CHECK(esp_lcd_panel_invert_color(lcd_panel_handle, true)); // ? TODO: clarify if it's needed
    ESP_ERROR_CHECK(esp_lcd_panel_mirror(lcd_panel_handle, true, false)); // ? TODO: clarify if it's needed
    ESP_ERROR_CHECK(esp_lcd_panel_disp_on_off(lcd_panel_handle, true));

    //-----------------LVGL INIT-------------------
    const lvgl_port_cfg_t lvgl_cfg = ESP_LVGL_PORT_INIT_CONFIG();
    ESP_ERROR_CHECK(lvgl_port_init(&lvgl_cfg));

    const lvgl_port_display_cfg_t disp_cfg = 
    {
        .io_handle = io_handle,
        .panel_handle = lcd_panel_handle,
        .buffer_size = LCD_WIDTH_RES*LCD_HEIGHT_RES,
        .double_buffer = false, // TODO: try true
        .hres = LCD_WIDTH_RES,
        .vres = LCD_HEIGHT_RES,
        .monochrome = false,
        .color_format = LV_COLOR_FORMAT_RGB565,
        .rotation = {
            .swap_xy = false,
            .mirror_x = true,
            .mirror_y = false,
        },
        .flags = {
            .buff_dma = true,
            .swap_bytes = false,
            .direct_mode = true, // TODO: try full refresh and partial
        }
    };
    display_obj = lvgl_port_add_disp(&disp_cfg);


    lv_obj_t *scr = lv_scr_act();

    /* Create image */
    // lv_obj_t *test_img = lv_img_create(scr);
    // lv_img_set_src(test_img, &clown);
    // // lv_img_set_src(test_img, &clown_rgb8);
    // lv_obj_align(test_img, LV_ALIGN_CENTER, 0, 0);

    lv_example_get_started_1();

    // lvgl_port_lock(0);
    // display_obj = lv_display_create(LCD_WIDTH_RES, LCD_HEIGHT_RES);
    // lv_display_set_buffers(display_obj, render_buf, NULL, sizeof(render_buf), LV_DISPLAY_RENDER_MODE_DIRECT);
    // lv_display_set_flush_cb(display_obj, my_flush_cb);
}