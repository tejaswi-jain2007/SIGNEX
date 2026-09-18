# NTRO SIGINT System — Operator & Developer Usage Guide

> **Project:** Automated Model for Analysis of .IQ and .WAV Files with Signal Parameter Extraction  
> **Target Environment:** Completely Air-Gapped High-Assurance Workstation  
> **Document:** Standard Operating Procedures (SOP) & Usage Manual  
> **Document Version:** 1.0.0

---

## 1. System Requirements & Environment Setup

### 1.1 Prerequisites
- **Operating System:** Windows 10/11 64-bit or Linux (Ubuntu 20.04/22.04 LTS)
- **Python Version:** Python 3.10 or higher
- **Hardware Recommendations:**
  - Minimum 8 GB RAM (16 GB recommended for files $> 2\text{ GB}$)
  - Multi-core x86_64 CPU
  - Optional NVIDIA GPU with CUDA support (PyTorch will automatically detect and accelerate AMC inference if present; CPU fallback is fully operational)

### 1.2 Virtual Environment & Installation
Open PowerShell or your command prompt in the project root:

```powershell
# Navigate to project root
cd c:\Users\auau\OneDrive\Desktop\SIH

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1
# (Or in Command Prompt: .\venv\Scripts\activate.bat)

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies from requirements.txt
pip install -r requirements.txt
```

### 1.3 Verifying Installation
Verify that all core libraries are accessible:

```powershell
python -c "import torch, numpy, scipy, PyQt6, matplotlib, h5py, openpyxl; print('All core libraries imported successfully!')"
```

---

## 2. Model Weights & Training Workflows

