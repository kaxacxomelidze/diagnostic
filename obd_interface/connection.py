import os
from dataclasses import dataclass

from obd_interface.compat import HAVE_PYOBD, obd
from obd_interface.simulator import SimulatedOBDConnection


@dataclass
class ConnectionConfig:
    """Runtime configuration for OBD connection."""

    port: str | None = None
    baudrate: int | None = None
    fast: bool = True
    timeout: float = 1.0
    allow_simulation_fallback: bool = True


class OBDConnection:
    def __init__(self, config: ConnectionConfig | None = None):
        self.config = config or ConnectionConfig(
            port=os.getenv("OBD_PORT") or None,
            baudrate=int(os.getenv("OBD_BAUDRATE", "0")) or None,
            fast=os.getenv("OBD_FAST", "1") != "0",
            timeout=float(os.getenv("OBD_TIMEOUT", "1.0")),
            allow_simulation_fallback=os.getenv("OBD_SIM_FALLBACK", "1") != "0",
        )
        self.connection = None
        self.simulation_mode = False

    def connect(self) -> bool:
        kwargs = {
            "portstr": self.config.port,
            "baudrate": self.config.baudrate,
            "fast": self.config.fast,
            "timeout": self.config.timeout,
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if HAVE_PYOBD:
            self.connection = obd.OBD(**kwargs)
            if self.connection.is_connected():
                print("✅ Connected to OBD-II")
                return True

        if self.config.allow_simulation_fallback:
            self.connection = SimulatedOBDConnection()
            self.simulation_mode = True
            print("⚠️ OBD adapter not found. Running in simulation mode.")
            return True

        print("❌ Failed to connect (python-OBD unavailable or adapter not found)")
        return False

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected")
