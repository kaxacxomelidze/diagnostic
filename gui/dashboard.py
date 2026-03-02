import csv
import os
from datetime import datetime

import pyqtgraph as pg
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.actuator_panel import ActuatorPanel
from gui.circular_gauge import CircularGauge
from gui.dynamic_multi_graph import MultiSensorGraph
from utils.dtc_codes import get_description


class Dashboard(QMainWindow):
    def __init__(self, obd_reader, obd_writer):
        super().__init__()
        self.reader = obd_reader
        self.writer = obd_writer
        self.last_command_status = {}

        self.setWindowTitle("Professional OBD-II Dashboard")
        self.setGeometry(80, 80, 1400, 860)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        root_layout = QHBoxLayout(self.central_widget)

        left = QVBoxLayout()
        right = QVBoxLayout()
        root_layout.addLayout(left, 2)
        root_layout.addLayout(right, 3)

        gauge_grid = QGridLayout()
        left.addLayout(gauge_grid)

        self.rpm_gauge = CircularGauge("RPM", 0, 8000, "RPM", [(0, 5000, "green"), (5000, 7000, "yellow"), (7000, 8000, "red")])
        self.speed_gauge = CircularGauge("Speed", 0, 240, "km/h", [(0, 120, "green"), (120, 180, "yellow"), (180, 240, "red")])
        self.coolant_gauge = CircularGauge("Coolant", 0, 120, "°C", [(0, 90, "green"), (90, 105, "yellow"), (105, 120, "red")])
        self.throttle_gauge = CircularGauge("Throttle", 0, 100, "%", [(0, 70, "green"), (70, 90, "yellow"), (90, 100, "red")])
        self.oil_gauge = CircularGauge("Oil Pressure", 0, 10, "bar", [(0, 3, "red"), (3, 7, "green"), (7, 10, "yellow")])

        gauge_grid.addWidget(self.rpm_gauge, 0, 0)
        gauge_grid.addWidget(self.speed_gauge, 0, 1)
        gauge_grid.addWidget(self.coolant_gauge, 1, 0)
        gauge_grid.addWidget(self.throttle_gauge, 1, 1)
        gauge_grid.addWidget(self.oil_gauge, 2, 0, 1, 2)

        self.actuator_btn = QPushButton("Open Actuator Panel")
        self.actuator_btn.clicked.connect(self.open_actuator_panel)
        left.addWidget(self.actuator_btn)

        self.actuator_status = QLabel("Actuator overlay: no recent commands")
        left.addWidget(self.actuator_status)

        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground("w")
        self.graph_widget.addLegend()
        self.graph_widget.setLabel("left", "Sensor value")
        self.graph_widget.setLabel("bottom", "Time index")

        right.addWidget(QLabel("Real-time Multi Sensor Graph"))
        right.addWidget(self.graph_widget, 4)

        sensors = {"RPM": "b", "Speed": "g", "Coolant": "r", "Throttle": "y", "Oil": "m"}
        limits = {
            "RPM": (0, 7000),
            "Speed": (0, 180),
            "Coolant": (0, 105),
            "Throttle": (0, 90),
            "Oil": (0, 7),
        }
        self.multi_graph = MultiSensorGraph(self.graph_widget, sensors, limits)

        self.dtc_list = QListWidget()
        right.addWidget(QLabel("DTC Codes"))
        right.addWidget(self.dtc_list, 2)

        os.makedirs("logs", exist_ok=True)
        self.log_path = "logs/vehicle_log.csv"
        new_file = not os.path.exists(self.log_path)
        self.log_file = open(self.log_path, "a", newline="", encoding="utf-8")
        self.csv_writer = csv.writer(self.log_file)
        if new_file:
            self.csv_writer.writerow(["Timestamp", "RPM", "Speed", "Coolant", "Throttle", "Oil Pressure"])

        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start()

    def closeEvent(self, event):
        self.log_file.close()
        super().closeEvent(event)

    def open_actuator_panel(self):
        self.actuator_window = ActuatorPanel(self.writer, on_command_applied=self.register_actuator_change)
        self.actuator_window.show()

    def register_actuator_change(self, param, value, success):
        mapped = {
            "Throttle": "Throttle",
            "IdleRPM": "RPM",
        }
        sensor = mapped.get(param)
        if sensor:
            self.last_command_status[sensor] = success
        self.actuator_status.setText(f"Actuator command: {param}={value} -> {'OK' if success else 'FAIL'}")

    def update_dashboard(self):
        rpm = self.reader.get_rpm()
        speed = self.reader.get_speed()
        coolant = self.reader.get_coolant_temp()
        throttle = self.reader.get_throttle()
        oil = self.reader.get_oil_pressure()
        dtcs = self.reader.get_dtc_codes()

        gauges = [
            (self.rpm_gauge, rpm, 7000),
            (self.speed_gauge, speed, 180),
            (self.coolant_gauge, coolant, 105),
            (self.throttle_gauge, throttle, 90),
            (self.oil_gauge, oil, 7),
        ]
        for gauge, value, limit in gauges:
            gauge.update_value(value)
            gauge.setStyleSheet("background-color: rgba(255,0,0,40);" if value > limit else "")

        actuator_changes = {"RPM": False, "Speed": False, "Coolant": False, "Throttle": False, "Oil": False}
        for sensor, changed in self.last_command_status.items():
            actuator_changes[sensor] = changed
        self.last_command_status.clear()

        self.multi_graph.append_values(
            {
                "RPM": rpm,
                "Speed": speed,
                "Coolant": coolant,
                "Throttle": throttle,
                "Oil": oil,
            },
            actuator_changes=actuator_changes,
        )

        self.dtc_list.clear()
        for code, _desc in dtcs:
            self.dtc_list.addItem(f"{code}: {get_description(code)}")

        self.csv_writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            rpm,
            speed,
            coolant,
            throttle,
            oil,
        ])
        self.log_file.flush()
