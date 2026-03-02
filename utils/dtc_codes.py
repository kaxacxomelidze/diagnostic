DTC_DESCRIPTIONS = {
    "P0100": "Mass or Volume Air Flow Circuit Malfunction",
    "P0171": "System Too Lean (Bank 1)",
    "P0174": "System Too Lean (Bank 2)",
    "P0300": "Random/Multiple Cylinder Misfire Detected",
    "P0420": "Catalyst System Efficiency Below Threshold",
    "P0442": "Evaporative Emission System Leak Detected (small leak)",
    "P0500": "Vehicle Speed Sensor A",
}


def get_description(code: str) -> str:
    return DTC_DESCRIPTIONS.get(code, "Unknown DTC Code")
