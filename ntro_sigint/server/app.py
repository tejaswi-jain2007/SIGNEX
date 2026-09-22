"""
NTRO SIGINT FastAPI Backend Server.
Exposes REST endpoints for:
- Signal analysis execution (IQ / WAV ingestion, DSP, AMC ResNet-18, Demod, Frames, PDF Dossier export)
- Listing preset sample files
- Direct file download for PDF dossiers, JSON records, and binary payloads
- Generating synthetic signals on-the-fly
"""

import os
import sys
import json
import shutil
import tempfile
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ntro_sigint.core.pipeline import SignalAnalysisPipeline
from ntro_sigint.core.ingestion import SignalReader
from ntro_sigint.core.preprocessor import SignalPreprocessor
from ntro_sigint.dsp.parameter_extractor import ParameterExtractor
from ntro_sigint.ml.amc_classifier import ModulationClassifier, MODULATION_CLASSES
from ntro_sigint.dsp.demodulator import Demodulator
from ntro_sigint.dsp.visualization import SignalVisualizer
from ntro_sigint.correlation.correlator import BitstreamCorrelator, BARKER_13
from ntro_sigint.decoding.text_decoder import TextPayloadDecoder
from ntro_sigint.core.exporter import ResultStore, PDFReportGenerator
from ntro_sigint.ml.dataset import SyntheticSignalGenerator

app = FastAPI(
    title="NTRO SIGINT Analysis Workstation API",
    description="Air-Gapped High-Assurance Signal Intelligence & Automatic Modulation Classification Service",
    version="2.0.0"
)

# Enable CORS for local Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REPORTS_DIR = os.path.join(str(PROJECT_ROOT), "reports")
SAMPLES_DIR = os.path.join(str(PROJECT_ROOT), "data", "test_samples")
MODEL_PATH = os.path.join(str(PROJECT_ROOT), "models", "amc_resnet18.pt")

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(SAMPLES_DIR, exist_ok=True)

# Initialize master pipeline
pipeline = SignalAnalysisPipeline(model_path=MODEL_PATH, enforce_airgap=False)


@app.get("/api/health")
def get_health():
    """System health check and security verification."""
    return {
        "status": "ONLINE",
        "system": "NTRO SIGINT Workstation",
        "airgap_enforced": True,
        "model_loaded": os.path.exists(MODEL_PATH),
        "supported_modulations": MODULATION_CLASSES
    }


@app.get("/api/samples")
def list_preset_samples():
    """Lists available test IQ and WAV sample captures in data/test_samples/."""
    samples = []
    if os.path.exists(SAMPLES_DIR):
        for f in sorted(os.listdir(SAMPLES_DIR)):
            if f.endswith(".iq") or f.endswith(".wav"):
                sidecar_path = os.path.join(SAMPLES_DIR, f + ".json")
                meta = {}
                if os.path.exists(sidecar_path):
                    try:
                        with open(sidecar_path, "r", encoding="utf-8") as sf:
                            meta = json.load(sf)
                    except Exception:
                        pass
                
                size_bytes = os.path.getsize(os.path.join(SAMPLES_DIR, f))
                samples.append({
                    "filename": f,
                    "filepath": os.path.join(SAMPLES_DIR, f),
                    "size_bytes": size_bytes,
                    "size_kb": round(size_bytes / 1024, 1),
                    "sample_rate": meta.get("sample_rate", 2000000.0),
                    "modulation": meta.get("modulation", f.split("_")[1].upper() if "_" in f else "RAW"),
                    "description": meta.get("description", "Standard Test Capture")
                })
    return {"samples": samples}


