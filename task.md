# Project Task Tracking: NTRO Signal Analysis System (SIH ID 26147)

## Status Overview
- **Status**: In Progress
- **Current Sprint**: Setup & Phase 1 Core Ingestion/Preprocessing
- **Hardware Profile**: NVIDIA GeForce RTX 3050 Laptop GPU (4GB VRAM, CUDA 13.3)
- **Deployment Mode**: Air-Gapped Offline Desktop System

---

## Task Checklist

### [x] 1. Project Setup & Excel Tracking System
- [x] 1.1 Generate comprehensive `NTRO_ID26147_Project_Tracker.xlsx`
  - [x] Dashboard & Subsystem Matrix
  - [x] Module Work Breakdown (Working vs Not Working tracking)
  - [x] Model Training Tracker (GPU configuration, runs, hyperparams, class metrics)
  - [x] API & Interface Directory
  - [x] Improvements & Optimization Log
  - [x] Project Changelog
- [x] 1.2 Generate comprehensive `NTRO_ID26147_Test_Case_Tracker.xlsx`
  - [x] Master Test Plan (All 147 module test cases: ING, PRE, VIS, PAR, AMC, DEM, INT, FEC, COR, GUI, PER, SEC, STORE, E2E)
  - [x] Regression Suite (All 20 regression test cases: REG-001 to REG-020)
  - [x] Acceptance Gates (All 13 gates: AG-01 to AG-13)
  - [x] Requirements Traceability Matrix (RTM)
  - [x] Bug & Issue Tracking tab
- [x] 1.3 Initialize package structure `ntro_sigint/` per System Design § 4.2
- [x] 1.4 Setup dependencies in `requirements.txt` (numpy, scipy, openpyxl, torch, pytest, matplotlib, h5py)

---

### [x] 2. Phase 1: Ingestion & Signal Preprocessing
- [x] 2.1 File Ingestion (`ntro_sigint/core/ingestion.py`)
  - [x] Float32, Int16, Int8 raw .iq parsing with normalization
  - [x] Mono/Stereo WAV parsing via RIFF header extraction
  - [x] Memory-mapped processing (`np.memmap`) for large files (up to 2 GB)
  - [x] Sidecar JSON metadata parser and default fallback
  - [x] Corrupt file, empty file, odd sample count, and truncated payload error handling
- [x] 2.2 Signal Preprocessing (`ntro_sigint/core/preprocessor.py`)
  - [x] DC offset removal (mean subtraction)
  - [x] Gram-Schmidt IQ imbalance correction (amplitude and phase orthogonalization)
  - [x] Polyphase rational resampling
  - [x] Clipping / saturation detection & warning threshold
  - [x] Unit power normalization
  - [x] Windowing support (Hann, Hamming, Blackman)
- [x] 2.3 Automated Test Suite for Ingestion & Preprocessing
  - [x] Execute & verify TC-ING-001 to TC-ING-015 (15/15 passed)
  - [x] Execute & verify TC-PRE-001 to TC-PRE-008 (8/8 passed)
  - [x] Regression tests REG-001, REG-002, REG-016 (3/3 passed)
  - [x] Acceptance Gate A1 cleared
  - [x] Update Excel Test Tracker and Project Tracker with actual results

---

### [x] 3. Phase 2: Signal Parameter Extraction & DSP Foundations
- [x] 3.1 Parameter Extractor (`ntro_sigint/dsp/parameter_extractor.py`)
  - [x] Sampling rate $F_s$ estimation via autocorrelation
  - [x] Symbol rate detection via transition energy and cyclostationary processing
  - [x] 3-dB and occupied bandwidth measurement (99% power)
  - [x] Center frequency and carrier frequency offset estimation
  - [x] SNR estimation (cumulant and noise floor estimation)
  - [x] PAPR and crest factor calculation
  - [x] Time-domain envelope analysis & burst duty cycle
  - [x] Spectral flatness (Wiener entropy)
- [x] 3.2 Automated Tests for TC-PAR-001 to TC-PAR-010 (10/10 passed)
- [x] Regression tests REG-005, REG-006 passed; Acceptance Gate A3 cleared
- [x] 3.3 Update Excel Trackers with verified results

---

### [ ] 4. Phase 3: Automatic Modulation Classification (AMC) & GPU Training
- [ ] 4.1 Dataset Pipeline & Synthetic Signal Generator (`ntro_sigint/ml/dataset.py`)
  - [ ] Synthetic signal generation for BPSK, QPSK, 8-PSK, 16-QAM, 64-QAM, 2-FSK, 4-FSK, AM, FM
  - [ ] AWGN, carrier frequency offset, and phase noise channel modeling
  - [ ] RadioML 2016/2018 compatible HDF5 data loader
- [ ] 4.2 Deep Learning AMC Architecture (`ntro_sigint/ml/amc_classifier.py`)
  - [ ] ResNet-18 1D CNN for raw I/Q samples (shape: `[Batch, 2, 1024]`)
  - [ ] Cumulant-based classical ML fallback (C42, C40, C63, etc.)
  - [ ] Out-of-Distribution (OOD) & low confidence detector (< 0.70 threshold)
