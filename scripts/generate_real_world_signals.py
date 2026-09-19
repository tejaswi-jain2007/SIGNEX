"""
Generates realistic tactical, military, aviation, space, emergency, and maritime
signal captures (.iq and .wav) with encoded English intelligence and distress sentences.
"""

import os
import sys
import json
import wave
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ntro_sigint.ml.dataset import SyntheticSignalGenerator

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "test_samples")
os.makedirs(DATA_DIR, exist_ok=True)

REAL_SIGNALS = [
    {
        "id": "real_sos_mayday_maritime",
        "mod": "BPSK",
        "fs": 2000000.0,
        "snr": 26.0,
        "msg": "MAYDAY MAYDAY FISHING VESSEL SAGAR-1 ENGINE FIRE SINKING AT 15.24N 73.81E 6 CREW ABOARD NEED IMMEDIATE RESCUE OVER",
        "desc": "Maritime VHF Distress & Mayday Emergency Call"
    },
    {
        "id": "real_military_patrol_report",
        "mod": "QPSK",
        "fs": 2000000.0,
        "snr": 28.0,
        "msg": "PATROL BRAVO-2 TO HQ // SECTOR 7 BORDER CLEAR // GRID: 34.12N 74.88E // NO HOSTILE CONTACT // STATUS: NOMINAL",
        "desc": "Tactical Military Border Recon Patrol Stream"
    },
    {
        "id": "real_aviation_acars_telemetry",
        "mod": "2-FSK",
        "fs": 1000000.0,
        "snr": 27.0,
        "msg": "ACARS AIR-INDIA 302 FLIGHT ROUTE BOM-DEL ALTITUDE 35000FT CABIN PRESSURE 11.2PSI FUEL 8500KG STATUS NOMINAL",
        "desc": "Commercial Aircraft ACARS Engine & Route Telemetry"
    },
    {
        "id": "real_satellite_space_beacon",
        "mod": "BPSK",
        "fs": 2000000.0,
        "snr": 25.0,
        "msg": "ISRO SATELLITE BEACON // BATTERY: 28.4V // SOLAR PANEL: 98% // TEMP: -12.5C // UPLINK LOCKED // NTRO SIGINT",
        "desc": "ISRO Orbital Satellite Downlink & Power Telemetry"
    },
    {
        "id": "real_pocsag_hospital_alert",
        "mod": "2-FSK",
        "fs": 1000000.0,
        "snr": 29.0,
        "msg": "EMERGENCY ALERT // CODE RED TRAUMA CENTER // ICU ROOM 104 // MEDICAL TEAM ASSISTANCE REQUIRED IMMEDIATELY",
        "desc": "POCSAG Hospital Emergency Room Pager Broadcast"
    },
    {
        "id": "real_tactical_special_forces_sos",
        "mod": "BPSK",
        "fs": 2000000.0,
        "snr": 24.0,
        "msg": "I NEED HELP URGENT // POSITION COMPROMISED AT EXTRACTION POINT DELTA // SEND IMMEDIATE EVAC",
        "desc": "Special Operations Extraction Distress Beacon"
    },
    {
        "id": "real_air_traffic_control_broadcast",
        "mod": "QPSK",
        "fs": 2000000.0,
        "snr": 28.0,
        "msg": "ATC DELHI TOWER TO FLIGHT VT-XYZ WIND 270 AT 12 KNOTS RUNWAY 28 LEFT CLEARED FOR ILS APPROACH",
        "desc": "Civil Air Traffic Control Digital Uplink"
    },
    {
        "id": "real_defence_drone_telemetry",
        "mod": "16-QAM",
        "fs": 2000000.0,
        "snr": 30.0,
        "msg": "DRONE RECON UAV-9 // TARGET VEHICLE CONVOY TRACKED // SPEED: 65 KM/H // HEADING: 180 // NTRO DEFENCE",
        "desc": "Defence Drone Target Acquisition & Telemetry Stream"
    }
]

print("=" * 70)
print("GENERATING REAL-WORLD RF INTELLIGENCE SIGNALS (.IQ & .WAV)")
print("=" * 70)

for s in REAL_SIGNALS:
    num_samples = 65536
    sig = SyntheticSignalGenerator.generate_signal(
        mod_type=s["mod"],
        num_samples=num_samples,
        snr_db=s["snr"],
        fs=s["fs"],
        message_text=s["msg"],
        random_seed=101
    )

    # 1. Save complex64 .iq file
    iq_filename = f"{s['id']}.iq"
    iq_path = os.path.join(DATA_DIR, iq_filename)
    with open(iq_path, "wb") as f:
        f.write(sig.astype(np.complex64).tobytes())

    # 2. Save .json metadata sidecar
    meta = {
        "sample_rate": s["fs"],
        "center_freq": 1000000.0,
        "format": "complex64",
        "modulation": s["mod"],
        "nominal_snr_db": s["snr"],
        "description": s["desc"],
        "embedded_message": s["msg"]
    }
    with open(iq_path + ".json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # 3. Save standard SDR stereo .wav file (16-bit PCM: Left=I, Right=Q)
    wav_filename = f"{s['id']}.wav"
    wav_path = os.path.join(DATA_DIR, wav_filename)

    # Normalize IQ to int16 range
    max_val = np.max(np.abs([sig.real, sig.imag]))
    scale = 32000.0 / max(1e-6, max_val)
    i_pcm = (sig.real * scale).astype(np.int16)
    q_pcm = (sig.imag * scale).astype(np.int16)

    stereo_pcm = np.empty(len(i_pcm) * 2, dtype=np.int16)
    stereo_pcm[0::2] = i_pcm
    stereo_pcm[1::2] = q_pcm

    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(int(min(192000, s["fs"])))
        wf.writeframes(stereo_pcm.tobytes())

    # Metadata for WAV
    wav_meta = meta.copy()
    wav_meta["format"] = "wav"
    with open(wav_path + ".json", "w", encoding="utf-8") as f:
        json.dump(wav_meta, f, indent=2)

    print(f"[OK] Generated {iq_filename} & {wav_filename}")
    print(f"     Mod: {s['mod']} | Message: '{s['msg'][:50]}...'")

print("=" * 70)
print(f"Successfully generated {len(REAL_SIGNALS) * 2} signals in data/test_samples/!")
print("=" * 70)
