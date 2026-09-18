"""
Demo runner for NTRO SIGINT System.
Demonstrates:
1. Synthesizing a realistic modulated signal (e.g. QPSK / 16-QAM with channel noise).
2. Saving it to an IQ capture file with metadata sidecar.
3. Running the full end-to-end Air-Gapped SIGINT Analysis Pipeline.
4. Extracting RF parameters, modulation classification, bitstream demodulation, and PDF dossier generation.
"""

import os
import json
import tempfile
import numpy as np

import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ntro_sigint.core.pipeline import SignalAnalysisPipeline
from ntro_sigint.ml.dataset import SyntheticSignalGenerator

def run_demo():
    print("=" * 70)
    print("NTRO SIGINT SIGNAL ANALYSIS SYSTEM — DEMO RUNNER")
    print("=" * 70)

    # 1. Synthesize test signal
    print("[1/4] Generating synthetic QPSK signal (SNR = 22 dB, Fs = 2.0 MSps)...")
    gen = SyntheticSignalGenerator()
    samples = gen.generate_signal("QPSK", num_samples=65536, snr_db=22.0, fs=2.0e6, sps=8)

    # 2. Save capture file
    os.makedirs("data", exist_ok=True)
    iq_filepath = os.path.join("data", "demo_capture_qpsk.iq")
    iq_interleaved = np.empty(len(samples) * 2, dtype=np.float32)
    iq_interleaved[0::2] = samples.real
    iq_interleaved[1::2] = samples.imag
    with open(iq_filepath, "wb") as f:
        f.write(iq_interleaved.tobytes())

    sidecar_filepath = iq_filepath + ".json"
    with open(sidecar_filepath, "w", encoding="utf-8") as f:
        json.dump({"sample_rate": 2000000.0, "center_freq": 100000.0, "format": "float32"}, f, indent=2)

    print(f"      Saved I/Q capture to: {iq_filepath}")
    print(f"      Saved sidecar JSON to: {sidecar_filepath}")

    # 3. Initialize & run pipeline
    print("\n[2/4] Initializing Signal Analysis Pipeline with ResNet-18 AMC model...")
    pipeline = SignalAnalysisPipeline(model_path="models/amc_resnet18.pt", enforce_airgap=False)

    print("\n[3/4] Processing signal capture...")
    os.makedirs("reports", exist_ok=True)
    result = pipeline.process_file(
        filepath=iq_filepath,
        output_dir="reports",
        generate_pdf=True
    )

    # 4. Display results
    print("\n[4/4] Pipeline Results Summary:")
    print("-" * 70)
    print(f"Input File          : {result.input_file}")
    print(f"Sample Rate         : {result.sample_rate / 1e6:.2f} MSps")
    print(f"Duration            : {result.duration_sec * 1000:.2f} ms ({len(samples)} samples)")
    print(f"Modulation Detected : {result.classification['predicted_class']} (Confidence: {result.classification['confidence'] * 100:.2f}%)")
    print(f"Estimated SNR       : {result.parameters.get('snr_db', 0.0):.2f} dB")
    print(f"Carrier Offset (CFO): {result.parameters.get('carrier_frequency_offset', 0.0):.2f} Hz")
    print(f"Estimated Baud Rate : {result.parameters.get('symbol_rate', 0.0):.2f} Baud")
    print(f"3dB Bandwidth       : {result.parameters.get('bandwidth_3db', 0.0):.2f} Hz")
    print(f"99% Occupied BW     : {result.parameters.get('occupied_bandwidth_99', 0.0):.2f} Hz")
    print(f"PAPR                : {result.parameters.get('papr_db', 0.0):.2f} dB")
    print(f"Spectral Flatness   : {result.parameters.get('spectral_flatness', 0.0):.4f}")
    if result.demodulation:
        print(f"Demodulated Bits    : {result.demodulation.get('bit_count', 0)} bits")
        print(f"Demodulation EVM    : {result.demodulation.get('evm_percent', 0.0):.2f}%")
    print(f"Execution Time      : {result.execution_time_sec:.3f} seconds")
    print("-" * 70)
    print("Generated Artifacts:")
    for k, v in result.exported_files.items():
        print(f" - {k.upper()}: {v}")
    print("=" * 70)
    print("SUCCESS: End-to-end analysis completed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    run_demo()
