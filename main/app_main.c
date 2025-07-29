/* MQTT (over TCP) Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include "hardware_cfg.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_heap_caps.h"
#include "esp_lvgl_port.h"

#include "driver/gpio.h"

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <inttypes.h>
#include "esp_system.h"
#include "nvs_flash.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "protocol_examples_common.h"

#include "esp_log.h"
#include "mqtt_client.h"

#include "driver/gpio.h"

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "sdkconfig.h"


static const char *TAG = "mqtt_example";

// lvgl global vars
static lv_display_t *display_obj;
static esp_lcd_panel_handle_t lcd_panel_handle;
static esp_lcd_panel_io_handle_t io_handle;
lv_obj_t *screen;
LV_IMAGE_DECLARE(circle);
LV_FONT_DECLARE(Sakana);
static lv_obj_t * speed_label;
static char velocity_str[15];

// hall sensor global var
static uint32_t hall_counter;
static uint32_t prev_hall_counter;

void app_lcd_init(void)
{
    //-----------------PHYSICAL LCD INIT-------------------
    // SPI initialization
    const spi_bus_config_t buscfg = GC9A01_PANEL_BUS_SPI_CONFIG(LCD_PIN_NUM_SCLK, LCD_PIN_NUM_MOSI, MAX_TRANSF_SIZE);
    spi_bus_initialize(LCD_SPI_HOST, &buscfg, SPI_DMA_CH_AUTO);

    // LCD I/O initialization (attaching to SPI)
    io_handle = NULL;
    const esp_lcd_panel_io_spi_config_t io_config = GC9A01_PANEL_IO_SPI_CONFIG(LCD_PIN_NUM_CS, LCD_PIN_NUM_DC,
        NULL, NULL);
    ESP_ERROR_CHECK(esp_lcd_new_panel_io_spi((esp_lcd_spi_bus_handle_t)LCD_SPI_HOST, &io_config, &io_handle));

    lcd_panel_handle = NULL;
    const esp_lcd_panel_dev_config_t lcd_panel_config = {
        .reset_gpio_num = LCD_PIN_NUM_RST,
#if ESP_IDF_VERSION < ESP_IDF_VERSION_VAL(5, 0, 0)
        .color_space = ESP_LCD_COLOR_SPACE_BGR,
#else
        .rgb_endian = LCD_RGB_ENDIAN_BGR, // empirically found out that it's needed
#endif
        .bits_per_pixel = LCD_BPP,
    };

    // NOTE: display panel is the physical hardware displaying the pixels
    // gc9a01 panel driver init (install)
    ESP_ERROR_CHECK(esp_lcd_new_panel_gc9a01(io_handle, &lcd_panel_config, &lcd_panel_handle));
    ESP_ERROR_CHECK(esp_lcd_panel_reset(lcd_panel_handle));
    ESP_ERROR_CHECK(esp_lcd_panel_init(lcd_panel_handle));
    ESP_ERROR_CHECK(esp_lcd_panel_invert_color(lcd_panel_handle, true)); // empirically found out that it's needed
    ESP_ERROR_CHECK(esp_lcd_panel_mirror(lcd_panel_handle, true, false)); // empirically found out that it's needed
    ESP_ERROR_CHECK(esp_lcd_panel_disp_on_off(lcd_panel_handle, true));
}


void app_lvgl_init(void)
{
    //-----------------LVGL INIT-------------------
    // lvgl esp port init (default routine for this component)
    const lvgl_port_cfg_t lvgl_cfg = ESP_LVGL_PORT_INIT_CONFIG();
    ESP_ERROR_CHECK(lvgl_port_init(&lvgl_cfg));

        // lvgl display object creation 
    const lvgl_port_display_cfg_t disp_cfg = 
        {
            .io_handle = io_handle,
            .panel_handle = lcd_panel_handle,
            .buffer_size = (LCD_WIDTH_RES*LCD_HEIGHT_RES/2),
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
                .swap_bytes = true, // needed for correct pixel values order for this panel
                .full_refresh = false,
                .direct_mode = false, // TODO: try full refresh and partial
            }
        };

    ESP_LOGI("MEM", "LVGL buffer size1: %lu bytes", disp_cfg.buffer_size);
    // this is default display since it's the only one
    display_obj = lvgl_port_add_disp(&disp_cfg);

    // screen activation (attached to default display)
    screen = lv_scr_act();
}

static void gpio_isr_handler(void* arg)
{
    hall_counter++;
}

void app_gpio_hall_sensor_init(void)
{
    gpio_config_t io_conf = {};

    // interrupt of rising edge
    io_conf.intr_type = GPIO_INTR_NEGEDGE;

    // bit mask of the pin
    io_conf.pin_bit_mask = (1ULL << 13);

    // set as input mode
    io_conf.mode = GPIO_MODE_INPUT;

    // enable pull-up mode
    // io_conf.pull_down_en = 1;

    gpio_config(&io_conf);

    // install gpio isr service
    gpio_install_isr_service(ESP_INTR_FLAG_LEVEL3);

    // hook isr handler for specific gpio pin
    gpio_isr_handler_add(GPIO_NUM_13, gpio_isr_handler, (void*) GPIO_NUM_13);

    gpio_dump_io_configuration(stdout, (1ULL << 13));

    hall_counter = 0;
}

void velocity_show(lv_timer_t * timer)
// void velocity_show()

{
    // update velocity
    // TODO: find out how to use \n so that everything stays centered
    sprintf(velocity_str, "%ld RPM", (hall_counter*60));
    lv_label_set_text_static(speed_label, velocity_str);
    lv_obj_set_style_text_color(lv_screen_active(), lv_color_hex(0x9027ff), LV_PART_MAIN); // doesn't work without it (why?)
    prev_hall_counter = hall_counter;
    // printf("hall_counter: %ld\n", (hall_counter));
    // reset counter
    hall_counter = 0;
}

void background_init()
{
    /* Create image */
    lv_obj_t *test_img = lv_img_create(screen);
    lv_img_set_src(test_img, &circle);
    lv_obj_align(test_img, LV_ALIGN_CENTER, 0, 0);
}

