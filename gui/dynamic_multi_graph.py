from collections import deque

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from PyQt5.QtGui import QColor


class MultiSensorGraph:
    def __init__(self, plot_widget, sensors, limits=None, max_points=120):
        self.plot_widget = plot_widget
        self.max_points = max_points
        self.sensors = sensors
        self.limits = limits if limits else {s: (0, 9999) for s in sensors}

        self.data = {name: deque(maxlen=max_points) for name in sensors}
        self.overlay_data = {name: deque(maxlen=max_points) for name in sensors}
        self.new_values = {name: 0.0 for name in sensors}
        self.flash_state = False

        self.curves = {}
        self.overlay_curves = {}

        for sensor, color in sensors.items():
            self.curves[sensor] = plot_widget.plot(
                pen=pg.mkPen(color=color, width=2),
                name=sensor,
            )
            self.overlay_curves[sensor] = pg.ScatterPlotItem(size=9, brush=QColor("red"))
            plot_widget.addItem(self.overlay_curves[sensor])

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(200)

    def append_values(self, values_dict, actuator_changes=None):
        for s, v in values_dict.items():
            if s in self.new_values:
                self.new_values[s] = float(v)

        actuator_changes = actuator_changes or {}
        for s in self.sensors:
            changed = actuator_changes.get(s, False)
            self.overlay_data[s].append(self.new_values[s] if changed else None)

    def update_plot(self):
        self.flash_state = not self.flash_state

        for sensor in self.sensors:
            self.data[sensor].append(self.new_values[sensor])
            y_data = list(self.data[sensor])
            x_data = list(range(len(y_data)))

            min_val, max_val = self.limits.get(sensor, (0, 9999))
            current = y_data[-1]
            if current > max_val or current < min_val:
                line_color = QColor("red") if self.flash_state else QColor(self.sensors[sensor])
            else:
                line_color = QColor(self.sensors[sensor])

            self.curves[sensor].setData(x=x_data, y=y_data, pen=pg.mkPen(line_color, width=2))

            overlay_y = list(self.overlay_data[sensor])
            overlay_points = [
                {"pos": (i, v)}
                for i, v in enumerate(overlay_y)
                if v is not None
            ]
            self.overlay_curves[sensor].setData(overlay_points)
