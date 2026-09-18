# NTRO SIGINT System (SIH 2026 Problem Statement ID 26147) — Comprehensive Technical Reference

> **Project Title:** Automated model for analysis of .IQ and .WAV files along with signal parameter extraction  
> **Target Environment:** Completely Air-Gapped High-Assurance Intelligence / Defense SIGINT Workstation  
> **Classification:** STRICTLY AIR-GAPPED // MISSION-CRITICAL REFERENCE  
> **Version:** 1.0.0

---

## 1. Executive Summary & Operational Scope

The **NTRO SIGINT Signal Analysis Platform** is an air-gapped, end-to-end signal intelligence (SIGINT) and electronic support measures (ESM) processing system designed to ingest, condition, classify, demodulate, decode, and analyze radio frequency (RF) intercepts packaged in raw in-phase/quadrature (`.iq`, `.raw`, `.dat`) and audio container (`.wav`) formats.

### Core Capabilities Implemented
1. **Air-Gapped Operation & Integrity Guard:** Monitored execution preventing any live socket operations via runtime monkey-patching of the standard `socket` library (`AirGapGuard`), enforcing zero network leakage.
2. **Robust Stream Ingestion:** Native parsing of real and complex I/Q streams across multiple bit depths (`float32`, `int16`, `int8`), byte orderings (little-endian, big-endian), memory-mapped chunk streaming for large intercept captures (>2 GB), and JSON sidecar metadata discovery.
3. **Hardware-Impairment Conditioning:** DC offset rejection, Gram-Schmidt orthogonalization for I/Q amplitude/phase imbalance compensation, ADC clipping and dynamic range distortion detection, fourth-order moment SNR estimation, polyphase FIR anti-aliasing resampling, and windowed filtering with filter warm-up transients discarded.
4. **Precision DSP Parameter Extraction:** Automated blind estimation of signal center frequency ($f_c$), 3 dB and 20 dB bandwidth ($B_{3\text{dB}}$, $B_{20\text{dB}}$), symbol/baud rate estimation via envelope/magnitude spectral analysis, peak-to-average power ratio (PAPR), carrier frequency offset (CFO via spectral-peak FFT), spectral flatness (Wiener entropy), and envelope statistical moments.
5. **Hybrid Automatic Modulation Classification (AMC):** Dual-tier classification pipeline coupling a 1D Deep Residual Network (1D ResNet-18) operating on raw $2 \times 1024$ I/Q tensors with analytical high-order cumulant features ($C_{20}, C_{40}, C_{42}$) and physical decision guards (CFO de-rotation, kurtosis thresholds, low-confidence OOD rejection).
6. **Constellation Slicing & Demodulation:** Costas carrier phase/frequency tracking loops coupled with hard-decision Gray-coded Euclidean slicers supporting BPSK, QPSK, 8-PSK, 16-QAM, 64-QAM, and 2-FSK discriminator demodulation.
7. **Forward Error Correction (FEC) & De-interleaving:** NASA standard $K=7, R=1/2$ Convolutional Soft/Hard Viterbi decoding with precomputed trellis transitions, full Galois Field $\text{GF}(2^8)$ Reed-Solomon decoding with Berlekamp-Massey error locator polynomial solving and Chien search root finding, concatenated RS+Viterbi decoding, and Block, Forney Convolutional, Pseudo-Random (LFSR), and Diagonal de-interleavers.
8. **Frame Synchronization & Protocol Dissection:** Multi-preamble bipolar cross-correlation supporting Barker codes (7, 11, 13-bit) and CCSDS ASM-32 with Hamming threshold tolerance and $180^\circ$ phase inversion recovery, 48-bit frame header extraction, and CRC-16-CCITT / CRC-32 data validation.
9. **Secure Cryptographic Archiving & Visual Reporting:** PBKDF2-HMAC-SHA256 key derivation with Counter (CTR) mode stream encryption, HMAC-SHA256 integrity tags, SHA-256 chain-of-custody tracking, tamper-resistant JSON exports, and automated multi-page classified dossier generation using Matplotlib `PdfPages`.
10. **Tactical Desktop GUI:** A modular PyQt6 workstation interface featuring dual dark/light themes, drag-and-drop file ingestion, dynamic viewport time-domain and spectrogram zooming, interactive constellation phase trajectory plots, raw frame hex viewers, parameter telemetry tables, and background worker threads (`QThread`) maintaining real-time responsiveness.

---

## 2. Directory Structure & Codebase Inventory

