# MQTT Speed Publisher/Subscriber

Простой проект для демонстрации работы с MQTT протоколом. Включает в себя:
- Отправитель (publisher) случайных значений скорости
- Получатель (subscriber) значений скорости

## Требования

- Python 3.x
- Make
- MQTT брокер (например, Mosquitto)

## Установка

1. Создание и активация виртуального окружения:
```bash
make setup
```

## Использование

1. Запуск MQTT серввера
```bash
./server/start_mqtt.sh
```

2. Запуск программ:
  - Запуск отправителя:
     ```bash
     make run-publisher
     ```
  - Запуск получателя:
     ```bash
     make run-subscriber
     ```
  - Запуск GUI:
     ```bash
     make run-gui
     ```

3. Очистка проекта:
```bash
make clean
```
