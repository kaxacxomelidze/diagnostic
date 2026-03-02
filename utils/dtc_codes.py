DTC_DATABASE = {
    "P0100": {
        "title": "Mass or Volume Air Flow Circuit Malfunction",
        "severity": "medium",
        "system": "Intake",
        "recommendation": "Inspect MAF sensor wiring and intake leaks.",
    },
    "P0171": {
        "title": "System Too Lean (Bank 1)",
        "severity": "high",
        "system": "Fuel/Air",
        "recommendation": "Check vacuum leaks, fuel pressure, and MAF readings.",
    },
    "P0174": {
        "title": "System Too Lean (Bank 2)",
        "severity": "high",
        "system": "Fuel/Air",
        "recommendation": "Inspect intake leaks and injector behavior on bank 2.",
    },
    "P0300": {
        "title": "Random/Multiple Cylinder Misfire Detected",
        "severity": "critical",
        "system": "Ignition/Combustion",
        "recommendation": "Avoid heavy load. Check plugs, coils, and fuel delivery.",
    },
    "P0420": {
        "title": "Catalyst System Efficiency Below Threshold",
        "severity": "medium",
        "system": "Emissions",
        "recommendation": "Inspect catalytic converter and O2 sensor trends.",
    },
    "P0442": {
        "title": "Evaporative Emission System Leak Detected (small leak)",
        "severity": "low",
        "system": "EVAP",
        "recommendation": "Check fuel cap seal and EVAP lines.",
    },
    "P0500": {
        "title": "Vehicle Speed Sensor A",
        "severity": "medium",
        "system": "Transmission/ABS",
        "recommendation": "Inspect VSS sensor signal and wiring harness.",
    },
}


def get_dtc_info(code: str) -> dict:
    base = DTC_DATABASE.get(
        code,
        {
            "title": "Unknown DTC Code",
            "severity": "unknown",
            "system": "Unknown",
            "recommendation": "Use OEM documentation or extended DTC database.",
        },
    )
    return {"code": code, **base}


def get_description(code: str) -> str:
    return get_dtc_info(code)["title"]
