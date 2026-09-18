"""
Generate a diverse suite of sample .IQ and .WAV test files for testing in GUI / CLI.
Generates files for:
- QPSK
- 16-QAM
- BPSK
- 8-PSK
- 2-FSK
- 4-FSK
- 64-QAM
- AM-DSB
- WBFM
"""

import os
import sys
import json
from pathlib import Path
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ntro_sigint.ml.dataset import SyntheticSignalGenerator, MODULATION_CLASSES

def generate_test_iq_suite():
    output_dir = os.path.join(str(PROJECT_ROOT), "data", "test_samples")
    os.makedirs(output_dir, exist_ok=True)
    gen = SyntheticSignalGenerator()

    sample_configs = [
        {"mod": "QPSK", "snr": 25.0, "fs": 2.0e6, "fc": 100000.0, "samples": 65536, "desc": "Clean QPSK Satellite Telemetry"},
        {"mod": "16-QAM", "snr": 28.0, "fs": 4.0e6, "fc": 250000.0, "samples": 65536, "desc": "High-Order 16-QAM Broadband Link"},
        {"mod": "BPSK", "snr": 18.0, "fs": 1.0e6, "fc": 50000.0, "samples": 65536, "desc": "Standard BPSK Tactical Datalink"},
        {"mod": "8-PSK", "snr": 22.0, "fs": 2.0e6, "fc": 150000.0, "samples": 65536, "desc": "8-PSK High Spectral Efficiency Carrier"},
        {"mod": "2-FSK", "snr": 20.0, "fs": 1.0e6, "fc": 0.0, "samples": 65536, "desc": "2-FSK Military Frequency Shift Keying"},
        {"mod": "4-FSK", "snr": 22.0, "fs": 2.0e6, "fc": 80000.0, "samples": 65536, "desc": "4-FSK Multi-Level FSK Telemetry"},
        {"mod": "64-QAM", "snr": 30.0, "fs": 5.0e6, "fc": 300000.0, "samples": 65536, "desc": "64-QAM Dense Constellation Link"},
        {"mod": "AM-DSB", "snr": 24.0, "fs": 1.0e6, "fc": 0.0, "samples": 65536, "desc": "AM Double Sideband Voice Broadcast"},
        {"mod": "WBFM", "snr": 26.0, "fs": 2.0e6, "fc": 120000.0, "samples": 65536, "desc": "Wideband Frequency Modulated Radio"},
    ]

    print("=" * 70)
    print("GENERATING SAMPLE TEST IQ FILES FOR GUI & CLI VERIFICATION")
    print(f"Target Directory: {output_dir}")
    print("=" * 70)

    for cfg in sample_configs:
        mod = cfg["mod"]
        fs = cfg["fs"]
        snr = cfg["snr"]
        n_samp = cfg["samples"]
        fc = cfg["fc"]

        # Generate baseband signal
        sig = gen.generate_signal(mod, num_samples=n_samp, snr_db=snr, fs=fs, sps=8)

        # Apply center frequency shift if specified
        if fc != 0.0:
            t = np.arange(n_samp) / fs
            sig = sig * np.exp(1j * 2.0 * np.pi * fc * t).astype(np.complex64)

        # File naming
        filename_base = f"sample_{mod.lower().replace('-', '_')}"
        iq_file = os.path.join(output_dir, f"{filename_base}.iq")
        sidecar_file = os.path.join(output_dir, f"{filename_base}.iq.json")

        # Save float32 interleaved I/Q
        iq_interleaved = np.empty(len(sig) * 2, dtype=np.float32)
        iq_interleaved[0::2] = sig.real
        iq_interleaved[1::2] = sig.imag
        with open(iq_file, "wb") as f:
            f.write(iq_interleaved.tobytes())

        # Save metadata sidecar
        sidecar = {
            "sample_rate": fs,
            "center_freq": fc,
            "format": "float32",
            "modulation": mod,
            "nominal_snr_db": snr,
            "description": cfg["desc"]
        }
        with open(sidecar_file, "w", encoding="utf-8") as f:
            json.dump(sidecar, f, indent=2)

        file_size_kb = os.path.getsize(iq_file) / 1024
        print(f" [OK] Generated: {filename_base}.iq ({file_size_kb:.1f} KB) -> {mod} @ {fs/1e6:.1f} MSps ({cfg['desc']})")

    print("=" * 70)
    print(f"All sample IQ files generated successfully in: data/test_samples/")
    print("You can now open the GUI and click 'Browse' to select any of these files!")
    print("=" * 70)

if __name__ == "__main__":
    generate_test_iq_suite()
