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
from utils.dtc_codes import get_dtc_info


class Dashboard(QMainWindow):
    def __init__(self, obd_reader, obd_writer, simulation_mode=False):
        super().__init__()
        self.reader = obd_reader
        self.writer = obd_writer
        self.simulation_mode = simulation_mode
        self.last_command_status = {}
        self.logging_enabled = True
        self.sample_counter = 0

        self.setWindowTitle("Professional OBD-II Dashboard")
        self.setGeometry(80, 80, 1460, 900)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        root_layout = QHBoxLayout(self.central_widget)

        left = QVBoxLayout()
        right = QVBoxLayout()
        root_layout.addLayout(left, 2)
        root_layout.addLayout(right, 3)

        mode_label = QLabel("MODE: SIMULATION" if simulation_mode else "MODE: LIVE OBD")
        mode_label.setStyleSheet(
            "font-weight: bold; padding: 6px; border-radius: 4px;"
            + ("background: #ffe8a3; color: #7a5600;" if simulation_mode else "background: #d8f5d2; color: #1d6b1d;")
        )
        left.addWidget(mode_label)

        self.health_label = QLabel("Vehicle Health: initializing")
        self.vin_label = QLabel(f"VIN: {self.reader.get_vin()}")
        self.logging_label = QLabel("Logging: ON")
        left.addWidget(self.health_label)
        left.addWidget(self.vin_label)
        left.addWidget(self.logging_label)

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

        action_row = QHBoxLayout()
        self.actuator_btn = QPushButton("Open Actuator Panel")
        self.actuator_btn.clicked.connect(self.open_actuator_panel)
        action_row.addWidget(self.actuator_btn)

        self.toggle_log_btn = QPushButton("Pause Logging")
        self.toggle_log_btn.clicked.connect(self.toggle_logging)
        action_row.addWidget(self.toggle_log_btn)
        left.addLayout(action_row)

        self.actuator_status = QLabel("Actuator overlay: no recent commands")
        left.addWidget(self.actuator_status)

        self.alerts_list = QListWidget()
        left.addWidget(QLabel("Live Alerts"))
        left.addWidget(self.alerts_list)

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

        dtc_actions = QHBoxLayout()
        self.clear_dtc_btn = QPushButton("Clear DTC View")
        self.clear_dtc_btn.clicked.connect(self.dtc_clear)
        dtc_actions.addWidget(self.clear_dtc_btn)
        self.export_dtc_btn = QPushButton("Export DTC Report")
        self.export_dtc_btn.clicked.connect(self.export_dtc_report)
        dtc_actions.addWidget(self.export_dtc_btn)

        self.dtc_list = QListWidget()
        right.addWidget(QLabel("DTC Codes (code | severity | system | recommendation)"))
        right.addLayout(dtc_actions)
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

    def toggle_logging(self):
        self.logging_enabled = not self.logging_enabled
        self.toggle_log_btn.setText("Resume Logging" if not self.logging_enabled else "Pause Logging")
        self.logging_label.setText(f"Logging: {'ON' if self.logging_enabled else 'PAUSED'}")

    def dtc_clear(self):
        self.dtc_list.clear()

    def export_dtc_report(self):
        report_path = "logs/dtc_report.csv"
        with open(report_path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["code", "title", "severity", "system", "recommendation"])
            for i in range(self.dtc_list.count()):
                line = self.dtc_list.item(i).text()
                # code|severity|system|title|recommendation
                parts = [p.strip() for p in line.split("|")]
                if len(parts) == 5:
                    writer.writerow([parts[0], parts[3], parts[1], parts[2], parts[4]])
        self.alerts_list.insertItem(0, f"[{datetime.now().strftime('%H:%M:%S')}] DTC report exported: {report_path}")

    def register_actuator_change(self, param, value, success):
        mapped = {
            "Throttle": "Throttle",
            "IdleRPM": "RPM",
        }
        sensor = mapped.get(param)
        if sensor:
            self.last_command_status[sensor] = success
        self.actuator_status.setText(f"Actuator command: {param}={value} -> {'OK' if success else 'FAIL'}")

    def _add_alert(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.alerts_list.insertItem(0, f"[{timestamp}] {message}")
        while self.alerts_list.count() > 50:
            self.alerts_list.takeItem(self.alerts_list.count() - 1)

    def _evaluate_health(self, rpm, speed, coolant, throttle, oil, dtc_count):
        if dtc_count > 0:
            return "⚠️ ATTENTION: DTC Present"
        if coolant > 105 or oil > 7 or speed > 180 or throttle > 90:
            return "⚠️ ATTENTION: Parameter Out-of-Range"
        if rpm <= 0 and speed <= 0:
            return "IDLE / STOPPED"
        return "✅ HEALTHY"

    def update_dashboard(self):
        self.sample_counter += 1

        rpm = self.reader.get_rpm()
        speed = self.reader.get_speed()
        coolant = self.reader.get_coolant_temp()
        throttle = self.reader.get_throttle()
        oil = self.reader.get_oil_pressure()
        dtcs = self.reader.get_dtc_codes()

        gauges = [
            (self.rpm_gauge, rpm, 7000, "RPM"),
            (self.speed_gauge, speed, 180, "Speed"),
            (self.coolant_gauge, coolant, 105, "Coolant"),
            (self.throttle_gauge, throttle, 90, "Throttle"),
            (self.oil_gauge, oil, 7, "Oil"),
        ]
        for gauge, value, limit, name in gauges:
            gauge.update_value(value)
            out = value > limit
            gauge.setStyleSheet("background-color: rgba(255,0,0,40);" if out else "")
            if out and self.sample_counter % 5 == 0:
                self._add_alert(f"{name} exceeded limit ({value:.1f} > {limit})")

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
        for dtc in dtcs:
            code = str(dtc[0]) if isinstance(dtc, (list, tuple)) and len(dtc) > 0 else str(dtc)
            info = get_dtc_info(code)
            self.dtc_list.addItem(
                f"{info['code']} | {info['severity']} | {info['system']} | {info['title']} | {info['recommendation']}"
            )

        self.health_label.setText(
            "Vehicle Health: "
            + self._evaluate_health(rpm, speed, coolant, throttle, oil, len(dtcs))
        )

        if self.logging_enabled:
            self.csv_writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                rpm,
                speed,
                coolant,
                throttle,
                oil,
            ])
            self.log_file.flush()
