from PyQt5.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ActuatorPanel(QWidget):
    def __init__(self, writer, on_command_applied=None):
        super().__init__()
        self.writer = writer
        self.on_command_applied = on_command_applied
        self.setWindowTitle("ECU Parameter Control")
        self.resize(380, 260)

        root = QVBoxLayout(self)
        form_group = QGroupBox("Actuator parameters")
        form = QFormLayout(form_group)
        root.addWidget(form_group)

        self.param_inputs = {}
        self.status_label = QLabel("Ready")

        for param, (minimum, maximum) in writer.limits.items():
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"{minimum} .. {maximum}")
            row_layout.addWidget(input_field)

            btn = QPushButton(f"Set {param}")
            btn.clicked.connect(lambda _, p=param: self.set_param(p))
            row_layout.addWidget(btn)

            self.param_inputs[param] = input_field
            form.addRow(QLabel(param), row_widget)

        root.addWidget(self.status_label)

    def set_param(self, param):
        try:
            value = float(self.param_inputs[param].text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid number")
            return

        result = self.writer.set_parameter(param, value)
        self.status_label.setText(result)
        QMessageBox.information(self, "Result", result)

        if self.on_command_applied:
            self.on_command_applied(param, value, result.startswith("✅"))
