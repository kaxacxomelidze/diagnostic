# OBD-II Professional Diagnostic Dashboard

Enhanced PyQt5 desktop dashboard for vehicle diagnostics with:

- Live gauges: RPM, speed, coolant, throttle, oil pressure
- Dynamic multi-sensor graph with flashing out-of-range alerts
- Actuator control panel with safety limits and history logging
- DTC reader with severity, affected system, and recommendation text
- DTC report export to CSV
- Live alert feed for threshold violations and actions
- CSV vehicle telemetry logging (pause/resume)
- Automatic simulation fallback when no adapter is connected

## Install libraries

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` includes:
- `pyqt5`
- `pyqtgraph`
- `obd`

## Run application

```bash
python main.py
```

## Run tests (no pytest required)

```bash
python -m unittest -v tests/test_runtime.py
```

## Configuration

Optional env vars:

- `OBD_PORT` (example `/dev/ttyUSB0`)
- `OBD_BAUDRATE` (example `38400`)
- `OBD_FAST` (`1` or `0`)
- `OBD_TIMEOUT` (seconds, e.g. `1.0`)
- `OBD_SIM_FALLBACK` (`1` default; set `0` to disable simulation mode)

## Logs and reports

- `logs/vehicle_log.csv`: periodic vehicle telemetry
- `logs/actuator_history.csv`: actuator command history
- `logs/dtc_report.csv`: exported DTC report from dashboard button

## Notes

- If `python-OBD` is installed and adapter exists, app runs in live mode; otherwise it still runs in simulation mode.
- Real actuator writing still needs ECU/UDS-specific implementation for production vehicles.
- In simulation mode, sensor values are generated to let you test UI behavior end-to-end.
