#!/usr/bin/env python3
"""
Тестовый скрипт для проверки расчета калорий
"""

def calculate_calories(speed, duration_minutes, weight=70.0):
    """
    Расчет калорий на основе скорости вращения гиробола
    Используется формула: калории = MET * вес * время_в_часах
    где MET (Metabolic Equivalent of Task) зависит от интенсивности
    """
    # Определяем MET на основе скорости
    # Низкая скорость (0-30): легкая нагрузка
    # Средняя скорость (30-70): умеренная нагрузка  
    # Высокая скорость (70+): интенсивная нагрузка
    
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
    
    # Рассчитываем калории: MET * вес * время_в_часах
    calories = met * weight * duration_hours
    
    return calories, intensity, met

def test_calorie_calculation():
    """Тестирует расчет калорий для различных сценариев"""
    
    print("=== Тест расчета калорий для гиробола ===\n")
    
    # Тестовые сценарии
    test_cases = [
        {"speed": 20, "duration_min": 5, "weight": 70, "description": "Низкая скорость, короткая тренировка"},
        {"speed": 50, "duration_min": 10, "weight": 70, "description": "Средняя скорость, средняя тренировка"},
        {"speed": 80, "duration_min": 15, "weight": 70, "description": "Высокая скорость, длинная тренировка"},
        {"speed": 40, "duration_min": 30, "weight": 60, "description": "Средняя скорость, длинная тренировка, легкий вес"},
        {"speed": 90, "duration_min": 20, "weight": 80, "description": "Высокая скорость, средняя тренировка, тяжелый вес"},
    ]
    
    for i, case in enumerate(test_cases, 1):
        calories, intensity, met = calculate_calories(
            case["speed"], 
            case["duration_min"], 
            case["weight"]
        )
        
        print(f"Тест {i}: {case['description']}")
        print(f"  Скорость: {case['speed']} об/мин")
        print(f"  Длительность: {case['duration_min']} минут")
        print(f"  Вес: {case['weight']} кг")
        print(f"  Интенсивность: {intensity} (MET = {met})")
        print(f"  Калории: {calories:.1f}")
        print(f"  Калории/мин: {calories/case['duration_min']:.1f}")
        print()

if __name__ == "__main__":
    test_calorie_calculation()