The system includes pre-trained 1D ResNet-18 weights stored at [`models/amc_resnet18.pt`](file:///c:/Users/auau/OneDrive/Desktop/SIH/models/amc_resnet18.pt) (approx. 15.5 MB), capable of classifying 9 modulation schemes: `BPSK`, `QPSK`, `8-PSK`, `16-QAM`, `64-QAM`, `2-FSK`, `4-FSK`, `AM-DSB`, and `WBFM`.

### 2.1 Re-training or Fine-Tuning the AMC Classifier
If you wish to retrain the model from scratch on newly generated synthetic signals with channel impairments:

```powershell
python scripts/train_amc.py
```

- **Script Behavior:**
  - Invokes `SyntheticSignalGenerator` to generate batches with random SNR ($-10\text{ dB}$ to $+30\text{ dB}$), CFO, and phase noise.
  - Trains for 20 epochs using the `AdamW` optimizer and cross-entropy loss.
  - Automatically evaluates validation accuracy on an 80/20 train/test split.
  - Saves the best checkpoint to [`models/amc_resnet18.pt`](file:///c:/Users/auau/OneDrive/Desktop/SIH/models/amc_resnet18.pt).

---

## 3. Launching & Using the System (Desktop GUI & Web UI)

The system provides two 1:1 identical operator interfaces:
1. **Tactical Desktop GUI (PyQt6)**: Standalone native workstation.
2. **Tactical Web UI (React + FastAPI)**: Modern web interface with identical headings, cards, tabs, and DSP engine.

### 3.1 Starting the Web Application (React + FastAPI)
Run the master web launcher:

```powershell
python main.py web
# or
python run_web.py
```
- **React Frontend**: `http://localhost:5173`
- **FastAPI Backend**: `http://127.0.0.1:8000`

### 3.2 Starting the Native Desktop GUI (PyQt6)
Execute the GUI module directly:

```powershell
python ntro_sigint/gui/main_window.py
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  NTRO SIGINT WORKSTATION - [AIR-GAP ACTIVE]                       [-] [X]   │
├───────────────┬─────────────────────────────────────────────┬───────────────┤
│ FILE INGEST   │  VISUALIZATION TABS                         │ TELEMETRY     │
│ [Browse...]   │  ┌───────────────────────────────────────┐  │ Modulation:   │
│ test_file.iq  │  │ Time-Domain / Spectrogram             │  │ QPSK (94.2%)  │
│               │  │                                       │  │               │
│ Rate: 2.0 MSps│  ├───────────────────────────────────────┤  │ Parameters:   │
│ Type: float32 │  │ Constellation / Welch PSD             │  │ fc: 100.0 kHz │
│               │  │                                       │  │ BW:  80.0 kHz │
│ [x] Ingestion │  ├───────────────────────────────────────┤  │ Baud: 50 kBaud│
│ [x] Condition │  │ Frame Hex / Protocol Dissection       │  │ SNR: 18.5 dB  │
│ [x] AMC Class │  │                                       │  │ PAPR: 4.2 dB  │
│ [x] Demod     │  └───────────────────────────────────────┘  │ CFO: +120 Hz  │
│ [x] Decode    │                                             │               │
│ [Run Analysis]│  Status: Analysis Complete (0.84s)          │ [Export PDF]  │
└───────────────┴─────────────────────────────────────────────┴───────────────┘
```

### 3.2 Step-by-Step Operator Workflow

1. **Select an Input Capture:**
   - Click the **Browse** button (or press `Ctrl+O`) to pick an RF capture file (`.iq`, `.wav`, `.raw`, `.dat`).
   - You can also **drag and drop** a file directly onto the left control panel.
2. **Configure Signal Parameters & Overrides:**
   - **Sample Rate ($F_s$):** Choose from standard receiver clock rates (e.g., $1.0\text{ MSps}$, $2.0\text{ MSps}$, $10.0\text{ MSps}$) or type a custom frequency.
   - **Data Format:** If the file is raw I/Q without a `.json` sidecar, select the data encoding: `float32`, `int16`, or `int8`.
3. **Select Processing Pipeline Stages:**
   - Use the checkboxes to toggle individual processing stages:
     - `Signal Conditioning` (DC offset correction, Gram-Schmidt balance)
     - `Automatic Modulation Classification` (ResNet-18 + cumulant ensemble)
     - `Demodulation` (Costas carrier recovery + symbol slicing)
     - `FEC & De-interleaving` (Viterbi $K=7$ and Reed-Solomon decoding)
     - `Frame Sync & Header Dissection` (Barker / CCSDS sync and CRC check)
4. **Execute Analysis:**
   - Click **Run Analysis** (or press `Ctrl+R`).
   - An asynchronous background worker thread (`QThread`) executes the pipeline without freezing the interface. A progress bar tracks execution.
5. **Inspect the Results:**
   - **Telemetry Panel (Right):** Read extracted parameters: Center Frequency ($f_c$), $3\text{ dB}$ Bandwidth, $20\text{ dB}$ Bandwidth, Baud Rate, estimated SNR, PAPR, CFO, and Spectral Flatness.
   - **Modulation Card:** View the classified modulation scheme and confidence score bar.
   - **Visualizer Tabs (Center):**
     - Click **Time-Domain / Spectrogram** to view waveform amplitude and STFT waterfall.
     - Click **Constellation / Welch PSD** to view I/Q symbol clusters and spectral density.
     - Click **Frame Hex** to review decoded bitstreams, extracted header fields (Length, Sequence, Type, Flags), and CRC verification status.
6. **Export Classified Dossier:**
   - Click **Export PDF Report** (or press `Ctrl+E`).
   - Enter an output destination; the system compiles and saves a classified two-page intelligence dossier.

### 3.3 Keyboard Shortcuts
| Shortcut | Action |
| :--- | :--- |
| `Ctrl+O` | Open File Dialog |
| `Ctrl+R` | Execute Analysis Pipeline |
| `Ctrl+E` | Export PDF Intelligence Dossier |
| `Ctrl+Q` | Exit Application |

---

## 4. Programmatic Python API Usage

You can embed the system into automated ingestion scripts or batch pipelines via Python.

### 4.1 Running the Full Pipeline

```python
from pathlib import Path
from ntro_sigint.core.pipeline import SignalAnalysisPipeline

# 1. Initialize the master pipeline
pipeline = SignalAnalysisPipeline(
    model_path="models/amc_resnet18.pt",
    enable_security=True  # Enforces AirGapGuard and PathSanitizer
)

# 2. Process an intercept file
result = pipeline.process_file(
    file_path="tests/fixtures/sample_qpsk.iq",  # or any .iq / .wav file
    sample_rate=2000000.0,                      # 2.0 MSps (if not in sidecar)
    data_format="float32",                      # float32, int16, int8
    options={
        "enable_conditioning": True,
        "enable_amc": True,
        "enable_demod": True,
        "enable_fec": True,
        "enable_sync": True,
        "export_pdf": True,
        "output_dir": "reports"
    }
)

# 3. Access extracted metrics
print(f"Success: {result.success}")
print(f"Modulation: {result.parameters.modulation_type} ({result.parameters.modulation_confidence * 100:.1f}%)")
print(f"Center Frequency: {result.parameters.center_freq:.2f} Hz")
print(f"Estimated SNR: {result.parameters.snr_db:.2f} dB")
print(f"Baud Rate: {result.parameters.symbol_rate:.2f} Baud")
print(f"PDF Dossier Generated: {result.pdf_report_path}")
```

### 4.2 Step-by-Step Low-Level Component Usage

#### Ingesting Raw I/Q Files
```python
from ntro_sigint.core.ingestion import SignalReader

reader = SignalReader()
# Load entire file into complex64 array
signal_data = reader.read_file("data/capture.iq", sample_rate=2e6, data_format="int16")
print(f"Loaded {len(signal_data.samples)} samples from {signal_data.filename}")

# Or stream in chunks for multi-gigabyte captures
for chunk in reader.stream_chunks("data/huge_capture.iq", chunk_size=65536, data_format="float32"):
    # chunk is a np.ndarray of np.complex64
    pass
```

#### Signal Conditioning & Preprocessing
```python
from ntro_sigint.core.preprocessor import SignalPreprocessor

preprocessor = SignalPreprocessor()
# Remove DC offset, balance IQ, and estimate SNR
clean_samples = preprocessor.remove_dc_offset(signal_data.samples)
balanced_samples = preprocessor.correct_iq_imbalance(clean_samples)
snr_est = preprocessor.estimate_snr_cumulants(balanced_samples)
print(f"Estimated SNR: {snr_est:.2f} dB")
```

#### Extracting RF Parameters
```python
from ntro_sigint.dsp.parameter_extractor import ParameterExtractor

extractor = ParameterExtractor()
params = extractor.extract_all(balanced_samples, sample_rate=2e6)
print(f"3dB Bandwidth: {params.bandwidth_3db:.1f} Hz")
print(f"Carrier Offset: {params.carrier_offset:.1f} Hz")
print(f"PAPR: {params.papr_db:.2f} dB")
```

#### Automatic Modulation Classification
```python
from ntro_sigint.ml.amc_classifier import ModulationClassifier

classifier = ModulationClassifier(model_path="models/amc_resnet18.pt")
prediction, confidence = classifier.classify(balanced_samples)
print(f"Classified: {prediction} with confidence {confidence:.4f}")
```

#### Demodulation & Slicing
```python
from ntro_sigint.dsp.demodulator import Demodulator

demodulator = Demodulator()
# Recover carrier phase and slice bits
demod_res = demodulator.demodulate(balanced_samples, mod_type="QPSK")
demod_bits = demod_res.bits
print(f"Demodulated {len(demod_bits)} raw bits. EVM: {demod_res.evm_percent:.2f}%")
```

#### Forward Error Correction (Viterbi & Reed-Solomon)
```python
from ntro_sigint.decoding.fec import ConvolutionalCodec, ReedSolomonGF8

# Viterbi K=7 R=1/2 Decoding
viterbi = ConvolutionalCodec()
decoded_bits = viterbi.decode(demod_bits)

# Reed-Solomon GF(2^8) Decoding
rs = ReedSolomonGF8(n=255, k=223)
corrected_bytes = rs.decode(raw_received_bytes)
```

#### Frame Synchronization & Dissection
```python
from ntro_sigint.correlation.correlator import BitstreamCorrelator

correlator = BitstreamCorrelator()
frames = correlator.correlate_and_extract(decoded_bits, sync_pattern="CCSDS_ASM_32")
for frame in frames:
    print(f"Frame Seq: {frame.sequence_number}, Length: {frame.payload_length} bytes, CRC Valid: {frame.crc_valid}")
```

---

## 5. Verification & Testing

The repository features an automated test suite comprising 147 test cases.

### 5.1 Running the Full Test Suite
```powershell
pytest tests/ -v
```

### 5.2 Running a Specific Subsystem Test
```powershell
# Test AMC classifier and cumulants
pytest tests/test_amc.py -v

# Test FEC decoders (Viterbi & Reed-Solomon)
pytest tests/test_fec.py -v

# Test air-gap security enforcement
pytest tests/test_security.py -v

# Test end-to-end processing pipeline
pytest tests/test_pipeline.py -v
```

### 5.3 Updating Test Trackers
To refresh the Excel test case tracker with real execution results:

```powershell
python scripts/update_tracker_results.py
```
This updates [`NTRO_ID26147_Test_Case_Tracker.xlsx`](file:///c:/Users/auau/OneDrive/Desktop/SIH/NTRO_ID26147_Test_Case_Tracker.xlsx) with live pass/fail marks and execution timestamps.

---

## 6. Operational Troubleshooting & FAQs

### Q1: Why do I get a `SecurityViolationError: Network socket creation blocked by AirGapGuard`?
- **Cause:** The system is operating in high-assurance air-gapped mode. An imported package or script attempted to open an outgoing or incoming TCP/UDP network socket.
- **Resolution:** This is intended security behavior. In air-gapped defense environments, live network connections are prohibited. If running development scripts where local telemetry is needed, initialize the pipeline with `enable_security=False`.

### Q2: My raw `.iq` file produces pure noise or 0% AMC confidence.
- **Check 1 (Sample Rate):** Make sure the configured sample rate matches the SDR hardware clock.
- **Check 2 (Data Format):** If the file contains 16-bit signed integers, ensure `data_format="int16"` is selected rather than `float32`.
- **Check 3 (Sidecar File):** Place a `<filename>.json` file alongside the capture containing:
  ```json
  {
    "sample_rate": 2000000.0,
    "center_freq": 433920000.0,
    "data_format": "int16"
  }
  ```

### Q3: Why does batch processing from the GUI not execute items in the queue?
- **Status:** Batch processing inside the PyQt6 GUI queue is currently `PLANNED / NOT IMPLEMENTED`.
- **Workaround:** Use the programmatic batch processor in Python:
  ```python
  from ntro_sigint.core.pipeline import SignalAnalysisPipeline
  pipeline = SignalAnalysisPipeline()
  results = pipeline.process_batch(["file1.iq", "file2.iq", "file3.wav"], sample_rate=2e6)
  ```

### Q4: Does the system support 4-FSK demodulation?
- **Status:** 4-FSK is classified by the AMC engine and supported by the synthetic dataset generator, but the 4-level frequency discriminator slicer in `ntro_sigint/dsp/demodulator.py` is `PLANNED / NOT IMPLEMENTED`. Binary 2-FSK demodulation is fully operational.