- [ ] 4.3 Model Training on Internal GPU (NVIDIA RTX 3050 Laptop)
  - [ ] PyTorch training script with CUDA acceleration and mixed precision (FP16)
  - [ ] Model weights checkpointing (`models/amc_resnet18.pt`)
  - [ ] Per-class confusion matrix, precision/recall/F1, and accuracy vs SNR curve
- [ ] 4.4 Automated Tests for TC-AMC-001 to TC-AMC-012
- [ ] 4.5 Update Excel Trackers with model training runs and test outcomes

---

### [ ] 5. Phase 4: Demodulation, De-interleaving & FEC Decoding
- [ ] 5.1 Demodulator Suite (`ntro_sigint/dsp/demodulator.py`)
  - [ ] Carrier recovery (Costas loop) and symbol timing recovery (Gardner)
  - [ ] PSK Demodulators: BPSK, QPSK, 8-PSK
  - [ ] QAM Demodulators: 16-QAM, 64-QAM with Gray de-mapping
  - [ ] FSK Demodulator: 2-FSK non-coherent/coherent detector
  - [ ] Soft-decision symbol metric generation (LLR)
- [ ] 5.2 De-interleaver Suite (`ntro_sigint/decoding/interleaver.py`)
  - [ ] Block de-interleaver ($M \times N$)
  - [ ] Convolutional de-interleaver (Forney/Ramsey)
  - [ ] Diagonal and Helical de-interleaver
  - [ ] Pseudo-Random LFSR de-interleaver
- [ ] 5.3 FEC Decoder Suite (`ntro_sigint/decoding/fec.py`)
  - [ ] Hard/Soft Viterbi Decoder (rate 1/2, $K=7$ polynomials 171/133, and configurable)
  - [ ] Reed-Solomon Decoder over $\text{GF}(2^8)$ (e.g. RS(255, 223), RS(204, 188))
  - [ ] LDPC Belief Propagation Decoder
  - [ ] Concatenated RS + Viterbi Decoder
- [ ] 5.4 Automated Tests for TC-DEM-001 to 012, TC-INT-001 to 007, TC-FEC-001 to 010
- [ ] 5.5 Update Excel Trackers

---

### [ ] 6. Phase 5: Bitstream Correlation, Frame Extraction & Export
- [ ] 6.1 Bitstream Correlator (`ntro_sigint/correlation/correlator.py`)
  - [ ] Synchronization search (Barker 7/11/13, Gold codes, custom preambles)
  - [ ] Bit-slip / phase ambiguity tolerance
  - [ ] Packet header parsing (length, type, CRC check)
  - [ ] Payload extractor & descrambler
- [ ] 6.2 Storage, Reporting & Versioning (`ntro_sigint/core/exporter.py`)
  - [ ] Structured JSON export (extracted parameters, modulation, confidence, metadata)
  - [ ] Binary payload extraction (.bin, .hex)
  - [ ] Executive PDF report generation with embedded spectral & constellation figures
- [ ] 6.3 Security & Air-Gap Compliance (`ntro_sigint/core/security.py`)
  - [ ] Socket blocking & network isolation enforcement
  - [ ] Safe path validation (prevent path traversal / directory escaping)
  - [ ] Local audit logging and data retention policy
- [ ] 6.4 Automated Tests for TC-COR, TC-STORE, TC-SEC
- [ ] 6.5 Update Excel Trackers

---

### [ ] 7. Phase 6: Desktop GUI (PyQt6) & High-Performance Visualization
- [ ] 7.1 DSP Visualization Engine (`ntro_sigint/dsp/visualization.py`)
  - [ ] FFT Spectrogram & Waterfall computation (pyqtgraph integration)
  - [ ] Constellation diagrams with density heatmaps
  - [ ] Power Spectral Density (Welch method) and Phase Trajectory
- [ ] 7.2 PyQt6 Application Framework (`ntro_sigint/gui/`)
  - [ ] Main window with dark-themed responsive layout
  - [ ] Non-blocking pipeline execution via QThread workers
  - [ ] Interactive zoom/pan, cursor markers, frequency measurement
  - [ ] Summary dashboard, parameter cards, classification badges, payload hex viewer
- [ ] 7.3 Automated Tests for TC-VIS-001 to 010 and TC-GUI-001 to 015
- [ ] 7.4 Update Excel Trackers

---

### [ ] 8. Phase 7: End-to-End Testing, Acceptance Gates & Final Delivery
- [ ] 8.1 Execute End-to-End integration suite (TC-E2E-001 to TC-E2E-010)
- [ ] 8.2 Execute Performance & Stress testing (TC-PER-001 to TC-PER-010)
- [ ] 8.3 Execute 20 Regression Tests (REG-001 to REG-020)
- [ ] 8.4 Evaluate and certify 13 Acceptance Gates (AG-01 to AG-13)
- [ ] 8.5 Finalize and deliver both Excel Tracking Workbooks with 100% verified data
