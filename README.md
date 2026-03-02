# OBD-II Professional Diagnostic Dashboard

Enhanced PyQt5 desktop dashboard for vehicle diagnostics with:

- Live gauges: RPM, speed, coolant, throttle, oil pressure
- Dynamic multi-sensor graph with flashing out-of-range alerts
- Actuator control panel with safety limits and history logging
- DTC reader with code descriptions
- CSV vehicle telemetry logging
- **Automatic simulation fallback** when no adapter is connected

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Project structure

```text
OBD_Diagnostics/
├── main.py
├── gui/
│   ├── dashboard.py
│   ├── circular_gauge.py
│   ├── actuator_panel.py
│   └── dynamic_multi_graph.py
├── obd_interface/
│   ├── connection.py
│   ├── reader.py
│   ├── writer.py
│   └── simulator.py
└── utils/
    └── dtc_codes.py
```

## Configuration

Optional env vars:

- `OBD_PORT` (example `/dev/ttyUSB0`)
- `OBD_BAUDRATE` (example `38400`)
- `OBD_FAST` (`1` or `0`)
- `OBD_TIMEOUT` (seconds, e.g. `1.0`)
- `OBD_SIM_FALLBACK` (`1` default; set `0` to disable simulation mode)

## Logs

- `logs/vehicle_log.csv`: periodic vehicle telemetry
- `logs/actuator_history.csv`: actuator command history

## Notes

- Uses `python-OBD`; real actuator writing needs ECU/UDS-specific implementation.
- In simulation mode, sensor values are generated to let you test UI behavior end-to-end.
