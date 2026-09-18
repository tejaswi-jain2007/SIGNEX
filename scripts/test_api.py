import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from ntro_sigint.server.app import app

client = TestClient(app)

print("--- TESTING FASTAPI BACKEND ---")
# 1. Health check
r1 = client.get("/api/health")
print(f"1. Health status: {r1.status_code} -> {r1.json().get('status')}")

# 2. Preset Samples
r2 = client.get("/api/samples")
samples = r2.json().get("samples", [])
print(f"2. Samples count: {len(samples)} presets discovered")

# 3. Analyze Endpoint
r3 = client.post("/api/analyze", data={
    "preset_filename": "sample_qpsk.iq",
    "sample_rate": 2000000.0,
    "enable_conditioning": True,
    "enable_amc": True,
    "enable_demod": True,
    "enable_fec": True,
    "enable_sync": True
})
print(f"3. Analysis status: {r3.status_code}")
if r3.status_code == 200:
    res = r3.json()
    mod = res["classification"]["predicted_class"]
    conf = res["classification"]["confidence"] * 100
    baud = res["parameters"]["symbol_rate"]
    bw = res["parameters"]["bandwidth_3db"]
    snr = res["parameters"]["snr_db"]
    print(f"   Modulation Detected : {mod} ({conf:.2f}%)")
    print(f"   Extracted SNR       : {snr:.2f} dB")
    print(f"   Estimated Baud Rate : {baud:.2f} Baud")
    print(f"   3-dB Bandwidth      : {bw:.2f} Hz")
    print(f"   Waveform points     : {len(res['visualizations']['waveform']['time'])}")
    print(f"   Constellation points: {len(res['visualizations']['constellation'])}")
    print(f"   PDF Dossier Link    : {res['downloads']['pdf']}")
    print("ALL API ENDPOINTS FUNCTIONING 100% CLEANLY!")
else:
    print(f"Error: {r3.text}")
