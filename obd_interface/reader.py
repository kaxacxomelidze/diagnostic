from obd_interface.compat import obd


class OBDReader:
    def __init__(self, connection):
        self.connection = connection

    def _read_numeric(self, command, default=0.0):
        response = self.connection.query(command)
        if response.is_null() or response.value is None:
            return default
        try:
            return float(response.value.magnitude)
        except Exception:
            return default

    def get_rpm(self):
        return self._read_numeric(obd.commands.RPM)

    def get_speed(self):
        return self._read_numeric(obd.commands.SPEED)

    def get_coolant_temp(self):
        return self._read_numeric(obd.commands.COOLANT_TEMP)

    def get_throttle(self):
        return self._read_numeric(obd.commands.THROTTLE_POS)

    def get_oil_pressure(self):
        oil_cmd = getattr(obd.commands, "OIL_PRESSURE", None)
        if oil_cmd is None:
            return 0.0
        return self._read_numeric(oil_cmd)

    def get_dtc_codes(self):
        response = self.connection.query(obd.commands.GET_DTC)
        if response.is_null() or response.value is None:
            return []
        return list(response.value)
