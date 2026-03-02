import os
from dataclasses import dataclass

import obd


@dataclass
class ConnectionConfig:
    """Runtime configuration for OBD connection."""

    port: str | None = None
    baudrate: int | None = None
    fast: bool = True
    timeout: float = 1.0


class OBDConnection:
    def __init__(self, config: ConnectionConfig | None = None):
        self.config = config or ConnectionConfig(
            port=os.getenv("OBD_PORT") or None,
            baudrate=int(os.getenv("OBD_BAUDRATE", "0")) or None,
            fast=os.getenv("OBD_FAST", "1") != "0",
            timeout=float(os.getenv("OBD_TIMEOUT", "1.0")),
        )
        self.connection = None

    def connect(self) -> bool:
        kwargs = {
            "portstr": self.config.port,
            "baudrate": self.config.baudrate,
            "fast": self.config.fast,
            "timeout": self.config.timeout,
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        self.connection = obd.OBD(**kwargs)
        if self.connection.is_connected():
            print("✅ Connected to OBD-II")
            return True

        print("❌ Failed to connect")
        return False

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected")