The repository is organized into modular packages located in [`ntro_sigint`](file:///c:/Users/auau/OneDrive/Desktop/SIH/ntro_sigint) alongside orchestration scripts and comprehensive test suites:

```text
c:\Users\auau\OneDrive\Desktop\SIH
├── ntro_sigint/
│   ├── __init__.py                     # Package metadata (v1.0.0)
│   ├── core/                           # Core architectural & security modules
│   │   ├── pipeline.py                 # Master SignalAnalysisPipeline orchestrator
│   │   ├── ingestion.py                # File parsing, format decoding, chunked streaming
│   │   ├── preprocessor.py             # Signal conditioning, IQ balance, SNR estimation
│   │   ├── security.py                 # Air-gap guard, path sanitizer, audit log, memory guard
│   │   └── exporter.py                 # CTR CryptoStore, ResultStore JSON/ZIP, PDF report
│   ├── dsp/                            # Digital Signal Processing engine
│   │   ├── parameter_extractor.py      # RF measurements (BW, baud, CFO, PAPR, flatness)
│   │   ├── demodulator.py              # Costas loop, symbol timing, constellation slicing
│   │   └── visualization.py            # Spectrogram, Welch PSD, constellation, eye diagrams
│   ├── ml/                             # Machine Learning / AMC subsystems
│   │   ├── amc_classifier.py           # 1D ResNet-18, CumulantFeatureExtractor, AMC ensemble
│   │   └── dataset.py                  # SyntheticSignalGenerator, channel simulation, HDF5 export
│   ├── decoding/                       # Forward Error Correction & Interleavers
│   │   ├── fec.py                      # Viterbi (K=7), Reed-Solomon GF(2^8), Concatenated
│   │   └── interleaver.py              # Block, Convolutional (Forney), Pseudo-Random, Diagonal
│   ├── correlation/                    # Frame synchronization & protocol dissection
│   │   └── correlator.py               # Barker/CCSDS correlation, 48-bit header parser, CRC
│   └── gui/                            # Graphical User Interface
│       ├── main_window.py              # PyQt6 SIGINTMainWindow & AnalysisWorkerThread
│       └── widgets/                    # GUI sub-widgets
├── scripts/
│   ├── train_amc.py                    # Training routine for ResNet-18 AMC weights
│   ├── generate_trackers.py            # Automated generator for Excel project/test trackers
│   └── update_tracker_results.py       # Automated runner & synchronizer for test case results
├── tests/                              # Automated test suite (14 test files, 147 test cases)
│   ├── test_amc.py                     # AMC classifier, cumulants, ResNet-18 tests
│   ├── test_ingestion.py               # Raw IQ, WAV, endianness, streaming tests
│   ├── test_preprocessor.py            # DC offset, IQ balance, clipping, resampling tests
│   ├── test_dsp.py                     # Bandwidth, baud rate, CFO, PAPR tests
│   ├── test_demodulator.py             # BPSK, QPSK, 8-PSK, QAM, Costas loop tests
│   ├── test_fec.py                     # Viterbi K=7, Reed-Solomon GF(256), Concatenated tests
│   ├── test_interleaver.py             # Interleaver roundtrip tests
│   ├── test_correlator.py              # Barker-13, CCSDS-32, header parsing, CRC tests
│   ├── test_security.py                # AirGapGuard, path traversal, memory zeroing tests
│   ├── test_exporter.py                # CryptoStore CTR, PDF generation, JSON integrity tests
│   ├── test_dataset.py                 # Synthetic signal generator & channel noise tests
│   ├── test_pipeline.py                # Full pipeline orchestration tests
│   ├── test_e2e.py                     # End-to-end integration workflows
│   └── test_gui.py                     # Headless PyQt6 GUI tests
├── models/
│   └── amc_resnet18.pt                 # Pre-trained 1D ResNet-18 PyTorch weights (15.5 MB)
├── data/                               # Captures and workspace data
├── reports/                            # Generated PDF/JSON/ZIP audit artifacts
├── fixtures/                           # Test fixtures and static intercept samples
└── requirements.txt                    # System dependencies
```

---

## 3. Technology Stack & Dependencies

All dependencies are defined in [`requirements.txt`](file:///c:/Users/auau/OneDrive/Desktop/SIH/requirements.txt):

| Package | Version / Purpose | Implemented Usage in Codebase |
| :--- | :--- | :--- |
| **Python** | `>= 3.10` | Base runtime environment |
| **NumPy** | Array manipulations & vector math | High-performance vectorized I/Q arrays, FFTs, cumulant math |
| **SciPy** | DSP & signal processing | `scipy.signal` (resample_poly, welch, spectrogram, firwin, lfilter), `scipy.io.wavfile` |
| **PyTorch** | Deep learning framework | 1D CNN (`ResNet18_1D`), tensor conversions, weight serialization |
| **PyQt6** | Desktop GUI platform | `QtWidgets`, `QtCore`, `QtGui`, `QThread` non-blocking UI |
| **Matplotlib** | Visualization & reporting | Matplotlib figures embedded in PyQt6 canvas and PDF dossier export (`PdfPages`) |
| **H5Py** | HDF5 binary storage | Dataset compilation & synthetic signal batch serialization |
| **OpenPyXL** | Spreadsheet manipulation | Generating and updating Project & Test Case Excel trackers |
| **Pytest** | Test execution framework | Test suite orchestration, fixtures, parametrized tests |
| **Pytest-Timeout** | Test execution guard | Preventing hanging runs during mathematical solver execution |
| **PyQtGraph** | Listed in requirements | `PLANNED / NOT IMPLEMENTED` *(Matplotlib is currently used across the entire GUI)* |
| **ReportLab** | Listed in requirements | `PLANNED / NOT IMPLEMENTED` *(Matplotlib PdfPages is used for high-fidelity 2-page PDF dossiers)* |

---

## 4. End-to-End System Architecture & Pipeline Flow

The central pipeline is orchestrated by `SignalAnalysisPipeline` in [`ntro_sigint/core/pipeline.py`](file:///c:/Users/auau/OneDrive/Desktop/SIH/ntro_sigint/core/pipeline.py). The pipeline enforces strict data contracts between discrete processing stages:

```
[Raw Intercept File: .iq, .wav, .raw, .dat]
                     │
                     ▼
       ┌───────────────────────────┐
       │   Stage 1: Ingestion      │  SignalReader (mmap / chunk stream / sidecar)
       └─────────────┬─────────────┘
                     ▼
       ┌───────────────────────────┐
       │ Stage 2: Preprocessing    │  DC removal, Gram-Schmidt IQ balance, SNR cumulant
       └─────────────┬─────────────┘
                     ▼
       ┌───────────────────────────┐
       │ Stage 3: DSP Estimation   │  ParameterExtractor (fc, BW, Baud, PAPR, CFO, Flatness)
       └─────────────┬─────────────┘
                     ▼
       ┌───────────────────────────┐
       │   Stage 4: Hybrid AMC     │  Cumulants -> CFO De-rotation -> ResNet-18 -> Guard
       └─────────────┬─────────────┘
                     ▼
       ┌───────────────────────────┐
       │   Stage 5: Demodulation   │  Costas Loop -> Hard Slicer -> Raw Demodulated Bits
       └─────────────┬─────────────┘
                     ▼
       ┌───────────────────────────┐
       │ Stage 6: De-interleaving  │  Block / Forney / LFSR / Diagonal permutation
       └─────────────┬─────────────┘
                     ▼
       ┌───────────────────────────┐
       │ Stage 7: FEC Decoding     │  Viterbi K=7 / Reed-Solomon GF(256) / Concatenated
       └─────────────┬─────────────┘
                     ▼
       ┌───────────────────────────┐
       │ Stage 8: Correlation/Sync │  Barker / CCSDS-32 Match, Header Dissection, CRC
       └─────────────┬─────────────┘
                     ▼
       ┌───────────────────────────┐
       │ Stage 9: Secure Exporter  │  Encrypted JSON, 2-Page PDF Dossier, Audit Signatures
       └───────────────────────────┘
```

---

## 5. Detailed Module-by-Module Technical Specification

### 5.1 Core Subsystem

#### 5.1.1 Ingestion Engine (`ntro_sigint/core/ingestion.py`)
- **Primary Class:** `SignalReader`
- **Data Container:** `SignalData`
  - Fields: `samples` (`np.ndarray` of `np.complex64`), `sample_rate` (`float`), `center_freq` (`float`), `timestamp` (`datetime`), `filename` (`str`), `metadata` (`dict`), `source_format` (`str`).
- **Format Decoding Capabilities:**
  - **Raw I/Q (`.iq`, `.raw`, `.dat`):**
    - Supported dtypes: `float32`, `int16`, `int8`, `uint8`.
    - Endianness handling: Little-endian (`<`) and Big-endian (`>`).
    - Channel ordering: Interleaved I followed by Q ($I_0, Q_0, I_1, Q_1, \dots$).
    - Conversion formula for integer types:
      $$I_{\text{float}} = \frac{I_{\text{int}}}{\text{scale}}, \quad Q_{\text{float}} = \frac{Q_{\text{int}}}{\text{scale}}, \quad s = I_{\text{float}} + j Q_{\text{float}}$$
      where $\text{scale} = 32768.0$ for `int16` and $128.0$ for `int8`.
  - **WAV Container (`.wav`):**
    - Supports mono (treated as real-valued RF or pre-demodulated audio; converted to analytic signal via Hilbert transform if configured) and stereo (Channel 0 = In-Phase $I$, Channel 1 = Quadrature $Q$).
    - Supports PCM bit depths: 8-bit unsigned, 16-bit signed, 24-bit signed (via 3-byte packing normalization), 32-bit float/int.
  - **Memory-Mapped Streaming:**
    - Method: `stream_chunks(file_path, chunk_size, ...)`
    - Employs `np.memmap` in read-only mode (`r`), yielding successive overlapping or contiguous chunks of `np.complex64` data without exhausting physical workstation RAM on multi-gigabyte intercepts.
  - **Sidecar Metadata:**
    - Automatically checks for `<filename>.json` sidecars containing center frequency, sample rate, hardware receiver gain, and timestamp offsets.

#### 5.1.2 Preprocessor & Signal Conditioner (`ntro_sigint/core/preprocessor.py`)
- **Primary Class:** `SignalPreprocessor`
- **Conditioning Functions:**
  - **DC Offset Removal:** Subtracts complex mean: $s[n] \leftarrow s[n] - \mu_s$.
  - **Gram-Schmidt Orthogonalization (IQ Imbalance Correction):**
    - Estimates amplitude mismatch $\epsilon$ and phase error $\phi$:
      $$I_{\text{norm}} = \frac{I}{\sqrt{2 \langle I^2 \rangle}}, \quad Q' = Q - I_{\text{norm}} \frac{\langle I_{\text{norm}} Q \rangle}{\langle I_{\text{norm}}^2 \rangle}, \quad Q_{\text{norm}} = \frac{Q'}{\sqrt{2 \langle Q'^2 \rangle}}$$
      $$s_{\text{balanced}}[n] = I_{\text{norm}}[n] + j Q_{\text{norm}}[n]$$
  - **Clipping Detection:** Scans for full-scale ADC saturation samples (magnitude exceeding threshold $\ge 0.999$), reporting clipping ratio and dynamic range warnings.
  - **SNR Estimation via 4th-Order Cumulants:**
    - Uses non-data-aided $M_2$ and $M_4$ moment estimation:
      $$\hat{P}_s = \sqrt{2 M_2^2 - M_4}, \quad \hat{P}_n = M_2 - \hat{P}_s, \quad \text{SNR}_{\text{est}} = 10 \log_{10}\left(\frac{\hat{P}_s}{\hat{P}_n}\right)$$
  - **Polyphase Resampling:** Employs `scipy.signal.resample_poly` with Kaiser windowed anti-aliasing low-pass filter to prevent spectral aliasing across variable ADC clocks.
  - **Filter Warm-up Transient Removal:** Truncates filter group delay samples ($N_{\text{taps}} / 2$) from the beginning of processed streams.

#### 5.1.3 Security & High-Assurance Architecture (`ntro_sigint/core/security.py`)
- **Classes:** `AirGapGuard`, `PathSanitizer`, `SecureTempDirectory`, `ConfigValidator`, `AuditLogger`, `MemoryGuard`
- **Air-Gap Verification:**
  - `AirGapGuard.enforce()` replaces `socket.socket`, `socket.create_connection`, and `socket.getaddrinfo` with raising stubs (`SecurityViolationError`), ensuring zero network socket instantiation by libraries, telemetry tools, or external packages.
- **Path Sanitization:**
  - `PathSanitizer.sanitize_path()` prevents path traversal attacks (`../`, hidden system files, null bytes) and forces file operations to remain strictly within defined workspace boundaries.
- **Memory Zeroization:**
  - `MemoryGuard.zero_array()` overwrites sensitive memory buffers (decrypted payloads, raw intercepts, keys) with zeros before deallocation using direct byte operations.
- **Audit Logging:**
  - `AuditLogger` generates cryptographically hashed append-only audit trails with timestamps, user session markers, and automatic redaction of binary buffers.

#### 5.1.4 Secure Exporter & Reporting Engine (`ntro_sigint/core/exporter.py`)
- **Classes:** `CryptoStore`, `ResultStore`, `PDFReportGenerator`
- **Cryptographic Engine (`CryptoStore`):**
  - Key Derivation: PBKDF2-HMAC-SHA256 with 100,000 iterations and a random 16-byte salt.
  - Stream Cipher: Custom Counter (CTR) mode encryption using SHA-256 state hashing.
  - Message Authentication: HMAC-SHA256 tag calculated over ciphertext, salt, and nonce for tamper detection.
- **Result Packaging (`ResultStore`):**
  - Formats results into structured JSON with SHA-256 chain-of-custody checksums.
  - Generates self-contained `.zip` audit archives including parameters, raw bitstreams, decrypted frames, and execution logs.
- **Visual Intelligence Dossier (`PDFReportGenerator`):**
  - Uses `matplotlib.backends.backend_pdf.PdfPages` to compile a two-page classified intelligence report:
    - **Page 1:** Header with security classification banner, capture metadata, signal telemetry summary table, estimated SNR, AMC confidence card, and time-domain / Welch PSD spectral density plots.
    - **Page 2:** High-resolution constellation trajectory plot, demodulated symbol distribution, frame synchronization table (Barker/CCSDS), decoded protocol header disassembly, and raw payload hex dump.

---

### 5.2 Digital Signal Processing (DSP) Subsystem

#### 5.2.1 Parameter Extractor (`ntro_sigint/dsp/parameter_extractor.py`)
- **Primary Class:** `ParameterExtractor`
- **Data Container:** `SignalParameters`
  - Fields: `center_freq` ($Hz$), `bandwidth_3db` ($Hz$), `bandwidth_20db` ($Hz$), `symbol_rate` ($Baud$), `snr_db` ($dB$), `papr_db` ($dB$), `carrier_offset` ($Hz$), `spectral_flatness` ($0.0 - 1.0$), `modulation_type` ($str$), `modulation_confidence` ($float$), `num_samples` ($int$), `duration_sec` ($float$).
- **Extraction Algorithms:**
  - **Occupied Bandwidth ($3\text{ dB} / 20\text{ dB}$):** Computes Welch PSD; determines the maximum peak power $P_{\max}$; locates left and right frequency bounds where PSD drops below $P_{\max} - 3\text{ dB}$ and $P_{\max} - 20\text{ dB}$ using vectorized spline/linear interpolation.
  - **Carrier Frequency Offset (CFO):** Computes non-linear squaring ($M=2$) or fourth-power ($M=4$) operations on the I/Q samples to collapse PSK constellations into a discrete tone at $M \cdot \Delta f$, followed by fine-bin FFT peak detection:
    $$\Delta \hat{f} = \frac{1}{M} \arg\max_f \left| \mathcal{F}\left\{ s^M[n] \right\} \right|$$
  - **Symbol Rate (Baud Rate) Estimation:** Evaluates magnitude envelope $e[n] = |s[n]|$ or non-linear differentiation; performs high-resolution Welch PSD of the envelope; strips DC and harmonics; identifies the dominant cyclic spectral peak corresponding to the baud frequency $R_s = 1/T_s$.
  - **Peak-to-Average Power Ratio (PAPR):**
    $$\text{PAPR}_{\text{dB}} = 10 \log_{10}\left( \frac{\max_n |s[n]|^2}{\frac{1}{N} \sum_{n=0}^{N-1} |s[n]|^2} \right)$$
  - **Spectral Flatness (Wiener Entropy):** Ratio of geometric mean to arithmetic mean of the PSD:
    $$\gamma = \frac{\exp\left(\frac{1}{K} \sum_{k=0}^{K-1} \ln S[k]\right)}{\frac{1}{K} \sum_{k=0}^{K-1} S[k]}$$

#### 5.2.2 Demodulation Engine (`ntro_sigint/dsp/demodulator.py`)
- **Primary Class:** `Demodulator`
- **Data Container:** `DemodResult`
  - Fields: `symbols` (`np.ndarray`), `bits` (`np.ndarray` of `uint8`), `evm_percent` ($float$), `constellation_points` (`np.ndarray`), `carrier_phase_error` ($float$).
- **Demodulation Schemes:**
  - **Costas Loop Carrier Recovery:** Second-order phase-locked loop tracking residual phase error $\phi[n]$ and frequency offset $\omega[n]$ with configurable loop bandwidth $\alpha, \beta$:
    $$e[n] = \text{sign}(I[n]) \cdot Q[n] - \text{sign}(Q[n]) \cdot I[n]$$
    $$\omega[n+1] = \omega[n] + \beta \cdot e[n], \quad \phi[n+1] = \phi[n] + \omega[n] + \alpha \cdot e[n]$$
    $$s_{\text{corrected}}[n] = s[n] e^{-j \phi[n]}$$
  - **BPSK:** Slices real axis $I \gtrless 0 \to \{0, 1\}$.
  - **QPSK:** Slices quadrants $(\text{sign}(I), \text{sign}(Q))$ with Gray mapping:
    $$00 \to (+1, +1), \quad 01 \to (-1, +1), \quad 11 \to (-1, -1), \quad 10 \to (+1, -1)$$
  - **8-PSK:** Sector slicer over 8 octants with Gray phase sequence ($0^\circ, 45^\circ, 90^\circ, \dots, 315^\circ$).
  - **16-QAM:** Dual 4-PAM slicers along $I$ and $Q$ axes with decision thresholds at $-2/\sqrt{10}, 0, +2/\sqrt{10}$, mapping each axis to 2 Gray-coded bits (total 4 bits/symbol).
  - **64-QAM:** Dual 8-PAM slicers along $I$ and $Q$ axes with 7 decision boundaries per axis, mapping to 6 Gray-coded bits/symbol.
  - **2-FSK:** Quadrature frequency discriminator demodulation:
    $$\Delta \theta[n] = \text{angle}(s[n] \cdot s^*[n-1]) \gtrless 0 \to \{1, 0\}$$
  - **4-FSK:** `PLANNED / NOT IMPLEMENTED` *(4-FSK is included in dataset generator and AMC classifier class lists, but multi-level FSK slicer is not implemented in `demodulator.py`)*.

#### 5.2.3 Visualization Suite (`ntro_sigint/dsp/visualization.py`)
- **Primary Class:** `SignalVisualizer`
- **Visual Plots Produced:**
  - **Spectrogram:** Short-Time Fourier Transform (STFT) with configurable window lengths, overlap ratios, and logarithmic dB color scaling.
  - **Welch PSD:** Power spectral density estimation with selectable windowing (Hann, Hamming, Blackman).
  - **Constellation & Phase Trajectory:** 2D I/Q scatter plot overlaid with continuous inter-symbol trajectory vectors and ideal reference constellation points.
  - **Waterfall Plot:** Rolling time-frequency 2D intensity grid for monitoring burst activity.
  - **Viewport Slicing:** Interactive slicing of microsecond/millisecond signal segments for zoom analysis.

---

### 5.3 Machine Learning & Automatic Modulation Classification (AMC)

#### 5.3.1 AMC Classifier Architecture (`ntro_sigint/ml/amc_classifier.py`)
- **Primary Classes:** `ResNet18_1D`, `CumulantFeatureExtractor`, `ModulationClassifier`
- **Supported Modulation Classes (9 Classes):**
  1. `BPSK`
  2. `QPSK`
  3. `8-PSK`
  4. `16-QAM`
  5. `64-QAM`
  6. `2-FSK`
  7. `4-FSK`
  8. `AM-DSB`
  9. `WBFM`

```
Input Tensor: [Batch, 2, 1024] (Channel 0: I, Channel 1: Q)
                     │
                     ▼
             Conv1d(2 -> 64, kernel_size=7, stride=2, padding=3)
                     │
             BatchNorm1d(64) + ReLU + MaxPool1d(kernel_size=3, stride=2)
                     │
             ┌──────────────────────────────┐
             │ Layer 1: 2 x ResBlock1D(64)  │
             └──────────────┬───────────────┘
                            ▼
             ┌──────────────────────────────┐
             │ Layer 2: 2 x ResBlock1D(128) │ (Stride 2 downsample)
             └──────────────┬───────────────┘
                            ▼
             ┌──────────────────────────────┐
             │ Layer 3: 2 x ResBlock1D(256) │ (Stride 2 downsample)
             └──────────────┬───────────────┘
                            ▼
             ┌──────────────────────────────┐
             │ Layer 4: 2 x ResBlock1D(512) │ (Stride 2 downsample)
             └──────────────┬───────────────┘
                            ▼
             AdaptiveAvgPool1d(1) -> Flatten [Batch, 512]
                            ▼
             Linear(512 -> 9) -> Softmax Probabilities
```

- **Cumulant Feature Extraction (`CumulantFeatureExtractor`):**
  - Evaluates normalized zero-lag moments and cumulants:
    $$C_{20} = E[s^2], \quad C_{21} = E[|s|^2]$$
    $$C_{40} = E[s^4] - 3 C_{20}^2$$
    $$C_{41} = E[s^3 s^*] - 3 C_{20} C_{21}$$
    $$C_{42} = E[|s|^4] - |C_{20}|^2 - 2 C_{21}^2$$
  - Also computes envelope kurtosis, instantaneous frequency variance, and phase non-linearity metrics.
- **Ensemble Decision & Physics Guard Logic:**
  1. **Analog / FSK Rule Guard:** If envelope variance is extreme and $C_{42}$ matches constant modulus FM or high-index AM, routes to FSK/AM before CNN to avoid phase confusion.
  2. **CFO Pre-Correction:** Estimates coarse CFO and de-rotates the 1024-sample window before presenting it to the ResNet to avoid constellation rotation artifacts.
  3. **Deep ResNet Inference:** Evaluates class probabilities via the pre-trained weights (`models/amc_resnet18.pt`).
  4. **8-PSK Physics Guard:** Verifies $|C_{40}|$ cumulant magnitude; if the CNN predicts 8-PSK but $|C_{40}|$ is significantly non-zero (indicating QPSK/BPSK symmetry), corrects the prediction.
  5. **Out-of-Distribution (OOD) & Confidence Rejection:** If maximum softmax confidence $< 0.70$ or SNR $< -6\text{ dB}$, tags classification as `UNKNOWN / LOW_CONFIDENCE`.

#### 5.3.2 Synthetic Dataset Generator (`ntro_sigint/ml/dataset.py`)
- **Primary Class:** `SyntheticSignalGenerator`
- **Channel Impairment Emulation:**
  - Additive White Gaussian Noise (AWGN) across configurable SNR ranges ($-10\text{ dB}$ to $+30\text{ dB}$).
  - Carrier Frequency Offset (CFO) and Doppler drift.
  - Phase jitter and phase noise.
  - Root-Raised Cosine (RRC) pulse shaping filter with configurable roll-off factors ($\beta \in [0.20, 0.35]$).
- **Batch Dataset Export:**
  - `create_synthetic_dataset()` generates thousands of labeled 1024-sample I/Q frames and saves them in HDF5 format (`.h5`) for offline model training.

#### 5.3.3 Model Training Script (`scripts/train_amc.py`)
- Synthesizes training batches on-the-fly using `SyntheticSignalGenerator`.
- Trains `ResNet18_1D` using `AdamW` optimizer, cross-entropy loss, learning rate scheduling, and an 80/20 train/validation split.
- Automatically saves optimal validation checkpoint weights to `models/amc_resnet18.pt`.

---

### 5.4 Forward Error Correction (FEC) & De-interleaving Subsystem

#### 5.4.1 FEC Decoders (`ntro_sigint/decoding/fec.py`)
- **Classes:** `ConvolutionalCodec`, `ReedSolomonGF8`, `ConcatenatedCodec`
- **NASA Standard Convolutional Codec ($K=7, R=1/2$):**
  - Generator Polynomials: $G_1 = 171_8 = 1111001_2$, $G_2 = 133_8 = 1011011_2$.
  - Trellis States: $2^{K-1} = 64$ states.
  - **Optimized Viterbi Decoder:** Features precomputed transition tuples `(prev_state, input_bit, out0, out1)` eliminating dynamic bit-shifting in inner loops, with survivor path management and traceback decoding. Supports hard-decision inputs and soft-decision likelihoods.
- **Reed-Solomon Decoder over $\text{GF}(2^8)$ (`ReedSolomonGF8`):**
  - Field: Galois Field $\text{GF}(256)$ with primitive polynomial $p(x) = x^8 + x^4 + x^3 + x^2 + 1$ ($0x11D$).
  - Full algebraic implementation:
    - Log and antilog (exponent) lookup tables for constant-time $\text{GF}$ multiplication and division.
    - Syndrome computation: $S_i = r(\alpha^i)$ for $i = 1, \dots, 2t$.
    - Berlekamp-Massey algorithm to determine the error locator polynomial $\Lambda(x)$.
    - Chien search to find roots of $\Lambda(x)$ (error locations).
    - Forney's algorithm / Gaussian elimination to calculate error magnitudes.
- **Concatenated Codec (`ConcatenatedCodec`):**
  - Chained decoder: Viterbi inner decoder followed by Reed-Solomon outer decoder.
- **LDPC Decoder:** `PLANNED / NOT IMPLEMENTED` *(Referenced in docstring comments, but no LDPC parity check matrix solver is implemented)*.

#### 5.4.2 Interleavers (`ntro_sigint/decoding/interleaver.py`)
- **Classes:** `BlockInterleaver`, `ConvolutionalInterleaver`, `PseudoRandomInterleaver`, `DiagonalInterleaver`
- **Architectures:**
  - **Block Interleaver:** Matrix transposition ($M \times N$ matrix, write rows, read columns; de-interleaver writes columns, reads rows).
  - **Convolutional Interleaver (Forney):** Array of $I$ shift register branches with incremental delays $(0, D, 2D, \dots, (I-1)D)$.
  - **Pseudo-Random Interleaver:** Linear Feedback Shift Register (LFSR) seeded permutation generator.
  - **Diagonal Interleaver:** Cyclic diagonal index offset interleaving.

---

### 5.5 Frame Correlation & Protocol Dissection Subsystem

#### 5.5.1 Correlator Engine (`ntro_sigint/correlation/correlator.py`)
- **Primary Class:** `BitstreamCorrelator`
- **Data Containers:** `FrameSyncMatch`, `ParsedFrame`
- **Synchronization Sequences Supported:**
  - `BARKER_7`: `[1, 1, 1, 0, 0, 1, 0]`
  - `BARKER_11`: `[1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0]`
  - `BARKER_13`: `[1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]`
  - `CCSDS_ASM_32`: `0x1ACFFC1D` (`00011010110011111111110000011101`)
- **Correlation & Phase Ambiguity Resolution:**
  - Converts bitstream to bipolar format ($0 \to -1, 1 \to +1$).
  - Evaluates cross-correlation across incoming stream against preambles.
  - Detects both normal correlation peak and inverted peak ($180^\circ$ Costas loop BPSK/QPSK phase inversion). If inverted, automatically inverts subsequent bitstream polarity.
  - Supports configurable Hamming distance error tolerance (e.g., up to 2-3 bit errors in preamble).
- **Frame Header Dissection (48-bit Tactical Frame Specification):**
  - `Sync Pattern` (32 bits / 16 bits)
  - `Frame Length` (16 bits, big-endian)
  - `Sequence Counter` (16 bits)
  - `Protocol / Payload Type ID` (8 bits)
  - `Flags` (8 bits: encryption flag, fragmentation, priority)
  - `Payload` ($N$ bytes)
  - `Checksum / CRC` (16 or 32 bits)
- **Error Detection Implementations:**
  - `CRC-16-CCITT`: Polynomial $x^{16} + x^{12} + x^5 + 1$ ($0x1021$).
  - `CRC-32-IEEE`: Polynomial $0xEDB88320$.

---

### 5.6 Graphical User Interface (PyQt6 Desktop)

#### 5.6.1 Main Interface Architecture (`ntro_sigint/gui/main_window.py`)
- **Primary Classes:** `SIGINTMainWindow`, `AnalysisWorkerThread`
- **Window Layout:**
  - **Left Control Panel:**
    - File Ingestion Card: file path display, "Browse" button, sample rate selection, data format overrides (`float32`, `int16`, `int8`, `WAV`).
    - Processing Pipeline Configuration: check boxes to toggle Ingestion, Conditioning, AMC, Demodulation, FEC, Frame Sync.
    - Execution Controls: "Run Analysis", "Stop / Abort", "Batch Queue".
  - **Center Multi-Tab Visualization Panel:**
    - `Tab 1: Time Domain & Spectrogram`: Interactive Matplotlib figure canvas rendering time-domain I/Q magnitude and STFT waterfall.
    - `Tab 2: Constellation & PSD`: I/Q scatter plot displaying demodulated symbol constellations alongside Welch power spectral density.
    - `Tab 3: Frame Hex & Dissection`: Hexadecimal byte inspector rendering decoded frames, ASCII representation, and CRC integrity status.
  - **Right Telemetry & Intelligence Panel:**
    - Modulation Classification Card: Dominant prediction, confidence gauge bar (green $\ge 85\%$, amber $70-85\%$, red $< 70\%$), secondary candidate.
    - Signal Telemetry Table: 16 extracted RF metrics ($f_c$, $B_{3\text{dB}}$, $B_{20\text{dB}}$, Baud, SNR, PAPR, CFO, Flatness, etc.).
    - Audit & Chain of Custody Box: Input SHA-256 hash, execution runtime, air-gap status badge (`AIR-GAP ACTIVE`).
- **Non-Blocking Architecture:**
  - Heavy computation executes inside `AnalysisWorkerThread(QThread)`.
  - Emits Qt signals: `sig_progress(int)`, `sig_status(str)`, `sig_result(dict)`, `sig_error(str)`.
  - UI remains responsive at 60 FPS; users can pan/zoom figures without freezing the desktop window.
- **Theme Engine:**
  - Full support for tactical Dark Theme (`#1e1e2e` dark slate background with neon cyan `#00ffff` and lime `#50fa7b` accents) and High-Contrast Light Theme.
- **Keyboard Shortcuts:**
  - `Ctrl+O`: Open File Dialog
  - `Ctrl+R`: Run Analysis
  - `Ctrl+E`: Export PDF Dossier
  - `Ctrl+Q`: Exit Application

---

## 6. Implementation Status Matrix

The following matrix documents the exact status of all specifications against the real codebase:

| Capability / Module | Component | Implementation Status | Notes / Location |
| :--- | :--- | :--- | :--- |
| **Air-Gap Security Guard** | `AirGapGuard` | **IMPLEMENTED** | Monkey-patches `socket` (`security.py`) |
| **Path Traversal Sanitizer** | `PathSanitizer` | **IMPLEMENTED** | Path validation & traversal block (`security.py`) |
| **Memory Overwrite/Zeroing** | `MemoryGuard` | **IMPLEMENTED** | Zeroization of buffers (`security.py`) |
| **Raw IQ Ingestion** | `SignalReader` | **IMPLEMENTED** | float32, int16, int8, uint8 (`ingestion.py`) |
| **WAV Ingestion** | `SignalReader` | **IMPLEMENTED** | 8/16/24/32-bit PCM mono/stereo (`ingestion.py`) |
| **Memory-Mapped Streaming** | `stream_chunks` | **IMPLEMENTED** | `np.memmap` chunked processing (`ingestion.py`) |
| **DC Offset Correction** | `SignalPreprocessor` | **IMPLEMENTED** | Mean subtraction (`preprocessor.py`) |
| **Gram-Schmidt IQ Balance** | `SignalPreprocessor` | **IMPLEMENTED** | Amplitude/phase orthogonalization (`preprocessor.py`) |
| **ADC Clipping Detection** | `SignalPreprocessor` | **IMPLEMENTED** | Saturation ratio detection (`preprocessor.py`) |
| **Cumulant SNR Estimation** | `SignalPreprocessor` | **IMPLEMENTED** | $M_2, M_4$ moment SNR estimation (`preprocessor.py`) |
| **Polyphase Resampling** | `SignalPreprocessor` | **IMPLEMENTED** | `scipy.signal.resample_poly` (`preprocessor.py`) |
| **Bandwidth (3dB / 20dB)** | `ParameterExtractor`| **IMPLEMENTED** | Welch PSD thresholding (`parameter_extractor.py`) |
| **Symbol Rate Estimation** | `ParameterExtractor`| **IMPLEMENTED** | Envelope PSD cyclic peak detection (`parameter_extractor.py`) |
| **CFO Estimation** | `ParameterExtractor`| **IMPLEMENTED** | Squaring / 4th-power FFT peak (`parameter_extractor.py`) |
| **PAPR & Spectral Flatness** | `ParameterExtractor`| **IMPLEMENTED** | Wiener entropy & peak/avg ratio (`parameter_extractor.py`) |
| **1D ResNet-18 AMC** | `ResNet18_1D` | **IMPLEMENTED** | 1D CNN with weights `amc_resnet18.pt` (`amc_classifier.py`) |
| **Cumulant Feature Extractor** | `CumulantFeatures` | **IMPLEMENTED** | $C_{20}, C_{40}, C_{42}$ moment extraction (`amc_classifier.py`) |
| **Physics Decision Guard** | `ModulationClassifier`| **IMPLEMENTED** | CFO de-rotation & cumulant rule guard (`amc_classifier.py`) |
| **Costas Loop Demodulation** | `Demodulator` | **IMPLEMENTED** | 2nd-order Costas loop (`demodulator.py`) |
| **BPSK / QPSK Slicers** | `Demodulator` | **IMPLEMENTED** | Hard Gray slicing (`demodulator.py`) |
| **8-PSK / 16-QAM Slicers** | `Demodulator` | **IMPLEMENTED** | Sector / 4-PAM slicers (`demodulator.py`) |
| **64-QAM Slicer** | `Demodulator` | **IMPLEMENTED** | 8-PAM dual axis slicer (`demodulator.py`) |
| **2-FSK Demodulator** | `Demodulator` | **IMPLEMENTED** | Quadrature discriminator (`demodulator.py`) |
| **4-FSK Demodulator** | `Demodulator` | `PLANNED / NOT IMPLEMENTED` | Exists in AMC classifier, not in demodulator |
| **Viterbi K=7 R=1/2 FEC** | `ConvolutionalCodec` | **IMPLEMENTED** | Fast precomputed transitions (`fec.py`) |
| **Reed-Solomon GF(256) FEC**| `ReedSolomonGF8` | **IMPLEMENTED** | Berlekamp-Massey & Chien (`fec.py`) |
| **Concatenated RS+Viterbi** | `ConcatenatedCodec` | **IMPLEMENTED** | Inner Viterbi + Outer RS (`fec.py`) |
| **LDPC Decoder** | `FecSubsystem` | `PLANNED / NOT IMPLEMENTED` | Mentioned in docstring, no class implemented |
| **De-interleavers** | Interleaver classes | **IMPLEMENTED** | Block, Forney, LFSR, Diagonal (`interleaver.py`) |
| **Barker 7/11/13 Sync** | `BitstreamCorrelator`| **IMPLEMENTED** | Bipolar cross-correlation (`correlator.py`) |
| **CCSDS ASM-32 Sync** | `BitstreamCorrelator`| **IMPLEMENTED** | 32-bit correlation (`correlator.py`) |
| **48-Bit Header Dissection**| `BitstreamCorrelator`| **IMPLEMENTED** | Length, Seq, Type, Flags parser (`correlator.py`) |
| **CRC-16 / CRC-32 Check** | `BitstreamCorrelator`| **IMPLEMENTED** | Standard CRC polynomials (`correlator.py`) |
| **CTR Mode Encrypted Store**| `CryptoStore` | **IMPLEMENTED** | PBKDF2 + CTR + HMAC-SHA256 (`exporter.py`) |
| **2-Page Classified PDF** | `PDFReportGenerator`| **IMPLEMENTED** | Matplotlib `PdfPages` dossier (`exporter.py`) |
| **PyQt6 Desktop GUI** | `SIGINTMainWindow` | **IMPLEMENTED** | 3-panel UI, QThread worker (`main_window.py`) |
| **GUI Batch Queue Processing** | `action_run_batch` | `PLANNED / NOT IMPLEMENTED` | Clears queue; programmatic batch works |
| **PyQtGraph Real-Time Plots** | Requirements | `PLANNED / NOT IMPLEMENTED` | Matplotlib canvases used instead |
| **ReportLab PDF Backend** | Requirements | `PLANNED / NOT IMPLEMENTED` | Matplotlib PdfPages used instead |

---

## 7. Verification & Test Suite Architecture

The system contains an automated test suite executed via `pytest`:

```bash
pytest tests/ -v
```

### Test Suite Structure (14 Test Suites, 147 Test Cases):
1. [`tests/test_security.py`](file:///c:/Users/auau/OneDrive/Desktop/SIH/tests/test_security.py): Validates `AirGapGuard` socket blocking, path traversal attacks, and memory zeroization.
2. [`tests/test_ingestion.py`](file:///c:/Users/auau/OneDrive/Desktop/SIH/tests/test_ingestion.py): Validates little/big endian raw IQ parsing, 8/16/24/32-bit WAV containers, and memory-mapped streaming.
3. [`tests/test_preprocessor.py`](file:///c:/Users/auau/OneDrive/Desktop/SIH/tests/test_preprocessor.py): Tests DC offset subtraction, Gram-Schmidt IQ balancing, clipping flags, and resampling.
4. [`tests/test_dsp.py`](file:///c:/Users/auau/OneDrive/Desktop/SIH/tests/test_dsp.py): Validates $3\text{ dB}/20\text{ dB}$ bandwidth calculations, baud rate envelope detection, CFO accuracy, and spectral flatness.
5. [`tests/test_amc.py`](file:///c:/Users/auau/OneDrive/Desktop/SIH/tests/test_amc.py): Tests `ResNet18_1D` forward passes, cumulant extraction ($C_{20}, C_{40}, C_{42}$), and classification accuracy.
6. [`tests/test_demodulator.py`](file:///c:/Users/auau/OneDrive/Desktop/SIH/tests/test_demodulator.py): Validates Costas loop convergence, BPSK, QPSK, 8-PSK, 16-QAM, 64-QAM, and 2-FSK bit slicing.
7. [`tests/test_fec.py`](file:///c:/Users/auau/OneDrive/Desktop/SIH/tests/test_fec.py): Tests Viterbi $K=7$ error correction under noise, Reed-Solomon $\text{GF}(256)$ multi-symbol correction, and concatenated decoding.
8. [`tests/test_interleaver.py`](file:///c:/Users/auau/OneDrive/Desktop/SIH/tests/test_interleaver.py): Tests matrix roundtrip interleaving across Block, Forney, LFSR, and Diagonal algorithms.
9. [`tests/test_correlator.py`](file:///c:/Users/auau/OneDrive/Desktop/SIH/tests/test_correlator.py): Tests Barker and CCSDS synchronization, $180^\circ$ phase inversion recovery, header parsing, and CRC-16/32 checks.
10. [`tests/test_exporter.py`](file:///c:/Users/auau/OneDrive/Desktop/SIH/tests/test_exporter.py): Tests CTR encryption/decryption roundtrips, HMAC tamper checks, JSON export signatures, and PDF generation.
11. [`tests/test_dataset.py`](file:///c:/Users/auau/OneDrive/Desktop/SIH/tests/test_dataset.py): Validates synthetic signal generator across all 9 modulation formats and noise channel impairments.
12. [`tests/test_pipeline.py`](file:///c:/Users/auau/OneDrive/Desktop/SIH/tests/test_pipeline.py): Exercises the complete `SignalAnalysisPipeline` orchestrator on synthetic files.
13. [`tests/test_e2e.py`](file:///c:/Users/auau/OneDrive/Desktop/SIH/tests/test_e2e.py): End-to-end integration workflows from raw file ingestion through decrypted telemetry output.
14. [`tests/test_gui.py`](file:///c:/Users/auau/OneDrive/Desktop/SIH/tests/test_gui.py): Headless PyQt6 verification of window instantiation, signal emission, and tab switching.

---

## 8. Cryptographic & Security Compliance

- **Zero-Network Policy:** Enforced programmatically at application bootstrap before any other imports occur.
- **Data-at-Rest Protection:** Standard results and raw payload extractions are optionally written to disk using PBKDF2-derived keys and Counter-mode encryption.
- **Audit Verification:** Every result artifact includes a cryptographic SHA-256 digest of the ingested raw capture, guaranteeing non-repudiation in intelligence environments.
