import sys

from PyQt5.QtWidgets import QApplication

from gui.dashboard import Dashboard
from obd_interface.connection import OBDConnection
from obd_interface.reader import OBDReader
from obd_interface.writer import OBDWriter


def main():
    obd_conn = OBDConnection()
    if not obd_conn.connect():
        return

    reader = OBDReader(obd_conn.connection)
    writer = OBDWriter(obd_conn.connection)

    app = QApplication(sys.argv)
    dashboard = Dashboard(reader, writer, simulation_mode=obd_conn.simulation_mode)
    dashboard.show()

    exit_code = app.exec_()
    obd_conn.disconnect()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
