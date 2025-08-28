import sys
import time
import socket
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QPushButton, QLabel, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QStackedWidget, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QMargins
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PySide6.QtGui import QPainter
import paho.mqtt.client as mqtt
import json
import os
from datetime import datetime
import math


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


class SpeedMonitor(QMainWindow):
    new_data = Signal(float, float)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Gyroball - Speed Monitor")
        self.setMinimumSize(800, 600)

        self.broker = get_local_ip()
        self.port = 1883
        self.topic = "speed/values"

        self.speeds = []
        self.times = []
        self.start_time = None
        self.is_recording = False

        # Параметры пользователя для расчета калорий
        self.current_user = None
        self.weight = 70.0
        self.height = 170.0
        self.age = 25
        self.gender = "Мужской"
        self.calories_per_minute = 0.0
        self.total_calories = 0.0

        self.connection_status = False

        # Сначала показываем окно авторизации
        self.show_auth_window()

    def show_auth_window(self):
        """Показывает окно авторизации"""
        try:
            from user_auth import UserAuth
            self.auth_window = UserAuth()
            self.auth_window.user_logged_in.connect(self.on_user_logged_in)
            self.auth_window.show()
        except ImportError:
            print("Auth window not available, using default settings")
            self.initialize_app()

    def on_user_logged_in(self, user_data):
        """Обработчик успешной авторизации пользователя"""
        self.current_user = user_data
        self.weight = user_data['weight']
        # значение по умолчанию для старых пользователей
        self.height = user_data.get('height', 170.0)
        self.age = user_data['age']
        self.gender = user_data['gender']

        self.initialize_app()

    def initialize_app(self):
        """Инициализирует приложение после авторизации"""
        self.setup_ui()
        self.load_last_measurement()

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.connect_mqtt()

        self.new_data.connect(self.add_data)

        # Показываем главное окно
        self.show()

    def calculate_calories(self, speed, duration_minutes):
        """
        Расчет калорий на основе скорости вращения гиробола с учетом пола и возраста
        Используется улучшенная формула с учетом базового метаболизма
        """
        # Определяем MET на основе скорости
        if speed < 30:
            met = 2.0  # легкая нагрузка
        elif speed < 70:
            met = 4.0  # умеренная нагрузка
        else:
            met = 6.0  # интенсивная нагрузка

        # Конвертируем время в часы
        duration_hours = duration_minutes / 60.0

        # Рассчитываем базовый метаболизм (BMR) по формуле Миффлина-Сан Жеора
        if self.gender == "Мужской":
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161

        # Рассчитываем калории с учетом базового метаболизма и активности
        # Формула: Калории = (BMR * MET * время_в_часах) / 24
        calories = (bmr * met * duration_hours) / 24

        return calories

    def open_settings(self):
        """Открывает окно настроек веса"""
        try:
            from weight_settings import WeightSettings
            self.settings_window = WeightSettings()
            self.settings_window.show()
            # Обновляем вес после закрытия окна настроек
            self.settings_window.destroyed.connect(
                self.update_weight_from_settings)
        except ImportError:
            print("Settings window not available")

    def update_weight_from_settings(self):
        """Обновляет вес из настроек"""
        if self.current_user:
            # Обновляем данные пользователя
            try:
                import json
                with open('users.json', 'r', encoding='utf-8') as f:
                    users = json.load(f)
                if self.current_user['username'] in users:
                    self.weight = users[self.current_user['username']]['weight']
                    self.height = users[self.current_user['username']].get(
                        'height', 170.0)
                    self.age = users[self.current_user['username']]['age']
                    self.gender = users[self.current_user['username']]['gender']
                    self.current_user = users[self.current_user['username']]
                    # Обновляем информацию о пользователе в интерфейсе
                    user_info = f"Пользователь: {self.current_user['name']} | Вес: {self.weight}кг | Рост: {self.height}см | Возраст: {self.age} | Пол: {self.gender}"
                    self.user_info_label.setText(user_info)
            except Exception as e:
                print(f"Error updating user settings: {e}")

    def logout_user(self):
        """Смена пользователя"""
        self.hide()
        self.show_auth_window()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Информация о пользователе
        if self.current_user:
            user_info = f"Пользователь: {self.current_user['name']} | Вес: {self.weight}кг | Рост: {self.height}см | Возраст: {self.age} | Пол: {self.gender}"
        else:
            user_info = "Пользователь не авторизован"

        self.user_info_label = QLabel(user_info)
        self.user_info_label.setAlignment(Qt.AlignCenter)
        self.user_info_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #2E86AB; margin: 5px;")
        layout.addWidget(self.user_info_label)

        self.status_label = QLabel("Connecting to MQTT...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: orange;")
        layout.addWidget(self.status_label)

        # Создаем горизонтальный layout для скорости и калорий
        metrics_layout = QHBoxLayout()

        # Левая колонка - скорость
        speed_layout = QVBoxLayout()
        self.speed_label = QLabel("Speed: 0.00")
        self.speed_label.setAlignment(Qt.AlignCenter)
        self.speed_label.setStyleSheet("font-size: 48px; font-weight: bold;")
        speed_layout.addWidget(self.speed_label)

        self.avg_label = QLabel("Average: 0.00")
        self.avg_label.setAlignment(Qt.AlignCenter)
        self.avg_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        speed_layout.addWidget(self.avg_label)

        metrics_layout.addLayout(speed_layout)

        # Правая колонка - калории
        calories_layout = QVBoxLayout()
        self.calories_label = QLabel("Calories: 0.0")
        self.calories_label.setAlignment(Qt.AlignCenter)
        self.calories_label.setStyleSheet(
            "font-size: 48px; font-weight: bold; color: #FF6B35;")
        calories_layout.addWidget(self.calories_label)

        self.calories_per_min_label = QLabel("Cal/min: 0.0")
        self.calories_per_min_label.setAlignment(Qt.AlignCenter)
        self.calories_per_min_label.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #FF6B35;")
        calories_layout.addWidget(self.calories_per_min_label)

        metrics_layout.addLayout(calories_layout)

        layout.addLayout(metrics_layout)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_recording)
        self.start_button.setStyleSheet("font-size: 18px; padding: 10px;")
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("font-size: 18px; padding: 10px;")
        button_layout.addWidget(self.stop_button)

        self.stats_button = QPushButton("Statistics")
        self.stats_button.clicked.connect(self.toggle_view)
        self.stats_button.setStyleSheet("font-size: 18px; padding: 10px;")
        button_layout.addWidget(self.stats_button)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)
        self.settings_button.setStyleSheet("font-size: 18px; padding: 10px;")
        button_layout.addWidget(self.settings_button)

        self.logout_button = QPushButton("Сменить пользователя")
        self.logout_button.clicked.connect(self.logout_user)
        self.logout_button.setStyleSheet(
            "font-size: 18px; padding: 10px; background-color: #A23B72; color: white;")
        button_layout.addWidget(self.logout_button)

        layout.addLayout(button_layout)

        # Create stacked widget for chart and statistics
        self.stacked_widget = QStackedWidget()

        # Chart page
        chart_widget = QWidget()
        chart_layout = QVBoxLayout(chart_widget)

        self.chart = QChart()
        self.chart.setTitle("Speed Over Time")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.legend().hide()
        self.chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        self.axis_x = QValueAxis()
        self.axis_x.setTitleText("Time (s)")
        self.axis_x.setLabelFormat("%.1f")
        self.axis_x.setTickCount(10)
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Speed")
        self.axis_y.setLabelFormat("%.1f")
        self.axis_y.setTickCount(10)
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series = QLineSeries()
        self.series.setPointsVisible(True)
        self.series.setPointLabelsVisible(False)
        self.chart.addSeries(self.series)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)
        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_layout.addWidget(chart_view)

        # Statistics page
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)

        stats_label = QLabel("Speed Statistics")
        stats_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        stats_layout.addWidget(stats_label)

        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(8)
        self.stats_table.setHorizontalHeaderLabels(
            ["Date", "User", "Duration", "Max Speed", "Average Speed", "Calories", "Cal/min", "Weight"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        stats_layout.addWidget(self.stats_table)

        # Progress chart page
        progress_widget = QWidget()
        progress_layout = QVBoxLayout(progress_widget)
        progress_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(0)

        progress_label = QLabel("Speed Progress")
        progress_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        progress_layout.addWidget(progress_label)

        self.progress_chart = QChart()
        self.progress_chart.setTitle("Speed Progress Over Time")
        self.progress_chart.setAnimationOptions(QChart.SeriesAnimations)
        self.progress_chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        self.progress_chart.setMargins(QMargins(10, 10, 10, 10))
        self.progress_chart.setBackgroundRoundness(0)

        self.max_speed_series = QLineSeries()
        self.max_speed_series.setName("Max Speed")
        self.avg_speed_series = QLineSeries()
        self.avg_speed_series.setName("Average Speed")
        self.progress_chart.addSeries(self.max_speed_series)
        self.progress_chart.addSeries(self.avg_speed_series)

        self.progress_axis_x = QDateTimeAxis()
        self.progress_axis_x.setTitleText("Date")
        self.progress_axis_x.setFormat("dd.MM.yyyy")
        self.progress_axis_x.setTickCount(10)
        self.progress_axis_x.setLabelsAngle(-45)
        self.progress_axis_y = QValueAxis()
        self.progress_axis_y.setTitleText("Speed")
        self.progress_axis_y.setLabelFormat("%.1f")
        self.progress_axis_y.setTickCount(10)
        self.progress_chart.addAxis(self.progress_axis_x, Qt.AlignBottom)
        self.progress_chart.addAxis(self.progress_axis_y, Qt.AlignLeft)
        self.max_speed_series.attachAxis(self.progress_axis_x)
        self.max_speed_series.attachAxis(self.progress_axis_y)
        self.avg_speed_series.attachAxis(self.progress_axis_x)
        self.avg_speed_series.attachAxis(self.progress_axis_y)

        progress_chart_view = QChartView(self.progress_chart)
        progress_chart_view.setRenderHint(QPainter.Antialiasing)
        progress_chart_view.setMinimumHeight(600)
        progress_chart_view.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        progress_layout.addWidget(progress_chart_view)
        progress_widget.setMinimumHeight(600)
        progress_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(chart_widget)
        self.stacked_widget.addWidget(stats_widget)
        self.stacked_widget.addWidget(progress_widget)

        layout.addWidget(self.stacked_widget)

        # Load initial statistics
        self.load_statistics()

    def connect_mqtt(self):
        try:
            self.client.connect(self.broker, self.port)
            self.client.subscribe(self.topic)
            self.client.loop_start()
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")

    def on_message(self, client, userdata, message):
        if self.is_recording:
            speed = float(message.payload.decode())
            current_time = time.time() - self.start_time
            self.new_data.emit(speed, current_time)

    @Slot(float, float)
    def add_data(self, speed, current_time):
        self.speeds.append(speed)
        self.times.append(current_time)
        print(
            f"Добавлена точка: t={current_time:.3f}, speed={speed:.2f}, всего точек: {len(self.speeds)}")
        self.update_display()

    def update_display(self):
        if not self.is_recording or not self.times:
            return

        if self.speeds:
            current_speed = self.speeds[-1]
            self.speed_label.setText(f"Speed: {current_speed:.2f}")
            avg_speed = sum(self.speeds) / len(self.speeds)
            self.avg_label.setText(f"Average: {avg_speed:.2f}")

            # Обновляем калории
            duration_minutes = self.times[-1] / 60.0
            self.total_calories = self.calculate_calories(
                avg_speed, duration_minutes)
            self.calories_per_minute = self.calculate_calories(
                avg_speed, 1.0)  # калории за минуту

            self.calories_label.setText(f"Calories: {self.total_calories:.1f}")
            self.calories_per_min_label.setText(
                f"Cal/min: {self.calories_per_minute:.1f}")

        if len(self.times) > 1:
            self.series.clear()
            window_size = self.times[-1]
            current_time = self.times[-1]
            if current_time > window_size:
                left = 0
                right = current_time
            else:
                left = 0
                right = current_time

            for t, s in zip(self.times, self.speeds):
                if left <= t <= right:
                    self.series.append(t, s)

            self.axis_x.setRange(left, right)

            visible_speeds = [s for t, s in zip(
                self.times, self.speeds) if left <= t <= right]
            if visible_speeds:
                min_speed = min(visible_speeds)
                max_speed = max(visible_speeds)
                speed_range = max_speed - min_speed
                padding = speed_range * 0.1 if speed_range > 0 else 1
                self.axis_y.setRange(min_speed - padding, max_speed + padding)
        self.repaint()

    def start_recording(self):
        self.is_recording = True
        self.start_time = time.time()
        self.speeds.clear()
        self.times.clear()
        self.series.clear()
        self.axis_x.setRange(0, 10)
        self.axis_y.setRange(0, 100)
        self.total_calories = 0.0
        self.calories_per_minute = 0.0
        self.calories_label.setText("Calories: 0.0")
        self.calories_per_min_label.setText("Cal/min: 0.0")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_recording(self):
        if self.is_recording and self.speeds:
            # Save statistics
            duration = self.times[-1] if self.times else 0
            max_speed = max(self.speeds) if self.speeds else 0
            avg_speed = sum(self.speeds) / \
                len(self.speeds) if self.speeds else 0

            # Рассчитываем финальные калории
            duration_minutes = duration / 60.0
            total_calories = self.calculate_calories(
                avg_speed, duration_minutes)
            calories_per_minute = self.calculate_calories(avg_speed, 1.0)

            stats = {
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'duration': duration,
                'max_speed': max_speed,
                'avg_speed': avg_speed,
                'calories': total_calories,
                'calories_per_minute': calories_per_minute,
                'user': self.current_user['username'] if self.current_user else 'unknown',
                'user_name': self.current_user['name'] if self.current_user else 'Unknown',
                'weight': self.weight,
                'height': self.height,
                'age': self.age,
                'gender': self.gender
            }

            try:
                existing_stats = []
                if os.path.exists('speed_statistics.json'):
                    with open('speed_statistics.json', 'r') as f:
                        existing_stats = json.load(f)

                existing_stats.append(stats)

                with open('speed_statistics.json', 'w') as f:
                    json.dump(existing_stats, f, indent=4)

                # Reload statistics after saving
                self.load_statistics()
            except Exception as e:
                print(f"Error saving statistics: {e}")

        self.is_recording = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def load_last_measurement(self):
        try:
            if os.path.exists('last_measurement.json'):
                with open('last_measurement.json', 'r') as f:
                    data = json.load(f)
                    self.speeds = data.get('speeds', [])
                    self.times = data.get('times', [])
                    if self.speeds and self.times:
                        self.update_display()
        except Exception as e:
            print(f"Error loading last measurement: {e}")

    def save_last_measurement(self):
        try:
            data = {
                'speeds': self.speeds,
                'times': self.times,
                'total_calories': self.total_calories,
                'calories_per_minute': self.calories_per_minute
            }
            with open('last_measurement.json', 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving last measurement: {e}")

    def closeEvent(self, event):
        self.save_last_measurement()
        self.client.loop_stop()
        self.client.disconnect()
        event.accept()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connection_status = True
            self.status_label.setText("Connected to MQTT broker")
            self.status_label.setStyleSheet(
                "font-size: 20px; font-weight: bold; color: green;")
            client.subscribe(self.topic)
        else:
            self.connection_status = False
            self.status_label.setText("Failed to connect to MQTT broker")
            self.status_label.setStyleSheet(
                "font-size: 20px; font-weight: bold; color: red;")

    def on_disconnect(self, client, userdata, rc):
        self.connection_status = False
        self.status_label.setText("Disconnected from MQTT broker")
        self.status_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: red;")

    def load_statistics(self):
        try:
            if os.path.exists('speed_statistics.json'):
                with open('speed_statistics.json', 'r') as f:
                    stats = json.load(f)

                self.stats_table.setRowCount(len(stats))
                for i, record in enumerate(stats):
                    self.stats_table.setItem(
                        i, 0, QTableWidgetItem(record['date']))

                    # Показываем пользователя
                    user_name = record.get(
                        'user_name', record.get('user', 'Unknown'))
                    self.stats_table.setItem(i, 1, QTableWidgetItem(user_name))

                    self.stats_table.setItem(i, 2, QTableWidgetItem(
                        f"{record['duration']:.1f}s"))
                    self.stats_table.setItem(i, 3, QTableWidgetItem(
                        f"{record['max_speed']:.2f}"))
                    self.stats_table.setItem(i, 4, QTableWidgetItem(
                        f"{record['avg_speed']:.2f}"))

                    # Добавляем колонки с калориями
                    calories = record.get('calories', 0.0)
                    calories_per_min = record.get('calories_per_minute', 0.0)

                    self.stats_table.setItem(i, 5, QTableWidgetItem(
                        f"{calories:.1f}"))
                    self.stats_table.setItem(i, 6, QTableWidgetItem(
                        f"{calories_per_min:.1f}"))

                    # Показываем вес
                    weight = record.get('weight', 0.0)
                    self.stats_table.setItem(i, 7, QTableWidgetItem(
                        f"{weight:.1f}кг"))
        except Exception as e:
            print(f"Error loading statistics: {e}")

    def toggle_view(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index == 0:  # Chart view
            self.stacked_widget.setCurrentIndex(1)  # Switch to stats
            self.stats_button.setText("Progress")
            self.load_statistics()
        elif current_index == 1:  # Stats view
            self.stacked_widget.setCurrentIndex(2)  # Switch to progress
            self.stats_button.setText("Chart")
            self.update_progress_chart()
        else:  # Progress view
            self.stacked_widget.setCurrentIndex(0)  # Switch to chart
            self.stats_button.setText("Statistics")

    def update_progress_chart(self):
        try:
            if os.path.exists('speed_statistics.json'):
                with open('speed_statistics.json', 'r') as f:
                    stats = json.load(f)

                # Clear existing data
                self.max_speed_series.clear()
                self.avg_speed_series.clear()

                if not stats:
                    return

                # Add data points
                min_date = None
                max_date = None
                min_speed = float('inf')
                max_speed = 0

                for record in stats:
                    date = datetime.strptime(
                        record['date'], "%Y-%m-%d %H:%M:%S")
                    max_speed = record['max_speed']
                    avg_speed = record['avg_speed']

                    # Convert datetime to milliseconds since epoch
                    msecs = int(date.timestamp() * 1000)

                    self.max_speed_series.append(msecs, max_speed)
                    self.avg_speed_series.append(msecs, avg_speed)

                    if min_date is None or date < min_date:
                        min_date = date
                    if max_date is None or date > max_date:
                        max_date = date
                    min_speed = min(min_speed, avg_speed)
                    max_speed = max(max_speed, max_speed)

                # Set axis ranges
                if min_date and max_date:
                    # Add padding to the date range (20% on each side)
                    date_range = (max_date - min_date).total_seconds()
                    padding = date_range * 0.2
                    min_date = datetime.fromtimestamp(
                        min_date.timestamp() - padding)
                    max_date = datetime.fromtimestamp(
                        max_date.timestamp() + padding)

                    self.progress_axis_x.setRange(min_date, max_date)

                    # Add fixed padding to speed range
                    # Fixed padding at bottom
                    min_speed = max(0, min_speed - 1)
                    max_speed = max_speed + 1  # Fixed padding at top

                    self.progress_axis_y.setRange(min_speed, max_speed)

                # Reset zoom and let the chart auto-scale
                self.progress_chart.zoomReset()

                # Calculate all speeds
                all_speeds = []
                for record in stats:
                    all_speeds.append(record['max_speed'])
                    all_speeds.append(record['avg_speed'])

                if all_speeds:
                    min_speed = min(all_speeds)
                    max_speed = max(all_speeds)
                    # Добавим небольшой запас (например, 10% от диапазона)
                    padding = (max_speed - min_speed) * \
                        0.1 if max_speed > min_speed else 1
                    self.progress_axis_y.setRange(
                        max(0, min_speed - padding), max_speed + padding)

        except Exception as e:
            print(f"Error updating progress chart: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SpeedMonitor()
    window.show()
    sys.exit(app.exec())
