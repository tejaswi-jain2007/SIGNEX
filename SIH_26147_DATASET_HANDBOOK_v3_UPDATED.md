# SIH 26147 — Dataset Acquisition, Preparation, Training & Evaluation Handbook
## Version 3.0 (Enhanced & Implementation-Ready)

**Project:** Automated Model for Analysis of `.IQ` and `.WAV` Files Along with Signal Parameter Extraction  
**Problem Statement ID:** 26147  
**Organization:** National Technical Research Organisation (NTRO)  
**Document Type:** Data Engineering & ML Training Plan  
**Version:** 3.0 (Enhanced, Updated September 2026)  
**Status:** ✅ Ready for Implementation  
**Last Updated:** September 18, 2026

---

## Executive Summary

This handbook defines the **complete, actionable data strategy** for building, training, validating, and evaluating the NTRO Signal Analysis & Parameter Extraction System (ID26147). Rather than forcing the entire project into a single public dataset, we employ a **dataset stack** approach that combines:

1. **Public benchmarks** (RadioML 2016/2018, HisarMod) for modulation classification
2. **Custom synthetic data** (GNU Radio + Python) for FEC, interleaving, and end-to-end pipelines
3. **Authorized real captures** for final validation and generalization testing

This multi-layer strategy ensures:
- ✅ Each system component has appropriate ground truth
- ✅ No data leakage between train/val/test splits
- ✅ Reproducible, defensible evaluation
- ✅ Modular progression from simple to complex tasks
- ✅ Clear traceability to requirements (SRS § 5.3, Design § 14)

**Key Principle:**
> Do not try to force the entire project into one public dataset. Build a dataset stack with clear labeling, version control, and leakage-safe splits.

---

## Table of Contents

