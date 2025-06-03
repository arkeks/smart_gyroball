import sys
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QPushButton, QLabel, QHBoxLayout)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtGui import QPainter
import paho.mqtt.client as mqtt


class SpeedMonitor(QMainWindow):
    new_data = Signal(float, float)  

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gyroball Speed Monitor")
        self.setMinimumSize(800, 600)

        self.broker = "localhost"
        self.port = 1883
        self.topic = "speed/values"

        self.speeds = []
        self.times = []
        self.start_time = None
        self.is_recording = False

        self.connection_status = False

        self.setup_ui()

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.connect_mqtt()

        self.new_data.connect(self.add_data)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.status_label = QLabel("Connecting to MQTT...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: orange;")
        layout.addWidget(self.status_label)

        
        self.speed_label = QLabel("Speed: 0.00")
        self.speed_label.setAlignment(Qt.AlignCenter)
        self.speed_label.setStyleSheet("font-size: 48px; font-weight: bold;")
        layout.addWidget(self.speed_label)

    
        self.avg_label = QLabel("Average: 0.00")
        self.avg_label.setAlignment(Qt.AlignCenter)
        self.avg_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        layout.addWidget(self.avg_label)

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
        layout.addLayout(button_layout)

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
        layout.addWidget(chart_view)

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
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_recording(self):
        self.is_recording = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def closeEvent(self, event):
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SpeedMonitor()
    window.show()
    sys.exit(app.exec())