void label_init()
{
    sprintf(velocity_str, "%ld RPM", (hall_counter));
    speed_label = lv_label_create(lv_screen_active());
    lv_label_set_text(speed_label, velocity_str);
    lv_obj_set_style_text_font(speed_label, &Sakana, LV_PART_MAIN);
    lv_obj_set_style_text_color(lv_screen_active(), lv_color_hex(0x9027ff), LV_PART_MAIN);
    lv_obj_align(speed_label, LV_ALIGN_CENTER, 0, 0);
}



static void log_error_if_nonzero(const char *message, int error_code)
{
    if (error_code != 0) {
        ESP_LOGE(TAG, "Last error %s: 0x%x", message, error_code);
    }
}

/*
 * @brief Event handler registered to receive MQTT events
 *
 *  This function is called by the MQTT client event loop.
 *
 * @param handler_args user data registered to the event.
 * @param base Event base for the handler(always MQTT Base in this example).
 * @param event_id The id for the received event.
 * @param event_data The data for the event, esp_mqtt_event_handle_t.
 */
static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data)
{
    ESP_LOGD(TAG, "Event dispatched from event loop base=%s, event_id=%" PRIi32 "", base, event_id);
    esp_mqtt_event_handle_t event = event_data;
    esp_mqtt_client_handle_t client = event->client;
    int msg_id;
    switch ((esp_mqtt_event_id_t)event_id) {
    case MQTT_EVENT_CONNECTED:
        ESP_LOGI(TAG, "MQTT_EVENT_CONNECTED");
        msg_id = esp_mqtt_client_publish(client, "speed/values", "0", 0, 1, 0);
        ESP_LOGI(TAG, "sent publish successful, msg_id=%d", msg_id);

        // msg_id = esp_mqtt_client_subscribe(client, "speed/values", 0);
        ESP_LOGI(TAG, "sent subscribe successful, msg_id=%d", msg_id);

        // msg_id = esp_mqtt_client_subscribe(client, "speed/values", 1);
        ESP_LOGI(TAG, "sent subscribe successful, msg_id=%d", msg_id);

        // msg_id = esp_mqtt_client_unsubscribe(client, "speed/values");
        ESP_LOGI(TAG, "sent unsubscribe successful, msg_id=%d", msg_id);
        break;
    case MQTT_EVENT_DISCONNECTED:
        ESP_LOGI(TAG, "MQTT_EVENT_DISCONNECTED");
        break;

    case MQTT_EVENT_SUBSCRIBED:
        ESP_LOGI(TAG, "MQTT_EVENT_SUBSCRIBED, msg_id=%d", event->msg_id);
        msg_id = esp_mqtt_client_publish(client, "speed/values", "0", 0, 0, 0);
        // ESP_LOGI(TAG, "sent publish successful, msg_id=%d", msg_id);
        break;
    case MQTT_EVENT_UNSUBSCRIBED:
        ESP_LOGI(TAG, "MQTT_EVENT_UNSUBSCRIBED, msg_id=%d", event->msg_id);
        break;
    case MQTT_EVENT_PUBLISHED:
        ESP_LOGI(TAG, "MQTT_EVENT_PUBLISHED, msg_id=%d", event->msg_id);
        break;
    case MQTT_EVENT_DATA:
        ESP_LOGI(TAG, "MQTT_EVENT_DATA");
        printf("TOPIC=%.*s\r\n", event->topic_len, event->topic);
        printf("DATA=%.*s\r\n", event->data_len, event->data);

        // if (!(strncmp(event->topic, "/class/group_2/pump", event->topic_len) || strncmp(event->data, "do", event->data_len))) {
        //     watering = true;
        // }
        break;
    case MQTT_EVENT_ERROR:
        ESP_LOGI(TAG, "MQTT_EVENT_ERROR");
        if (event->error_handle->error_type == MQTT_ERROR_TYPE_TCP_TRANSPORT) {
            log_error_if_nonzero("reported from esp-tls", event->error_handle->esp_tls_last_esp_err);
            log_error_if_nonzero("reported from tls stack", event->error_handle->esp_tls_stack_err);
            log_error_if_nonzero("captured as transport's socket errno",  event->error_handle->esp_transport_sock_errno);
            ESP_LOGI(TAG, "Last errno string (%s)", strerror(event->error_handle->esp_transport_sock_errno));

        }
        break;
    default:
        ESP_LOGI(TAG, "Other event id:%d", event->event_id);
        break;
    }
}

