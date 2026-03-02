"""Compatibility helpers for environments without python-OBD installed."""

from types import SimpleNamespace


class _DummyOBDConnection:
    def __init__(self, *args, **kwargs):
        self._connected = False

    def is_connected(self):
        return False

    def close(self):
        return None


class _DummyCommands(SimpleNamespace):
    RPM = "RPM"
    SPEED = "SPEED"
    COOLANT_TEMP = "COOLANT_TEMP"
    THROTTLE_POS = "THROTTLE_POS"
    OIL_PRESSURE = "OIL_PRESSURE"
    GET_DTC = "GET_DTC"


try:
    import obd as _real_obd  # type: ignore

    obd = _real_obd
    HAVE_PYOBD = True
except Exception:
    obd = SimpleNamespace(OBD=_DummyOBDConnection, commands=_DummyCommands())
    HAVE_PYOBD = False
