import math
import random
import time

from obd_interface.compat import obd


class SimulatedResponse:
    def __init__(self, value=None):
        self.value = value

    def is_null(self):
        return self.value is None


class SimulatedMeasurement:
    def __init__(self, magnitude):
        self.magnitude = magnitude


class SimulatedOBDConnection:
    """Small in-memory OBD simulator for offline GUI testing."""

    def __init__(self):
        self._start = time.time()
        self._connected = True

    def is_connected(self):
        return self._connected

    def close(self):
        self._connected = False

    def query(self, cmd):
        t = time.time() - self._start

        if cmd == obd.commands.RPM:
            value = 900 + 700 * (1 + math.sin(t * 1.8))
            return SimulatedResponse(SimulatedMeasurement(value))

        if cmd == obd.commands.SPEED:
            value = max(0, 40 + 40 * math.sin(t * 0.5) + random.uniform(-2, 2))
            return SimulatedResponse(SimulatedMeasurement(value))

        if cmd == obd.commands.COOLANT_TEMP:
            value = min(110, 75 + t * 0.03 + random.uniform(-0.6, 0.6))
            return SimulatedResponse(SimulatedMeasurement(value))

        if cmd == obd.commands.THROTTLE_POS:
            value = max(0, min(100, 25 + 20 * math.sin(t * 1.2) + random.uniform(-3, 3)))
            return SimulatedResponse(SimulatedMeasurement(value))

        oil_cmd = getattr(obd.commands, "OIL_PRESSURE", None)
        if oil_cmd and cmd == oil_cmd:
            value = max(1, min(8, 3.5 + 1.8 * math.sin(t) + random.uniform(-0.2, 0.2)))
            return SimulatedResponse(SimulatedMeasurement(value))

        if cmd == obd.commands.GET_DTC:
            if int(t) % 40 > 30:
                return SimulatedResponse([("P0171", "System Too Lean")])
            return SimulatedResponse([])

        return SimulatedResponse(None)
