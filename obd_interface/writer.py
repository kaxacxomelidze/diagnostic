import csv
import os
from datetime import datetime


class OBDWriter:
    def __init__(self, connection, log_dir="logs"):
        self.connection = connection
        self.limits = {
            "Throttle": (0.0, 100.0),
            "FuelTrim": (-20.0, 20.0),
            "IdleRPM": (600.0, 1200.0),
        }

        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, "actuator_history.csv")

        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Parameter", "Value", "Status"])

    def set_parameter(self, param, value):
        if param not in self.limits:
            return f"❌ Parameter '{param}' not supported"

        min_val, max_val = self.limits[param]
        if not (min_val <= value <= max_val):
            status = f"❌ Out of safe limits ({min_val}-{max_val})"
            self._log(param, value, status)
            return status

        try:
            # In a production version, send a UDS/OBD service message here.
            status = f"✅ {param} set to {value}"
            self._log(param, value, status)
            return status
        except Exception as exc:
            status = f"❌ Error: {exc}"
            self._log(param, value, status)
            return status

    def _log(self, param, value, status):
        with open(self.log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                param,
                value,
                status,
            ])
