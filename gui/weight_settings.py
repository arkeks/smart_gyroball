import json
import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QPushButton, QLabel, QHBoxLayout, QLineEdit,
                               QMessageBox)
from PySide6.QtCore import Qt


class WeightSettings(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weight Settings")
        self.setFixedSize(400, 200)

        self.settings_file = 'user_settings.json'
        self.current_weight = self.load_weight()

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Заголовок
        title_label = QLabel("Настройка веса для расчета калорий")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # Поле ввода веса
        weight_layout = QHBoxLayout()
        weight_label = QLabel("Вес (кг):")
        weight_label.setStyleSheet("font-size: 14px;")
        weight_layout.addWidget(weight_label)

        self.weight_input = QLineEdit()
        self.weight_input.setText(str(self.current_weight))
        self.weight_input.setStyleSheet("font-size: 14px; padding: 5px;")
        weight_layout.addWidget(self.weight_input)

        layout.addLayout(weight_layout)

        # Кнопки
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_weight)
        self.save_button.setStyleSheet("font-size: 14px; padding: 8px;")
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.close)
        self.cancel_button.setStyleSheet("font-size: 14px; padding: 8px;")
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # Информация о расчете
        info_label = QLabel(
            "Расчет калорий основан на MET (Metabolic Equivalent of Task):\n"
            "• Низкая скорость (0-30): 2.0 MET (легкая нагрузка)\n"
            "• Средняя скорость (30-70): 4.0 MET (умеренная нагрузка)\n"
            "• Высокая скорость (70+): 6.0 MET (интенсивная нагрузка)\n"
            "Формула: Калории = MET × Вес × Время_в_часах"
        )
        info_label.setStyleSheet("font-size: 12px; color: #666; margin: 10px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

    def load_weight(self):
        """Загружает сохраненный вес пользователя"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('weight', 70.0)
        except Exception:
            pass
        return 70.0  # значение по умолчанию

    def save_weight(self):
        """Сохраняет вес пользователя"""
        try:
            weight = float(self.weight_input.text())
            if weight <= 0 or weight > 300:
                QMessageBox.warning(
                    self, "Ошибка", "Вес должен быть от 1 до 300 кг")
                return

            settings = {'weight': weight}
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)

            QMessageBox.information(self, "Успех", "Вес успешно сохранен!")
            self.close()

        except ValueError:
            QMessageBox.warning(
                self, "Ошибка", "Введите корректное числовое значение")


if __name__ == '__main__':
    app = QApplication([])
    window = WeightSettings()
    window.show()
    app.exec()
