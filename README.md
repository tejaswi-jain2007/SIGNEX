# 📡 SIGHTEX — Signal Extraction & Analysis Engine
> **National Technical Research Organisation (NTRO) Problem Statement ID 26147**  
> *Air-Gapped, High-Throughput Automatic Modulation Classification (AMC) & SIGINT Demodulation Platform*

---

## 🌟 Overview

**SIGHTEX** is an intelligence-grade, air-gapped Signals Intelligence (SIGINT) processing workstation designed for rapid RF signal ingestion, digital signal processing (DSP), deep learning Automatic Modulation Classification (AMC), bitstream decoding, and automated intelligence report generation.

Built with a high-performance **FastAPI (Python 3.10+)** backend and a modern **React + Vite** frontend UI featuring real-time DSP visualizers, tactical telemetry dials, and offline air-gap perimeter enforcement.

---

## ✨ Key Features

- **🧠 Deep Learning AMC Engine**: PyTorch-powered ResNet-18 classifier supporting 10+ standard and tactical modulation schemes (`BPSK`, `QPSK`, `8PSK`, `16QAM`, `64QAM`, `2FSK`, `4FSK`, `16APSK`, `32APSK`, `OFDM`, `UNKNOWN`).
- **📊 Real-Time DSP Visualizers**:
  - High-resolution Time-Domain Waveform (Spline interpolation with peak detectors).
  - Multi-frequency Spectrum Density & FFT Spectrogram (Hann, Hamming, Blackman windows).
  - I/Q Constellation Scatter & Power Distribution plots.
  - Raw Hex & Synchronized ASCII bitstream viewer.
- **🛡️ 100% Air-Gapped Standalone**: Zero outbound telemetry, strict local execution, and tamper-resistant audit logs.
- **📑 Automated Intelligence Dossiers**: One-click generation of exportable forensic PDF dossiers and machine-readable JSON data packages.
- **⚡ Batch Processing Pipeline**: Asynchronous batch queue execution for high-volume RF recordings.
- **🌓 Tactical Dual Theming**: Instant Light / Dark mode switching with `Ctrl + T` or UI toggle.

---

## 🚀 How to Run SIGHTEX

### 📋 Prerequisites
- **Python 3.10+**
- **Node.js 18+ & npm**
- **Git**

---

### Option 1: Quickstart (Single Command)

The automated runner starts both the **FastAPI backend** (`http://127.0.0.1:8000`) and the **React web workstation** (`http://localhost:5173`) in one go:

```bash
# 1. Clone repository
git clone https://github.com/tejaswi-jain2007/sightex.git
cd sightex

# 2. Setup Python environment & install dependencies
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt

# 3. Setup Frontend dependencies
cd frontend
npm install
cd ..

# 4. Launch SIGHTEX Web Workstation
python run_web.py
```

*Open your browser and navigate to **`http://localhost:5173`**.*

---

### Option 2: Manual Step-by-Step Launch

#### Step 1: Start Backend (FastAPI)
```bash
# In project root:
.\venv\Scripts\activate
python -m uvicorn ntro_sigint.server.app:app --host 127.0.0.1 --port 8000 --reload
```
*API Swagger Docs available at: `http://127.0.0.1:8000/docs`*

#### Step 2: Start Frontend (React + Vite)
```bash
# In a new terminal:
cd frontend
npm run dev
```

---

### Option 3: Desktop Tkinter GUI Mode

For lightweight standalone terminal and desktop operation without a web browser:
```bash
python main.py gui
```

---

### Option 4: Headless CLI & Batch Execution

Analyze a single capture or folder of raw RF recordings directly from terminal:
```bash
# Single file analysis:
python main.py cli --file data/test_samples/sample_01_bpsk.iq --output reports/analysis.json

# Batch mode:
python main.py batch --input-dir data/test_samples --output-dir reports/
```

---

## ⌨️ Keyboard Shortcuts (Web Workstation)

| Shortcut | Action |
|---|---|
| `Ctrl + R` | **Run / Re-run Signal Analysis** |
| `Ctrl + E` | **Open Export Report Modal (PDF / JSON)** |
| `Ctrl + T` | **Toggle Light / Dark Mode** |
| `Ctrl + Z` | **Undo Last File Selection** |

---

## 📂 Project Architecture

```
sightex/
├── data/
│   ├── dataset/             # Synthesized dataset splits
│   └── test_samples/        # Raw I/Q test recordings (.iq, .npy, .wav)
├── frontend/                # React + Vite Tactical Workstation
│   ├── src/
│   │   ├── assets/          # Official branding & logos
│   │   ├── components/      # UI panels (Sidebar, Control, Visualization, Telemetry)
│   │   ├── App.jsx          # Root State, Event Bus & Theming
│   │   └── index.css        # Tactical design system & utilities
│   └── package.json
├── models/                  # Trained PyTorch AMC ResNet weights
├── ntro_sigint/             # Core SIGINT & DSP Python Engine
│   ├── ingestion/           # File parser (.iq, .wav, .npy, .bin)
│   ├── dsp/                 # Filtering, SNR, Symbol Rate, CFO estimation
│   ├── amc/                 # Deep learning modulation classification
│   ├── demod/               # Constellation & bitstream extraction
│   ├── export/              # PDF dossier & JSON report generator
│   └── server/              # FastAPI REST server endpoints
├── tests/                   # Pytest automated test suite
├── main.py                  # Master entry point (web, gui, cli, batch)
├── run_web.py               # Concurrent server + client launcher
└── requirements.txt         # Backend Python dependencies
```

---

## 🧪 Running Automated Tests

Run the comprehensive pytest suite verifying DSP math, model inference, and API endpoints:

```bash
pytest tests/ -v
```

---

## 🔒 Security & Air-Gap Compliance

- **Zero Outbound Sockets**: All model inference, spectrum calculations, and report rendering happen 100% locally.
- **Audit Trails**: Ingestion and classification actions log immutable timestamped records for forensic accountability.

---

## 📜 License
Developed for NTRO SIGINT Challenge (ID 26147). All rights reserved.
