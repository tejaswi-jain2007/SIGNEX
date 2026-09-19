import os
import sys
import json
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ntro_sigint.ml.dataset import SyntheticSignalGenerator

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "test_samples")
os.makedirs(DATA_DIR, exist_ok=True)

SAMPLES = [
    {
        "filename": "sample_bpsk.iq",
        "mod": "BPSK",
        "fs": 2000000.0,
        "msg": "NTRO BEACON // LAT: 28.6139N LON: 77.2090E // FREQ: 2.412 GHz // STATUS: OPERATIONAL",
        "desc": "BPSK Tactical Beacon with GPS Telemetry"
    },
    {
        "filename": "sample_qpsk.iq",
        "mod": "QPSK",
        "fs": 2000000.0,
        "msg": "SATELLITE TELEMETRY // SENSOR: IR-CAM-4 // TEMP: 24.5C // ALTITUDE: 420KM // STATUS: NOMINAL // NTRO SIGINT",
        "desc": "QPSK Satellite Telemetry & Sensor Packet"
    },
    {
        "filename": "sample_2_fsk.iq",
        "mod": "2-FSK",
        "fs": 1000000.0,
        "msg": "TACTICAL VHF DATA LINK // NODE: ALPHA-09 // AUTH: VERIFIED // MESSAGE: AIRSPACE MONITOR ACTIVE",
        "desc": "2-FSK Tactical Data Link Message"
    },
    {
        "filename": "sample_16_qam.iq",
        "mod": "16-QAM",
        "fs": 2000000.0,
        "msg": "HIGH-SPEED DIGITAL BACKHAUL // PACKET: 0x4A12 // TRANSMITTER: 0x01FA // PAYLOAD: SECURE ENCLAVE ACTIVE",
        "desc": "16-QAM High-Speed Backhaul Stream"
    },
    {
        "filename": "sample_64_qam.iq",
        "mod": "64-QAM",
        "fs": 2000000.0,
        "msg": "WIDEBAND MICROWAVE RELAY // LINK SNR: +28.4 dB // THROUGHPUT: 155 MBPS // CARRIER LOCK CONFIRMED",
        "desc": "64-QAM Microwave Relay Carrier"
    }
]

for s in SAMPLES:
    iq_path = os.path.join(DATA_DIR, s["filename"])
    meta_path = iq_path + ".json"

    # Generate 65,536 samples with embedded message
    sig = SyntheticSignalGenerator.generate_signal(
        mod_type=s["mod"],
        num_samples=65536,
        snr_db=28.0,
        fs=s["fs"],
        message_text=s["msg"],
        random_seed=42
    )

    # Save as complex64 binary .iq
    with open(iq_path, "wb") as f:
        f.write(sig.astype(np.complex64).tobytes())

    # Save sidecar metadata
    meta = {
        "sample_rate": s["fs"],
        "center_freq": 100000.0,
        "format": "complex64",
        "modulation": s["mod"],
        "nominal_snr_db": 28.0,
        "description": s["desc"],
        "embedded_message": s["msg"]
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Generated {s['filename']} with embedded message: '{s['msg'][:40]}...'")

print("All rich test samples generated successfully!")
