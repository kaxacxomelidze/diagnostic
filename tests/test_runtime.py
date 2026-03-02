import os
import tempfile
import unittest

from obd_interface.connection import OBDConnection
from obd_interface.reader import OBDReader
from obd_interface.writer import OBDWriter
from utils.dtc_codes import get_dtc_info


class RuntimeBehaviorTests(unittest.TestCase):
    def test_connection_falls_back_to_simulation(self):
        os.environ["OBD_SIM_FALLBACK"] = "1"
        conn = OBDConnection()
        self.assertTrue(conn.connect())
        self.assertTrue(conn.simulation_mode)
        conn.disconnect()

    def test_reader_returns_numeric_values(self):
        os.environ["OBD_SIM_FALLBACK"] = "1"
        conn = OBDConnection()
        conn.connect()
        reader = OBDReader(conn.connection)

        self.assertGreaterEqual(reader.get_rpm(), 0)
        self.assertGreaterEqual(reader.get_speed(), 0)
        self.assertGreaterEqual(reader.get_coolant_temp(), 0)
        self.assertGreaterEqual(reader.get_throttle(), 0)
        self.assertGreaterEqual(reader.get_oil_pressure(), 0)
        self.assertIsInstance(reader.get_dtc_codes(), list)
        self.assertIsInstance(reader.get_vin(), str)

        conn.disconnect()

    def test_writer_limits_and_logging(self):
        os.environ["OBD_SIM_FALLBACK"] = "1"
        conn = OBDConnection()
        conn.connect()

        with tempfile.TemporaryDirectory() as d:
            writer = OBDWriter(conn.connection, log_dir=d)
            ok = writer.set_parameter("Throttle", 35)
            bad = writer.set_parameter("Throttle", 999)
            unsupported = writer.set_parameter("NoSuchParam", 1)

            self.assertTrue(ok.startswith("✅"))
            self.assertTrue(bad.startswith("❌"))
            self.assertTrue(unsupported.startswith("❌"))

            self.assertTrue(os.path.exists(os.path.join(d, "actuator_history.csv")))

        conn.disconnect()


if __name__ == "__main__":
    unittest.main()


class DtcInfoTests(unittest.TestCase):
    def test_known_and_unknown_dtc_info(self):
        known = get_dtc_info("P0171")
        unknown = get_dtc_info("P9999")
        self.assertEqual(known["code"], "P0171")
        self.assertIn("severity", known)
        self.assertEqual(unknown["title"], "Unknown DTC Code")