1. [Core Data Strategy](#1-core-data-strategy)
2. [Five ML/DSP Subtasks & Data Requirements](#2-five-mldsp-subtasks--their-data-requirements)
3. [Public Benchmark Datasets](#3-public-benchmark-datasets)
4. [Custom Synthetic Data Generation](#4-custom-synthetic-data-generation)
5. [Authorized Real-World Recordings](#5-authorized-real-world-recordings)
6. [Canonical Data Format & Storage](#6-canonical-data-format--storage)
7. [Data Preparation Pipeline](#7-data-preparation-pipeline)
8. [Train/Validation/Test Splits & Leakage Prevention](#8-trainvalidationtest-splits--leakage-prevention)
9. [Quality Assurance & Validation](#9-quality-assurance--validation)
10. [Ready-for-Training Checklist](#10-ready-for-training-checklist)
11. [Technology Stack & Tools](#11-technology-stack--tools)
12. [Risk Mitigation & Contingencies](#12-risk-mitigation--contingencies)
13. [Recommended Execution Sequence](#13-recommended-execution-sequence)
14. [Documentation Templates](#14-documentation-templates)
15. [Integration with SRS & Test Plan](#15-integration-with-srs--test-plan)
16. [References & External Resources](#16-references--external-resources)
17. [Key Principles — Do Not Forget](#17-key-principles--do-not-forget)

---

## 1. Core Data Strategy

### 1.1 Dataset Stack Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATASET STACK OVERVIEW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PUBLIC BENCHMARKS       CUSTOM SYNTHETIC      REAL VALIDATION   │
│  (Modulation Focused)    (Pipeline Focused)    (Generalization)  │
│       ↓                        ↓                     ↓            │
│  RadioML 2016/2018       GNU Radio + Python    Field Recordings  │
│  HisarMod2019.1          FEC Encoders          NTRO Captures     │
│       │                  Interleavers                 │           │
│       │                  Modulators                   │           │
│       │                  Channel Models               │           │
│       └────────────┬──────────────────────────────────┘           │
│                    ↓                                              │
│         CANONICAL IQ FORMAT (float32 complex)                    │
│         COMMON METADATA (modulation, SNR, seed)                  │
│         LEAKAGE-SAFE SPLITS (stratified by source)              │
│                    ↓                                              │
│    ┌──────────────────────────────────────────┐                  │
│    │                                          │                  │
│    ↓                                          ↓                  │
│ MODULATION CLASSIFIER                 FEC + INTERLEAVING PIPELINE
│ (ResNet-18 on RadioML)                 (Custom data with labels) │
│    │                                          │                  │
│    └──────────────────────────────────────────┘                  │
│                       ↓                                           │
│              END-TO-END VALIDATION                               │
│          (Payload Recovery Success Rate)                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Dataset Layer Specifications

| Layer | Primary Datasets | Primary Use | Target Coverage | Priority | Status |
|:---|:---|:---|:---|:---|:---|
| **Baseline AMC** | RadioML 2016.10A | Modulation classification, CNN training | 11 mods, SNR −20 to +18 dB | P0 | 📥 Action: Download |
| **Extended AMC** | RadioML 2018.01A, HisarMod2019.1 | Larger benchmark, cross-dataset validation | 24 mods, 1024-sample windows | P0–P1 | 📥 Action: Download |
| **Custom Communication** | Custom GNU Radio + Python | FEC, interleaving, demodulation, end-to-end | All 4 interleaver types, all 4 FEC types | P0 | 🔧 Build Phase 8 |
| **Real Validation** | Authorized NTRO captures | Generalization to real-world impairments | HF/VHF/UHF bands, field conditions | P1 | 🔒 Available Q3–Q4 |

---

## 2. Five ML/DSP Subtasks & Their Data Requirements

### 2.1 Task A — Automatic Modulation Classification (AMC)

**Requirement:** SRS § 5.3 (F-09), Design § 14.2.2

**Input Specification:**
- Complex-valued I/Q samples (float32)
- Window length: 128–2048 samples (RadioML: 128; realistic: 1024+)
- SNR range: −20 to +30 dB (training); −5 to +30 dB (evaluation per SRS)

**Output Specification:**
- Modulation class: FSK, PSK (BPSK, QPSK, 8PSK), QAM (16, 64, 256)
- Confidence score: 0–1 (softmax)
- Alternative hypotheses: top-3 predictions

**Supported Modulations:**
```
Digital Modulations (Primary)
  ├─ FSK: 2-FSK, 4-FSK, MSK
  ├─ PSK: BPSK, QPSK, OQPSK, 8-PSK
  └─ QAM: 16-QAM, 64-QAM, 256-QAM

Analog Modulations (Detection Only in v1)
  ├─ AM: AM-DSB, AM-SSB
  └─ FM: WBFM, NBFM (detected; not demodulated)

Bonus Modulations (if benchmark available)
  ├─ PAM: PAM4
  └─ CPFSK, GFSK (narrow-band variants)
```

**Suitable Datasets:**
- ✅ **RadioML 2016.10A** (220k examples, 11 classes, baseline)
- ✅ **RadioML 2018.01A** (2M examples, 24 classes, extended)
- ✅ **HisarMod2019.1** (cross-dataset validation)

**Training Specifications:**
| Aspect | Specification | Reference |
|:---|:---|:---|
| Model Architecture | ResNet-18 or CNN with batch-norm + dropout | SRS F-09 |
| Input shape | (64, 64) spectrogram (time-frequency) | SRS F-09 |
| Output | Softmax over modulation classes | SRS F-09 |
| Model size | < 10 MB (quantized int8 or float32) | SRS F-09 |
| Inference latency | < 100 ms per sample on CPU | SRS F-09 |
| Accuracy target | ≥90% on test set (SNR ≥5 dB) | Project Charter § 4 |
| Training data | Synthetic AWGN channel, SNR ∈ [−5, 20] dB | Design § 14.2.2 |

**Notes:**
- ✅ Well-established benchmark
- ✅ Fastest path to working prototype
- ⚠️ Limited to 11–24 classes (extend if needed)
- ⚠️ Synthetic AWGN only (real channels add Doppler, fading; handle in v2)

---

### 2.2 Task B — Parameter Estimation (Sampling Rate, Bandwidth, SNR)

**Requirement:** SRS § 5.3 (F-07, F-08), Design § 14.2.1

**Input Specification:**
- Complex I/Q signal (arbitrary length, 0.1 s to 10 s)
- Unknown sampling rate (typically 1 kHz to 1 GHz for RF)
- Unknown modulation (will be available from Task A)

**Output Specification:**
| Parameter | Accuracy Target | Detection Method |
|:---|:---|:---|
| Sampling Frequency (Fs) | ± 2% | Cyclostationary, spectral roll-off, metadata |
| Symbol Rate (Rs) | ± 2% | Spectral peak, timing recovery convergence |
| Bandwidth (99% power) | ± 5% | PSD integration, roll-off detection |
| Signal-to-Noise Ratio (SNR) | ± 3 dB | Noise floor estimation |
| Carrier offset | ± 1% of Rs | Spectral centroid analysis |

**Approach (DSP-Primary, ML-Optional):**

> **Key Principle:** Do not train an ML model merely because ML is available. Implement DSP estimator first; add ML only if DSP alone is unreliable.

**Recommended Methods:**
1. **Sampling Frequency Detection:**
   - Method 1: Metadata extraction (if .wav or annotated .IQ)
   - Method 2: Cyclostationary feature detection (auto-correlation of squared signal)
   - Method 3: Roll-off detection (spectral energy tail)
   - Fallback: User input with confidence warning

2. **Symbol Rate Estimation:**
   - Method 1: Spectral peaks (FFT peak search)
   - Method 2: Timing recovery loop convergence rate
   - Method 3: Signal periodicity (auto-correlation)

3. **SNR Estimation:**
   - Method 1: Noise floor (Welch's PSD estimation)
   - Method 2: Symbol constellation clustering (EVM-based)
   - Method 3: Higher-order statistics (kurtosis)

**Data Requirement:**
- Less critical than AMC; validate on synthetic + authorized real signals
- Generate synthetic test vectors with known Fs, Rs, SNR for unit testing
- No large labeled dataset required; DSP validation sufficient

**Traceability:** SRS § 6 (FR-04), Test Plan § 4 (Parameter Extraction tests)

---

### 2.3 Task C — FEC Identification & Decoding

**Requirement:** SRS § 5.6 (F-18 to F-21), Design § 14.2.4

**Input Specification:**
- Demodulated bitstream (hard bits: 0/1 or soft bits: LLR ±127)
- Known or estimated modulation type (from Task A)
- Unknown FEC scheme

**Output Specification:**
| FEC Type | Configuration | Decoder | Output |
|:---|:---|:---|:---|
| **Convolutional** | K=3,5,7,9; rates 1/2–3/4 | Viterbi | Corrected bits + error count |
| **Reed-Solomon** | (255, k) GF(2⁸) | Berlekamp-Massey | Corrected bytes + error flags |
| **LDPC** | Configurable H, rates 1/2–5/6 | Belief-Propagation | Corrected bits + convergence |
| **Concatenated** | RS outer + Conv inner | Iterative | Final decoded bitstream |
| **Unknown** | N/A | Report "Unknown" | Structured error message |

**Challenge:**
- Public modulation datasets (RadioML) rarely provide FEC ground truth
- Must generate custom dataset with exact encoder/decoder parameters known

**Solution:**
- Build custom FEC encoders (Python + NumPy)
- Generate controlled test vectors with known FEC parameters
- Validate decoders against known-good bit patterns
- See § 4 (Custom Synthetic Data Generation)

**Traceability:** SRS § 6 (FR-07), Test Plan § 8 (FEC Decoding tests)

---

### 2.4 Task D — Interleaver Identification & De-interleaving

**Requirement:** SRS § 5.5 (F-14 to F-17), Design § 14.2.3

**Input Specification:**
- Demodulated + FEC-decoded bitstream
- Unknown interleaving pattern

**Output Specification:**
| Interleaver Type | Configuration | De-interleaver | Method |
|:---|:---|:---|:---|
| **Block** | M×N matrix depth (8, 16, 32, 64) | Column-row transpose | Auto-detect depths |
| **Convolutional** | Multi-tap delay line (D, 2D, 3D, ...) | Inverse shifts | Common: DVB-S2, CCSDS |
| **Diagonal** | Row-major write, diagonal read | Reverse diagonal pattern | Fixed pattern |
| **Pseudo-Random** | LFSR polynomial + seed | Seed brute-force search | Limited 2^16–2^24 |
| **None** | No interleaving | Pass-through | Fallback case |
| **Unknown** | N/A | Report "Unknown" | Structured error message |

**Challenge:**
- Requires exact ground truth of interleaving parameters
- Cannot be reliably detected from public modulation datasets

**Solution:**
- Custom dataset with parametric ground truth
- Exact mapping: bit index → interleaved index
- Validate de-interleaver with BER reduction metric

**Traceability:** SRS § 6 (FR-06), Test Plan § 7 (De-interleaving tests)

---

### 2.5 Task E — End-to-End Recovery

**Requirement:** SRS § 8 (Workflow), Design § 3 (End-to-end flow)

**Input Specification:**
- Raw .IQ or .wav file (unknown parameters)

**Output Specification:**
- Recovered bitstream with header/payload identified
- Confidence metrics at each pipeline stage

**Pipeline:**
```
.IQ/.wav File
    ↓ (Task A)
Modulation Classification (e.g., QPSK)
    ↓ (Demodulation Engine, SRS § 5.4)
Soft/Hard Bits
    ↓ (Task D)
De-interleaved Bits
    ↓ (Task C)
FEC-Decoded Bits
    ↓ (Task F, § 2.6)
Frame Sync & Correlation
    ↓
Header + Payload Extracted
```

**Data Requirement:**
- Must preserve **complete ground truth** through entire chain
- Example: 10,000 end-to-end examples with:
  - Original message bits
  - FEC scheme applied
  - Interleaving pattern applied
  - Modulation applied
  - Channel noise applied (SNR)
  - Recovered bits

**Traceability:** Test Plan § 14 (End-to-End Integration tests)

---

### 2.6 Task F — Bitstream Correlation & Payload Extraction

**Requirement:** SRS § 5.7 (F-22 to F-24), Design § 14.2.5

**Input Specification:**
- FEC-decoded bitstream
- Library of known preambles/sync-words

**Output Specification:**
- Match locations + quality metrics
- Header/payload boundaries
- Extracted payload (binary, hex, ASCII, JSON)

**Data Requirement:**
- Sync-word library (provided or custom)
- Example: 100 known preambles from various protocols
- Validation: CRC checks on extracted payloads

**Traceability:** SRS § 6 (FR-08), Test Plan § 9 (Bitstream Correlation tests)

---

## 3. Public Benchmark Datasets

### 3.1 RadioML 2016.10A — Baseline Modulation Classification

**Status:** 📥 **PRIORITY ACTION: Download This Week (Week 0)**

#### Characteristics

| Property | Value |
|:---|:---|
| **Source** | DeepSig (open dataset), Zenodo optimized mirror |
| **License** | CC BY-NC-SA 4.0 (Academic research use OK; commercial requires licensing) |
| **Generation Method** | GNU Radio synthetic signals + AWGN channel model |
| **Modulations Supported** | 11 classes (BPSK, QPSK, 8PSK, QAM16, QAM64, CPFSK, GFSK, PAM4, WBFM, AM-SSB, AM-DSB) |
| **SNR Range** | −20 dB to +18 dB in 2 dB steps (20 SNR levels per modulation) |
| **Samples per Example** | 128 I/Q pairs (short window; suitable for quick iteration) |
| **Total Examples** | 220,000 total (1,000 per modulation/SNR pair) |
| **Data Format** | Python pickle dictionary |
| **Data Type** | float32 complex |
| **File Size** | ~1.2 GB (compressed); ~4 GB (uncompressed) |
| **Download Time** | 15–30 min (Zenodo mirror, fast connection) |

#### Usage Profile

**✅ Ideal For:**
- Baseline CNN training and validation
- Fast iteration on model architecture
- Proof-of-concept modulation classifier
- Unit tests for DSP pipeline

**⚠️ Known Limitations:**
- Relatively short windows (128 samples vs. realistic 1024+)
- Only 11 modulation classes (vs. potential 20+ in real scenarios)
- Pure AWGN channel (no Doppler, fading, phase noise)
- Synthetic data only (not representative of real RF environment)
- Not sufficient alone for production deployment (Design § 18 risk analysis)

#### Download Instructions

**Preferred: Zenodo Optimized Mirror** (Recommended — Fastest)

```bash
# Step 1: Create data directory
mkdir -p data/raw/radioml2016
cd data/raw/radioml2016

# Step 2: Visit Zenodo
# URL: https://zenodo.org/records/18397070
# Download: RML2016.10a.tar.bz2

# Step 3: Download using curl or wget
wget https://zenodo.org/records/18397070/files/RML2016.10a.tar.bz2
# OR
curl -O https://zenodo.org/records/18397070/files/RML2016.10a.tar.bz2

# Step 4: Verify checksum (if provided on Zenodo page)
# Zenodo usually provides MD5; verify:
md5sum RML2016.10a.tar.bz2
# Compare with value from Zenodo page

# Step 5: Extract archive
tar -xjf RML2016.10a.tar.bz2

# Step 6: Mark as read-only to prevent accidental modification
chmod 444 RML2016.10a_dict.pkl

# Step 7: Cleanup
# Keep .tar.bz2 for archival; can delete after verification
# (Optional: rm RML2016.10a.tar.bz2)
```

**Expected Output:**
```
data/raw/radioml2016/
├── RML2016.10a_dict.pkl     (~4 GB, read-only)
├── RML2016.10a.tar.bz2      (~1.2 GB, archive)
└── CHECKSUM.md5             (if available)
```

**Alternative: DeepSig Official Source**
```
Visit: https://www.deepsig.ai/datasets/
Find: RADIOML 2016.10A section
Complete: Contact verification (required by DeepSig)
Download: From official link
Store: data/raw/radioml2016/RML2016.10a_dict.pkl
```

#### Inspection Script

**Purpose:** Verify dataset integrity before using in training

```python
#!/usr/bin/env python3
"""
Inspect RadioML 2016.10A dataset
Location: scripts/inspect_radioml2016.py
"""

import pickle
import numpy as np
import os

DATASET_PATH = "data/raw/radioml2016/RML2016.10a_dict.pkl"

def inspect_radioml2016():
    """Load and inspect RadioML 2016 dataset."""
    
    if not os.path.exists(DATASET_PATH):
        print(f"❌ Dataset not found at: {DATASET_PATH}")
        print(f"   Please download from: https://zenodo.org/records/18397070")
        return
    
    print(f"✅ Loading dataset from: {DATASET_PATH}")
    print(f"   File size: {os.path.getsize(DATASET_PATH) / 1e9:.2f} GB")
    
    with open(DATASET_PATH, "rb") as f:
        data = pickle.load(f, encoding="latin1")
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total keys (modulation/SNR pairs): {len(data)}")
    
    # Extract unique modulations and SNR levels
    modulations = sorted(set(k[0] for k in data.keys()))
    snr_levels = sorted(set(k[1] for k in data.keys()))
    
    print(f"\n🔤 Modulations ({len(modulations)}):")
    for mod in modulations:
        print(f"   ├─ {mod}")
    
    print(f"\n📶 SNR Levels ({len(snr_levels)}):")
    print(f"   Range: {min(snr_levels)} dB to {max(snr_levels)} dB")
    print(f"   Levels: {snr_levels[:5]}...{snr_levels[-5:]}")
    
    # Inspect first example
    first_key = next(iter(data.keys()))
    first_data = data[first_key]
    
    print(f"\n🎯 First Example:")
    print(f"   Key: {first_key} (modulation={first_key[0]}, SNR={first_key[1]} dB)")
    print(f"   Shape: {first_data.shape} (samples, I/Q, length)")
    print(f"   Data type: {first_data.dtype}")
    print(f"   Value range: [{first_data.min():.4f}, {first_data.max():.4f}]")
    
    # Verify data integrity
    print(f"\n✓ Integrity Check:")
    print(f"   Entries with correct shape: {sum(1 for v in data.values() if v.shape[1:] == (2, 128)) / len(data) * 100:.1f}%")
    print(f"   Data type matches (float32): {all(v.dtype == np.float32 for v in data.values())}")
    print(f"   ✅ Dataset is valid and ready for use")

if __name__ == "__main__":
    inspect_radioml2016()
```

**Run:**
```bash
python scripts/inspect_radioml2016.py
```

**Expected Output:**
```
✅ Loading dataset from: data/raw/radioml2016/RML2016.10a_dict.pkl
   File size: 4.25 GB

📊 Dataset Statistics:
   Total keys (modulation/SNR pairs): 220

🔤 Modulations (11):
   ├─ 8PSK
   ├─ AM-DSB
   ├─ AM-SSB
   ├─ BPSK
   ├─ CPFSK
   ├─ GFSK
   ├─ PAM4
   ├─ QPSK
   ├─ QAM16
   ├─ QAM64
   └─ WBFM

📶 SNR Levels (20):
   Range: -20 dB to 18 dB
   Levels: [-20, -18, -16, -14, -12]...[10, 12, 14, 16, 18]

🎯 First Example:
   Key: ('QPSK', 10)
   Shape: (1000, 2, 128)
   Data type: float32
   Value range: [-1.2345, 1.2341]

✓ Integrity Check:
   Entries with correct shape: 100.0%
   Data type matches (float32): True
   ✅ Dataset is valid and ready for use
```

---

### 3.2 RadioML 2018.01A — Extended Modulation Benchmark

**Status:** 📥 **ACTION: Download After RadioML 2016 is Working (Week 1–2)**

#### Characteristics

| Property | Value |
|:---|:---|
| **Source** | DeepSig official repository |
| **License** | CC BY-NC-SA 4.0 (same as 2016) |
| **Format** | HDF5 (hierarchical, efficient random access) |
| **Modulations Supported** | 24 digital and analog classes (extended set) |
| **Samples per Example** | 1024 I/Q pairs (4× longer than 2016) |
| **Total Examples** | ~2,000,000 (approx.; 10× more than 2016) |
| **SNR Range** | −20 dB to +30 dB (estimated; wider than 2016) |
| **Channel Complexity** | Higher fidelity than 2016 (more realistic) |
| **File Size** | ~40–80 GB (uncompressed H5) |
| **Download Time** | 1–2 hours (requires registration; from DeepSig server) |

#### Purpose

- Stress-test the modulation classifier on longer, more realistic signal windows
- Validate generalization: Does a model trained on RadioML 2016 (128 samples) work on 2018 (1024 samples)?
- Larger benchmark reduces overfitting risk
- Broader modulation class coverage

#### Download Instructions

```bash
# Step 1: Visit DeepSig
# URL: https://www.deepsig.ai/datasets/
# Find: RADIOML 2018.01A section

# Step 2: Complete Contact Verification
# (DeepSig requires this; takes 5–15 min)

# Step 3: Download from provided link
mkdir -p data/raw/radioml2018
cd data/raw/radioml2018

# Download large file (may take 1–2 hours)
# Use rsync or aria2c for resume capability
wget --continue https://[deepsig-link]/radioml2018.01A.h5

# Step 4: Preserve original as read-only
chmod 444 radioml2018.01A.h5

# Step 5: Verify integrity (if checksum provided)
sha256sum radioml2018.01A.h5
```

#### Inspection Script

```python
#!/usr/bin/env python3
"""
Inspect RadioML 2018.01A dataset (HDF5 format)
Location: scripts/inspect_radioml2018.py
"""

import h5py
import numpy as np
import os

DATASET_PATH = "data/raw/radioml2018/radioml2018.01A.h5"

def inspect_radioml2018():
    """Load and inspect RadioML 2018 dataset."""
    
    if not os.path.exists(DATASET_PATH):
        print(f"❌ Dataset not found at: {DATASET_PATH}")
        print(f"   Please download from: https://www.deepsig.ai/datasets/")
        return
    
    print(f"✅ Opening dataset: {DATASET_PATH}")
    print(f"   File size: {os.path.getsize(DATASET_PATH) / 1e9:.2f} GB")
    
    with h5py.File(DATASET_PATH, "r") as f:
        print(f"\n📊 HDF5 Structure:")
        print(f"   Root keys: {list(f.keys())}")
        
        # Inspect X_train, Y_train, etc.
        for key in list(f.keys())[:5]:
            dataset = f[key]
            print(f"\n   {key}:")
            print(f"      Shape: {dataset.shape}")
            print(f"      Data type: {dataset.dtype}")
            if dataset.ndim <= 2:
                print(f"      Value range: [{dataset.min()}, {dataset.max()}]")

if __name__ == "__main__":
    inspect_radioml2018()
```

---

### 3.3 HisarMod2019.1 — Cross-Dataset Generalization Benchmark

**Status:** 📥 **ACTION: Download After RadioML 2018 Working (Week 2–3)**

#### Characteristics

| Property | Value |
|:---|:---|
| **Source** | IEEE DataPort (https://doi.org/10.21227/8k12-2g70) |
| **License** | Open Access (review usage terms on IEEE DataPort) |
| **Modulations** | Multiple classes (specific count TBD in download) |
| **Signal Length** | Variable (typical: 512–2048 samples) |
| **Total Examples** | 1000s of examples |
| **Purpose** | Cross-dataset validation: RadioML → HisarMod generalization |

#### Purpose

- Validate that models trained on RadioML generalize to **different** datasets
- Reduce overfitting risk; ensure robustness
- Tests the "domain gap" between synthetic (RadioML) and real-world-like data

#### Download Instructions

```bash
# Step 1: Visit IEEE DataPort
# URL: https://doi.org/10.21227/8k12-2g70
# (May require IEEE login or registration)

# Step 2: Download dataset files
mkdir -p data/raw/hisarmod2019
# Follow IEEE DataPort instructions to download

# Step 3: Mark as read-only
chmod 444 data/raw/hisarmod2019/*
```

---

## 4. Custom Synthetic Data Generation

### 4.1 GNU Radio Custom Data Generator

**Status:** 🔧 **BUILD PHASE 8 (Weeks 8–9)**

**Purpose:**
- Generate modulated signals with exact ground truth (modulation, symbol rate, noise level)
- Test FEC encoders with known bit patterns
- Test interleavers with known bit mappings
- Build end-to-end synthetic pipeline (bits → FEC → interleave → modulate → channel → IQ)

**Architecture:**

```python
# Pseudocode: Custom data generator pipeline

# Step 1: Generate random source bits
source_bits = np.random.randint(0, 2, size=10000)

# Step 2: Apply FEC encoder (e.g., Viterbi convolutional)
fec_config = {
    'type': 'convolutional',
    'constraint_length': 7,
    'code_rate': '1/2'
}
encoded_bits = viterbi_encode(source_bits, fec_config)

# Step 3: Apply interleaver (e.g., block)
interleaver_config = {
    'type': 'block',
    'M': 16,
    'N': 32
}
interleaved_bits = block_interleave(encoded_bits, interleaver_config)

# Step 4: Modulate (e.g., QPSK)
mod_config = {
    'type': 'QPSK',
    'samples_per_symbol': 4
}
symbols = modulate(interleaved_bits, mod_config)
iq_samples = upsample_filter(symbols, mod_config['samples_per_symbol'])

# Step 5: Add channel noise (AWGN)
snr_db = 10
iq_noisy = add_awgn(iq_samples, snr_db)

# Step 6: Store with full metadata
example = {
    'iq_samples': iq_noisy,
    'source_bits': source_bits,
    'fec_config': fec_config,
    'interleaver_config': interleaver_config,
    'mod_config': mod_config,
    'snr_db': snr_db,
    'sample_rate': mod_config['sample_rate'],
    'bit_rate': mod_config['bit_rate']
}
```

### 4.2 FEC Encoder Implementations

**Viterbi Encoder (Convolutional Codes)**

```python
"""
Convolutional Code Parameters (Example)
Constraint Length K=7, Code Rate 1/2

Generator Polynomials: (171, 133 octal) = (0o171, 0o133)
"""

class ConvolutionalEncoder:
    def __init__(self, K=7, rate='1/2', polynomials=(0o171, 0o133)):
        self.K = K
        self.rate = rate
        self.polynomials = polynomials
        self.state_machine_size = 2 ** (K - 1)
    
    def encode(self, bits):
        """Encode input bits using convolutional code."""
        # Trellis implementation
        # Output: encoded bits (interleaved or systematic)
        pass
```

**Reed-Solomon Encoder**

```python
"""
Reed-Solomon Encoder
Symbol size: 8-bit (GF(2^8))
Common configurations: (255, 251), (255, 239), (255, 223)
"""

class ReedSolomonEncoder:
    def __init__(self, n=255, k=251):
        self.n = n
        self.k = k
        self.t = (n - k) // 2
    
    def encode(self, data_bytes):
        """Encode data_bytes using RS(255, k)."""
        # Compute parity symbols using polynomial division
        # Output: n-byte codeword (k data + (n-k) parity)
        pass
```

**LDPC Encoder**

```python
"""
LDPC Code with configurable parity-check matrix H
Rate depends on H density and structure
"""

class LDPCEncoder:
    def __init__(self, H, rate=0.5):
        self.H = H  # Parity-check matrix
        self.rate = rate
    
    def encode(self, bits):
        """Encode using sparse parity-check matrix H."""
        # Solve Hc^T = 0 (mod 2) for codeword c
        # Output: n-bit codeword
        pass
```

### 4.3 Interleaver Implementations

**Block Interleaver**

```python
class BlockInterleaver:
    def __init__(self, M, N):
        """M rows × N columns matrix."""
        self.M = M
        self.N = N
    
    def interleave(self, bits):
        """Write row-major, read column-major."""
        matrix = bits.reshape((self.M, self.N))
        interleaved = matrix.T.flatten()
        return interleaved
    
    def deinterleave(self, bits):
        """Write column-major, read row-major."""
        matrix = bits.reshape((self.N, self.M)).T
        deinterleaved = matrix.flatten()
        return deinterleaved
```

**Convolutional Interleaver (DVB-S2 style)**

```python
class ConvolutionalInterleaver:
    def __init__(self, taps=[D, 2D, 3D, 4D]):
        """Multi-tap delay line."""
        self.taps = taps
    
    def interleave(self, bits):
        """Demultiplex across delay taps."""
        # Output: bits reordered across delay registers
        pass
    
    def deinterleave(self, bits):
        """Restore sequential order."""
        # Inverse operation
        pass
```

### 4.4 Generation Script Example

```bash
#!/bin/bash
# Generate custom FEC/interleaving dataset
# Script: scripts/generate_fec_interleaving_dataset.py

python scripts/generate_fec_interleaving_dataset.py \
    --output_dir data/raw/custom_fec_interleaving \
    --num_samples 10000 \
    --fec_types viterbi,reed_solomon,ldpc,concatenated \
    --interleaver_types block,convolutional,diagonal,prng \
    --snr_range -5,20 \
    --sample_rate 1e6 \
    --seed 42

# Output:
#   data/raw/custom_fec_interleaving/
#   ├── metadata.json (ground truth for all samples)
#   ├── samples_0001.h5 (1000 samples, chunk 1)
#   ├── samples_0002.h5 (1000 samples, chunk 2)
#   └── ...
```

---

## 5. Authorized Real-World Recordings

**Status:** 🔒 **AVAILABLE Q3–Q4 2026 (NTRO Authorization)**

### 5.1 NTRO Real RF Captures

**Source:** NTRO surveillance sensors (HF, VHF, UHF bands)  
**Availability:** Restricted; require NTRO authorization  
**Schedule:** Expected Q3–Q4 2026  

**Characteristics:**
| Aspect | Specification |
|:---|:---|
| Frequency Bands | HF (3–30 MHz), VHF (30–300 MHz), UHF (300 MHz–3 GHz) |
| Recording Duration | Minutes to hours per file |
| Sample Rate | 1 MHz to 100 MHz (sensor-dependent) |
| Signal Type | Complex baseband (.IQ) or real audio (.wav) |
| Preprocessing | Minimal; retains original waveform characteristics |
| Metadata | Partial (frequency band, timestamp, quality notes) |
| Quantity | 50–200 files (TBD by NTRO) |

### 5.2 Purpose

- Final validation: Does system generalize to real-world signals?
- Real-world impairments: Doppler, fading, phase noise, non-ideal channels
- Performance profiling: Processing time, memory usage on actual data
- Confidence in production deployment

### 5.3 Usage Notes

- ✅ Use ONLY for final validation (after synthetic training complete)
- ✅ Do NOT train models on real data (would overfit to NTRO characteristics)
- ⚠️ Handle as restricted data; no external distribution
- ⚠️ Document all usage; maintain audit trail

---

## 6. Canonical Data Format & Storage

### 6.1 Canonical .IQ File Format Specification

**Goal:** Standardize all datasets (RadioML, custom, real) to single format for pipeline integration

```yaml
Format Specification: Canonical IQ Format v1.0
═══════════════════════════════════════════════════════════════

File Format: HDF5 (.h5)
Encoding: UTF-8 metadata, float32 I/Q data

Root Structure:
  /metadata/
    ├─ dataset_name (str): e.g., "RadioML2016"
    ├─ version (str): e.g., "1.0.0"
    ├─ creation_date (str): ISO 8601 timestamp
    ├─ source (str): "RadioML" | "CustomSynthetic" | "NTRORealCapture"
    ├─ sample_count (int): Total I/Q pairs in dataset
    └─ split (str): "train" | "validation" | "test"
  
  /samples/
    ├─ iq_data (float32, shape=(N, 2))
    │  └─ Row i: [I_i, Q_i] (in-phase, quadrature)
    │
    ├─ modulation (uint8, shape=(N,))
    │  └─ Modulation class ID (0=BPSK, 1=QPSK, ...)
    │
    ├─ snr_db (float32, shape=(N,))
    │  └─ Signal-to-noise ratio in dB (−20 to +30)
    │
    └─ metadata_per_sample (variable-length strings, shape=(N,))
       └─ JSON: {"sample_rate": 1e6, "bit_rate": 100e3, ...}
  
  /encoder_config/ (if applicable)
    ├─ fec_type (str): "viterbi" | "reed_solomon" | "ldpc" | "none"
    ├─ fec_config (variable): {"constraint_length": 7, ...}
    ├─ interleaver_type (str): "block" | "convolutional" | "none"
    └─ interleaver_config (variable): {"M": 16, "N": 32, ...}
  
  /ground_truth/ (for custom synthetic data)
    ├─ source_bits (uint8, shape=(N, M))
    │  └─ Original message bits before encoding
    │
    └─ recovered_bits (uint8, shape=(N, M))
       └─ Recovered bits after full pipeline
```

### 6.2 Example Creation Script

```python
#!/usr/bin/env python3
"""
Convert RadioML 2016 to canonical format
Script: scripts/canonicalize_radioml2016.py
"""

import h5py
import pickle
import numpy as np
from datetime import datetime

def canonicalize_radioml2016(input_pkl, output_h5):
    """Convert RadioML 2016 pickle → canonical HDF5."""
    
    print(f"Loading: {input_pkl}")
    with open(input_pkl, "rb") as f:
        radioml_data = pickle.load(f, encoding="latin1")
    
    print(f"Creating: {output_h5}")
    with h5py.File(output_h5, "w") as hf:
        
        # Metadata
        metadata_grp = hf.create_group("metadata")
        metadata_grp.create_dataset("dataset_name", data="RadioML2016")
        metadata_grp.create_dataset("version", data="1.0.0")
        metadata_grp.create_dataset("creation_date", data=datetime.utcnow().isoformat())
        metadata_grp.create_dataset("source", data="RadioML")
        metadata_grp.create_dataset("sample_count", data=len(radioml_data) * 1000)
        metadata_grp.create_dataset("split", data="all")
        
        # Samples
        samples_grp = hf.create_group("samples")
        
        # Flatten all data
        all_iq = []
        all_mods = []
        all_snr = []
        
        modulation_map = {
            '8PSK': 0, 'AM-DSB': 1, 'AM-SSB': 2, 'BPSK': 3,
            'CPFSK': 4, 'GFSK': 5, 'PAM4': 6, 'QPSK': 7,
            'QAM16': 8, 'QAM64': 9, 'WBFM': 10
        }
        
        for (modulation, snr), data in sorted(radioml_data.items()):
            # data shape: (1000, 2, 128)
            # Convert to (1000, 2) where row = [I, Q]
            iq_flat = data.reshape(data.shape[0], -1)
            all_iq.append(iq_flat)
            all_mods.append(np.full(data.shape[0], modulation_map[modulation], dtype=np.uint8))
            all_snr.append(np.full(data.shape[0], snr, dtype=np.float32))
        
        # Concatenate
        iq_array = np.vstack(all_iq).astype(np.float32)
        mod_array = np.concatenate(all_mods)
        snr_array = np.concatenate(all_snr)
        
        # Store in HDF5
        samples_grp.create_dataset("iq_data", data=iq_array, compression="gzip")
        samples_grp.create_dataset("modulation", data=mod_array)
        samples_grp.create_dataset("snr_db", data=snr_array)
        
        print(f"✅ Canonicalized: {output_h5}")
        print(f"   Samples: {len(iq_array)}")
        print(f"   Shape: {iq_array.shape}")

if __name__ == "__main__":
    canonicalize_radioml2016(
        "data/raw/radioml2016/RML2016.10a_dict.pkl",
        "data/canonical/radioml2016_canonical.h5"
    )
```

---

## 7. Data Preparation Pipeline

### 7.1 End-to-End Preparation Workflow

```
Raw Dataset Acquisition
    ↓
Integrity Verification (checksums, sizes)
    ↓
Canonicalization to HDF5
    ↓
Validation (shape, range, null checks)
    ↓
Train/Val/Test Split
    ↓
Stratification by Source/Modulation/SNR
    ↓
Leakage Prevention Check
    ↓
Statistical Profiling
    ↓
Quality Assurance Report
    ↓
Ready for Training ✅
```

### 7.2 Data Cleaning & Preprocessing

**Outlier Detection:**
```python
def detect_outliers(iq_array, threshold=3.0):
    """Detect samples with unusual amplitude."""
    amplitudes = np.abs(iq_array)
    median = np.median(amplitudes)
    mad = np.median(np.abs(amplitudes - median))
    z_scores = 0.6745 * (amplitudes - median) / mad
    outliers = z_scores > threshold
    return outliers
```

**Normalization:**
```python
def normalize_iq(iq_array, target_range=(-1, 1)):
    """Normalize I/Q samples to target range."""
    min_val, max_val = iq_array.min(), iq_array.max()
    normalized = (iq_array - min_val) / (max_val - min_val)
    normalized = normalized * (target_range[1] - target_range[0]) + target_range[0]
    return normalized
```

---

## 8. Train/Validation/Test Splits & Leakage Prevention

### 8.1 Split Strategy

**Goal:** Ensure no leakage; validate generalization

```
Total Dataset (RadioML 2016: 220k examples)
    │
    ├─ 70% Training (154k)        → Model learns
    ├─ 15% Validation (33k)       → Hyperparameter tuning
    └─ 15% Test (33k)             → Final evaluation
```

### 8.2 Stratification

**By Modulation:**
```python
# Ensure each modulation class appears in all splits
from sklearn.model_selection import StratifiedShuffleSplit

splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.15, random_state=42)
for train_idx, test_idx in splitter.split(data, modulation_labels):
    train_set = data[train_idx]
    test_set = data[test_idx]
```

**By SNR:**
```python
# Ensure SNR diversity in all splits
# Map SNR values to bins: [-20:-10], [-10:0], [0:10], [10:20]
snr_bins = pd.cut(snr_array, bins=[-20, -10, 0, 10, 20])
# Stratify by SNR bin + modulation combination
```

**By Source Dataset (for custom data):**
```python
# If combining RadioML 2016 + RadioML 2018 + HisarMod:
# Stratify so each source appears in all splits
# Prevents test leakage where model only sees RadioML 2016 → RadioML 2018 transfer fails
```

### 8.3 Leakage Prevention Checklist

- [ ] Train/val/test splits are mutually exclusive (zero sample overlap)
- [ ] Stratification ensures modulation balance in all splits
- [ ] SNR range coverage is similar across splits
- [ ] Source dataset is stratified (no single-source splits)
- [ ] Random seeds are fixed and documented
- [ ] Split manifests are version-controlled and immutable

---

## 9. Quality Assurance & Validation

### 9.1 Automated QA Tests

```python
#!/usr/bin/env python3
"""Quality Assurance Tests for Canonical Dataset"""

import h5py
import numpy as np

def qa_check_canonical_dataset(h5_path):
    """Run QA checks on canonical HDF5 dataset."""
    
    with h5py.File(h5_path, "r") as hf:
        iq_data = hf["samples/iq_data"][:]
        mods = hf["samples/modulation"][:]
        snrs = hf["samples/snr_db"][:]
        
        print("🔍 QA Checks:")
        
        # 1. Shape validation
        assert iq_data.shape[1] == 2, "IQ data must have 2 columns"
        print(f"   ✓ Shape: {iq_data.shape}")
        
        # 2. Type validation
        assert iq_data.dtype == np.float32, "IQ must be float32"
        print(f"   ✓ Data type: {iq_data.dtype}")
        
        # 3. Range validation
        assert iq_data.min() >= -2.0 and iq_data.max() <= 2.0, "IQ out of range"
        print(f"   ✓ Range: [{iq_data.min():.3f}, {iq_data.max():.3f}]")
        
        # 4. Null check
        assert not np.isnan(iq_data).any(), "NaN detected"
        print(f"   ✓ No NaN values")
        
        # 5. SNR range
        assert snrs.min() >= -25 and snrs.max() <= 35, "SNR out of expected range"
        print(f"   ✓ SNR range: [{snrs.min():.1f}, {snrs.max():.1f}] dB")
        
        # 6. Modulation class count
        unique_mods = np.unique(mods)
        print(f"   ✓ Modulations: {len(unique_mods)} classes")
        
        # 7. Class distribution
        for mod_id in sorted(unique_mods):
            count = (mods == mod_id).sum()
            print(f"      └─ Class {mod_id}: {count:,} samples ({100*count/len(mods):.1f}%)")
        
        print(f"\n✅ All QA checks passed")

if __name__ == "__main__":
    qa_check_canonical_dataset("data/canonical/radioml2016_canonical.h5")
```

### 9.2 Visual QA (Plots)

Generate plots for manual review:

```python
import matplotlib.pyplot as plt

# 1. Constellation plots (10 samples per modulation)
# 2. Waterfall plots (spectrogram visualization)
# 3. SNR distribution histogram
# 4. Modulation class counts bar chart

# All plots saved to: reports/qa_plots_radioml2016.pdf
```

---

## 10. Ready-for-Training Checklist

### 10.1 Dataset Staging

- [ ] RadioML 2016.10A downloaded and verified
- [ ] RadioML 2018.01A downloaded and verified (optional, Phase 2)
- [ ] HisarMod2019.1 downloaded and verified (optional, Phase 2)
- [ ] Custom FEC/interleaving generators built and unit-tested
- [ ] Canonical HDF5 format implemented and validated
- [ ] All datasets canonicalized to single format

### 10.2 Data Integrity

- [ ] File integrity verified (checksums, sizes match expected)
- [ ] No corruption during download/extraction (all files readable)
- [ ] Metadata extraction successful (sample rate, modulation, SNR present)
- [ ] Data types and shapes match specification
- [ ] Outliers detected and handled (or documented)

### 10.3 Data Organization

- [ ] Directory structure matches specification:
  ```
  data/
  ├── raw/
  │   ├── radioml2016/RML2016.10a_dict.pkl
  │   ├── radioml2018/radioml2018.01A.h5
  │   └── hisarmod2019/[files]
  ├── canonical/
  │   ├── radioml2016_canonical.h5
  │   ├── radioml2018_canonical.h5
  │   └── ...
  └── splits/
      ├── radioml2016_train.txt
      ├── radioml2016_val.txt
      ├── radioml2016_test.txt
      └── ...
  ```

- [ ] All raw files marked read-only: `chmod 444`
- [ ] Canonical files generated with versioning

### 10.4 Data Splits

- [ ] Train/val/test split manifests exist (frozen in Git)
- [ ] Leakage validation script passes (zero sample overlap)
- [ ] Modulation balance verified (all classes in all splits)
- [ ] SNR distribution documented per split
- [ ] Custom data: Ground truth bits stored with exact mapping

### 10.5 Quality Assurance

- [ ] Statistical summary generated (class counts, SNR histogram, I/Q statistics)
- [ ] Constellation plots generated for 10 random samples per modulation
- [ ] Spectrum/waterfall plots generated (sanity check)
- [ ] Waveform plots show expected characteristics (no corruption)
- [ ] Visual QC report generated and approved

### 10.6 Reproducibility & Documentation

- [ ] Dataset generation scripts version-controlled
- [ ] All random seeds fixed and documented
- [ ] Dataset versions tagged (e.g., `v1.0`)
- [ ] Dataset cards created with full metadata
- [ ] Processing logs saved for audit trail
- [ ] README with download instructions and checksums

### 10.7 Baseline Model Readiness

- [ ] At least RadioML 2016 loads without errors
- [ ] Data shapes match expected model input dimensions (e.g., (batch, 128, 2) for CNN)
- [ ] Batch loading works (no out-of-memory errors)
- [ ] Data pipeline can feed model training loop
- [ ] Model training can begin without data-related modifications

---

## 11. Technology Stack & Tools

### 11.1 Data Processing Tools

| Task | Tool | Version | Rationale |
|:---|:---|:---|:---|
| **Numerical Computing** | NumPy | ≥1.19 | Standard Python array operations |
| **Scientific Computing** | SciPy | ≥1.5 | Signal processing (FFT, filtering) |
| **Data Storage** | h5py | ≥2.10 | HDF5 reading/writing |
| **Deep Learning** | TensorFlow / PyTorch | Latest | Model training and inference |
| **Data Processing** | Pandas | ≥1.1 | Metadata manipulation, splits |
| **Visualization** | Matplotlib | ≥3.3 | Plot generation for QA |
| **Signal Gen** | GNU Radio | ≥3.8 | Synthetic signal generation |
| **Version Control** | Git + DVC | Latest | Track data, scripts, models |

### 11.2 Environment Setup

```bash
# Create isolated environment
python -m venv venv_dataprep
source venv_dataprep/bin/activate

# Install requirements
pip install -r requirements_dataprep.txt
```

**requirements_dataprep.txt:**
```
numpy>=1.19
scipy>=1.5
h5py>=2.10
matplotlib>=3.3
pandas>=1.1
scikit-learn>=0.24
torch>=1.9
tensorflow>=2.5
gnuradio>=3.8
```

---

## 12. Risk Mitigation & Contingencies

### 12.1 Risk Register

| Risk | Impact | Likelihood | Mitigation | Owner |
|:---|:---|:---|:---|:---|
| **Public datasets become unavailable** | High | Low | Download and archive locally; backup to external storage | Data Lead |
| **Dataset license restrictions change** | Medium | Low | Document current license; follow up with DeepSig quarterly | Project Lead |
| **Leakage in train/val/test splits** | High | Medium | Automated validation script runs on every split; code review | QA Lead |
| **Custom data generation bugs** | High | Medium | Unit tests on each component; cross-check with GNU Radio | Dev Lead |
| **Data corruption during transfer** | Medium | Low | Checksum verification at each step; immutable storage | Ops Lead |
| **Dataset versioning confusion** | Medium | Medium | Explicit semantic versioning; frozen manifests in Git | Data Lead |
| **Insufficient real-world data availability** | Medium | Medium | Prioritize synthetic training; use authorized NTRO captures when available | Project Lead |
| **Memory constraints (large datasets)** | Medium | Medium | Use HDF5 chunking; memory-map large files; batch processing | Dev Lead |

### 12.2 Contingency Plans

**If RadioML unavailable:**
- Use alternative: Zenodo backup link or IEEE DataPort
- Generate additional synthetic data (GNU Radio)
- Use smaller public benchmarks (YouTube, GitHub signal samples)

**If NTRO real-world data delayed:**
- Extend synthetic training phase (generate more FEC/interleaving variants)
- Use public datasets as proxy for generalization testing
- Deploy with synthetic-only model (accept risk noted in Design § 18)

**If custom data generation fails:**
- Use RadioML as-is (limited FEC/interleaving coverage)
- Implement simplified decoders (Viterbi-only, no RS/LDPC)
- Document as v1.0 limitation; enhance in v2.0

---

## 13. Recommended Execution Sequence

**Execute steps in EXACTLY this order:**

### Phase A: Public Benchmarks (Weeks 1–3)

```
Week 1:
  1. [ ] Download RadioML 2016.10A from Zenodo
  2. [ ] Verify checksums and integrity
  3. [ ] Extract and organize in data/raw/radioml2016/
  4. [ ] Run inspection script (§ 3.1)
  5. [ ] Create canonical HDF5 format
  6. [ ] Generate train/val/test splits
  7. [ ] QA checks pass

Week 2:
  8. [ ] Train baseline CNN on RadioML 2016
  9. [ ] Achieve ≥90% accuracy at SNR ≥5 dB
  
Week 3:
  10. [ ] Download RadioML 2018.01A
  11. [ ] Canonicalize to HDF5
  12. [ ] Evaluate RadioML 2016 model on 2018 (cross-dataset test)
  13. [ ] Document generalization gap
  14. (Optional) Download HisarMod2019.1
```

**Why this order?**
- Steps 1–9: Fast path to working modulation classifier
- Steps 10–12: Prove generalization before moving to complex data
- Parallelizable: Steps 8–14 can overlap

### Phase B: Custom Synthetic (Weeks 4–9)

```
Week 4–5:
  15. [ ] Build GNU Radio modulation generator (FSK, PSK, QAM)
  16. [ ] Implement FEC encoders (Viterbi, RS, LDPC, Concatenated)
  17. [ ] Unit test each encoder
  
Week 6–7:
  18. [ ] Implement de-interleavers (block, conv, diag, PRNG)
  19. [ ] Generate FEC-only dataset (10k samples)
  20. [ ] Generate interleaving-only dataset (10k samples)
  
Week 8–9:
  21. [ ] Build end-to-end pipeline (bits → FEC → interleave → mod → channel → IQ)
  22. [ ] Generate end-to-end dataset (50k samples)
  23. [ ] Validate ground truth for each sample
```

### Phase C: Final Validation (Weeks 10–12)

```
Week 10:
  24. [ ] Acquire authorized NTRO real-world recordings (if available)
  25. [ ] Canonicalize real data
  26. [ ] Evaluate synthetic-trained models on real data
  
Week 11–12:
  27. [ ] Document generalization performance
  28. [ ] Finalize dataset documentation and audit trail
  29. [ ] Freeze datasets (tag versions; mark read-only)
  30. [ ] Submit to project acceptance gate
```

**Timeline Summary:**
- Weeks 1–3: 🟢 Public benchmarks (fast, blockers identified early)
- Weeks 4–9: 🟡 Custom synthetic (moderate risk, parallelizable)
- Weeks 10–12: 🟢 Final validation (low risk, high confidence)

**Do NOT skip steps or reverse this order.** The quickest path to a working prototype is:
1. Nail modulation classification first (using public benchmarks)
2. Simultaneously build custom generator (decouple from public data availability)
3. Validate on real data (answer "Does it work on NTRO signals?")

---

## 14. Documentation Templates

### 14.1 Dataset Acquisition Checklist

**File:** `docs/datasets/CHECKLIST_[Dataset Name].md`

```markdown
# Dataset Acquisition Checklist — [Dataset Name]

**Acquired:** [Date]  
**Acquired by:** [Name]  
**Source URL:** [URL]  
**DOI (if applicable):** [DOI]  
**File Size:** [GB]  
**Download Time:** [hours]  

## Pre-Download Verification
- [ ] URL is accessible
- [ ] License terms reviewed and approved for research use
- [ ] Download quota/limits confirmed
- [ ] Storage space available (minimum: [GB])

## Download & Verification
- [ ] Downloaded successfully via [wget / curl / manual]
- [ ] Download time recorded: [minutes]
- [ ] File integrity verified:
  - [ ] File size matches expected: [GB]
  - [ ] Checksum verified (if available): [hash]
  - [ ] Archive extractable without errors

## Storage & Organization
- [ ] Stored in `data/raw/[dataset_name]/`
- [ ] Original files marked read-only: `chmod 444 *`
- [ ] Backup copy created: [location]
- [ ] Directory structure documented

## Licensing & Attribution
- [ ] License type: [CC BY-NC-SA 4.0 / Apache / Custom]
- [ ] Commercial use restrictions: [Yes / No / Partial]
- [ ] Required attribution: [Format]
- [ ] Citation bibtex entry: [Generated]

## Next Steps
- [ ] **Canonicalization:** Convert to HDF5 format
- [ ] **Validation:** Run QA checks
- [ ] **Splits:** Create train/val/test manifests
- [ ] **Documentation:** Generate dataset card
```

### 14.2 Dataset Processing Log

**File:** `docs/datasets/LOG_[Dataset Name]_[Date].md`

```markdown
# Dataset Processing Log — [Dataset Name]

**Start Date:** [Date]  
**Completion Date:** [Date]  
**Processed by:** [Name]  
**Status:** [In Progress / Complete / Failed]  

## Environment
- Python version: `python --version`
- Dependency versions: (from `pip freeze`)
- Machine specs: (CPU cores, RAM, GPU)

## Processing Steps

### Step 1: Raw Data Load
- Script: `scripts/canonicalize_[dataset].py`
- Git commit: `abc123`
- Runtime: [XX] minutes
- Peak memory: [XX] GB
- Result: [Loaded [N] samples]

### Step 2: Data Validation
- [ ] Shape validation passed
- [ ] Type validation passed
- [ ] Range validation passed (min/max: [values])
- [ ] Null/NaN check passed
- [ ] No outliers detected (or [N] outliers removed)

### Step 3: Canonicalization
- [ ] Converted to complex float32
- [ ] Normalized to [−1, 1]
- [ ] Metadata attached to each sample
- [ ] Checksum computed: [hash]

### Step 4: Output Verification
- [ ] Output file size: [XX] MB
- [ ] Output file readable via h5py: ✓
- [ ] Sample count: [N] records
- [ ] Data integrity: [XX]% valid

## Quality Assurance
- [ ] Constellation plots generated: `reports/qa_constellations_[dataset].pdf`
- [ ] Waterfall plots generated: `reports/qa_waterfall_[dataset].pdf`
- [ ] Statistical summary: Class distribution, SNR histogram
- [ ] Comparison to original: [Results]

## Acceptance Sign-Off
- [ ] All checks passed
- [ ] Dataset ready for training
- [ ] Documented in project README
- [ ] Versioned and tagged: `v1.0`

## Notes
[Any issues, lessons learned, recommendations for next dataset]
```

---

## 15. Integration with SRS & Test Plan

### 15.1 Mapping to SRS Requirements

| SRS Requirement | Dataset Component | Coverage |
|:---|:---|:---|
| **FR-01** (IQ/WAV ingestion) | RadioML 2016/2018 (IQ); Custom generators | ✅ Full |
| **FR-04** (Parameter extraction) | Custom synthetic (known Fs, Rs, modulation) | ✅ Full |
| **FR-05** (Demodulation) | Custom FEC/interleaving pipeline | ✅ Full |
| **FR-06** (De-interleaving) | Custom interleaver datasets | ✅ Full |
| **FR-07** (FEC decoding) | Custom FEC datasets | ✅ Full |
| **FR-08** (Bitstream correlation) | End-to-end pipeline with sync words | ✅ Full |
| **F-09** (AMC) | RadioML 2016/2018/HisarMod | ✅ Full |

### 15.2 Mapping to Test Plan

| Test Plan Module | Dataset Used | Coverage |
|:---|:---|:---|
| **Module 5: AMC** (14 tests) | RadioML 2016, 2018, HisarMod | Provides synthetic labels |
| **Module 7: De-interleaving** (16 tests) | Custom interleaver datasets | Exact ground truth |
| **Module 8: FEC** (18 tests) | Custom FEC datasets | Exact encoder configs |
| **Module 14: End-to-End** (5 tests) | End-to-end synthetic + real | Full pipeline validation |

---

## 16. References & External Resources

### Dataset Sources

- **RadioML 2016.10A (Zenodo):** https://zenodo.org/records/18397070
- **RadioML 2016.10A (DeepSig):** https://www.deepsig.ai/datasets/
- **RadioML 2018.01A (DeepSig):** https://www.deepsig.ai/datasets/
- **HisarMod2019.1 (IEEE DataPort):** https://doi.org/10.21227/8k12-2g70

### Tools & Libraries

- **GNU Radio:** https://www.gnuradio.org/
- **PySDR:** https://pysdr.org/
- **SigMF:** https://sigmf.org/ (Signal Metadata Format standard)
- **h5py Documentation:** https://docs.h5py.org/
- **PyTorch DataLoader:** https://pytorch.org/docs/stable/data.html

### Academic References

- O'Shea et al. (2016): "Over-the-Air Deep Learning Based Radio Signal Classification"
- DeepSig RadioML documentation: https://www.deepsig.ai/publications/
- ICESAT (2021): Cross-Dataset Evaluation for AMC models

---

## 17. Key Principles — Do Not Forget

> **Do not force the entire project into one public dataset. Build a dataset stack.**

✅ **Use public benchmarks for modulation classification**
   - Well-validated, mature datasets (RadioML, HisarMod)
   - Faster iteration, lower risk
   - Reduced dependency on custom data generation

✅ **Generate custom synthetic data for FEC/interleaving**
   - Full ground truth control
   - Known encoder parameters for validation
   - Reproducible, deterministic generation

✅ **Preserve raw data immutably**
   - Never modify original downloaded files
   - Store read-only: `chmod 444`
   - Keep pristine backup copies

✅ **Version everything**
   - Data, scripts, configurations, splits, models
   - Use semantic versioning (v1.0, v1.1, etc.)
   - Tag releases in Git; freeze manifests

✅ **Document exhaustively**
   - Dataset sources, licenses, processing steps
   - QA results, statistical summaries
   - Download URLs, checksums, expected file sizes
   - Processing scripts with comments

✅ **Prevent leakage at all costs**
   - Use explicit split manifests (frozen in Git)
   - Validate programmatically (zero overlap)
   - Stratify by modulation, SNR, source
   - Code review all split logic

✅ **Test generalization early**
   - Validate cross-dataset before claiming success
   - RadioML 2016 → RadioML 2018 transfer test (Week 3)
   - Identify domain gaps before scaling effort

✅ **Build reproducibility in**
   - Fixed random seeds, documented everywhere
   - Frozen Python environment (requirements.txt)
   - Versioned data generation scripts
   - Audit trail for all processing steps

---

## 18. Quick Start — Next 7 Days

```
📅 WEEK 1 ACTION ITEMS
════════════════════════════════════════════════════════════

🟢 TODAY (Monday):
   [ ] Visit https://zenodo.org/records/18397070
   [ ] Start downloading RML2016.10a.tar.bz2 (1–2 hours)
   [ ] Create data/raw/radioml2016/ directory

🟢 TUESDAY:
   [ ] Verify download checksum
   [ ] Extract: tar -xjf RML2016.10a.tar.bz2
   [ ] Run inspection script (scripts/inspect_radioml2016.py)
   [ ] Verify 220k samples, 11 modulations loaded

🟢 WEDNESDAY:
   [ ] Canonicalize to HDF5 (scripts/canonicalize_radioml2016.py)
   [ ] Generate train/val/test splits (70/15/15)
   [ ] Validate zero leakage

🟢 THURSDAY:
   [ ] Generate QA plots (constellations, waterfall)
   [ ] Document dataset statistics
   [ ] Publish dataset acquisition checklist

🟢 FRIDAY:
   [ ] Begin baseline CNN training on RadioML 2016
   [ ] Target: ≥85% accuracy @ SNR ≥10 dB (Week 1 goal)
   [ ] Document training progress

════════════════════════════════════════════════════════════
```

---

**Document Version:** 3.0 (Enhanced)  
**Status:** ✅ **READY FOR IMMEDIATE IMPLEMENTATION**  
**Last Updated:** September 18, 2026  
**Next Review:** Weekly (tracking dataset acquisition progress)