static void mqtt_app_start(void)
{
    esp_mqtt_client_config_t mqtt_cfg = {
        .broker.address.uri = CONFIG_BROKER_URL,
    };
#if CONFIG_BROKER_URL_FROM_STDIN
    char line[128];

    if (strcmp(mqtt_cfg.broker.address.uri, "FROM_STDIN") == 0) {
        int count = 0;
        printf("Please enter url of mqtt broker\n");
        while (count < 128) {
            int c = fgetc(stdin);
            if (c == '\n') {
                line[count] = '\0';
                break;
            } else if (c > 0 && c < 127) {
                line[count] = c;
                ++count;
            }
            vTaskDelay(10 / portTICK_PERIOD_MS);
        }
        mqtt_cfg.broker.address.uri = line;
        printf("Broker url: %s\n", line);
    } else {
        ESP_LOGE(TAG, "Configuration mismatch: wrong broker url");
        abort();
    }
#endif /* CONFIG_BROKER_URL_FROM_STDIN */

    esp_mqtt_client_handle_t client = esp_mqtt_client_init(&mqtt_cfg);
    /* The last argument may be used to pass data to the event handler, in this example mqtt_event_handler */
    esp_mqtt_client_register_event(client, ESP_EVENT_ANY_ID, mqtt_event_handler, NULL);

    esp_mqtt_client_start(client);

    esp_mqtt_client_publish(client, "speed/values", "initial", strlen("initial"), 0, 0); 
    int msg_id = esp_mqtt_client_subscribe(client, "speed/values", 0);
    ESP_LOGI(TAG, "my sent subscribe successful, msg_id=%d", msg_id);

    char str[10];

    while(1)
    {
        vTaskDelay(100 / portTICK_PERIOD_MS);
        sprintf(str, "%ld", prev_hall_counter*60);
        esp_mqtt_client_publish(client, "speed/values", str, strlen(str), 0, 0); 
        // velocity_show();

    }

}

void app_main(void)
{
    app_lcd_init();
    app_lvgl_init();

    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    ESP_ERROR_CHECK(example_connect());

    app_gpio_hall_sensor_init();

    background_init();
    label_init();

    lv_timer_t * timer = lv_timer_create(velocity_show, 1000, &hall_counter);

    mqtt_app_start();
}

