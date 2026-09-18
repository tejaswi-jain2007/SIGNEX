# NTRO ID26147 — Automated Signal Analysis & Parameter Extraction System
## Consolidated Software Requirements Specification (SRS) & Product Requirements Document (PRD)

**Document Version:** 2.0 (Consolidated & Improved)  
**Date:** September 2026  
**Status:** Requirements Baseline (Engineering Phase)  
**Organization:** National Technical Research Organisation (NTRO)  
**Category:** Software / SIGINT & DSP  
**Target Deployment:** Air-gapped Offline Desktop Application (Linux/Windows)

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Purpose & Vision](#system-purpose--vision)
3. [Product Overview & Flow](#product-overview--flow)
4. [Target Users & User Stories](#target-users--user-stories)
5. [System Features (Feature Breakdown)](#system-features-feature-breakdown)
6. [Functional Requirements (FR)](#functional-requirements-fr)
7. [Non-Functional Requirements (NFR)](#non-functional-requirements-nfr)
8. [System Workflow & Processing Pipeline](#system-workflow--processing-pipeline)
9. [Input/Output Data Specifications](#inputoutput-data-specifications)
10. [User Interface Requirements](#user-interface-requirements)
11. [Critical Technical Specifications](#critical-technical-specifications)
12. [Constraints & Assumptions](#constraints--assumptions)
13. [Known Gaps & Mitigation](#known-gaps--mitigation)
14. [Acceptance Criteria](#acceptance-criteria)
15. [Out of Scope (Initial Version)](#out-of-scope-initial-version)
16. [Implementation Roadmap](#implementation-roadmap)

---

## 1. Executive Summary

This document consolidates the NTRO Problem Statement 26147 into a technical SRS/PRD for a **desktop-based automated signal analysis platform**. The system ingests raw RF recordings (.IQ complex baseband, .wav audio) from terrestrial HF/VHF/UHF sensors, processes them through an integrated DSP and ML pipeline, and outputs structured analysis including:

- **Signal parameter extraction** (sampling rate, modulation family, bandwidth, SNR)
- **Modulation classification** (FSK, PSK, QAM families)
- **Demodulation** (FSK/PSK/QAM into bitstreams)
- **De-interleaving** (block, convolutional, diagonal, pseudo-random)
- **Forward Error Correction (FEC)** (Viterbi, Reed-Solomon, Concatenated, LDPC)
- **Bitstream correlation** (header/payload detection)
- **Interactive visualization** (waterfall, constellation, spectrum)

**Key Constraints:**
- ✅ Air-gapped offline deployment (zero network requests)
- ✅ File sizes up to 2GB with streaming processing
- ✅ GUI-driven, analyst-friendly interface
- ✅ Modular, extensible architecture
- ✅ Reproducible results with full provenance tracking

---

## 2. System Purpose & Vision

### 2.1 Problem Statement
Current SIGINT signal analysis is **manual and inefficient**:
- Analysts manually script each analysis (time-consuming, error-prone)
- Unknown sensor parameters (gain, offset, sample rate) create data quality issues
- Fine-grained parameter extraction (modulation subtype, FEC scheme, interleaver depth) is missing
- No unified tool for end-to-end signal demodulation and decoding

### 2.2 Solution Vision
Build a **unified, GUI-driven desktop platform** that:
1. Accepts unknown .IQ and .wav recordings as input
2. Automatically detects signal characteristics (with manual override capability)
3. Demodulates and decodes signals through a complete DSP pipeline
4. Visualizes signal features interactively
5. Exports analysis results for downstream correlation and investigation

### 2.3 Target Impact
- **Speed:** From hours of manual analysis → minutes of automated processing
- **Quality:** Consistent, reproducible parameter extraction
- **Usability:** Analyst-friendly GUI, no scripting required
- **Extensibility:** Modular architecture for adding new modulations/codes/protocols

---

## 3. Product Overview & Flow

### 3.1 High-Level Data Flow

```
┌─────────────────┐
│  Input File     │
│  .IQ or .wav    │
└────────┬────────┘
         │
         ▼
┌──────────────────────────┐
│ 1. FILE INGESTION        │
│ - Parse format           │
│ - Extract metadata       │
│ - Normalize samples      │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 2. SIGNAL INSPECTION     │
│ - Waveform display       │
│ - FFT spectrum           │
│ - Waterfall/spectrogram  │
│ - Constellation (IQ)     │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 3. PARAMETER EXTRACTION  │
│ - Sampling frequency Fs  │
│ - Bandwidth              │
│ - Power / SNR estimate   │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 4. MODULATION ANALYSIS   │
│ - Feature-based (HOC)    │
│ - ML classifier (CNN)    │
│ - Confidence scoring     │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 5. DEMODULATION          │
│ - FSK / PSK / QAM        │
│ - Timing recovery        │
│ - Carrier sync           │
│ - Symbol/bit output      │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 6. DE-INTERLEAVING       │
│ - Block / Convolutional  │
│ - Diagonal / Pseudo-Rand │
│ - Bit reordering         │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 7. FEC DECODING          │
│ - Viterbi (Conv)         │
│ - RS (Block)             │
│ - Concatenated / LDPC    │
│ - Error correction       │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 8. CORRELATION & SYNC    │
│ - Header detection       │
│ - Payload extraction     │
│ - Frame boundaries       │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ 9. EXPORT & REPORTING    │
│ - Parameters (PDF/JSON)  │
│ - Bitstream (BIN/HEX)    │
│ - Visualizations         │
│ - Full provenance        │
└──────────────────────────┘
```

### 3.2 Pipeline Processing Stages

| Stage | Input | Processing | Output |
|-------|-------|-----------|--------|
| 1. Ingestion | `.IQ` / `.wav` file | Parse format, metadata, normalize samples | Validated signal object + metadata |
| 2. Visualization | Signal object | Compute FFT, spectrogram, constellation | Time/freq-domain plots (GUI) |
| 3. Feature extraction | Signal segment | Measure bandwidth, power, SNR, spectral peaks | Feature vector |
| 4. Modulation classification | Features + CNN | Hybrid detection (features + ML) | Modulation class + confidence |
| 5. Demodulation | Signal + modulation config | Phase/timing recovery, symbol mapping | Soft/hard bitstream |
| 6. De-interleaving | Bitstream | Apply configured inverse transform | Bit reordering |
| 7. FEC decoding | Reordered bits | Viterbi / RS / LDPC algorithms | Corrected bitstream |
| 8. Correlation | Decoded bitstream | Cross-correlate with preamble library | Header/payload boundaries |
| 9. Reporting | All results | Aggregate with provenance | Exportable report + visualizations |

---

## 4. Target Users & User Stories

### 4.1 Target User Personas

| Persona | Role | Primary Goals |
|---------|------|-------------|
| **Signal Analyst** | SIGINT analyst | Rapidly identify unknown signal characteristics without manual scripting |
| **DSP Engineer** | Signal processing specialist | Validate demodulation algorithms, test new FEC configurations |
| **Threat Analyst** | Intelligence officer | Extract actionable intelligence (headers, payloads) from intercepted signals |
| **Researcher** | Academic / industry researcher | Benchmark modulation classifiers, validate codec implementations |

### 4.2 User Stories

| ID | User Role | User Story | Acceptance Criteria |
|----|-----------|-----------|-------------------|
| US-01 | Analyst | Upload .IQ or .wav file and immediately view time-frequency spectrum | File loads <3s; waterfall + constellation update dynamically |
| US-02 | DSP Engineer | Automatically detect modulation type and sampling rate without manual trial-and-error | Modulation + Fs displayed with confidence score; >90% accuracy for SNR ≥5dB (benchmark) |
| US-03 | Threat Analyst | Apply de-interleaving and FEC to recover corrupted bitstream | Viterbi/RS/LDPC engines execute; Bit Error Rate (BER) reduction visible |
| US-04 | Intelligence Officer | Correlate bitstream against known preambles to isolate headers and payloads | Preamble matches highlighted; payload extracted to JSON/Hex |
| US-05 | Analyst | Manually override automatic detections when confidence is low | Parameter override UI provided; analysis re-runs with user-supplied values |
| US-06 | Engineer | Export complete analysis results with reproducibility metadata | Export includes input file hash, parameters, algorithm versions, timestamp |
| US-07 | Analyst | Inspect intermediate processing results (constellation, FEC syndrome) for debugging | Each stage exposes internal state (plots, bit patterns, syndrome data) |

---

## 5. System Features (Feature Breakdown)

### Feature Module 1: Universal Signal File Ingestion & Parsing

**F-01: Dual-Format Support**
- Support complex I/Q baseband data (float32, int16 binary; see § 9.1 for exact layout)
- Support real audio / digitized RF (.wav PCM 16/24/32-bit, IEEE Float32)
- Parse WAV metadata chunks (RIFF headers, sample rate, channel count, bit depth)
- Manual offset configuration for raw .IQ binary streams without headers

**F-02: Metadata Extraction**
- Extract or prompt for: sampling frequency, channel count, data type, sample width
- Detect endianness (little-endian vs. big-endian) from context or user input
- Validate file integrity before loading into memory

**F-03: Signal Normalization & Preprocessing**
- DC offset removal (subtract mean)
- IQ imbalance correction (normalize I and Q power separately)
- Automatic power normalization to [−1, +1] range or user-specified range
- Handle clipping / saturation warnings

---

### Feature Module 2: Interactive Spectral & Spatial Visualization Engine

**F-04: Dynamic 2D Waterfall/Spectrogram Plot**
- Compute power spectral density (PSD) using configurable FFT size (512–8192 points)
- Support window functions: Hann, Hamming, Blackman-Harris, Rectangular
- Real-time rendering at ≥25 FPS for responsive panning/zooming
- Color map selection (viridis, hot, jet, etc.) with dynamic range adjustment (dB scale)
- Adjustable FFT overlap (50%, 75%, 87.5%) to trade time/frequency resolution
- Zoom/pan controls for detailed inspection

**F-05: I/Q Constellation Diagram**
- Real-time 2D scatter plot: In-Phase vs. Quadrature components
- Adjustable symbol persistence (fade-out trails for motion visualization)
- Color mapping: symbol density, error vector magnitude (EVM), or time index
- Overlay of ideal constellation points (for reference)
- Symbol clustering visualization for SNR/noise assessment

**F-06: Power Spectral Density (PSD) Plot**
- Interactive line chart showing frequency spectrum (dB vs. frequency)
- Automatic peak detection and labeling (carrier, sidebands)
- 3dB bandwidth markers
- Noise floor estimation
- Interactive cursors for frequency readout

---

### Feature Module 3: Automated Parameter Extraction & Automatic Modulation Classification (AMC)

**F-07: Sampling Frequency (Fs) Estimation**
- **Method 1 — Metadata:** Extract from WAV file or user input
- **Method 2 — Spectral Analysis:** Cyclostationary feature detection (auto-correlation of squared signal)
- **Method 3 — Roll-off Detection:** Locate spectral roll-off edges (bandwidth limit)
- **Accuracy Target:** ±2% of true Fs (e.g., if Fs=1 MHz, estimate within ±20 kHz)
- **Fallback:** Report "unknown" with manual input option

**F-08: Signal Feature Extraction**
- Bandwidth estimation (99% power spectral width)
- Power level (dBm reference or normalized)
- Signal-to-Noise Ratio (SNR) estimation (via spectral noise floor)
- Spectral centroid (weighted mean frequency)
- Spectral kurtosis (indicator of modulation type)
- Higher-Order Cumulants: C₄₀, C₄₂ (features for modulation classification)

**F-09: Automatic Modulation Classification (AMC)**
- **Hybrid Approach:**
  - **Tier 1 (Rule-based, Fast):** Use HOC features + decision tree to pre-classify
  - **Tier 2 (ML, Accurate):** CNN/ResNet classifier for final modulation type
  - **Conflict Resolution:** If Tier 1 and Tier 2 disagree, report both + combined confidence

- **Supported Modulations:**
  - **FSK:** 2-FSK, 4-FSK, MSK (Minimum Shift Keying)
  - **PSK:** BPSK, QPSK, 8-PSK, OQPSK
  - **QAM:** 16-QAM, 64-QAM, 256-QAM
  - **Analog:** AM, FM (detection only; not demodulated in initial version)

- **ML Model Specifications:**
  - Architecture: ResNet-18 or CNN with batch-norm + dropout
  - Input: Spectrogramm (64×64 time-freq matrix, normalized)
  - Output: Softmax over modulation classes + confidence score
  - Model size: < 10 MB (quantized int8 or float32)
  - Inference latency: < 100 ms on CPU
  - Training dataset: Synthetic signals with SNR ∈ [−5, 20] dB
  - **Accuracy target:** ≥90% on benchmark test set with SNR ≥5 dB

**F-10: Carrier Frequency & Offset Recovery**
- Estimate carrier frequency relative to baseband center (DC)
- Detect frequency offset (Doppler, LO mismatch, etc.)
- Report as offset in Hz or % of bandwidth

---

### Feature Module 4: Digital Demodulation Engine

**F-11: Carrier & Phase Synchronization**
- **Method 1 — Costas Loop:** For BPSK, QPSK (2nd/4th-order phase detector)
- **Method 2 — Squaring Loop:** For FSK (fold and correlate with expected tones)
- **Method 3 — Decision-Directed PLL:** Use tentative symbol decisions for lock refinement
- Output: Phase-corrected complex baseband samples

**F-12: Symbol Clock Recovery**
- **Method 1 — Mueller & Müller:** Timing error detector (standard for digital comms)
- **Method 2 — Gardner:** Early-late gate timing recovery
- **Method 3 — Spectral Peak:** Find symbol rate via PSD spectral lines
- Output: Interpolated/resampled samples at exact symbol timing

**F-13: Demodulation Output Formats**
- **Soft Bits:** Log-likelihood ratios (LLRs) for FEC decoders (−127 to +127)
- **Hard Bits:** Binary bitstream (0/1)
- **Symbols:** Complex constellation points (I/Q pairs)
- Symbol confidence / EVM metrics

---

### Feature Module 5: De-Interleaving Engine

**F-14: Block De-interleaving**
- Matrix-based column-row transposition
- Configurable depth (rows M, columns N) with M×N = total bits
- Supports both row-major and column-major write/read orders
- Auto-detect: Try common depths (8, 16, 32, 64) and evaluate (limited scope)

**F-15: Convolutional De-interleaving**
- Multi-shift-register delay line array (e.g., delays [D, 2D, 3D, ...])
- Reorder dispersed bits back to sequential order
- Configurable number of taps and delay multiplier
- Common patterns: DVB-S2 (2×6), CCSDS

**F-16: Diagonal De-interleaving**
- Diagonal matrix traversal pattern (write row-major, read diagonal)
- Depth and block size configurable

**F-17: Pseudo-Random De-interleaving**
- LFSR-based or seed-driven pseudo-random permutation recovery
- Configurable LFSR polynomial (e.g., x^16 + x^5 + x^3 + 1)
- Brute-force seed search if unknown (limited to 2^16 or 2^24)

---

### Feature Module 6: Forward Error Correction (FEC) Decoding Engine

**F-18: Viterbi Decoder (Convolutional Codes)**
- Soft-decision and hard-decision variants
- Constraint lengths: K = 3, 5, 7, 9 (state machine sizes 8, 32, 128, 512)
- Code rates: 1/2, 1/3, 2/3, 3/4
- Traceback depth configurable (default: 5×K)
- Output: Decoded bitstream + syndrome/error flags

**F-19: Reed-Solomon Decoder**
- Symbol sizes: 8-bit (GF(2⁸), up to 255 symbols)
- Code configurations: (255,251), (255,239), (255,223), etc.
- Algorithms: Berlekamp-Massey syndrome computation + Chien search root finding
- Hard-decision input (byte arrays)
- Output: Corrected bitstream + error count

**F-20: Concatenated FEC Decoder**
- Outer RS + Inner Convolutional architecture
- Iterative decoding support (optional belief-propagation between stages)
- Configuration: (RS_config, Viterbi_config)

**F-21: LDPC Decoder**
- Belief Propagation / Sum-Product algorithm
- Configurable parity-check matrix H (rate depends on H density)
- Common rates: 1/2, 2/3, 3/4, 5/6
- Iteration count configurable (10–100 iterations)
- Output: Decoded bitstream + convergence status

---

### Feature Module 7: Bitstream Correlation & Payload Extraction

**F-22: Sliding-Window Correlation**
- Bitwise cross-correlation against candidate preamble/sync-word library
- Configurable Hamming distance threshold (exact match or N-bit mismatch tolerance)
- Output: Match locations, match quality metrics

**F-23: Header & Payload Dissection**
- Automatically identify packet frame boundaries
- Separate headers (preamble, sync-word, length field) from payload
- Identify trailers (CRC bytes, padding)

**F-24: Bitstream Export**
- Formats: Raw binary, Hex dump (0x prefix), ASCII (if decipherable), JSON structured
- Segment references (byte offset, bit offset)
- Confidence / quality metrics for matched regions

---

## 6. Functional Requirements (FR)

### File Ingestion (FR-01 to FR-03)

| Req ID | Priority | Requirement |
|--------|----------|------------|
| FR-01 | **HIGH** | System shall parse .IQ files (int16, float32) and .wav files (PCM 16/24/32-bit, IEEE float) up to 2 GB without memory exhaustion |
| FR-02 | **HIGH** | System shall detect and report file format, endianness, sample rate, and channel count; report clear error if file is malformed |
| FR-03 | **HIGH** | System shall normalize I/Q samples to [−1, +1] range and remove DC offset automatically |

### Signal Visualization (FR-04 to FR-10)

| Req ID | Priority | Requirement |
|--------|----------|------------|
| FR-04 | **HIGH** | System shall render time-domain waveform with zoom/pan at real-time responsiveness (≥25 FPS) |
| FR-05 | **HIGH** | System shall compute and display FFT spectrum (configurable: 512–8192 bins, multiple window functions) |
| FR-06 | **HIGH** | System shall render 2D waterfall/spectrogram with time-frequency-power color map and adjustable dynamic range |
| FR-07 | **MEDIUM** | System shall display I/Q constellation diagram with color-mapped density and optional symbol trails |
| FR-08 | **MEDIUM** | System shall estimate and display noise floor, 3dB bandwidth, and spectral peaks |
| FR-09 | **HIGH** | System shall estimate sampling frequency within ±2% error (or report "unknown") |
| FR-10 | **HIGH** | System shall compute higher-order statistics (C₄₀, C₄₂) and spectral features for classification |

### Parameter Extraction & AMC (FR-11 to FR-14)

| Req ID | Priority | Requirement |
|--------|----------|------------|
| FR-11 | **HIGH** | System shall classify modulation (FSK, PSK, QAM) with ≥90% accuracy for SNR ≥5 dB (benchmark test set) |
| FR-12 | **HIGH** | System shall report modulation classification confidence score and top-N alternatives |
| FR-13 | **MEDIUM** | System shall estimate carrier frequency offset and provide correction vector |
| FR-14 | **MEDIUM** | System shall estimate SNR from spectral noise floor; flag low-SNR signals for manual review |

### Demodulation (FR-15 to FR-19)

| Req ID | Priority | Requirement |
|--------|----------|------------|
| FR-15 | **HIGH** | System shall demodulate 2-FSK and 4-FSK signals into bitstreams |
| FR-16 | **HIGH** | System shall demodulate BPSK, QPSK, and 8-PSK signals with phase synchronization (Costas Loop or equivalent) |
| FR-17 | **HIGH** | System shall demodulate 16-QAM and 64-QAM signals with adaptive equalization (optional for initial version) |
| FR-18 | **HIGH** | System shall perform symbol timing recovery using Mueller-Müller or Gardner timing error detector |
| FR-19 | **MEDIUM** | System shall output soft-decision log-likelihood ratios (LLRs) for FEC decoders or hard bits on demand |

### De-Interleaving (FR-20 to FR-23)

| Req ID | Priority | Requirement |
|--------|----------|------------|
| FR-20 | **HIGH** | System shall execute block de-interleaving with configurable row/column depth |
| FR-21 | **HIGH** | System shall execute convolutional de-interleaving with configurable tap delays |
| FR-22 | **HIGH** | System shall execute diagonal and pseudo-random de-interleaving as specified in Feature Module 5 |
| FR-23 | **MEDIUM** | System shall attempt auto-detection of interleaver type/depth on small signal segments (limited search) |

### FEC Decoding (FR-24 to FR-27)

| Req ID | Priority | Requirement |
|--------|----------|------------|
| FR-24 | **HIGH** | System shall decode convolutional codes (K=3–9, rates 1/2–3/4) using soft-decision Viterbi algorithm |
| FR-25 | **HIGH** | System shall decode Reed-Solomon codes (8-bit symbols, configurable [n,k]) using Berlekamp-Massey algorithm |
| FR-26 | **MEDIUM** | System shall support concatenated (RS+Convolutional) decoding with multi-stage pipeline |
| FR-27 | **MEDIUM** | System shall support LDPC decoding (configurable parity-check matrix, belief-propagation iterations 10–100) |

### Bitstream Correlation (FR-28 to FR-30)

| Req ID | Priority | Requirement |
|--------|----------|------------|
| FR-28 | **HIGH** | System shall perform sliding-window cross-correlation against user-provided or library preambles |
| FR-29 | **HIGH** | System shall highlight detected header/payload boundaries and export as structured data (JSON/CSV) |
| FR-30 | **MEDIUM** | System shall compute match quality metrics (Hamming distance, correlation peak value) and report confidence |

### User Control & Workflow (FR-31 to FR-36)

| Req ID | Priority | Requirement |
|--------|----------|------------|
| FR-31 | **HIGH** | User shall be able to select time/frequency windows and re-run analysis on subsets |
| FR-32 | **HIGH** | User shall be able to override automatically detected parameters (modulation, Fs, FEC config) |
| FR-33 | **HIGH** | User shall run pipeline end-to-end or individual stages independently |
| FR-34 | **MEDIUM** | GUI shall show real-time processing status, progress bar, and stage indicators |
| FR-35 | **MEDIUM** | Processing shall be non-blocking (use background worker threads / async tasks) |
| FR-36 | **HIGH** | User shall be able to cancel long-running operations with graceful cleanup |

### Output & Reporting (FR-37 to FR-40)

| Req ID | Priority | Requirement |
|--------|----------|------------|
| FR-37 | **HIGH** | System shall generate exportable analysis report (PDF, JSON) with all extracted parameters |
| FR-38 | **HIGH** | System shall export decoded bitstream in multiple formats (binary, Hex, ASCII, JSON) |
| FR-39 | **MEDIUM** | System shall include visualizations (spectrum, waterfall, constellation) in exported reports |
| FR-40 | **HIGH** | System shall record full provenance: input file hash, parameters, algorithm versions, manual overrides, timestamp |

---

## 7. Non-Functional Requirements (NFR)

### NFR-01: Performance & Execution Speed

**Requirement:**
- Process 100 MB .IQ file through complete pipeline (FFT analysis, AMC, demodulation, FEC, correlation) in < 5 seconds on reference hardware (8-core CPU, 16 GB RAM)
- FFT computation: < 50 ms for 8192-point FFT
- AMC classification (CNN inference): < 100 ms
- Viterbi decoding: < 500 ms for 1 Mbps input

**Measurement:** Benchmarking on reference platform (Intel i5-10th gen or equiv.)

---

### NFR-02: Security & Air-Gapped Deployment

**Requirement:**
- ✅ Run 100% offline; zero external network requests
- ✅ No cloud dependencies, no API calls
- ✅ All ML models bundled locally (no remote model serving)
- ✅ File and analysis outputs stored on local encrypted filesystem (if encryption module available)
- ✅ No telemetry, analytics, or usage tracking

**Threat Model:**
- Malformed input files shall not crash the application (graceful error handling)
- Resource limits: Prevent 2GB file exhaustion via streaming reader design
- No code injection from user files (binary files treated as untrusted data)

---

### NFR-03: Usability & GUI Responsiveness

**Requirement:**
- Desktop GUI (PyQt6 / PySide6 / or equivalent) remains responsive during heavy processing
- Long-running tasks (FFT, ML inference, FEC) execute in asynchronous worker threads
- Progress indicators update at least once per 100 ms
- User can cancel operations at any stage
- Error messages are actionable (not generic system exceptions)

---

### NFR-04: Portability & Operating Environment

**Requirement:**
- Run natively on:
  - **Linux:** Ubuntu 22.04 LTS, RHEL 9 (and compatible derivatives)
  - **Windows:** Windows 10 / 11 64-bit
- All DSP libraries, GPU acceleration (CUDA/OpenCL), and GUI components packaged into:
  - Standalone executable or Python installer (.exe/.msi for Windows, .deb for Linux)
  - OR Docker container with pre-configured environment
- No external runtime installation required (Python, CUDA, etc. bundled if necessary)

---

### NFR-05: Extensibility & Modularity

**Requirement:**
- Architecture shall allow new modulation types, interleaving methods, and FEC codes to be added without rewriting core
- Plugin/module interface for DSP blocks (demodulators, decoders)
- Configuration file (JSON/YAML) for supported codebooks

---

### NFR-06: Reliability & Fault Tolerance

**Requirement:**
- Unsupported input formats → graceful error with clear message (not crash)
- Corrupted bitstream during FEC → report error count and decoder status
- Out-of-memory → fallback to streaming / windowed processing
- Incomplete file → process available data; report completion status

---

### NFR-07: Observability & Diagnostics

**Requirement:**
- System logs at stages: File load, FFT, AMC, Demod, FEC, Export
- Diagnostic output available (verbosity selectable)
- Intermediate results exportable: e.g., FFT output, constellation samples, FEC syndrome
- Reproducibility: Given same input + parameters, outputs match within floating-point tolerance

---

### NFR-08: Data Integrity

**Requirement:**
- Original samples never modified in place
- All derived data (FFT, features, constellation) recomputed or cached with invalidation logic
- Supports undo/redo for user parameter changes (if time/memory permits)

---

## 8. System Workflow & Processing Pipeline

### 8.1 Complete Processing Sequence

```
┌─────────────────────────────────────────────────────────────────┐
│                   USER INITIATES ANALYSIS                       │
└─────────────────────────────────────────────────────────────────┘
                              ▼
        ┌─────────────────────────────────────────────┐
        │ STEP 1: FILE INGESTION (Worker Thread)      │
        │  - Parse .IQ / .wav header                  │
        │  - Validate format, sample rate, channels   │
        │  - Prompt user if metadata missing          │
        │  - Load samples (streaming for >500 MB)     │
        │  - DC removal, normalization                │
        │  Status: [████░░] 20%                       │
        └─────────────────────────────────────────────┘
                              ▼
        ┌─────────────────────────────────────────────┐
        │ STEP 2: SIGNAL VISUALIZATION (Main Thread)  │
        │  - Compute FFT (configurable size)          │
        │  - Render waveform (time-domain)            │
        │  - Render spectrum (frequency-domain)       │
        │  - Compute spectrogram/waterfall (FFT loop) │
        │  - Extract I/Q components → constellation   │
        │  Status: [████████░] 40%                    │
        └─────────────────────────────────────────────┘
                              │
                ┌─────────────┴──────────────┐
                │ AUTO DETECTION TRIGGERED   │
                └─────────────┬──────────────┘
                              ▼
        ┌─────────────────────────────────────────────┐
        │ STEP 3: PARAMETER EXTRACTION (Worker)       │
        │  - Estimate Fs (metadata → cyclo. → rolloff)│
        │  - Compute C40, C42 (higher-order cumulants)│
        │  - Measure bandwidth, power, SNR            │
        │  - Compute spectral centroid, kurtosis      │
        │  - Flag low-SNR / uncertain signals         │
        │  Status: [██████████░] 50%                  │
        └─────────────────────────────────────────────┘
                              ▼
        ┌─────────────────────────────────────────────┐
        │ STEP 4: MODULATION CLASSIFICATION (Worker)  │
        │  - Tier 1 (HOC features + decision tree)    │
        │  - Tier 2 (CNN/ResNet inference)            │
        │  - Compute confidence score                 │
        │  - Report top-3 alternatives                │
        │  - Allow manual override                    │
        │  Status: [██████████████░] 60%              │
        └─────────────────────────────────────────────┘
                              │
                ┌─────────────┴──────────────────────┐
                │ USER CONFIRMS / OVERRIDES MODULATION
                └─────────────┬──────────────────────┘
                              ▼
        ┌─────────────────────────────────────────────┐
        │ STEP 5: DEMODULATION (Worker)               │
        │  - Apply carrier sync (Costas/PLL)          │
        │  - Symbol timing recovery (M&M / Gardner)   │
        │  - Map to constellation points              │
        │  - Generate soft bits (LLRs)                │
        │  - Compute EVM / quality metrics            │
        │  Status: [███████████████░] 70%             │
        └─────────────────────────────────────────────┘
                              ▼
        ┌─────────────────────────────────────────────┐
        │ STEP 6: DE-INTERLEAVING (Worker)            │
        │  - Select interleaver type (auto / user)    │
        │  - Apply inverse transform                  │
        │  - Reorder bitstream                        │
        │  Status: [████████████████░] 80%            │
        └─────────────────────────────────────────────┘
                              ▼
        ┌─────────────────────────────────────────────┐
        │ STEP 7: FEC DECODING (Worker)               │
        │  - Select decoder (Viterbi/RS/LDPC)         │
        │  - Execute decoding algorithm               │
        │  - Track BER, error flags                   │
        │  - Report convergence status                │
        │  Status: [████████████████░] 90%            │
        └─────────────────────────────────────────────┘
                              ▼
        ┌─────────────────────────────────────────────┐
        │ STEP 8: BITSTREAM CORRELATION (Worker)      │
        │  - Load preamble library                    │
        │  - Perform sliding-window correlation       │
        │  - Detect frame boundaries                  │
        │  - Extract headers / payloads               │
        │  Status: [██████████████████░] 95%          │
        └─────────────────────────────────────────────┘
                              ▼
        ┌─────────────────────────────────────────────┐
        │ STEP 9: EXPORT & REPORTING (Main Thread)    │
        │  - Aggregate all results                    │
        │  - Generate report (PDF/JSON)               │
        │  - Save visualizations (PNG)                │
        │  - Save bitstream (BIN/HEX/JSON)            │
        │  - Write provenance metadata                │
        │  Status: [████████████████████] 100%        │
        └─────────────────────────────────────────────┘
                              ▼
        ┌─────────────────────────────────────────────┐
        │ ANALYSIS COMPLETE                           │
        │ Ready for export / new analysis             │
        └─────────────────────────────────────────────┘
```

### 8.2 User Control Points

- **After Step 1:** Adjust Fs, channel count if detected incorrectly
- **After Step 2:** Select time/frequency window for re-analysis
- **After Step 4:** Accept auto-detected modulation OR override manually
- **After Step 5:** Review constellation quality; adjust timing/carrier settings if needed
- **After Step 6:** Verify de-interleaving parameters (depth, period)
- **After Step 7:** Check FEC decoder convergence; try alternative FEC if BER high
- **After Step 8:** Review frame boundaries; manually adjust sync-word if needed

---

## 9. Input/Output Data Specifications

### 9.1 Input File Formats

#### .IQ Format (Complex Baseband)

**Binary Layout (Most Common):**
```
Byte offset  Data
0–3          I_sample_0 (float32, little-endian)
4–7          Q_sample_0 (float32, little-endian)
8–11         I_sample_1 (float32, little-endian)
12–15        Q_sample_1 (float32, little-endian)
...
```

**Alternative (Integer):**
```
Byte offset  Data
0–1          I_sample_0 (int16, little-endian)
2–3          Q_sample_0 (int16, little-endian)
4–5          I_sample_1 (int16, little-endian)
6–7          Q_sample_1 (int16, little-endian)
...
```

**File Metadata (Optional):**
- `.iq` file may be accompanied by `.iq.txt` header specifying:
  ```
  SampleRate=1000000
  DataType=float32
  ChannelCount=1
  Endianness=little
  Offset=0
  ```

**Parser Requirements:**
- Support both interleaved (I,Q,I,Q,...) and separate-stream layouts
- Detect endianness (query user if ambiguous)
- Handle missing metadata gracefully

#### .WAV Format

**Standard WAV RIFF Structure:**
- RIFF header (chunk ID, size)
- fmt sub-chunk (sample rate, bit depth, channel count)
- data sub-chunk (PCM samples)

**Supported Sample Formats:**
- PCM 16-bit (signed int16)
- PCM 24-bit (signed int24)
- PCM 32-bit (signed int32)
- IEEE Float 32-bit (float32)

**Multi-channel WAV:**
- Mono (1 channel): Treat as real signal
- Stereo (2 channels): Left → I, Right → Q (treat as complex baseband)
- > 2 channels: Error (unsupported; ask user to extract I/Q pair)

---

### 9.2 Internal Data Model

| Data Object | Content | Purpose |
|-------------|---------|---------|
| `RawSignal` | I/Q samples (complex), metadata (Fs, duration, format) | Original loaded signal |
| `SignalSegment` | Time/frequency window, selected samples, source reference | Analysis on subset |
| `SignalFeatures` | Bandwidth, power, SNR, C40, C42, spectral peaks, Fs estimate | Extracted metrics |
| `ModulationResult` | Predicted class, confidence, top-N alternatives, feature evidence | Classification output |
| `DemodResult` | Symbols, soft/hard bits, EVM, carrier offset, timing offset | Demodulation state |
| `DecodingResult` | Interleaver type/params, FEC type/params, decoded bits, BER | Decoding state |
| `CorrelationResult` | Matched pattern indices, match quality, frame boundaries | Correlation results |
| `AnalysisReport` | Input metadata, all results, algorithm versions, provenance, timestamp | Final export |

---

### 9.3 Output Formats

#### Report Export (PDF / JSON)

**JSON Structure Example:**
```json
{
  "analysis_metadata": {
    "timestamp": "2026-09-18T14:35:22Z",
    "input_file": "signal_001.iq",
    "input_hash": "sha256:abc123...",
    "segment": { "start_sample": 0, "end_sample": 1000000 }
  },
  "detected_parameters": {
    "sampling_frequency_hz": 1000000,
    "bandwidth_hz": 50000,
    "power_dbm": -20,
    "snr_estimate_db": 8.5
  },
  "modulation": {
    "class": "QPSK",
    "confidence": 0.94,
    "alternatives": ["PSK", "8PSK"]
  },
  "demodulation": {
    "status": "SUCCESS",
    "evm_percent": 5.2,
    "symbol_rate_baud": 100000
  },
  "fec_decoding": {
    "method": "Viterbi",
    "code_rate": "1/2",
    "constraint_length": 7,
    "ber": 0.0001,
    "status": "CONVERGED"
  },
  "correlation": {
    "preamble_matches": [
      { "offset_bytes": 128, "confidence": 0.99 },
      { "offset_bytes": 2048, "confidence": 0.95 }
    ],
    "payload_start_bytes": [256, 2176]
  },
  "exported_artifacts": {
    "bitstream": "signal_001_decoded.bin",
    "spectrum": "signal_001_spectrum.png",
    "waterfall": "signal_001_waterfall.png",
    "constellation": "signal_001_constellation.png"
  }
}
```

#### Bitstream Export (Binary / Hex / JSON)

**Binary Format:**
```
Raw bytes: 0x7F 0xA5 0xC3 0x12 ...
```

**Hex Format:**
```
Offset (byte)  Hex Data
0x00           7F A5 C3 12 45 67 89 AB
0x08           CD EF 01 23 45 67 89 AB
...
```

**JSON Format:**
```json
{
  "bitstream": {
    "length_bits": 1048576,
    "data_hex": "7FA5C312456789AB...",
    "segments": [
      { "label": "header", "start_bit": 0, "end_bit": 16, "hex": "7FA5" },
      { "label": "payload", "start_bit": 16, "end_bit": 1048576, "hex": "C312..." }
    ]
  }
}
```

---

## 10. User Interface Requirements

### 10.1 Main GUI Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  Signal Analysis Tool — [Open File] [Settings] [Help]       [X] [−] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐   │
│  │  FILE & SESSION      │  │  SIGNAL VISUALIZATION            │   │
│  │                      │  │  ┌────────────────────────────┐  │   │
│  │ [Open] [Recent v]    │  │  │ Waterfall/Spectrogram      │  │   │
│  │ signal_001.iq        │  │  │ [Full] [Zoom] [Pan]        │  │   │
│  │ Format: IQ (float32) │  │  │ FFT Size: [512 ▼]          │  │   │
│  │ Sample Rate: 1 MHz   │  │  │ Window: [Hann ▼]           │  │   │
│  │ Duration: 10 sec     │  │  │                            │  │   │
│  │ Channels: 1          │  │  │ [Waterfall plot]           │  │   │
│  │                      │  │  │                            │  │   │
│  │ [Segment: 0–100k]    │  │  └────────────────────────────┘  │   │
│  │                      │  │  [Spectrum] [Constellation]      │   │
│  └──────────────────────┘  └──────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  PARAMETER EXTRACTION & DETECTION (Auto / Manual Override)   │  │
│  │  Fs:     [1000000 Hz] (from metadata)                        │  │
│  │  Bandwidth: [50 kHz]  (estimated)                            │  │
│  │  Power:  [−20 dBm]    SNR: [8.5 dB]                          │  │
│  │                                                              │  │
│  │  Modulation:  [QPSK ▼] (confidence: 94%) [Top 3]            │  │
│  │  Carrier Offset: [123.4 Hz]  [FEC Type: Viterbi ▼]          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  PROCESSING PIPELINE STATUS                                  │  │
│  │  [✓] File Ingestion    [✓] Visualization  [✓] Parameters     │  │
│  │  [✓] Modulation        [↻] Demodulation (50%)                │  │
│  │  [░] De-interleaving   [░] FEC Decoding   [░] Correlation    │  │
│  │  Progress: [███████░░░░░░░░░░░░░░░░░░░░░░] 35%               │  │
│  │  [Cancel]                                                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  DEMODULATION & DECODING CONFIGURATION                       │  │
│  │  ┌─ Demodulation Settings ─┐  ┌─ De-interleaving ─┐         │  │
│  │  │ Modulation: QPSK         │  │ Type: Block       │         │  │
│  │  │ Symbol Rate: [100000 ▼]  │  │ Depth: [32 x 32]  │         │  │
│  │  │ Carrier Sync: Costas PLL │  │ [Auto-detect]     │         │  │
│  │  │ [Apply Demodulation]     │  │ [Apply]           │         │  │
│  │  └─────────────────────────┘  └──────────────────┘         │  │
│  │                                                              │  │
│  │  ┌─ FEC Decoding ─────────────┐  ┌─ Bitstream View ─────┐   │  │
│  │  │ Method: Viterbi            │  │ [Hex] [Binary] [ASCII]│   │  │
│  │  │ Code Rate: 1/2, K=7        │  │ 7FA5C3124567...      │   │  │
│  │  │ Soft Decision: ON          │  │ Offset [0] Length: ▼ │   │  │
│  │  │ [Apply FEC Decode]         │  │ [Search] [Export]    │   │  │
│  │  └────────────────────────────┘  └──────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  DIAGNOSTIC OUTPUT                                           │  │
│  │ [Logs] [Events] [FEC Syndrome] [Correlation Results]          │  │
│  │ INFO: Detected modulation QPSK with 94% confidence           │  │
│  │ INFO: Viterbi decoder converged; BER = 1e-4                  │  │
│  │ INFO: Preamble match at byte 128 (confidence 99%)            │  │
│  │                                                              │  │
│  │ [Export Report] [Save Bitstream] [Copy to Clipboard]         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 10.2 Key GUI Panels

| Panel | Purpose | Key Controls |
|-------|---------|--------------|
| **File & Session** | Input file management | Open, recent files, metadata display, segment selection |
| **Waterfall** | Time-frequency visualization | FFT size, window function, zoom, pan, colormap |
| **Spectrum** | Frequency-domain view | Peak markers, 3dB BW, noise floor, zoom |
| **Constellation** | I/Q scatter plot | Color map (density/EVM/time), symbol trail, zoom |
| **Parameters** | Extracted signal characteristics | Fs, BW, power, SNR (read-only or manual override) |
| **Modulation** | Automatic detection result | Class, confidence, top-N alternatives, manual override |
| **Demodulation** | Demod configuration | Symbol rate, timing/carrier methods, demod button |
| **De-interleaving** | Interleaver config | Type, depth, parameters, auto-detect checkbox |
| **FEC Decoding** | Decoder selection & config | Codec type, rate, constraint length, soft/hard, decode button |
| **Bitstream View** | Output bitstream inspection | Hex/binary/ASCII modes, search, export |
| **Diagnostics** | Processing logs & errors | Multi-level logging, event history, warning/error highlights |

### 10.3 Usability Principles

1. **Auto + Manual:** Show automatic detections alongside manual override paths; analyst not forced to trust uncertain results
2. **Confidence Indicators:** Display confidence scores, evidence, "insufficient data" warnings
3. **Segment Inspection:** Allow user to view signal segment used for each major inference
4. **Plot Synchronization:** Selecting region in one view updates related views (e.g., waterfall zoom ↔ spectrum zoom)
5. **Reversibility:** User can undo manual overrides and re-run auto-detection
6. **Non-blocking UI:** Progress bars, cancellation buttons, worker thread status feedback
7. **Helpful Errors:** When processing fails, show actionable next steps, not raw stack traces

---

## 11. Critical Technical Specifications

### 11.1 Modulation Classification Accuracy Baseline

**Benchmark Test Set:**
- Synthetic signals: BPSK, QPSK, 8-PSK, 2-FSK, 4-FSK, 16-QAM, 64-QAM
- SNR levels: −5, 0, 3, 5, 10, 15, 20 dB
- Symbol rate: 100 kBaud
- Channel effects: AWGN only (Rayleigh fading in extended version)

**Target Accuracy:**
- **SNR ≥ 5 dB:** ≥90% (confusion mainly between similar classes, e.g., QPSK vs. 8-PSK)
- **SNR 0–5 dB:** ≥70% (allows for manual refinement)
- **SNR < 0 dB:** No accuracy guarantee; system flags as "low confidence"

---

### 11.2 Viterbi Decoder Performance

**Supported Configurations:**

| Constraint Length | State Count | Code Rate | Typical Use |
|-------------------|-------------|-----------|------------|
| K=3 | 8 | 1/2 | Legacy/simple systems |
| K=5 | 32 | 1/2, 1/3 | DVB-S, CCSDS |
| K=7 | 128 | 1/2, 2/3, 3/4 | Standards (WiFi, DVB-T) |
| K=9 | 512 | 1/2, 1/3 | High-protection systems |

**Performance:**
- Latency: < 100 ms for 100 kbps input (K=7, rate 1/2)
- Memory: < 1 MB lookup tables + state buffers
- BER reduction: Typically 4–6 dB at 10⁻⁶ BER threshold (SNR-dependent)

---

### 11.3 FFT & Spectrogram Parameters

| Parameter | Default | Range | Notes |
|-----------|---------|-------|-------|
| FFT Size (points) | 2048 | 256–8192 | Frequency resolution ∝ Fs/N |
| Window Function | Hann | Hann, Hamming, Blackman-Harris, Rect | Leakage vs. resolution trade-off |
| FFT Overlap | 50% | 25%, 50%, 75%, 87.5% | Time resolution ∝ overlap |
| Time Window (sec) | 0.1 | 0.01–1.0 (user-selectable) | Balance precision vs. stationarity |
| Dynamic Range (dB) | 60 | 20–100 | Color scale stretch |

---

### 11.4 Constellation Timing Recovery

**Mueller-Müller Detector:**
- Timing error: $e[n] = (a[n] y_I[n] - a[n-1] y_I[n-1]) \times y_Q[n]$
- Proportional-Integral loop filter
- Loop bandwidth: 1%–5% of symbol rate
- Convergence time: ~100 symbols

**Gardner Detector (Alternative):**
- Simpler, lower complexity
- Works for pulse shapes with zero-crossing at ±0.5T_s
- Loop bandwidth: 1%–10% of symbol rate

---

### 11.5 De-interleaving Search Strategy (Auto-Detection)

**For Block Interleaving:**
- Common depths: 8, 16, 32, 64, 128
- Test each depth on 10,000-bit segment
- Metrics: BER reduction post-decode, entropy change
- Accept first configuration that yields significant improvement

**For Convolutional Interleaving:**
- Common tap counts: 4, 8, 16
- Common delay multipliers: 1×, 2×, 4×
- Combinatorial search: max 256 configurations
- Time limit: 5 seconds (hardcoded abort)

**For Pseudo-Random Interleaving:**
- LFSR polynomial: x¹⁶ + x⁵ + x³ + 1 (common)
- Seed space: 2¹⁶ = 65,536
- Brute-force search with BER metric
- Time limit: 10 seconds

---

## 12. Constraints & Assumptions

### 12.1 Input/Output Constraints

| Constraint | Impact | Workaround |
|-----------|--------|-----------|
| Max file size: 2 GB | RAM budgets for large captures | Streaming reader: process 100 MB chunks |
| .IQ format not standardized | Parser ambiguity | Support 3–4 common layouts; ask user if mismatch |
| .wav metadata may be incorrect | Unreliable sample rate | Provide manual Fs override; validate with cyclostationary |
| Missing frame synchronization | Auto-detect fails for unknown protocols | Require user to specify preamble or accept manual extraction |

### 12.2 Processing Constraints

| Constraint | Rationale | Mitigation |
|-----------|-----------|-----------|
| Offline-only (no cloud ML) | Air-gap requirement | Bundle lightweight models (<10 MB) |
| Single-file input | Simplifies UI/UX | Support file queuing (future enhancement) |
| Real-time SDR not in scope | Time/complexity limits | Focus on recorded files; SDR integration as extension |
| Modulation auto-detect uncertain for novel modulations | Limited training data diversity | Provide manual modulation override; allow multi-selection |

### 12.3 Deployment Assumptions

| Assumption | Verification | Impact |
|-----------|--------------|--------|
| Python 3.10+ available (or bundled) | Check during install | Pre-package runtime if necessary |
| 16 GB RAM available | Prompt if insufficient | Implement streaming for >2 GB files |
| GPU support optional (CUDA 11.8+ or OpenCL) | Graceful fallback to CPU | Auto-detect; log GPU availability |
| Linux/Windows 64-bit target | Document OS requirements | Test on Ubuntu 22.04 LTS, Windows 11 |
| Air-gapped network (no internet) | Security requirement | No remote model serving; all models local |

---

## 13. Known Gaps & Mitigation

### Gap 1: IQ File Format Ambiguity

**Issue:** No standard .IQ file layout defined  
**Mitigation:**
- Support 3 common layouts: float32 interleaved, int16 interleaved, separate I/Q files
- Auto-detect by trying multiple parsers; report if ambiguous
- Provide .iq.txt sidecar format documentation
- Allow user manual format specification in UI

**Acceptance:** User can successfully load 4 different .IQ format variants

---

### Gap 2: Interleaving Parameter Auto-Detection Black Box

**Issue:** System claims to "detect" interleaving but algorithm unspecified  
**Mitigation:**
- Formalize parameter search algorithm (see § 11.5)
- Implement depth search (limited to common values)
- Use BER metric to validate hypotheses
- Time-limit search (abort after 10 sec)
- Fall back to manual input if search inconclusive

**Acceptance:** Auto-detect succeeds on 80% of benchmark interleaved signals; user can manually override

---

### Gap 3: ML Model Specifications Vague

**Issue:** "CNN/ResNet" architecture, training data, accuracy undefined  
**Mitigation:**
- Design ResNet-18 for modulation classification (50 conv layers)
- Train on synthetic signals (AWGN, 7 modulation classes)
- Quantize to int8 for offline deployment
- Document training dataset, hyperparameters, expected accuracy
- Validate accuracy on held-out test set

**Acceptance:** Model achieves ≥90% accuracy on benchmark SNR ≥5 dB

---

### Gap 4: FEC Codebook Incomplete

**Issue:** Constraint lengths (K=3–9) and rates not all realistic  
**Mitigation:**
- Prioritize common standards: K=7 (rate 1/2, 2/3, 3/4)
- Add K=5 for legacy systems
- K=9 optional (performance-critical systems)
- Implement RS (255,251), (255,239), (255,223) common configurations
- LDPC support optional for initial version

**Acceptance:** Viterbi K={5,7}, RS (255,251)/(255,239) fully implemented and tested

---

### Gap 5: No Test Vector / Benchmark Dataset

**Issue:** Acceptance criteria lack reference signals  
**Mitigation:**
- Generate synthetic signal library (100 test cases)
  - 10 signals per modulation × 7 modulation classes
  - SNR levels: 0, 5, 10, 15, 20 dB
  - Known bitstream output for validation
- Document test harness (pytest, synthetic signal generation code)
- Provide pre-computed reference results (BER curves, detection accuracy)

**Acceptance:** Test suite with 100+ synthetic signals + known outputs

---

## 14. Acceptance Criteria

### Functional Acceptance (End-to-End)

| AC ID | Criterion |
|-------|-----------|
| AC-F01 | User can open a valid .IQ file and view time-domain waveform, FFT spectrum, and waterfall within 3 seconds |
| AC-F02 | User can open a valid .wav file and view time-domain waveform, FFT spectrum, and waterfall within 3 seconds |
| AC-F03 | System displays extracted sampling frequency (from metadata or estimate) and indicates confidence ("from metadata" vs. "estimated") |
| AC-F04 | System auto-detects modulation (FSK, PSK, QAM) on benchmark signals with ≥90% accuracy for SNR ≥5 dB |
| AC-F05 | User can manually override auto-detected modulation and re-run analysis |
| AC-F06 | System demodulates BPSK/QPSK/8-PSK signals into soft bitstreams (LLRs); constellation plot shows expected clustering |
| AC-F07 | System demodulates 2-FSK/4-FSK signals into bitstreams; modulation indicator shows detected tones |
| AC-F08 | System demodulates 16-QAM/64-QAM signals into bitstreams; constellation shows expected grid pattern |
| AC-F09 | At least one successful demo: block de-interleaving of pre-interleaved bitstream yields correct output |
| AC-F10 | At least one successful demo: convolutional de-interleaving yields correct output |
| AC-F11 | At least one successful demo: diagonal de-interleaving yields correct output |
| AC-F12 | At least one successful demo: pseudo-random de-interleaving (with known seed) yields correct output |
| AC-F13 | Viterbi decoder (K=7, rate 1/2) successfully decodes test bitstream with measurable BER reduction |
| AC-F14 | Reed-Solomon decoder (255,251) successfully decodes test bitstream; corrects >90% of single-byte errors |
| AC-F15 | Concatenated decoder (RS outer + Viterbi inner) successfully decodes interleaved + FEC test bitstream |
| AC-F16 | LDPC decoder (if implemented) successfully decodes test bitstream with measurable BER reduction |
| AC-F17 | System performs bitstream correlation: identifies pre-defined preamble pattern and highlights header/payload boundaries |
| AC-F18 | System exports analysis results in JSON format including parameters, modulation, FEC status, decoded bitstream |
| AC-F19 | System exports bitstream in binary, hex, and ASCII formats |
| AC-F20 | GUI remains responsive during processing; progress bar updates; user can cancel long operations |

### Non-Functional Acceptance

| AC ID | Criterion |
|-------|-----------|
| AC-NF01 | Application launches on Windows 10/11 and Ubuntu 22.04 LTS without errors |
| AC-NF02 | Processes 100 MB .IQ file end-to-end in < 5 seconds (measured on reference hardware) |
| AC-NF03 | FFT computation (<50 ms for 8192-point FFT); CNN inference (<100 ms) |
| AC-NF04 | Malformed .IQ file → graceful error message (not crash); user can re-select file |
| AC-NF05 | Unsupported modulation → system indicates "unknown" and allows manual input |
| AC-NF06 | GUI does not freeze during FFT or FEC decoding; background workers used |
| AC-NF07 | System makes zero network requests (verified via network monitor) |
| AC-NF08 | Reproducibility: running same analysis twice on same file yields identical bitstream output (within floating-point tolerance) |

---

## 15. Out of Scope (Initial Version)

- ❌ Real-time RF capture from arbitrary SDR devices (USB-attached or network-based)
- ❌ Live RF demodulation and decoding (focus: recorded files)
- ❌ Encryption/cryptanalysis of protected communications
- ❌ Multi-file batch processing (single-file focus initially)
- ❌ Semantic interpretation of decoded payload (e.g., automatic protocol parsing beyond frame boundaries)
- ❌ Advanced equalization for severe multipath/fading channels
- ❌ Spectral coexistence analysis or interference mitigation
- ❌ Proprietary/undocumented protocol support (generic framework only)
- ❌ Cloud-based model serving or remote APIs
- ❌ Mobile app or web-based UI (desktop only)

---

## 16. Implementation Roadmap

### Phase 1: Core Infrastructure (Weeks 1–4)

**Deliverables:**
- ✅ File ingestion module (.IQ/.wav parsing, validation)
- ✅ Signal visualization (FFT, waterfall, constellation plots using Matplotlib/PyOpenGL)
- ✅ GUI skeleton (PyQt6 with main panels)
- ✅ Test file collection (synthetic signals, known modulations/SNR levels)

**Success:** User can load .IQ/.wav file and view spectrum/waterfall without crashes

---

### Phase 2: DSP & Parameter Extraction (Weeks 5–8)

**Deliverables:**
- ✅ Sampling frequency estimation (metadata + cyclostationary detection)
- ✅ Feature extraction (bandwidth, power, SNR, C40/C42 computation)
- ✅ Modulation classifier (feature-based decision tree)
- ✅ Integration with Phase 1 UI

**Success:** System detects modulation type with >80% accuracy on benchmark SNR ≥5 dB

---

### Phase 3: Demodulation (Weeks 9–12)

**Deliverables:**
- ✅ Costas Loop / PLL for phase synchronization
- ✅ Mueller-Müller timing recovery
- ✅ FSK demodulator (tone-based)
- ✅ PSK demodulator (BPSK, QPSK, 8-PSK)
- ✅ QAM demodulator (16-QAM, 64-QAM)
- ✅ Constellation plot integration

**Success:** Demodulates all supported modulations; constellation plot shows correct symbol clustering

---

### Phase 4: De-interleaving & FEC (Weeks 13–20)

**Deliverables:**
- ✅ Block de-interleaving module
- ✅ Convolutional de-interleaving module
- ✅ Diagonal de-interleaving module
- ✅ Pseudo-random de-interleaving module
- ✅ Viterbi decoder (K=5,7; rates 1/2, 2/3, 3/4)
- ✅ Reed-Solomon decoder (255,251)/(255,239)
- ✅ Concatenated (RS + Viterbi) decoder
- ✅ Integration with Phase 3 UI

**Success:** End-to-end pipeline processes interleaved+FEC-encoded test bitstream; BER reduction visible

---

### Phase 5: Correlation & Export (Weeks 21–24)

**Deliverables:**
- ✅ Bitstream correlation engine (sliding window, Hamming distance)
- ✅ Preamble library (50+ common sync-words)
- ✅ JSON/PDF report generation
- ✅ Bitstream export (binary, hex, ASCII)
- ✅ Provenance tracking (file hash, parameters, versions)

**Success:** Extracts header/payload from synthetic test bitstream; exports reproducible report

---

### Phase 6: ML Integration & Optimization (Weeks 25–28)

**Deliverables:**
- ✅ CNN/ResNet training pipeline (synthetic dataset)
- ✅ Model quantization (int8 for offline deployment)
- ✅ Hybrid classifier (feature-based + ML ensemble)
- ✅ Performance benchmarking & tuning
- ✅ GPU acceleration (CUDA optional)

**Success:** ML classifier achieves ≥90% accuracy; inference <100 ms on CPU

---

### Phase 7: Testing, Hardening & Deployment (Weeks 29–32)

**Deliverables:**
- ✅ Comprehensive test suite (100+ synthetic signals + real-world samples)
- ✅ Stress testing (2 GB files, resource limits)
- ✅ Security audit (no network requests, sandboxing)
- ✅ Installation package (Windows .exe, Linux .deb)
- ✅ User documentation & tutorial
- ✅ Acceptance testing vs. AC criteria

**Success:** Passes all AC criteria; deployable offline on Windows/Linux

---

## Appendix: Consolidated Requirements Traceability

### Problem Statement → Requirements Mapping

| PS Feature | Mapped FR | Mapped NFR | Acceptance Criteria |
|-----------|-----------|-----------|-------------------|
| Input: .IQ / .wav | FR-01 to FR-03 | NFR-02 (offline) | AC-F01, AC-F02 |
| Identify Fs | FR-09, FR-07 | — | AC-F03 |
| Identify modulation | FR-11, FR-12 | — | AC-F04 |
| Identify FEC | FR-24 to FR-27 | — | (FEC detected manually) |
| Identify interleaving | FR-20 to FR-23 | — | (Interleaver detected manually) |
| Demodulate FSK/PSK/QAM | FR-15 to FR-17 | — | AC-F06 to AC-F08 |
| De-interleave | FR-20 to FR-23 | — | AC-F09 to AC-F12 |
| FEC decode | FR-24 to FR-27 | — | AC-F13 to AC-F16 |
| Bitstream correlation | FR-28 to FR-30 | — | AC-F17 |
| GUI & visibility | FR-04 to FR-08, UI reqs | NFR-03 | AC-F01, AC-NF06 |
| Waterfall & spectral | FR-04, FR-06 | — | AC-F01, AC-F02 |
| Export / reporting | FR-37 to FR-40 | — | AC-F18, AC-F19 |

---

**Document Status:** Ready for Engineering Baseline Review  
**Next Steps:** Team validation of technical specs, benchmarking setup, resource allocation

