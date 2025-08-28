#!/usr/bin/env python3
"""
Тестовый скрипт для проверки улучшенного расчета калорий
с учетом пола, возраста и веса
"""


def calculate_bmr(weight, height, age, gender):
    """Рассчитывает базовый метаболизм по формуле Миффлина-Сан Жеора"""
    if gender == "Мужской":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return bmr


def calculate_calories(speed, duration_minutes, weight, height, age, gender):
    """
    Расчет калорий на основе скорости вращения гиробола с учетом пола, возраста и роста
    Используется улучшенная формула с учетом базового метаболизма
    """
    # Определяем MET на основе скорости
    if speed < 30:
        met = 2.0  # легкая нагрузка
        intensity = "легкая"
    elif speed < 70:
        met = 4.0  # умеренная нагрузка
        intensity = "умеренная"
    else:
        met = 6.0  # интенсивная нагрузка
        intensity = "интенсивная"

    # Конвертируем время в часы
    duration_hours = duration_minutes / 60.0

    # Рассчитываем базовый метаболизм (BMR) по формуле Миффлина-Сан Жеора
    bmr = calculate_bmr(weight, height, age, gender)

    # Рассчитываем калории с учетом базового метаболизма и активности
    # Формула: Калории = (BMR * MET * время_в_часах) / 24
    calories = (bmr * met * duration_hours) / 24

    return calories, intensity, met, bmr


def test_advanced_calorie_calculation():
    """Тестирует улучшенный расчет калорий для различных сценариев"""

    print("=== Тест улучшенного расчета калорий для гиробола ===\n")

    # Тестовые сценарии
    test_cases = [
        {
            "speed": 20, "duration_min": 10, "weight": 70, "height": 175, "age": 25, "gender": "Мужской",
            "description": "Молодой мужчина, низкая скорость"
        },
        {
            "speed": 50, "duration_min": 15, "weight": 65, "height": 165, "age": 30, "gender": "Женский",
            "description": "Женщина 30 лет, средняя скорость"
        },
        {
            "speed": 80, "duration_min": 20, "weight": 85, "height": 180, "age": 40, "gender": "Мужской",
            "description": "Мужчина 40 лет, высокая скорость"
        },
        {
            "speed": 40, "duration_min": 30, "weight": 55, "height": 160, "age": 20, "gender": "Женский",
            "description": "Молодая женщина, длинная тренировка"
        },
        {
            "speed": 90, "duration_min": 25, "weight": 95, "height": 185, "age": 35, "gender": "Мужской",
            "description": "Тяжелый мужчина, интенсивная тренировка"
        },
    ]

    for i, case in enumerate(test_cases, 1):
        calories, intensity, met, bmr = calculate_calories(
            case["speed"],
            case["duration_min"],
            case["weight"],
            case["height"],
            case["age"],
            case["gender"]
        )

        print(f"Тест {i}: {case['description']}")
        print(f"  Скорость: {case['speed']} об/мин")
        print(f"  Длительность: {case['duration_min']} минут")
        print(f"  Вес: {case['weight']} кг")
        print(f"  Рост: {case['height']} см")
        print(f"  Возраст: {case['age']} лет")
        print(f"  Пол: {case['gender']}")
        print(f"  Базовый метаболизм (BMR): {bmr:.1f} ккал/день")
        print(f"  Интенсивность: {intensity} (MET = {met})")
        print(f"  Калории: {calories:.1f}")
        print(f"  Калории/мин: {calories/case['duration_min']:.1f}")
        print()


def compare_calculation_methods():
    """Сравнивает старый и новый методы расчета калорий"""

    print("=== Сравнение методов расчета калорий ===\n")

    # Старый метод: калории = MET * вес * время_в_часах
    def old_calculate_calories(speed, duration_minutes, weight):
        if speed < 30:
            met = 2.0
        elif speed < 70:
            met = 4.0
        else:
            met = 6.0

        duration_hours = duration_minutes / 60.0
        calories = met * weight * duration_hours
        return calories

        # Тестовый случай
    speed = 60
    duration_min = 15
    weight = 70
    height = 175
    age = 25
    gender = "Мужской"

    old_calories = old_calculate_calories(speed, duration_min, weight)
    new_calories, intensity, met, bmr = calculate_calories(
        speed, duration_min, weight, height, age, gender)

    print(f"Тестовые параметры:")
    print(f"  Скорость: {speed} об/мин")
    print(f"  Длительность: {duration_min} минут")
    print(f"  Вес: {weight} кг")
    print(f"  Рост: {height} см")
    print(f"  Возраст: {age} лет")
    print(f"  Пол: {gender}")
    print()

    print(f"Старый метод (MET * вес * время):")
    print(f"  Калории: {old_calories:.1f}")
    print(f"  Калории/мин: {old_calories/duration_min:.1f}")
    print()

    print(f"Новый метод (с учетом BMR):")
    print(f"  Базовый метаболизм: {bmr:.1f} ккал/день")
    print(f"  Калории: {new_calories:.1f}")
    print(f"  Калории/мин: {new_calories/duration_min:.1f}")
    print()

    difference = new_calories - old_calories
    print(
        f"Разница: {difference:.1f} калорий ({difference/old_calories*100:.1f}%)")


if __name__ == "__main__":
    test_advanced_calorie_calculation()
    print("\n" + "="*60 + "\n")
    compare_calculation_methods()
