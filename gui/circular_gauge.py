import math

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPen
from PyQt5.QtWidgets import QWidget


class CircularGauge(QWidget):
    def __init__(self, label, min_val=0, max_val=100, units="", warning_zones=None):
        super().__init__()
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.units = units
        self.value = min_val
        self.warning_zones = warning_zones if warning_zones else []
        self.setMinimumSize(180, 180)

    def update_value(self, value):
        self.value = max(self.min_val, min(value, self.max_val))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(12, 12, -12, -12)
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2

        painter.setPen(QPen(Qt.lightGray, 6))
        painter.drawEllipse(center, radius, radius)

        for start, end, color in self.warning_zones:
            painter.setPen(QPen(QColor(color), 10))
            start_angle = 225 + 270 * (start - self.min_val) / (self.max_val - self.min_val)
            span_angle = 270 * (end - start) / (self.max_val - self.min_val)
            painter.drawArc(rect, int((360 - start_angle) * 16), int(-span_angle * 16))

        angle = 225 + 270 * (self.value - self.min_val) / (self.max_val - self.min_val)
        rad = math.radians(angle)

        painter.setPen(QPen(Qt.red, 3))
        painter.drawLine(
            center.x(),
            center.y(),
            int(center.x() + radius * 0.75 * math.cos(rad)),
            int(center.y() + radius * 0.75 * math.sin(rad)),
        )

        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(
            rect,
            Qt.AlignCenter,
            f"{self.label}\n{self.value:.1f} {self.units}".strip(),
        )
