# Master Test Plan & Comprehensive Test Cases
## Automated Model for Analysis of .IQ and .WAV Files with Signal Parameter Extraction

**Problem Statement ID:** 26147  
**Organization:** National Technical Research Organisation (NTRO)  
**Category:** Software / SIGINT & Digital Signal Processing  
**Document Type:** Master Test Plan & Test Case Specification  
**Version:** 2.0 (Consolidated & Enhanced)  
**Last Updated:** 2024  
**Status:** Ready for Implementation  

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Testing Strategy & Objectives](#testing-strategy--objectives)
3. [Test Levels & Scope](#test-levels--scope)
4. [Test Environment Requirements](#test-environment-requirements)
5. [Test Data Matrix](#test-data-matrix)
6. [Module 1: File Ingestion & Parsing](#module-1-file-ingestion--parsing)
7. [Module 2: Signal Preprocessing & Validation](#module-2-signal-preprocessing--validation)
8. [Module 3: Spectral & Spatial Visualization](#module-3-spectral--spatial-visualization)
9. [Module 4: Parameter Extraction](#module-4-parameter-extraction)
10. [Module 5: Automatic Modulation Classification (AMC)](#module-5-automatic-modulation-classification-amc)
11. [Module 6: Signal Demodulation](#module-6-signal-demodulation)
12. [Module 7: De-interleaving](#module-7-de-interleaving)
13. [Module 8: Forward Error Correction (FEC) Decoding](#module-8-forward-error-correction-fec-decoding)
14. [Module 9: Bitstream Correlation & Payload Extraction](#module-9-bitstream-correlation--payload-extraction)
15. [Module 10: GUI & User Interaction](#module-10-gui--user-interaction)
16. [Module 11: Performance & Resource Management](#module-11-performance--resource-management)
17. [Module 12: Security & Air-Gapped Operation](#module-12-security--air-gapped-operation)
18. [Module 13: Storage, Reporting & Versioning](#module-13-storage-reporting--versioning)
19. [Module 14: End-to-End Integration](#module-14-end-to-end-integration)
20. [Acceptance Criteria & Gates](#acceptance-criteria--gates)
21. [Requirements Traceability Matrix (RTM)](#requirements-traceability-matrix-rtm)
22. [Regression Test Suite](#regression-test-suite)
23. [Test Execution & Reporting](#test-execution--reporting)
24. [Critical Testing Rules](#critical-testing-rules)

---

## Executive Summary

This Master Test Plan defines **comprehensive, executable test specifications** for the NTRO Signal Analysis & Parameter Extraction System (ID26147). The system processes raw `.IQ` (complex baseband) and `.wav` (audio/RF) recordings to identify signal parameters, demodulate digital modulations, remove interleaving, decode Forward Error Correction (FEC), and extract packet headers and payloads.

### Key Testing Targets
- **Functional Coverage:** 100% of FRs (Functional Requirements) 1.1–8.1
- **Non-Functional Coverage:** All NFRs including performance, security, and reliability
- **AMC Accuracy:** ≥90% on held-out test set (SNR ≥ 5 dB)
- **DSP Precision:** Numerical validation against deterministic reference signals
- **Security:** Zero network operations, air-gapped verification
- **UI Responsiveness:** ≥25 FPS, non-blocking GUI during background processing

### Test Pyramid
```
┌─────────────────────────────────────┐
│   End-to-End (E2E) Tests            │  5 tests
├─────────────────────────────────────┤
│   System Tests                       │ 20 tests
├─────────────────────────────────────┤
│   Integration Tests                  │ 50 tests
├─────────────────────────────────────┤
│   Unit Tests (DSP/Algorithm)         │ 80 tests
└─────────────────────────────────────┘
```

---

## Testing Strategy & Objectives

### 1.1 Primary Objectives
1. **Functional Validation** – Every feature requirement implemented correctly
2. **Numerical Accuracy** – DSP calculations match reference implementations within tolerance
3. **Robustness** – Graceful handling of corrupted/edge-case inputs
4. **Performance** – Processing latency and memory usage within budgets
5. **Security** – Air-gapped compliance with zero external communication
6. **Usability** – GUI responsive and intuitive; workflow clear

### 1.2 Test Philosophy
- **Deterministic Test Vectors** – All signal processing validated against known-good references
- **Synthetic + Real Data** – Mix controlled test signals with actual RF captures
- **Isolation + Integration** – Unit test modules independently, then test cross-module flow
- **Failure Mode Coverage** – Test both success and defined failure modes
- **Traceability** – Every test maps to a requirement; every result logged
- **Reproducibility** – Pinned versions, checksummed fixtures, deterministic random seeds

### 1.3 Acceptance Philosophy
- **No Silent Corruption** – Unknown/low-confidence results flagged explicitly
- **Partial Success is Valid** – If demod succeeds but FEC fails, report what succeeded
- **Data Integrity > Speed** – Never trade accuracy for performance
- **Audit Trail** – Every analysis result traceable to input, config, model version

---

## Test Levels & Scope

### 2.1 Unit Testing (UT)
**Focus:** Individual algorithm correctness in isolation  
**Tools:** Python `pytest`, manual calculation verification  
**Examples:**
- FFT correctness against known inputs
- Modulation detection classifier on synthetic data
- Viterbi decoder on predefined bit sequences
- CRC/checksum calculations
- Matrix transforms (I/Q balancing, normalization)

**Scope:** ~80 tests covering all DSP primitives and ML components

### 2.2 Integration Testing (IT)
**Focus:** Data flow across module boundaries  
**Tools:** `pytest`, mock/stub components as needed  
**Examples:**
- IQ ingestion → FFT → Power estimation pipeline
- Demodulation output → De-interleaving → FEC flow
- Parameter extraction confidence propagation

**Scope:** ~50 tests verifying inter-module communication

### 2.3 System Testing (ST)
**Focus:** Full end-to-end workflows via GUI  
**Tools:** `pytest-qt`, PyQt6 testing framework  
**Examples:**
- Load file → run analysis → view results → export report
- Process multiple files in sequence
- GUI responsiveness during long-running tasks
- Error dialog appearance and clarity

**Scope:** ~20 tests covering user workflows

### 2.4 Performance & Stress Testing (PT)
**Focus:** Latency, throughput, resource usage  
**Tools:** `time`, `psutil`, memory profilers  
**Examples:**
- 100 MB file processing latency
- RAM consumption scaling with file size
- GPU utilization and memory leak detection
- Concurrent thread performance

**Scope:** ~10 tests with quantitative acceptance criteria

### 2.5 Security Verification (SV)
**Focus:** Air-gapped compliance and data safety  
**Tools:** Wireshark (packet capture), strace (syscall tracing)  
**Examples:**
- Zero network socket creation
- Temporary file cleanup on exit
- Offline execution verification
- Safe input path handling (no injection)

**Scope:** ~5 tests verifying isolation and safety

---

## Test Environment Requirements

### 3.1 Hardware

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Ubuntu 22.04 LTS / Windows 10 (64-bit) | Ubuntu 22.04 LTS (Air-Gapped Workstation) |
| **CPU** | Quad-Core Intel i5 / AMD Ryzen 5 (2.5 GHz) | 8-Core Intel i7/i9 or AMD Ryzen 7/9 (3.5+ GHz) |
| **RAM** | 16 GB DDR4 | 32 GB DDR4/DDR5 |
| **GPU** | Integrated OpenGL 3.3 | NVIDIA RTX 3060+ (CUDA 12+) |
| **Storage** | 10 GB SSD | 100 GB NVMe M.2 SSD (fast I/O) |
| **Network** | Disconnected (Air-Gapped) | Isolated lab network (no external routes) |

### 3.2 Software Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.11+ | Runtime & scripting |
| **NumPy** | 1.24.3+ | Matrix operations |
| **SciPy** | 1.11.0+ | Signal processing (FFT, filter design) |
| **PyTorch** | 2.0+ (or TensorFlow 2.13+) | ML inference |
| **PyQt6** | 6.5+ | GUI framework |
| **pytest** | 7.4+ | Unit testing framework |
| **pytest-qt** | 4.2.0+ | PyQt6 testing support |
| **GNU Radio** | 3.10+ (optional) | Advanced DSP/simulation |
| **matplotlib** | 3.7+ | Plotting & visualization verification |

### 3.3 Test Tools

| Tool | Purpose |
|------|---------|
| `pytest` + `pytest-qt` | Automated test execution & PyQt6 assertions |
| `pytest-cov` | Code coverage measurement |
| `Valgrind` / `AddressSanitizer` | Memory leak & corruption detection |
| `perf` | CPU profiling and cycle counting |
| `psutil` | Process resource monitoring |
| `Wireshark` | Network packet capture (verify zero traffic) |
| `strace` / `ProcessMonitor` | System call tracing (verify no network syscalls) |
| `Git` + Pre-commit hooks | Version control & test automation triggers |

---

## Test Data Matrix

### 4.1 Input File Fixtures

| Dataset ID | Type | Purpose | Specifications |
|-----------|------|---------|-----------------|
| **VALID-IQ-01** | IQ | Basic valid IQ | Float32, 44.1 kHz, 1M samples, known metadata |
| **VALID-IQ-02** | IQ | IQ without optional metadata | Float32, no center frequency / gain tags |
| **VALID-IQ-03** | IQ | Multiple IQ data types | int8, int16, float32 variants, same signal |
| **VALID-WAV-01** | WAV | Mono PCM WAV | 16-bit PCM, 48 kHz, 1M samples |
| **VALID-WAV-02** | WAV | Stereo/multi-channel | 2-channel 16-bit PCM, 48 kHz |
| **INVALID-FORMAT** | Binary | Unsupported file | Random binary/text data |
| **CORRUPT-IQ** | IQ | Truncated/corrupted | Incomplete payload (file cut mid-sample) |
| **CORRUPT-WAV** | WAV | Broken RIFF header | Invalid chunk size / missing audio data |
| **EMPTY-FILE** | Binary | 0-byte file | Empty input |
| **LOW-SNR** | IQ | Noisy signal | Signal at 5 dB SNR |
| **HIGH-SNR** | IQ | Clean signal | Signal at 20+ dB SNR |

### 4.2 Modulation Reference Fixtures

| Dataset ID | Modulation | Parameters | Use Case |
|-----------|-----------|-----------|----------|
| **REF-BPSK** | BPSK | 1 sps, zero phase offset | Demodulation accuracy |
| **REF-QPSK** | QPSK | 1 sps, 0/45/90/135° variants | Constellation plot validation |
| **REF-8PSK** | 8-PSK | 1 sps, all 8 symbols | Phase accuracy test |
| **REF-16QAM** | 16-QAM | 1 sps, standard mapping | Magnitude/phase test |
| **REF-64QAM** | 64-QAM | 1 sps, Gray coding | Complex constellation |
| **REF-FSK-2** | 2-FSK | Known tone spacing | Frequency detection |
| **REF-FSK-4** | 4-FSK | Known tone spacing | Multi-tone FSK |
| **REF-FADING** | QPSK | Rayleigh fading channel | Robustness test |

### 4.3 Coding & Interleaving Reference Fixtures

| Dataset ID | Code Type | Parameters | Purpose |
|-----------|-----------|-----------|---------|
| **REF-CONV-K7** | Convolutional | K=7, R=1/2, G=[133,171]oct | Viterbi test |
| **REF-RS-255-223** | Reed-Solomon | RS(255, 223) over GF(2^8) | Byte error correction |
| **REF-LDPC-1/2** | LDPC | Rate 1/2, 10 check nodes | Belief propagation |
| **REF-BLK-INT-4** | Block Interleave | 4x4 block | De-interleaving test |
| **REF-CONV-INT** | Convolutional | Depth=4, shift=1 | Interleaver inverse |
| **REF-DIAG-INT** | Diagonal | Permutation matrix | Diagonal reversal |
| **REF-PRNG-INT** | Pseudo-Random | Seed=12345, LCG | Random interleave |

### 4.4 Special Test Fixtures

| Dataset ID | Scenario | Content | Validation |
|-----------|----------|---------|------------|
| **MULTI-SIGNAL** | 2 simultaneous signals | BPSK + FSK overlapping | Separation capability |
| **BURSTY-NOISE** | Burst interference | Signal + impulse noise | Robustness |
| **DC-BIAS** | DC offset | Signal + 0.15V DC bias | DC removal verification |
| **IQ-IMBALANCE** | I/Q imbalance | 10% amplitude, 5° phase skew | Balancing algorithm |
| **LARGE-FILE** | Large input | 2 GB IQ file | Streaming/chunking |
| **HEADER-PAYLOAD** | Frame structure | Preamble + header + payload + CRC | Extraction test |

---

## Module 1: File Ingestion & Parsing

### Test Cases

| Test Case ID | Objective | Pre-conditions | Test Steps | Expected Result | Pass/Fail Criteria |
|--------------|-----------|----------------|-----------|-----------------|-------------------|
| **TC-ING-001** | Parse float32 IQ file | Valid `.iq` file (float32) available | 1. Open file picker → select `sample_float32.iq` → specify Float32 format → Load | Complex array populated; metadata loaded | Non-zero array; zero parse exceptions |
| **TC-ING-002** | Parse int16 IQ file | Valid `.iq` file (int16) available | 1. Select `sample_int16.iq` → specify Int16 format → Load | Samples normalized to [-1.0, +1.0] range | Correct scaling; correct sample count |
| **TC-ING-003** | Parse int8 IQ file | Valid `.iq` file (int8) available | 1. Select `sample_int8.iq` → specify Int8 format → Load | Samples normalized correctly | Min/max values within bounds |
| **TC-ING-004** | Parse mono WAV file | Valid mono `.wav` file (16-bit PCM, 48 kHz) | 1. Select `mono.wav` → Load | RIFF header parsed; sample rate, channels, duration extracted | Metadata matches RIFF chunk; waveform rendered |
| **TC-ING-005** | Parse multi-channel WAV | Stereo/multi-channel `.wav` file | 1. Select `stereo.wav` → Load | All channels ingested as separate time series | Channel count verified; no cross-talk |
| **TC-ING-006** | Handle byte-order (Endianness) | IQ file with explicit endian marker | 1. Load under correct endianness → verify statistics → Load under wrong endianness → observe corruption | Correct byte-order reproduces reference; wrong order is detected as invalid | Power/mean statistics differ by >3σ under wrong endian |
| **TC-ING-007** | Detect odd sample count | IQ file with incomplete I/Q pair | 1. Load file with odd scalar sample count | System detects incomplete pair; error message shown; no silent data shift | Parse error raised; no corruption |
| **TC-ING-008** | Reject unsupported extension | File with `.txt` or `.bin` (non-signal) extension | 1. Attempt to open unsupported file | System displays error dialog: "Unsupported file format" | User clearly informed; app remains stable |
| **TC-ING-009** | Handle empty file | 0-byte `.iq` or `.wav` file | 1. Attempt to load empty file | Error dialog: "File is empty" | No processing initiated; app stable |
| **TC-ING-010** | Detect truncated IQ payload | `.iq` file with incomplete samples (truncated) | 1. Load truncated `.iq` file | Parser identifies incomplete payload or fails with actionable error | Exception caught; user-friendly error shown |
| **TC-ING-011** | Detect corrupt WAV header | `.wav` file with broken RIFF/fmt chunk | 1. Attempt to load corrupted `.wav` | System catches exception; error dialog shown; app operational | "Invalid WAV Header" message; GUI responsive |
| **TC-ING-012** | Use IQ metadata sidecar | `.iq` file with accompanying `.json` metadata | 1. Load file with metadata tags (sample rate, center freq) | Metadata parsed and associated with signal object | Metadata fields populated correctly |
| **TC-ING-013** | Handle missing optional metadata | `.iq` file with no center frequency tag | 1. Load file; check metadata inspector | System marks missing fields as "Unknown" | File loads; missing metadata does not block processing |
| **TC-ING-014** | Ingest large file (2 GB) | 2 GB raw `.iq` file on NVMe drive | 1. Select 2 GB `.iq` file → Execute load → Monitor RAM | File mapped via `np.memmap` or chunking; MemoryError not raised | RAM usage < 2 GB above baseline; load completes in < 3 sec |
| **TC-ING-015** | Streaming/chunked processing | File larger than available RAM | 1. Process in chunks; verify chunk boundary handling | Signal integrity maintained across chunk boundaries | No sample loss/duplication at boundaries |

---

## Module 2: Signal Preprocessing & Validation

### Test Cases

| Test Case ID | Objective | Pre-conditions | Test Steps | Expected Result | Pass/Fail Criteria |
|--------------|-----------|----------------|-----------|-----------------|-------------------|
| **TC-PRE-001** | DC offset removal | IQ signal with +0.15V DC bias | 1. Load signal → Execute preprocessing → Compute mean of I/Q | Mean of I and Q reduced to ~0.0 | \|Mean(I)\| < 1e-5; \|Mean(Q)\| < 1e-5 |
| **TC-PRE-002** | I/Q imbalance correction | Signal with 10% amplitude imbalance, 5° phase | 1. Load unbalanced signal → Apply Gram-Schmidt correction | Amplitude and phase orthogonalized | Imbalance reduced by ≥20 dB; power equalized |
| **TC-PRE-003** | Sample rate normalization | Signal sampled at non-standard rate (44.1 kHz) | 1. Load signal → Resample to standard rate (48 kHz) if needed | Resampling preserves spectral characteristics | Spectral shape preserved; no aliasing artifacts |
| **TC-PRE-004** | Clipping detection | Signal with clipping/saturation | 1. Load clipped signal → Analyze peak statistics | System detects saturation and warns user | Clipping indicator displayed; recommendation offered |
| **TC-PRE-005** | SNR estimation | Known signal + AWGN at target SNR | 1. Load signal → Estimate SNR via cumulant method | Estimated SNR within ±2 dB of true SNR | \|SNR_est - SNR_true\| ≤ 2 dB |
| **TC-PRE-006** | Windowing consistency | Signal preprocessed with multiple window types | 1. Apply Hann, Hamming, Blackman windows → compare spectral leakage | Window choice does not corrupt signal classification | Modulation decision consistent across windows |
| **TC-PRE-007** | Normalization by power | Raw signal with arbitrary scaling | 1. Load signal → Normalize by power → Verify unit power | Signal power normalized to ~1.0 | 10*log10(E[s^2]) ≈ 0 dB |
| **TC-PRE-008** | Filter artifact inspection | High-pass/low-pass filter application | 1. Apply filter → Check impulse response duration | Filter transients do not corrupt signal start | First N_filt samples marked as warmup |

---

## Module 3: Spectral & Spatial Visualization

### Test Cases

| Test Case ID | Objective | Pre-conditions | Test Steps | Expected Result | Pass/Fail Criteria |
|--------------|-----------|----------------|-----------|-----------------|-------------------|
| **TC-VIS-001** | Render waterfall spectrogram | IQ signal loaded; FFT parameters configured | 1. Set FFT size=2048, window=Hann → Start waterfall rendering → Measure FPS | Smooth time-frequency-power spectrogram rendered at ≥25 FPS | FPS ≥ 25; color gradient smooth; no flicker |
| **TC-VIS-002** | FFT spectral plot accuracy | Known reference signal (e.g., pure tone) | 1. Load known tone → Compute FFT → Verify peak location and magnitude | Peak occurs at expected frequency; magnitude matches theory | Peak within ±1 bin; magnitude ±1 dB |
| **TC-VIS-003** | Dynamic range & color mapping | Waterfall with signals over wide power range | 1. Render waterfall → Inspect color scale mapping | Low-power details visible; high-power not saturated | Color map spans 60+ dB range; no clipping |
| **TC-VIS-004** | I/Q constellation diagram (QPSK) | QPSK demodulated symbols | 1. Load QPSK signal → Render constellation → Measure cluster positions | 4 symbol clusters appear at ±1±j locations | Cluster separation > 2σ noise |
| **TC-VIS-005** | I/Q constellation diagram (16QAM) | 16-QAM demodulated symbols | 1. Load 16-QAM signal → Render constellation | 16 symbol clusters at correct Gray-code positions | All clusters visible; separation quantified |
| **TC-VIS-006** | Power spectral density (PSD) | IQ signal | 1. Compute Welch PSD → Render → Compare to theoretical | PSD shape matches expected signal spectrum | Bandwidth measurement within ±5% |
| **TC-VIS-007** | Spectrogram with high time resolution | Chirp or frequency-hopping signal | 1. Render spectrogram with 512-point FFT, high overlap | Frequency transitions clearly visible over time | Chirp slope, hop times visible |
| **TC-VIS-008** | Phase trajectory plot | Demodulated symbols | 1. Render phase vs. time for PSK signal | Phase progression smooth; jumps only at symbol boundaries | No spurious phase discontinuities |
| **TC-VIS-009** | Zoom & pan functionality | Waterfall/spectrum displayed | 1. Click-drag to zoom; scroll to pan | Rendering responsive; no redraw lag | Interaction latency < 100 ms |
| **TC-VIS-010** | Export plots (PNG/PDF) | Visualization rendered | 1. Click "Export" → select format → save | Plot image saved to disk with correct resolution | File size appropriate; image readable |

---

## Module 4: Parameter Extraction

### Test Cases

| Test Case ID | Objective | Pre-conditions | Test Steps | Expected Result | Pass/Fail Criteria |
|--------------|-----------|----------------|-----------|-----------------|-------------------|
| **TC-PAR-001** | Sampling frequency ($F_s$) estimation | IQ signal with known $F_s$ | 1. Compute autocorrelation peaks → Identify repetition → Estimate $F_s$ | Estimated $F_s$ within ±1% of true value | \|$F_s$_est - $F_s$_true\| / $F_s$_true < 0.01 |
| **TC-PAR-002** | Symbol rate detection | BPSK/QPSK at known symbol rate | 1. Compute cumulants over sliding windows → Detect cyclostationary peaks | Detected symbol rate ±2% of true rate | Confidence score > 0.8 |
| **TC-PAR-003** | Bandwidth measurement | Signal with known 3-dB bandwidth | 1. Compute spectrum → Find -3 dB points → Calculate BW | Measured BW within ±5% of reference | Tolerance range achievable on real RF |
| **TC-PAR-004** | Center frequency estimation | Bandpass IQ signal | 1. Compute spectrum → Find peak → Read carrier freq | Center frequency within ±2% | Accuracy sufficient for subsequent analysis |
| **TC-PAR-005** | SNR & noise power estimation | Signal + AWGN at target SNR | 1. Estimate signal power (via cumulants) → Estimate noise floor (via FFT min) → Compute SNR | Estimated SNR ±2 dB of true SNR | Confidence intervals reported |
| **TC-PAR-006** | Power measurement (PAPR) | OFDM or multi-symbol signal | 1. Compute peak and average power → Calculate PAPR | PAPR measurement within ±1 dB of reference | Useful for modulation detection |
| **TC-PAR-007** | Frequency offset detection | Signal with 10 kHz frequency offset | 1. Estimate residual frequency offset via cumulant method | Offset measured as 10±2 kHz | Enable subsequent synchronization |
| **TC-PAR-008** | Time-domain envelope analysis | AM-modulated or bursty signal | 1. Compute analytical signal envelope → Extract envelope from IQ | Envelope shape matches expected modulation | Burst duty cycle measurable |
| **TC-PAR-009** | Spectral flatness (Wiener entropy) | Wideband noise vs. narrow signal | 1. Compute spectral entropy → Normalize | Entropy low for pure tone; high for noise | Useful for signal presence detection |
| **TC-PAR-010** | Crest factor measurement | Multi-carrier or linear modulation | 1. Compute crest factor (peak/RMS) | Crest factor within expected range for modulation | Parameter feeds into modulation classifier |

---

## Module 5: Automatic Modulation Classification (AMC)

### Test Cases

| Test Case ID | Objective | Pre-conditions | Test Steps | Expected Result | Pass/Fail Criteria |
|--------------|-----------|----------------|-----------|-----------------|-------------------|
| **TC-AMC-001** | BPSK classification (high SNR) | Ground-truth BPSK reference, 20 dB SNR | 1. Load BPSK signal → Run classifier → Read prediction | Predicted class = BPSK; confidence > 0.95 | Accuracy ≥95% on held-out BPSK set |
| **TC-AMC-002** | QPSK classification (high SNR) | Ground-truth QPSK reference, 20 dB SNR | 1. Load QPSK signal → Run classifier → Read prediction | Predicted class = QPSK; confidence > 0.90 | Accuracy ≥90% on held-out QPSK set |
| **TC-AMC-003** | 8-PSK classification | Ground-truth 8-PSK reference | 1. Load 8-PSK signal → Classify | Predicted class = 8-PSK | Accuracy ≥85% |
| **TC-AMC-004** | 16-QAM classification | Ground-truth 16-QAM reference | 1. Load 16-QAM signal → Classify | Predicted class = 16-QAM | Accuracy ≥80% |
| **TC-AMC-005** | 64-QAM classification | Ground-truth 64-QAM reference | 1. Load 64-QAM signal → Classify | Predicted class = 64-QAM | Accuracy ≥80% |
| **TC-AMC-006** | FSK classification (2-FSK) | Ground-truth 2-FSK reference | 1. Load 2-FSK signal → Classify | Predicted class = FSK | Accuracy ≥85% |
| **TC-AMC-007** | Low-SNR classification (5 dB) | QPSK at 5 dB SNR | 1. Load low-SNR signal → Classify → Check confidence | Prediction made; confidence appropriately reduced (0.6-0.7) | Low-confidence predictions flagged; not presented as certain |
| **TC-AMC-008** | Out-of-Distribution rejection | Signal of unknown modulation (not in training set) | 1. Load OOD signal → Classify | Prediction made; confidence < 0.5 or explicit "Unknown" flag | OOD detection working; no false high confidence |
| **TC-AMC-009** | Ambiguous class distinction (QPSK vs. 16-QAM) | Signal that resembles both | 1. Load ambiguous signal → Inspect confidence scores | Top-2 classes identified; confidence spread quantified | Tie-breaking logic documented |
| **TC-AMC-010** | Model version traceability | Analysis with 2 different trained models | 1. Analyze same input with Model v1 and v2 → Compare results | Results clearly tagged with model version; no artifact mixing | Version info in output report |
| **TC-AMC-011** | Batch classification | 100 sequential analysis runs | 1. Run batch mode on 100 files → Verify no data leakage | Results for file N do not contain artifacts from file N-1 | Batch isolation verified |
| **TC-AMC-012** | Confidence calibration | Classification confidence vs. actual accuracy | 1. Plot confidence vs. error rate on test set | Calibration curve monotonic; high-confidence predictions accurate | Brier score < 0.1 |

---

## Module 6: Signal Demodulation

### Test Cases

| Test Case ID | Objective | Pre-conditions | Test Steps | Expected Result | Pass/Fail Criteria |
|--------------|-----------|----------------|-----------|-----------------|-------------------|
| **TC-DEM-001** | Symbol timing recovery (Müller & Müller) | QPSK signal with unknown symbol phase | 1. Load signal without symbol timing → Run timing recovery → Examine eye diagram | Eye diagram opens; symbol decisions aligned | Timing error < 0.2 symbols |
| **TC-DEM-002** | Carrier phase/frequency recovery (PLL) | QPSK with 5 kHz frequency offset | 1. Load signal → Run PLL (Costas loop) → Measure residual offset | Residual offset < 100 Hz | Enable demodulation without error floors |
| **TC-DEM-003** | BPSK demodulation (clean) | Reference BPSK, 20 dB SNR, perfect timing | 1. Load BPSK → Demodulate → Extract bitstream → Compare to known bits | BER = 0 | Perfect recovery on clean reference |
| **TC-DEM-004** | QPSK demodulation (clean) | Reference QPSK, 20 dB SNR, perfect timing | 1. Load QPSK → Demodulate → Extract bits | BER = 0 | Perfect recovery on clean reference |
| **TC-DEM-005** | 16-QAM demodulation (clean) | Reference 16-QAM, 20 dB SNR | 1. Load 16-QAM → Demodulate → Extract bits | BER = 0 | Perfect recovery on clean reference |
| **TC-DEM-006** | FSK demodulation (2-FSK) | Reference 2-FSK with known tone spacing | 1. Load 2-FSK → Run tone detector → Extract bits | Bits match reference bitstream | BER = 0 on clean signal |
| **TC-DEM-007** | QPSK demodulation (low SNR, 5 dB) | QPSK at 5 dB SNR | 1. Demodulate at low SNR → Measure BER | BER consistent with theoretical performance | Soft-decision BER ~2% at 5 dB SNR |
| **TC-DEM-008** | PSK ambiguity resolution | PSK signal with unknown phase rotation | 1. Attempt demod with Viterbi sequence detection → Resolve ambiguity | Differential encoding or Viterbi resolves 4-way ambiguity | Phase ambiguity eliminated |
| **TC-DEM-009** | Differential detection (DQPSK) | Differentially-encoded QPSK | 1. Load DQPSK signal → Demodulate using differential detector | Bits recovered without requiring explicit phase ref | BER < 1e-3 on clean signal |
| **TC-DEM-010** | Matched filter + decision | Gaussian-shaped pulses (GMSK) | 1. Design matched filter → Apply to received signal → Make hard decisions | Maximize SNR; align decisions to symbol boundaries | ISI minimized; BER near theory |
| **TC-DEM-011** | Soft-decision symbol output (LLR) | Demodulator configured for soft output | 1. Demodulate → Generate log-likelihood ratios (LLRs) for each bit | LLRs provided to FEC decoder | LLRs have correct sign/magnitude relationship |
| **TC-DEM-012** | Demod with frequency offset | Signal with 5 kHz frequency offset | 1. Run demodulator → Correct frequency offset → Measure BER | Offset correction enables BER < 1e-3 | Frequency correction working |

---

## Module 7: De-interleaving

### Test Cases

| Test Case ID | Objective | Pre-conditions | Test Steps | Expected Result | Pass/Fail Criteria |
|--------------|-----------|----------------|-----------|-----------------|-------------------|
| **TC-INT-001** | Block de-interleaving (4x4) | Bitstream with known block interleaving | 1. Load interleaved bits → Apply 4x4 block de-interleaver → Compare to reference | De-interleaved bits match ground-truth order | Zero bit transpositions; correct permutation inverse |
| **TC-INT-002** | Convolutional de-interleaving (depth=4) | Bitstream with convolutional interleaving | 1. Load interleaved bits → Apply convolutional de-interleaver (depth=4) → Compare | De-interleaved order matches reference | Correct delay accumulation/reversal |
| **TC-INT-003** | Diagonal (rail-fence) de-interleaving | Bitstream with diagonal interleaving | 1. Load interleaved bits → Apply diagonal de-interleaver → Compare | De-interleaved bits match reference permutation | Rail-fence reversal correct |
| **TC-INT-004** | Pseudo-random de-interleaving | Bitstream with pseudo-random permutation (seed=12345) | 1. Load interleaved bits → Apply PRNG de-interleaver (seed match) → Compare | De-interleaved order matches reference | PRNG state synchronization correct |
| **TC-INT-005** | De-interleaver auto-detection | Unknown interleaved bitstream | 1. Attempt to auto-detect interleaver type → Run appropriate de-interleaver | System identifies correct interleaving scheme | Detected scheme matches injected type with >80% confidence |
| **TC-INT-006** | Cascaded de-interleaving (2-stage) | Double-interleaved bitstream | 1. Apply first de-interleaver → Apply second de-interleaver → Compare | Bitstream de-interleaved correctly (order-sensitive) | Both stage permutations applied in correct order |
| **TC-INT-007** | Burst error protection (interleaving resilience) | Interleaved bitstream; apply burst error | 1. Corrupt 10 consecutive bits after interleaving → De-interleave → Analyze error spread | Burst error dispersed across multiple codewords | Error spread improves downstream FEC performance |

---

## Module 8: Forward Error Correction (FEC) Decoding

### Test Cases

| Test Case ID | Objective | Pre-conditions | Test Steps | Expected Result | Pass/Fail Criteria |
|--------------|-----------|----------------|-----------|-----------------|-------------------|
| **TC-FEC-001** | Viterbi hard-decision decoding (K=7, R=1/2) | Convolutional-coded bitstream (K=7, R=1/2, G=[133,171]) | 1. Load coded bitstream → Run hard Viterbi decoder → Compare to reference bits | Decoded bits match reference; BER improvement observed | Hard-decision works; ~3 dB gain at high SNR |
| **TC-FEC-002** | Viterbi soft-decision decoding (LLR input) | LLRs from demodulator over noisy QPSK | 1. Feed LLRs to Soft Viterbi Decoder → Decode → Measure BER | Soft-decision yields ~2 dB coding gain vs. hard | Zero bit errors at lower SNR than hard Viterbi |
| **TC-FEC-003** | Reed-Solomon (255,223) decoding | RS-coded block over GF(2^8); 10 byte errors inserted | 1. Input corrupted RS codeword → Execute Berlekamp-Massey decoder → Verify output | All 10 byte errors corrected (t ≤ 16) | Decoded block matches ground truth; error count = 10 |
| **TC-FEC-004** | Reed-Solomon beyond error capability | RS(255,223) with 20 byte errors (exceeds t=16) | 1. Input block with 20 errors → Execute RS decoder | Decoder flags "Uncorrectable Error" exception | No silent corruption; user informed of failure |
| **TC-FEC-005** | Concatenated coding (RS outer + Viterbi inner) | Dual-layer encoded stream (outer RS + inner Viterbi) with burst noise | 1. Run Inner Viterbi → De-interleave → Run Outer RS → Inspect output | All error types corrected (random via Viterbi, bursts via RS) | Final output 100% error-free |
| **TC-FEC-006** | LDPC soft-decision decoding (sum-product) | LDPC code (rate 1/2) corrupted by AWGN | 1. Feed soft LLRs → Run iterative BP algorithm (max 50 iter) → Check parity | Syndrome $H \cdot x^T = 0$ satisfied within 12 iterations | Clean codeword recovered; iterations ≤ 50 |
| **TC-FEC-007** | FEC scheme auto-detection | Unknown encoded bitstream | 1. Run syndrome likelihood estimator → Measure detected FEC type | System identifies candidate FEC structure | Detected scheme matches injected coding |
| **TC-FEC-008** | Turbo code decoding (if applicable) | Turbo-coded bitstream | 1. Run turbo decoder with 4 iterations → Check output | Interleaver-dependent gain achieved | Performance near Shannon limit (within 1 dB) |
| **TC-FEC-009** | Erasure channel with FEC (fountain codes if used) | Coded data with packet loss | 1. Decode with missing packets → Verify recovery | Packets recovered up to code rate limit | Recovery threshold matches theoretical bound |
| **TC-FEC-010** | FEC failure reporting | FEC decoder unable to correct | 1. Force uncorrectable error scenario → Observe error handling | Decoder returns failure status; earlier-stage results preserved | Partial report generated; failure clearly documented |

---

## Module 9: Bitstream Correlation & Payload Extraction

### Test Cases

| Test Case ID | Objective | Pre-conditions | Test Steps | Expected Result | Pass/Fail Criteria |
|--------------|-----------|----------------|-----------|-----------------|-------------------|
| **TC-COR-001** | Frame sync correlation (exact match) | Decoded bitstream containing 32-bit sync word `0x1ACFFC1D` | 1. Load sync pattern → Execute sliding-window correlator → Locate peak | Peak occurs at exact sync start index | Correlation score = 32 at correct bit offset |
| **TC-COR-002** | Sync with bit errors (Hamming tolerance) | Bitstream with sync word + 2 flipped bits | 1. Set Hamming distance tolerance = 3 → Run correlator | Peak detected at correct offset despite errors | Match score = 30 ≥ threshold (29) |
| **TC-COR-003** | Header field dissection | Synchronized frame with 16-byte header (Sync + Length + ID + CRC) | 1. Execute header parser → Extract fields | Payload length, transmitter ID, sequence number extracted | Fields parsed into UI inspector table |
| **TC-COR-004** | Payload extraction & CRC-16 verification | Frame with payload + CRC-16 trailer | 1. Strip header/trailer → Compute CRC over payload → Compare with trailer | Calculated CRC matches frame trailer | Payload flagged as "Valid" |
| **TC-COR-005** | Payload export (binary/hex/JSON) | Valid extracted payload | 1. Click Export → Select format `.bin` / `.hex` / `.json` → Save | Files generated with correct content | Exported data byte-accurate |
| **TC-COR-006** | False sync rejection (random noise) | White noise bitstream | 1. Run correlator with pattern `0x1ACFFC1D` | Scores remain below threshold → "No Frame Sync Found" | Zero false-positive sync detections |
| **TC-COR-007** | Multi-frame extraction | Bitstream with N sequentially-framed payloads | 1. Correlate multiple sync words → Extract all frames | All N frames identified and extracted | Frame count = N; no frame loss |
| **TC-COR-008** | Payload size inference | Unknown frame structure | 1. Run heuristic length field parser → Infer payload size | System correctly interprets length field or reports ambiguity | Length extracted; extraction succeeds |
| **TC-COR-009** | Interleaved payload recovery | Payload with de-interleaving already applied | 1. Extract payload (assuming de-interleave already done) → Render bitstream | Payload bits in correct order | De-interleaving prerequisite validated |
| **TC-COR-010** | Partial payload recovery on FEC failure | FEC decoder unable to correct; partial payload available | 1. Attempt payload extract despite FEC failure → Report what's recoverable | Partial payload extracted; FEC failure documented | User sees recoverable data + warnings |

---

## Module 10: GUI & User Interaction

### Test Cases

| Test Case ID | Objective | Pre-conditions | Test Steps | Expected Result | Pass/Fail Criteria |
|--------------|-----------|----------------|-----------|-----------------|-------------------|
| **TC-GUI-001** | File picker dialog | Application main window open | 1. Click "Open File" → Browse to signal file → Select → Confirm | File selected; path displayed in UI | File path field updated; preview triggered |
| **TC-GUI-002** | Analysis start / progress indicator | File loaded; parameters set | 1. Click "Run Analysis" → Observe progress bar | Progress bar advances; stages labeled (Ingestion → Preprocessing → AMC → Demod → FEC) | Progress updates smoothly; ETA displayed |
| **TC-GUI-003** | Real-time plot rendering (waterfall) | Analysis in progress | 1. Observe waterfall plot during live processing | Spectrogram updates smoothly in real-time | Rendering non-blocking; GUI interactive |
| **TC-GUI-004** | Result inspection panel | Analysis complete | 1. Click each result tab (Spectrum / Constellation / Parameters / Classification) | Each tab displays appropriate visualization + metrics | All views load on demand; no delays |
| **TC-GUI-005** | Export report dialog | Analysis complete | 1. Click "Export Report" → Select format (PDF / JSON / CSV) → Save location | Report file generated on disk | Report contains analysis metadata + results |
| **TC-GUI-006** | Error message clarity | File loading fails (e.g., corrupt WAV) | 1. Attempt to load corrupt file → Observe error dialog | Clear error message with corrective action suggested | User understands problem; path forward offered |
| **TC-GUI-007** | Tooltip & help text | Mouse hover over UI elements | 1. Hover over parameter fields, buttons, etc. → Observe tooltips | Context-sensitive help appears | Tooltips accurate and concise |
| **TC-GUI-008** | Window resize & layout responsiveness | Application window resized | 1. Drag window edges to change size → Observe layout | Plots and tables resize correctly; no element clipping | Responsive layout preserved |
| **TC-GUI-009** | Multi-file batch mode | Multiple input files listed | 1. Select 5 files → Click "Batch Process" → Monitor completion | All files processed sequentially; results linked to sources | Batch output organized by input file |
| **TC-GUI-010** | Configuration persistence | User modifies settings (FFT size, window type, etc.) | 1. Change parameters → Close application → Reopen | Settings restored from previous session | Configuration file on disk; session state replayed |
| **TC-GUI-011** | Dark/Light theme toggle | Application theme selector present | 1. Click theme option → Observe UI colors | Entire GUI switches themes; plots readable in both modes | Theme consistent across all windows |
| **TC-GUI-012** | Keyboard shortcuts | Keyboard input focus | 1. Press Ctrl+O (open), Ctrl+S (save), etc. → Observe action | Shortcuts trigger expected operations | Shortcuts documented in Help menu |
| **TC-GUI-013** | Undo/Redo functionality (if applicable) | User makes analysis choices | 1. Run analysis A → Run analysis B → Click Undo → Verify return to A state | Previous analysis state restored | Undo stack maintained correctly |
| **TC-GUI-014** | Status bar updates | Various operations in progress | 1. Observe status bar during file load, processing, export | Status messages update in real-time | Clear indication of current operation |
| **TC-GUI-015** | Drag-and-drop file loading | GUI main window visible | 1. Drag `.iq` or `.wav` file onto window → Drop | File automatically loaded; processing can start | Drag-drop handler functional |

---

## Module 11: Performance & Resource Management

### Test Cases

| Test Case ID | Objective | Pre-conditions | Test Steps | Expected Result | Pass/Fail Criteria |
|--------------|-----------|----------------|-----------|-----------------|-------------------|
| **TC-PER-001** | Processing speed (100 MB file) | 100 MB raw `.iq` file on disk | 1. Start timer → Execute E2E pipeline → Stop timer | Entire pipeline completes in < 5.0 seconds on 8-core CPU | Total time ≤ 5.0 sec |
| **TC-PER-002** | GUI responsiveness during processing | 1 GB file being processed in background | 1. Trigger processing → Interact with GUI (move window, click tabs) → Measure latency | Main thread remains responsive; no "Not Responding" freezes | UI latency < 100 ms per interaction |
| **TC-PER-003** | Memory leak detection | 100 sequential file analysis runs | 1. Execute batch loop (100 files) → Log memory via `psutil` → Plot trend | Memory stabilizes after warmup; no unbounded growth | RAM growth < 50 MB over 100 iterations |
| **TC-PER-004** | Multi-core CPU utilization | 8-core workstation available | 1. Process large file with multiprocessing enabled → Monitor CPU cores via `htop` | Load distributed evenly; all cores active | All cores show > 80% utilization during processing |
| **TC-PER-005** | GPU acceleration (if available) | NVIDIA GPU with CUDA available | 1. Enable GPU mode → Process file → Compare GPU vs. CPU time | GPU processing faster by ≥2x vs. single-core | GPU/CPU speedup ratio quantified |
| **TC-PER-006** | Disk I/O throughput | Large file on fast NVMe SSD | 1. Load 2 GB file → Time ingestion step only | File read completes in < 2 seconds | Disk throughput ≥ 1 GB/sec achieved |
| **TC-PER-007** | FFT performance (parallelization) | FFT size 4096, 10k operations | 1. Benchmark single-threaded FFT → Benchmark multi-threaded → Compare | Multi-threaded FFT faster by ≥N (N = # cores) | Parallelization scaling near-linear |
| **TC-PER-008** | Model inference latency (AMC) | ML classifier running on CPU/GPU | 1. Measure time for single inference pass | Inference time < 100 ms per window (for real-time viability) | Inference latency within budget |
| **TC-PER-009** | Viterbi decoder throughput | Decoding 1M bits | 1. Measure bits/second decoded by Viterbi | Throughput > 1 Mbps on single core | Decoding speed meets real-time requirement |
| **TC-PER-010** | Scaling with file size | Files of 10 MB, 100 MB, 1 GB | 1. Process each file → Plot time vs. size → Measure scaling factor | Processing time scales linearly with file size | O(N) complexity confirmed |

---

## Module 12: Security & Air-Gapped Operation

### Test Cases

| Test Case ID | Objective | Pre-conditions | Test Steps | Expected Result | Pass/Fail Criteria |
|--------------|-----------|----------------|-----------|-----------------|-------------------|
| **TC-SEC-001** | Zero network socket verification | Wireshark packet capture active | 1. Launch app → Ingest file → Run analysis → Export report → Close → Inspect Wireshark log | Zero network sockets opened; zero DNS/HTTP/telemetry packets | Network log contains 0 packets from app PID |
| **TC-SEC-002** | Temporary file cleanup | Application session with signal file loaded | 1. Close application → Inspect `/tmp` and app cache dirs | Temporary buffers wiped; no unencrypted temp files remaining | Temp cache clean; zero orphan signal files on disk |
| **TC-SEC-003** | Offline standalone execution | Workstation disconnected from network (air-gapped) | 1. Disable network adapters → Boot system → Launch app → Run full pipeline | All functions work 100%; no network timeouts or errors | Zero network-related failures |
| **TC-SEC-004** | Input path sanitization (injection prevention) | File picker allows arbitrary paths | 1. Attempt to open file with path containing special chars: `../`, `\x00`, etc. | System sanitizes path; no command injection or directory traversal | File loading safe; no symlink attacks |
| **TC-SEC-005** | Config file validation | Application configuration file (JSON/YAML) | 1. Inject malicious config (code exec, symlink) → Run app → Observe behavior | Config parsed safely; malicious entries rejected or logged as errors | No arbitrary code execution from config |
| **TC-SEC-006** | Sensitive data in logs | Logging enabled during analysis | 1. Run analysis → Examine log files → Search for raw signal data, IQ samples, or keys | Logs do not contain raw signal samples; only metadata/parameters | Zero leakage of sensitive IQ data in logs |
| **TC-SEC-007** | Memory isolation (process sandboxing) | Multi-user workstation | 1. Run app under different user accounts simultaneously → Check process isolation | Each process memory isolated; no cross-user data leakage | Proc memory maps do not overlap |
| **TC-SEC-008** | Signal file permissions | Processed signal file in output directory | 1. Process file → Check output permissions → Verify readability by intended user only | Output files owned by user; world-readable bits not set | Permissions 0640 (rw-r-----) or stricter |

---

## Module 13: Storage, Reporting & Versioning

### Test Cases

| Test Case ID | Objective | Pre-conditions | Test Steps | Expected Result | Pass/Fail Criteria |
|--------------|-----------|----------------|-----------|-----------------|-------------------|
| **TC-STORE-001** | Result persistence (JSON export) | Analysis complete | 1. Export result as JSON → Close app → Reload JSON in Python → Verify content | Result file contains all analysis metadata and findings | File format parseable; data lossless |
| **TC-STORE-002** | Result traceability (input metadata) | Analysis result exported | 1. Inspect exported result → Check input filename, file hash, config, model version | Result linked to input file (name/hash), config version, model version | Audit trail complete; reproducibility possible |
| **TC-STORE-003** | Report generation (PDF) | Analysis complete | 1. Export as PDF → Open PDF → Verify content (plots, tables, text) | PDF contains analysis summary, plots, parameter table, classification | PDF readable; formatting intact |
| **TC-STORE-004** | Batch export with input mapping | 10 files processed in batch | 1. Export batch results → Verify each output filename maps to correct input | Every output maps to correct source file; no result mixing | Input/output mapping verified for all files |
| **TC-STORE-005** | Result versioning | Same file analyzed with 2 model versions | 1. Analyze with Model v1 → Export → Analyze with Model v2 → Export → Compare results | Results clearly tagged with model version; no artifact mixing | Version info prevents accidental comparison of incompatible results |
| **TC-STORE-006** | Incremental result saving (checkpoint) | Long-running analysis | 1. Start analysis → Kill process at 50% completion → Restart → Resume from checkpoint | Earlier stages' results saved and reused; no re-computation | Checkpoint files on disk; resume working |
| **TC-STORE-007** | Result archive compression | 50 result files | 1. Select "Archive Results" → Choose `.zip` or `.tar.gz` format → Save | Archive created with all results; metadata intact | Archive extractable; all files recoverable |
| **TC-STORE-008** | Encryption at rest (if required) | Sensitive result file | 1. Enable encryption option → Save result → Verify file is encrypted on disk → Reopen | File encrypted; unreadable without key/password | Decryption on load successful; content matches |
| **TC-STORE-009** | Metadata embedding in output | Analysis result saved to multiple formats | 1. Save result as JSON, CSV, PDF → Open each → Verify metadata present | Metadata (timestamp, user, model version) embedded in each format | Metadata human-readable or machine-extractable |
| **TC-STORE-010** | Long-term result reproducibility | Result saved 1 year ago | 1. Reload old result file with current software version → Compare analysis | System can parse old format; results match original | Backward compatibility maintained or clear migration path |

---

## Module 14: End-to-End Integration

### Test Cases

| Test Case ID | Objective | Pre-conditions | Test Steps | Expected Result | Pass/Fail Criteria |
|--------------|-----------|----------------|-----------|-----------------|-------------------|
| **TC-E2E-001** | Clean QPSK E2E (high SNR) | Reference QPSK signal (20 dB SNR) | 1. Load QPSK file → Run analysis → Export report | File → Parameter extraction → AMC (QPSK detected, confidence > 0.9) → Demodulation (BER = 0) → Output | E2E success; all stages pass; clean bitstream recovered |
| **TC-E2E-002** | BPSK with FEC E2E | BPSK signal with Viterbi coding | 1. Load → Analyze → Demodulate → Run Viterbi → Export | Viterbi decoding succeeds; output bitstream error-free | Coding gain demonstrated; FEC working |
| **TC-E2E-003** | FSK with de-interleaving E2E | 2-FSK signal with block interleaving | 1. Load → Classify → Demodulate FSK → De-interleave (block) → Compare output | De-interleaved bitstream matches reference order | Multi-stage pipeline integrated correctly |
| **TC-E2E-004** | Low-SNR E2E (5 dB QPSK) | QPSK at 5 dB SNR | 1. Load → Analyze → Demodulate → Measure BER | BER consistent with theoretical low-SNR performance (~2% at 5 dB) | System handles impaired signal gracefully |
| **TC-E2E-005** | Multi-signal separation E2E (optional) | Two signals (BPSK + FSK) overlapping | 1. Load → Attempt separation → Classify each → Demodulate each | System identifies both signals; classifies separately; demodulates both | Signal separation capability (if implemented) works |
| **TC-E2E-006** | Batch processing E2E | 5 different signal files | 1. Select all 5 files → Click "Batch Process" → Wait for completion | All 5 processed independently; results exported per file | Batch mode isolates analyses; no cross-contamination |
| **TC-E2E-007** | Persistence & reload E2E | Analysis result exported and closed | 1. Export result → Close application → Reopen → Load exported result | Result re-loaded; all analysis data restored; plots recreated | Result file self-contained; reload functional |
| **TC-E2E-008** | Model version traceability E2E | Analyze with Model A → Switch to Model B → Re-analyze same file | 1. Analyze file with Model A → Export → Switch to Model B → Re-analyze → Compare results | Results tagged with correct model; no artifact mixing | Version info prevents accidental comparison |
| **TC-E2E-009** | Failed decoder partial report E2E | Demodulation succeeds; FEC fails | 1. Run analysis on file with uncorrectable errors → Export report | Report retains demodulation results; FEC failure documented; partial success shown | System graceful on FEC failure; earlier results preserved |
| **TC-E2E-010** | Repeated analysis isolation E2E | Analyze file A then file B sequentially | 1. Load A → Analyze → Load B → Analyze → Verify B result has no A artifacts | B result clean; no state leak from A | Session isolation working; no cross-file contamination |

---

## Acceptance Criteria & Gates

The system is considered ready for deployment when **all** acceptance gates pass:

| Gate | Acceptance Rule | Validation Test(s) |
|------|-----------------|-------------------|
| **A1** | Valid IQ and WAV inputs load and convert to common signal representation without sample corruption | TC-ING-001, TC-ING-004, TC-ING-012 |
| **A2** | Spectrum, waterfall, and constellation visualizations match deterministic fixtures | TC-VIS-002, TC-VIS-004, TC-VIS-005 |
| **A3** | Sampling rate, bandwidth, power, SNR measured within documented tolerances | TC-PAR-001, TC-PAR-005, TC-PAR-006 |
| **A4** | AMC accuracy ≥90% on held-out test set (SNR ≥ 5 dB) | TC-AMC-001 to TC-AMC-006 |
| **A5** | Low-confidence and OOD inputs not falsely presented as reliable; flags shown | TC-AMC-007, TC-AMC-008 |
| **A6** | Demodulators recover clean test vectors; BER behavior documented across SNR range | TC-DEM-003 to TC-DEM-006 |
| **A7** | Interleaver inverses & FEC decoders recover known fixtures; uncorrectable cases flagged | TC-INT-001 to TC-INT-007, TC-FEC-001 to TC-FEC-007 |
| **A8** | Bitstream correlation finds headers/preambles and extracts payloads on deterministic fixtures | TC-COR-001 to TC-COR-006 |
| **A9** | GUI exposes input, progress, signal views, parameters, classification, decoding state, export | TC-GUI-001 to TC-GUI-015 |
| **A10** | Every analysis result traceable to input, config, model version; processing logs complete | TC-STORE-002, TC-STORE-005 |
| **A11** | Large-file processing (≥2 GB) within memory/resource limits | TC-ING-014, TC-PER-005 |
| **A12** | Security tests show zero unsafe path handling, no network operations, no data leakage in logs | TC-SEC-001, TC-SEC-004, TC-SEC-006 |
| **A13** | All P0 regression tests pass before release candidate | REG-001 to REG-020 |

---

## Requirements Traceability Matrix (RTM)

| Requirement ID | Requirement Description | Mapped Test Cases | Status |
|---|---|---|---|
| **FR-1.1** | IQ/WAV ingestion (up to 2 GB) | TC-ING-001, TC-ING-002, TC-ING-003, TC-ING-004, TC-ING-014 | Core |
| **FR-2.1** | Waterfall spectrogram (≥25 FPS) | TC-VIS-001, TC-VIS-003, TC-VIS-007 | Core |
| **FR-2.2** | I/Q constellation diagram | TC-VIS-004, TC-VIS-005 | Core |
| **FR-3.1** | Sampling frequency estimation | TC-PAR-001 | Core |
| **FR-3.2** | SNR estimation | TC-PAR-005 | Core |
| **FR-4.1** | AMC (BPSK, QPSK, 8-PSK, 16-QAM, 64-QAM, FSK) ≥90% accuracy | TC-AMC-001 to TC-AMC-006 | Core |
| **FR-5.1** | Demodulation (FSK, PSK, QAM) | TC-DEM-001 to TC-DEM-012 | Core |
| **FR-6.1** | De-interleaving (block, conv, diagonal, PRNG) | TC-INT-001 to TC-INT-007 | Core |
| **FR-7.1** | FEC decoding (Viterbi, RS, LDPC, concatenated) | TC-FEC-001 to TC-FEC-007 | Core |
| **FR-8.1** | Bitstream correlation & frame extraction | TC-COR-001 to TC-COR-010 | Core |
| **FR-8.2** | Payload export (binary, hex, JSON, PDF report) | TC-COR-005, TC-STORE-003 | Core |
| **NFR-1** | Processing latency < 5 sec (100 MB file) | TC-PER-001 | Performance |
| **NFR-2** | GUI responsiveness ≥25 FPS, non-blocking | TC-PER-002, TC-VIS-001 | Usability |
| **NFR-3** | Air-gapped security (zero network) | TC-SEC-001, TC-SEC-003 | Security |
| **NFR-4** | Memory leak prevention; no unbounded growth | TC-PER-003 | Reliability |

---

## Regression Test Suite

Execute **all** regression tests after changes to core DSP, ML, decoder logic, result schemas, or model versions:

| Regression ID | Area | Mandatory Tests | Frequency |
|---|---|---|---|
| **REG-001** | File ingestion (IQ/WAV) | TC-ING-001, TC-ING-004 | Every build |
| **REG-002** | Signal preprocessing (DC, I/Q balance) | TC-PRE-001, TC-PRE-002 | Every DSP change |
| **REG-003** | FFT/Spectrum correctness | TC-VIS-002, TC-VIS-003 | Every visualization change |
| **REG-004** | Waterfall rendering | TC-VIS-001 | Every GUI change |
| **REG-005** | Sampling rate extraction | TC-PAR-001 | Every parameter change |
| **REG-006** | SNR estimation | TC-PAR-005 | Every DSP change |
| **REG-007** | AMC core classes (BPSK–64QAM) | TC-AMC-001 to TC-AMC-006 | Every model update |
| **REG-008** | AMC confidence handling | TC-AMC-007, TC-AMC-008 | Every model update |
| **REG-009** | QPSK demodulation | TC-DEM-004 | Every demod change |
| **REG-010** | 16-QAM demodulation | TC-DEM-005 | Every demod change |
| **REG-011** | Block de-interleaving | TC-INT-001 | Every interleaver change |
| **REG-012** | Viterbi decoding | TC-FEC-001, TC-FEC-002 | Every FEC change |
| **REG-013** | Bitstream header detection | TC-COR-001, TC-COR-002 | Every correlation change |
| **REG-014** | GUI workflow | TC-GUI-001, TC-GUI-006 | Every GUI change |
| **REG-015** | Result traceability | TC-STORE-002, TC-STORE-005 | Every output format change |
| **REG-016** | Error handling | TC-ING-007, TC-GUI-006 | Every error path change |
| **REG-017** | Performance (latency, memory) | TC-PER-001, TC-PER-003 | Weekly |
| **REG-018** | Security (network, paths) | TC-SEC-001, TC-SEC-004 | Every security update |
| **REG-019** | E2E clean QPSK | TC-E2E-001 | Every release |
| **REG-020** | E2E low-SNR (5 dB) | TC-E2E-004 | Every release |

---

## Test Execution & Reporting

### Test Execution Phases

1. **Phase 1: Unit Testing** (Week 1–2)
   - Execute all UT tests (80 cases) in `pytest`
   - Target: ≥95% unit test pass rate
   - Deliverable: Unit test report + coverage metrics

2. **Phase 2: Integration Testing** (Week 3–4)
   - Execute IT tests (50 cases) covering pipeline stages
   - Target: ≥98% IT pass rate
   - Deliverable: Integration report; dependency issues logged

3. **Phase 3: System Testing** (Week 5–6)
   - Execute ST tests (20 cases) via `pytest-qt`
   - Target: ≥90% ST pass rate (some failures expected on edge cases)
   - Deliverable: System test report; GUI screenshots; error logs

4. **Phase 4: Performance & Security** (Week 7)
   - Execute PT (10 cases) and SV (5 cases)
   - Target: PT latency/memory budgets met; SV zero network traffic
   - Deliverable: Performance benchmark report; security audit log

5. **Phase 5: Acceptance & UAT** (Week 8)
   - Execute all 13 acceptance gates (A1–A13)
   - Target: All gates PASS
   - Deliverable: Acceptance sign-off document

### Test Reporting Template

```
Test Case ID:          TC-ING-001
Date:                  2024-01-15
Tester:                John Doe
Build/Commit:          v2.1.0-alpha-g5a3f2e
Model Version:         AMC_v3.1
Dataset Version:       TestSet_v1.0
Environment:           Ubuntu 22.04, Python 3.11, PyTorch 2.0
Test Data:             VALID-IQ-01
Expected Result:       Complex array populated; metadata loaded
Actual Result:         Loaded 1048576 samples into float32 array; metadata dict with 'sample_rate': 44100
Status:                PASS
Execution Time:        0.32 seconds
Evidence:              log file: test_20240115_ing001.log
Defect ID:             (none)
Notes:                 File loaded successfully; no exceptions
```

### Test Metrics Tracking

| Metric | Target | Tracking Method |
|--------|--------|-----------------|
| Test Pass Rate (Overall) | ≥95% | Jenkins/GitHub Actions dashboard |
| Code Coverage | ≥85% | pytest-cov report |
| Regression Suite Pass Rate | 100% | Pre-commit hook + nightly CI |
| Performance Benchmarks | Per NFR | Performance regression tracker |
| Security Audit Status | Zero critical | Manual security review + tool scan |

---

## Critical Testing Rules

1. **Never evaluate the model only on training set.** Always use held-out test set for AMC accuracy reporting.
2. **Prevent source-level leakage.** Multiple windows from same recording are excluded from train/test splits.
3. **Test clean and impaired signals separately.** Failures attributable to signal quality, not algorithm.
4. **Validate DSP calculations against reference.** Deterministic test vectors used to verify FFT, modulation, demod, FEC.
5. **Treat unknown/low-confidence as valid states.** Do not auto-fail when confidence < threshold; flag and report.
6. **Test both success and deliberate failures.** FEC decoder tested with both correctable and uncorrectable error patterns.
7. **Test complete pipeline + modules independently.** Errors can cancel/amplify across stages.
8. **Record exact software/model/dataset versions.** Reproducibility depends on version control.
9. **Re-run P0 regression after every core change.** DSP preprocessing, model, label mapping, sync, demod, interleaver, FEC, output schema changes.
10. **No silent data corruption.** Every error handling path explicitly tested; no assumptions about "it will work."

---

## Summary & Implementation Roadmap

This Master Test Plan provides **end-to-end coverage** for the NTRO Signal Analysis system, spanning:
- **155+ test cases** across 14 modules
- **5 test levels** (unit, integration, system, performance, security)
- **13 acceptance gates** mapping to functional & non-functional requirements
- **20-item regression suite** for stability & reproducibility

**Recommended Implementation Sequence:**
1. Set up test infrastructure (pytest, pytest-qt, CI/CD)
2. Build test data fixtures (synthetic + real RF captures)
3. Execute Phase 1–2 (unit + integration) in parallel with development
4. Lock acceptance gates before Phase 3 (system testing)
5. Perform final Phase 4–5 (performance/security/UAT) before release

**Success Criteria:**
- All 13 acceptance gates (A1–A13) **PASS**
- All 20 regression tests (REG-001 to REG-020) **PASS**
- Code coverage ≥85%
- Zero critical security findings
- Performance benchmarks met

---

**Document Revision History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Initial | NTRO Test Team | Original master test specification |
| 2.0 | Current | Consolidated | Merged two documents; added module structure; improved clarity |

**Next Steps:** Distribute to development & QA teams; establish test environment; begin Phase 1 execution.