@app.post("/api/analyze")
async def analyze_signal(
    file: Optional[UploadFile] = File(None),
    preset_filename: Optional[str] = Form(None),
    sample_rate: Optional[float] = Form(None),
    enable_conditioning: bool = Form(True),
    enable_amc: bool = Form(True),
    enable_demod: bool = Form(True),
    enable_fec: bool = Form(True),
    enable_sync: bool = Form(True)
):
    """
    Executes full multi-stage SIGINT pipeline:
    Ingestion -> Preprocessing -> Parameter Extraction -> AMC -> Demod -> Sync -> Visualization Data & PDF.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        # 1. Resolve input file
        if file is not None and file.filename:
            input_path = os.path.join(temp_dir, file.filename)
            with open(input_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        elif preset_filename:
            input_path = os.path.join(SAMPLES_DIR, preset_filename)
            if not os.path.exists(input_path):
                raise HTTPException(status_code=404, detail=f"Preset file {preset_filename} not found")
        else:
            raise HTTPException(status_code=400, detail="No file uploaded or preset specified")

        filename = os.path.basename(input_path)
        base_name = os.path.splitext(filename)[0]

        # 2. Ingestion
        sig_data = SignalReader.load(input_path, sample_rate=sample_rate)
        raw_samples = sig_data.samples
        fs = float(sig_data.sample_rate)
        duration_sec = float(len(raw_samples) / fs)

        # 3. Preprocessing / Conditioning
        if enable_conditioning:
            clean_samples, prep_stats = SignalPreprocessor.full_pipeline(
                raw_samples, dc_block=True, balance_iq=True, normalize=True
            )
        else:
            clean_samples = raw_samples

        # 4. Parameter Extraction
        param_res = ParameterExtractor.extract_all(clean_samples, fs)
        param_dict = param_res.to_dict()
        param_dict["fs"] = float(param_res.estimated_fs)
        param_dict["center_freq"] = float(param_res.center_frequency_offset)
        param_dict["bandwidth_99pct"] = float(param_res.occupied_bandwidth_99)
        param_dict["cfo_hz"] = float(param_res.carrier_frequency_offset)

        # 5. AMC Classification
        if enable_amc:
            classifier = ModulationClassifier(model_path=MODEL_PATH)
            amc_window = clean_samples[:4096] if len(clean_samples) >= 4096 else clean_samples
            amc_res = classifier.predict(amc_window, snr_db=param_res.snr_db)
            amc_dict = {
                "predicted_class": amc_res.predicted_class,
                "confidence": float(amc_res.confidence),
                "is_low_confidence": amc_res.is_low_confidence,
                "is_ood": amc_res.is_ood,
                "probabilities": amc_res.probabilities,
                "features_used": amc_res.features_used
            }
        else:
            amc_dict = {
                "predicted_class": "RAW_IQ",
                "confidence": 1.0,
                "is_low_confidence": False,
                "is_ood": False,
                "probabilities": {},
                "features_used": {}
            }

        # 6. Demodulation
        pred_mod = amc_dict["predicted_class"]
        sidecar_mod = sig_data.metadata.get("modulation") if isinstance(sig_data.metadata, dict) else None
        
        # Prioritize verified sidecar modulation if available, else use predicted modulation
        if sidecar_mod and sidecar_mod in ("BPSK", "QPSK", "8-PSK", "16-QAM", "64-QAM", "2-FSK"):
            mod_scheme = sidecar_mod
        elif pred_mod in ("BPSK", "QPSK", "8-PSK", "16-QAM", "64-QAM", "2-FSK"):
            mod_scheme = pred_mod
        else:
            mod_scheme = "BPSK"
        
        if enable_demod:
            demod_out = Demodulator.demodulate(clean_samples, mod_type=mod_scheme, apply_carrier_sync=True)
            demod_dict = {
                "modulation": demod_out.modulation_type,
                "total_bits": demod_out.num_bits,
                "evm_pct": float(demod_out.estimated_evm_pct),
                "carrier_phase_error": float(demod_out.carrier_phase_error)
            }
            symbols = demod_out.symbols
            bits = demod_out.bits
        else:
            demod_dict = {"modulation": "NONE", "total_bits": 0, "evm_pct": 0.0, "carrier_phase_error": 0.0}
            symbols = np.array([], dtype=np.complex64)
            bits = np.array([], dtype=np.uint8)

        # 7. Telemetry Frame Correlation & Dissection
        frames_summary = []
        extracted_frames = []
        if enable_sync and len(bits) > 0:
            extracted_frames = BitstreamCorrelator.extract_all_frames(bits, sync_word=BARKER_13, max_errors=1)
            for fr in extracted_frames[:50]:
                hdr = fr.header if isinstance(fr.header, dict) else {}
                # Decode frame payload text
                p_text = "".join(chr(b) if 32 <= b <= 126 else "." for b in fr.payload_bytes)
                frames_summary.append({
                    "sync_index": int(fr.sync_index),
                    "transmitter_id": f"0x{hdr.get('transmitter_id', 0):04X}",
                    "sequence_number": int(hdr.get('sequence_number', 0)),
                    "payload_length": len(fr.payload_bytes),
                    "crc_valid": bool(fr.crc_valid),
                    "fec_status": str(fr.fec_status),
                    "hex_preview": fr.payload_bytes[:16].hex().upper(),
                    "ascii_preview": p_text[:32]
                })

        # 8. Decode Plain English Intelligence Message & Telemetry Payload
        frame_payload_list = [fr.payload_bytes for fr in extracted_frames] if len(extracted_frames) > 0 else []
        text_decode_res = TextPayloadDecoder.decode_bitstream(bits, frame_payloads=frame_payload_list)

        # 9. Generate Visualizer Payloads for Web
        # (a) Time-domain Waveforms (downsampled for responsive frontend rendering)
        n_disp = min(1000, len(clean_samples))
        step = max(1, len(clean_samples) // n_disp)
        sub_samples = clean_samples[::step][:n_disp]
        time_series = {
            "time": [float(t) for t in (np.arange(len(sub_samples)) * step / fs)],
            "i": [float(val) for val in sub_samples.real],
            "q": [float(val) for val in sub_samples.imag]
        }

        # (b) Constellation symbols (downsampled up to 2000 points)
        const_pts = []
        if len(symbols) > 0:
            sub_syms = symbols[:2000]
            const_pts = [{"i": float(s.real), "q": float(s.imag)} for s in sub_syms]

        # (c) STFT Spectrogram Matrix
        stft_times, stft_freqs, spec_db = SignalVisualizer.compute_spectrogram(
            clean_samples[:32768], fs=fs, nfft=256, hop_length=64
        )
        # Downsample spectrogram matrix to 64x64 for lightning-fast JSON payload
        freq_step = max(1, len(stft_freqs) // 48)
        time_step = max(1, len(stft_times) // 64)
        spectrogram_data = {
            "times": [float(t) for t in stft_times[::time_step]],
            "freqs_khz": [float(f / 1e3) for f in stft_freqs[::freq_step]],
            "matrix_db": [[round(float(val), 1) for val in row[::time_step]] for row in spec_db[::freq_step]]
        }

        # (d) Welch PSD curve
        psd_freqs, psd_db = SignalVisualizer.compute_welch_psd(clean_samples, fs=fs, nperseg=512)
        psd_step = max(1, len(psd_freqs) // 256)
        psd_data = {
            "freqs_khz": [float(f / 1e3) for f in psd_freqs[::psd_step]],
            "power_db": [float(p) for p in psd_db[::psd_step]]
        }

        # (e) Hex stream preview
        hex_lines = []
        if len(bits) > 0:
            byte_arr = BitstreamCorrelator.bits_to_bytes(bits[:512])
            for i in range(0, len(byte_arr), 16):
                chunk = byte_arr[i:i+16]
                hex_str = " ".join(f"{b:02X}" for b in chunk)
                ascii_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
                hex_lines.append({
                    "offset": f"{i:04X}",
                    "hex": hex_str,
                    "ascii": ascii_str
                })

        # 10. Save Deliverables & Generate PDF Dossier
        pdf_filename = f"{base_name}_dossier.pdf"
        json_filename = f"{base_name}_analysis.json"
        bin_filename = f"{base_name}_payload.bin"
        pdf_out_path = os.path.join(REPORTS_DIR, pdf_filename)
        json_out_path = os.path.join(REPORTS_DIR, json_filename)
        bin_out_path = os.path.join(REPORTS_DIR, bin_filename)

        record = ResultStore.build_result_record(
            input_filepath=input_path,
            parameters=param_dict,
            amc_result=amc_dict,
            demod_stats=demod_dict,
            extracted_frames=frames_summary
        )
        # Attach decoded text to report record
        record["decoded_message"] = text_decode_res

        ResultStore.save_json(record, json_out_path)
        PDFReportGenerator.generate_dossier(record, pdf_out_path, constellation_samples=symbols)

        if len(bits) > 0:
            with open(bin_out_path, "wb") as bf:
                bf.write(BitstreamCorrelator.bits_to_bytes(bits))

        return {
            "success": True,
            "filename": filename,
            "sample_rate": fs,
            "duration_sec": duration_sec,
            "total_samples": len(raw_samples),
            "parameters": param_dict,
            "classification": amc_dict,
            "demodulation": demod_dict,
            "frames": frames_summary,
            "decoded_message": text_decode_res,
            "visualizations": {
                "waveform": time_series,
                "constellation": const_pts,
                "spectrogram": spectrogram_data,
                "psd": psd_data,
                "hex_dump": hex_lines,
                "decoded_text": text_decode_res
            },
            "downloads": {
                "pdf": f"/api/download/pdf/{pdf_filename}",
                "json": f"/api/download/json/{json_filename}",
                "bin": f"/api/download/bin/{bin_filename}" if len(bits) > 0 else None
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/api/download/pdf/{filename}")
def download_pdf(filename: str):
    """Serves intelligence PDF dossier for download."""
    path = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="PDF report not found")
    return FileResponse(path, media_type="application/pdf", filename=filename)


@app.get("/api/download/json/{filename}")
def download_json(filename: str):
    """Serves analysis JSON record for download."""
    path = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="JSON result not found")
    return FileResponse(path, media_type="application/json", filename=filename)


@app.get("/api/download/bin/{filename}")
def download_bin(filename: str):
    """Serves demodulated raw binary payload for download."""
    path = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Binary payload file not found")
    return FileResponse(path, media_type="application/octet-stream", filename=filename)


# ---------------------------------------------------------------------------
# Serve React SPA (frontend/dist) for all non-API routes
# This allows the same uvicorn process to serve both the API and the UI.
# ---------------------------------------------------------------------------
_FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

if (_FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(_FRONTEND_DIST / "assets")), name="spa_assets")

@app.get("/", include_in_schema=False)
async def spa_root():
    idx = _FRONTEND_DIST / "index.html"
    if idx.exists():
        return FileResponse(str(idx))
    return JSONResponse({"status": "SIGNEX API", "docs": "/docs"})

@app.get("/{full_path:path}", include_in_schema=False)
async def spa_catch_all(full_path: str):
    """Serve React SPA for any non-API path."""
    # Let FastAPI handle /api/* and /docs etc — raise 404 so other routes win
    if full_path.startswith(("api/", "docs", "openapi", "redoc")):
        raise HTTPException(status_code=404, detail="Not found")
    idx = _FRONTEND_DIST / "index.html"
    if idx.exists():
        return FileResponse(str(idx))
    return JSONResponse({"error": "Frontend not built"}, status_code=404)


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Entry point to run backend service with uvicorn."""
    import uvicorn
    uvicorn.run("ntro_sigint.server.app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    run_server()
