# OBD-II Professional Diagnostic Dashboard

Enhanced PyQt5 desktop dashboard for vehicle diagnostics with:

- Live gauges: RPM, speed, coolant, throttle, oil pressure
- Dynamic multi-sensor graph with flashing out-of-range alerts
- Actuator control panel with safety limits and history logging
- DTC reader with code descriptions
- CSV vehicle telemetry logging

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Project structure

```
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
│   └── writer.py
└── utils/
    └── dtc_codes.py
```

## Notes

- Uses `python-OBD`; real actuator writing needs ECU-specific logic.
- Optional env vars: `OBD_PORT`, `OBD_BAUDRATE`, `OBD_FAST`, `OBD_TIMEOUT`.
- Logs are saved in `logs/`.
