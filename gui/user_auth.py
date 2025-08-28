import json
import os
import hashlib
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QPushButton, QLabel, QHBoxLayout, QLineEdit,
                               QMessageBox, QComboBox, QStackedWidget, QFormLayout)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class UserAuth(QMainWindow):
    user_logged_in = Signal(dict)  # Сигнал с данными пользователя

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Gyroball - Авторизация")
        self.setFixedSize(600, 600)
        
        self.users_file = 'users.json'
        self.current_user = None
        
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Заголовок
        title_label = QLabel("Smart Gyroball")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px; color: #2E86AB;")
        layout.addWidget(title_label)

        # Stacked widget для переключения между логином и регистрацией
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # Страница логина
        self.login_widget = self.create_login_page()
        self.stacked_widget.addWidget(self.login_widget)

        # Страница регистрации
        self.register_widget = self.create_register_page()
        self.stacked_widget.addWidget(self.register_widget)

        # Кнопки переключения
        switch_layout = QHBoxLayout()
        
        self.switch_to_register_btn = QPushButton("Создать аккаунт")
        self.switch_to_register_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.switch_to_register_btn.setStyleSheet("font-size: 12px; padding: 5px;")
        switch_layout.addWidget(self.switch_to_register_btn)
        
        self.switch_to_login_btn = QPushButton("Уже есть аккаунт")
        self.switch_to_login_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.switch_to_login_btn.setStyleSheet("font-size: 12px; padding: 5px;")
        switch_layout.addWidget(self.switch_to_login_btn)
        
        layout.addLayout(switch_layout)

    def create_login_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Заголовок
        login_label = QLabel("Вход в систему")
        login_label.setAlignment(Qt.AlignCenter)
        login_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(login_label)

        # Форма логина
        form_layout = QFormLayout()
        
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Введите имя пользователя")
        self.login_username.setStyleSheet("font-size: 14px; padding: 8px;")
        form_layout.addRow("Имя пользователя:", self.login_username)
        
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Введите пароль")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setStyleSheet("font-size: 14px; padding: 8px;")
        form_layout.addRow("Пароль:", self.login_password)
        
        layout.addLayout(form_layout)

        # Кнопка входа
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.login_user)
        self.login_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #2E86AB; color: white;")
        layout.addWidget(self.login_button)

        layout.addStretch()
        return widget

    def create_register_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Заголовок
        register_label = QLabel("Регистрация")
        register_label.setAlignment(Qt.AlignCenter)
        register_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(register_label)

        # Форма регистрации
        form_layout = QFormLayout()
        
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Введите имя пользователя")
        self.register_username.setStyleSheet("font-size: 14px; padding: 8px;")
        form_layout.addRow("Имя пользователя:", self.register_username)
        
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Введите пароль")
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_password.setStyleSheet("font-size: 14px; padding: 8px;")
        form_layout.addRow("Пароль:", self.register_password)
        
        self.register_confirm_password = QLineEdit()
        self.register_confirm_password.setPlaceholderText("Подтвердите пароль")
        self.register_confirm_password.setEchoMode(QLineEdit.Password)
        self.register_confirm_password.setStyleSheet("font-size: 14px; padding: 8px;")
        form_layout.addRow("Подтверждение пароля:", self.register_confirm_password)
        
        self.register_name = QLineEdit()
        self.register_name.setPlaceholderText("Введите ваше имя")
        self.register_name.setStyleSheet("font-size: 14px; padding: 8px;")
        form_layout.addRow("Имя:", self.register_name)
        
        self.register_weight = QLineEdit()
        self.register_weight.setPlaceholderText("Введите вес в кг")
        self.register_weight.setStyleSheet("font-size: 14px; padding: 8px;")
        form_layout.addRow("Вес (кг):", self.register_weight)
        
        self.register_height = QLineEdit()
        self.register_height.setPlaceholderText("Введите рост в см")
        self.register_height.setStyleSheet("font-size: 14px; padding: 8px;")
        form_layout.addRow("Рост (см):", self.register_height)
        
        self.register_age = QLineEdit()
        self.register_age.setPlaceholderText("Введите возраст")
        self.register_age.setStyleSheet("font-size: 14px; padding: 8px;")
        form_layout.addRow("Возраст:", self.register_age)
        
        self.register_gender = QComboBox()
        self.register_gender.addItems(["Мужской", "Женский"])
        self.register_gender.setStyleSheet("font-size: 14px; padding: 8px;")
        form_layout.addRow("Пол:", self.register_gender)
        
        layout.addLayout(form_layout)

        # Кнопка регистрации
        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.clicked.connect(self.register_user)
        self.register_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #A23B72; color: white;")
        layout.addWidget(self.register_button)

        layout.addStretch()
        return widget

    def load_users(self):
        """Загружает список пользователей из файла"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            else:
                self.users = {}
        except Exception as e:
            print(f"Error loading users: {e}")
            self.users = {}

    def save_users(self):
        """Сохраняет список пользователей в файл"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving users: {e}")

    def hash_password(self, password):
        """Хеширует пароль"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self):
        """Регистрирует нового пользователя"""
        username = self.register_username.text().strip()
        password = self.register_password.text()
        confirm_password = self.register_confirm_password.text()
        name = self.register_name.text().strip()
        weight_str = self.register_weight.text().strip()
        height_str = self.register_height.text().strip()
        age_str = self.register_age.text().strip()
        gender = self.register_gender.currentText()

        # Проверки
        if not username or not password or not name or not weight_str or not height_str or not age_str:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return

        if username in self.users:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем уже существует!")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
            return

        try:
            weight = float(weight_str)
            height = float(height_str)
            age = int(age_str)
            
            if weight <= 0 or weight > 300:
                QMessageBox.warning(self, "Ошибка", "Вес должен быть от 1 до 300 кг!")
                return
                
            if height <= 0 or height > 250:
                QMessageBox.warning(self, "Ошибка", "Рост должен быть от 1 до 250 см!")
                return
                
            if age <= 0 or age > 120:
                QMessageBox.warning(self, "Ошибка", "Возраст должен быть от 1 до 120 лет!")
                return
                
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Вес, рост и возраст должны быть числами!")
            return

        # Создаем пользователя
        user_data = {
            'username': username,
            'password_hash': self.hash_password(password),
            'name': name,
            'weight': weight,
            'height': height,
            'age': age,
            'gender': gender,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }

        self.users[username] = user_data
        self.save_users()

        QMessageBox.information(self, "Успех", "Пользователь успешно зарегистрирован!")
        
        # Очищаем поля
        self.register_username.clear()
        self.register_password.clear()
        self.register_confirm_password.clear()
        self.register_name.clear()
        self.register_weight.clear()
        self.register_height.clear()
        self.register_age.clear()
        self.register_gender.setCurrentIndex(0)

    def login_user(self):
        """Авторизует пользователя"""
        username = self.login_username.text().strip()
        password = self.login_password.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите имя пользователя и пароль!")
            return

        if username not in self.users:
            QMessageBox.warning(self, "Ошибка", "Пользователь не найден!")
            return

        user_data = self.users[username]
        if user_data['password_hash'] != self.hash_password(password):
            QMessageBox.warning(self, "Ошибка", "Неверный пароль!")
            return

        # Обновляем время последнего входа
        user_data['last_login'] = datetime.now().isoformat()
        self.save_users()

        self.current_user = user_data
        QMessageBox.information(self, "Успех", f"Добро пожаловать, {user_data['name']}!")
        
        # Отправляем сигнал с данными пользователя
        self.user_logged_in.emit(user_data)
        self.close()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = UserAuth()
    window.show()
    sys.exit(app.exec())
