# System Design Document

## Automated Model for Analysis of .IQ and .WAV Files Along with Signal Parameter Extraction

**Problem Statement ID:** 26147  
**Organization:** National Technical Research Organisation (NTRO)  
**Category:** Software / SIGINT & Digital Signal Processing  
**Document Type:** System Design / Technical Architecture  
**Version:** 2.0 (Consolidated & Improved)  
**Status:** Proposed Design  
**Last Updated:** September 2026

---

## Executive Summary

This document defines the technical architecture for an automated signal intelligence (SIGINT) workstation that ingests raw radio frequency (RF) recordings in `.IQ` (complex baseband) and `.wav` (audio) formats and extracts communication parameters, performs demodulation, decoding, and frame extraction. The system targets HF, VHF, and UHF terrestrial signals and operates in air-gapped, offline environments.

The proposed solution combines **deterministic DSP**, **machine learning** for modulation classification, and **rule-based communication recovery** into a pipeline-oriented, modular architecture that can be progressively implemented, tested, and validated.

---

## 1. Document Purpose & Scope

### 1.1 Purpose

This System Design converts the official NTRO problem statement into an implementable technical architecture by:

- Defining the overall system structure, data flows, and module responsibilities
- Specifying key algorithms, datasets, and technology choices
- Identifying what is required vs. proposed vs. deferred
- Establishing validation criteria and risk mitigation strategies
- Providing a blueprint for phased implementation and team organization

### 1.2 In Scope

- `.IQ` and `.wav` file ingestion and validation
- Signal preprocessing, normalization, and segmentation
- Spectral analysis (FFT, waterfall, spectrogram, PSD)
- Parameter extraction (sampling rate, bandwidth, SNR, carrier offset)
- Automatic modulation classification (AMC)
- Demodulation (FSK, PSK, QAM)
- De-interleaving (block, convolutional, diagonal, pseudo-random)
- FEC decoding (convolutional/Viterbi, Reed-Solomon, concatenated, LDPC)
- Bitstream analysis and frame synchronization
- GUI visualization (constellation, waterfall, parameter displays)
- Export and reporting functionality
- Dataset generation and model training pipeline
- End-to-end testing and validation

### 1.3 Out of Scope (First Prototype)

- Universal recognition of every possible radio protocol
- Guaranteed interpretation of proprietary or encrypted communications
- Automatic decryption of encrypted signals
- Universal FEC/interleaver recognition for truly arbitrary unknown schemes
- Full real-time multi-channel SDR production deployment
- Wideband multi-signal decomposition (single isolated signal assumed)

These features may be added in later releases with appropriate data, validation, and algorithmic support.

---

## 2. Problem Context & Design Vision

### 2.1 Current State Problem

Raw RF data collected from diverse sensors across multiple geographic locations and time epochs is recorded as `.IQ` or `.wav` files. Manual analysis is time-consuming, operator-dependent, and lacks the precision required for:

- Exact modulation identification (e.g., 8-PSK vs. 16-PSK)
- FEC scheme discovery
- Interleaving pattern recovery
- Frame structure determination

### 2.2 Design Principle

The system architecture follows this principle:

> **Use deterministic signal processing where physical properties can be reliably estimated, machine learning where pattern classification requires learned features, and deterministic decoders where communication standards are known or sufficiently inferred.**

Rather than treating this as a single black-box AI model, the system is designed as a **testable pipeline of independently validatable stages**, providing:

- Better interpretability and debugging capability
- Controlled evaluation at each stage
- Ability to add capabilities progressively
- Clear confidence reporting at each step

### 2.3 System Objectives

1. **Automated Parameter Extraction** — Compute $F_s$ (sampling frequency), $R_s$ (symbol rate), modulation type, interleaving pattern, and FEC scheme without manual metadata input.
2. **Unified Visualization** — Render waterfall plots, PSD charts, and I/Q constellation diagrams in real-time.
3. **Complete DSP Pipeline** — Demodulate FSK, PSK, and QAM modulation schemes.
4. **Error Correction** — De-interleave and decode convolutional, Reed-Solomon, concatenated, and LDPC codes.
5. **Frame Extraction** — Perform bitwise correlation to locate sync words and isolate headers from payloads.
6. **Offline Security** — Operate in air-gapped environments with zero external network access.

---

## 3. End-to-End Workflow

```
User loads .IQ or .wav file
    ↓
File validation & metadata extraction
    ↓
Preprocessing (DC removal, IQ imbalance correction, normalization)
    ↓
Signal detection / segmentation
    ↓
Spectral analysis (FFT, waterfall, PSD plots)
    ↓
Parameter estimation (Fs, bandwidth, SNR, carrier offset)
    ↓
Modulation classification (ML + DSP features)
    ↓
Carrier & symbol timing synchronization
    ↓
Demodulation (FSK/PSK/QAM) → Soft/Hard bits
    ↓
Interleaver detection & de-interleaving
    ↓
FEC detection & decoding (Viterbi/RS/LDPC)
    ↓
Bitstream correlation & frame synchronization
    ↓
Header/Payload extraction & validation
    ↓
Results, confidence metrics, plots, and report export
```

---

## 4. High-Level System Architecture

### 4.1 Layered Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     GUI Layer (PyQt6)                       │
│  [File Upload] [Waterfall] [Constellation] [Parameters]     │
│                 [Control Panel] [Reports]                   │
└────────────────────────┬────────────────────────────────────┘
                         │ QThread async signals
┌────────────────────────▼────────────────────────────────────┐
│              Workflow Orchestrator & Controller              │
│         (Job state, config, logging, validation)             │
└─┬──────────────────────┬────────────────────────────────────┘
  │                      │
  ├──────────┬──────────┤
  │          │          │
┌─▼─┐  ┌────▼────┐  ┌──▼──────┐
│ I/O│  │ DSP     │  │ ML Inf. │
│Pars│  │Pipeline │  │ Engine  │
│ ing│  │         │  │         │
└──┬─┘  └────┬────┘  └──┬──────┘
   └─────────┼──────────┘
             │
    ┌────────▼────────┐
    │   Demodulation  │
    │   & Sync Loop   │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ De-interleaver  │
    │   & FEC Decod   │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  Bitstream      │
    │   Correlation   │
    │ & Frame Sync    │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ Results, Plots, │
    │    Reports      │
    └─────────────────┘
```

### 4.2 Module Architecture

```
ntro_sigint/
├── core/
│   ├── ingestion.py           # .IQ and .wav binary parsers
│   ├── preprocessor.py        # DC offset, IQ imbalance, normalization
│   └── orchestrator.py        # Pipeline controller & job manager
├── dsp/
│   ├── spectral.py            # FFT, STFT, waterfall, PSD computation
│   ├── parameter_estimation.py# Fs, Rs, bandwidth, SNR, CFO estimation
│   ├── demodulators.py        # FSK, PSK, QAM demodulation
│   └── synchronizers.py       # Costas Loop, Gardner TED, timing recovery
├── ml/
│   ├── amc_model.py           # ResNet-18 1D CNN for modulation classification
│   ├── cumulants.py           # Higher-order cumulants feature extraction
│   └── model_utils.py         # Dataset loading, training, evaluation
├── decoding/
│   ├── deinterleaver.py       # Block, Conv, Diagonal, PRNG de-interleaving
│   ├── fec_viterbi.py         # Convolutional code Viterbi decoder
│   ├── fec_rs.py              # Reed-Solomon GF(2^8) decoder
│   ├── fec_concatenated.py    # Concatenated RS + Convolutional decoder
│   └── fec_ldpc.py            # LDPC sum-product belief propagation
├── correlation/
│   └── frame_sync.py          # Preamble search, sync word detection, payload extraction
├── gui/
│   ├── app.py                 # Main PyQt6 application window
│   ├── widgets/
│   │   ├── waterfall_widget.py
│   │   ├── constellation_widget.py
│   │   ├── parameter_panel.py
│   │   └── report_viewer.py
│   └── styles.py              # Qt stylesheets
└── tests/
    ├── test_ingestion.py
    ├── test_dsp.py
    ├── test_ml.py
    ├── test_decoding.py
    └── test_integration.py
```

---

## 5. Input Data Architecture

### 5.1 File Formats

| Format | Representation | Data Types | Sample Rate | Parsing |
|:---|:---|:---|:---|:---|
| **`.IQ` (Baseband)** | Complex `I + jQ` | Interleaved `float32`, `int16`, `int8` | Metadata-free or sidecar JSON | Binary stream reader with configurable byte offsets, endianness |
| **`.wav` (Audio/RF)** | Real or Complex audio | PCM 16/24/32-bit, IEEE Float32 | Embedded in RIFF header | RIFF header parser extracting `fmt` chunk, `data` offset |

### 5.2 File Validation Workflow

1. **Header Inspection** — Confirm RIFF magic bytes (WAV) or assume binary (IQ)
2. **Size Feasibility** — Warn if file exceeds system RAM capacity; enable chunked processing
3. **Metadata Recovery** — For `.IQ`, attempt recovery from filename conventions or sidecar JSON; for `.wav`, extract sample rate and channel count
4. **Sample Integrity** — Detect truncated frames, missing I/Q pairs, bit depth mismatches
5. **Normalization** — Convert all formats to common internal representation (complex float32 normalized to $[-1, 1]$)

---

## 6. Signal Processing (DSP) Pipeline

### 6.1 Preprocessing Stage

**Goal:** Remove DC bias, compensate for I/Q imbalance, normalize power, and prepare for spectral analysis.

#### 6.1.1 DC Offset Removal
$$x_{\text{dc-free}}[n] = x[n] - \frac{1}{N} \sum_{k=0}^{N-1} x[k]$$

#### 6.1.2 I/Q Imbalance Correction
Apply Gram-Schmidt orthogonalization to compensate for amplitude skew and phase offset between I and Q channels:

$$Q' = \frac{Q - (Q \cdot I / \|I\|^2) I}{\|Q - (Q \cdot I / \|I\|^2) I\|}$$

#### 6.1.3 Power Normalization
Scale to unit variance:
$$x_{\text{norm}}[n] = \frac{x_{\text{dc-free}}[n]}{\text{std}(x_{\text{dc-free}})}$$

#### 6.1.4 Polyphase Resampling (Optional)
If acquisition sample rate is very high, apply polyphase FIR decimation to reduce computational load:
- Filter: Kaiser window, $\beta=8.6$, stop-band attenuation $> 100$ dB
- Decimation factor: $M = 2, 4, 8$ as appropriate

### 6.2 Spectral Analysis

#### 6.2.1 FFT Computation
- Window function: Hann or Blackman-Harris for dynamic range
- FFT size: 2048–8192 (configurable)
- Overlap: 50% for smooth spectral tracking

#### 6.2.2 Waterfall/Spectrogram
- Compute magnitude $|X_k|^2$ in dB scale (10 log₁₀)
- Stack FFT frames vertically with time as y-axis
- Display frequency as x-axis
- Colormap: Viridis or similar for visual distinction

#### 6.2.3 Power Spectral Density (PSD)
- Average spectrum across the entire signal or sliding window
- Estimate occupied bandwidth (e.g., 99% power containment)
- Detect peaks and nulls for modulation-specific features

---

## 7. Parameter Estimation

### 7.1 Sampling Frequency ($F_s$) Estimation

**Method 1: Metadata** — If WAV file, extract from RIFF header.

**Method 2: Autocorrelation** — For IQ files without metadata:
- Compute autocorrelation at expected periodicity intervals (e.g., integer multiples)
- Common GPS/RF standard rates: 1 MHz, 2 MHz, 4 MHz, 10 MHz, 20 MHz
- Match to known grid and verify consistency over signal duration

**Method 3: Cyclostationary** — Detect periodicity in power envelope or phase transitions to infer symbol rate and then estimate $F_s$ from known modulation schemes.

### 7.2 Symbol Rate ($R_s$) Estimation

**Method:** Cyclostationary Analysis
- Compute autocorrelation of $|x[n]|^2$ (power envelope)
- Peaks at multiples of symbol period $T_s = 1/R_s$
- Estimate $R_s$ in symbols/second

**Alternative:** Cumulant-based detection (see ML Section)

### 7.3 Bandwidth Estimation

- Compute occupied bandwidth from PSD as the frequency span containing 99% of signal power
- Alternative: measure 3dB bandwidth of peak in spectrum

### 7.4 SNR Estimation

$$\text{SNR}_{\text{dB}} = 10 \log_{10} \left( \frac{P_{\text{signal}}}{P_{\text{noise}}} \right)$$

- **Signal Power:** Power of modulated component (after bandpass filtering)
- **Noise Power:** Power in adjacent frequency bands or minimum spectral floor

---

## 8. Automatic Modulation Classification (AMC)

### 8.1 Feature-Based Detection (DSP Stage)

Compute higher-order cumulants to differentiate PSK from QAM:

$$C_{42} = E\left[x^4\right] - 3E\left[x^2\right]^2$$

- **PSK signals:** $C_{42}$ near zero (symmetric constellation)
- **QAM signals:** $C_{42}$ distinctly non-zero (asymmetric amplitude)

**Decision rule:** If $|C_{42}| < \tau_1$, likely PSK; else likely QAM.

### 8.2 Deep Learning Model (ML Stage)

**Architecture:** ResNet-18 1D CNN

```
Input: (Batch, 2, 1024) — [I/Q channels, 1024 samples]
    ↓
Conv1D(64 filters, kernel=3, stride=1, padding=1)
    ↓
ResBlock × 4 (residual connections, batch norm, ReLU)
    ↓
Global Average Pooling → (Batch, 64)
    ↓
Dense(128, ReLU) → Dropout(0.5)
    ↓
Dense(Num_Classes, Softmax)
    ↓
Output: Softmax probabilities over modulation classes
```

**Supported Modulation Classes:**
- 2-FSK, 4-FSK
- BPSK, QPSK, 8-PSK, 16-PSK
- 16-QAM, 64-QAM, 256-QAM (if feasible)

### 8.3 Dataset Architecture

| Property | Specification |
|:---|:---|
| **Signal Types** | 2-FSK, 4-FSK, BPSK, QPSK, 8-PSK, 16-QAM, 64-QAM |
| **SNR Range** | −10 dB to +20 dB in 2 dB increments |
| **Sample Window** | 1024 complex samples per frame |
| **Channel Impairments** | Carrier Frequency Offset (CFO), Phase Noise, AWGN, Rayleigh/Rician fading |
| **Training Set** | 50k frames per modulation type at each SNR |
| **Validation Set** | 10k frames per class (unseen SNR/CFO conditions) |
| **Test Set** | 5k frames per class (held-out scenarios) |

### 8.4 Dataset Generation (Python/NumPy)

```python
import numpy as np

def generate_modulated_signal(modulation, num_symbols=1024, snr_db=10, cfo_norm=0.01):
    """Generate synthetic modulated signal with channel impairments."""
    
    # Generate random bits
    bits = np.random.randint(0, 2, size=(num_symbols * bits_per_symbol(modulation)))
    
    # Modulate
    if modulation == 'QPSK':
        symbols = (1 - 2*bits[0::2]) + 1j*(1 - 2*bits[1::2])
        symbols /= np.sqrt(2)
    elif modulation == '16QAM':
        real_vals = (2*(bits[0::4] + 2*bits[1::4]) - 3) / np.sqrt(10)
        imag_vals = (2*(bits[2::4] + 2*bits[3::4]) - 3) / np.sqrt(10)
        symbols = real_vals + 1j*imag_vals
    # ... other modulations
    
    # Apply Carrier Frequency Offset (CFO)
    t = np.arange(len(symbols))
    symbols = symbols * np.exp(1j * 2 * np.pi * cfo_norm * t)
    
    # Add AWGN
    sig_power = np.mean(np.abs(symbols)**2)
    noise_power = sig_power / (10**(snr_db/10.0))
    noise = (np.random.normal(0, np.sqrt(noise_power/2), len(symbols)) + 
             1j*np.random.normal(0, np.sqrt(noise_power/2), len(symbols)))
    
    return symbols + noise

# Generate and save training batches
for modulation in MODULATIONS:
    for snr in SNR_RANGE:
        for i in range(NUM_SAMPLES_PER_CONFIG):
            signal = generate_modulated_signal(modulation, snr_db=snr)
            save_to_hdf5(signal, label=modulation)
```

### 8.5 Training Pipeline

| Hyperparameter | Value |
|:---|:---|
| **Loss Function** | Categorical Cross-Entropy |
| **Optimizer** | AdamW (LR=$10^{-3}$, weight decay=$10^{-4}$) |
| **Batch Size** | 64 |
| **Epochs** | 100 (with early stopping) |
| **Early Stopping Patience** | 10 epochs on validation loss |
| **Data Augmentation** | Phase rotation, random CFO, SNR scaling during training |
| **Target Accuracy** | ≥ 90% at SNR ≥ 5 dB |

---

## 9. Demodulation Architecture

### 9.1 Carrier Recovery (Costas Loop for PSK / Decision-Directed for QAM)

**Costas Loop for PSK:**
$$\phi_e[n] = \text{Im}\{y[n] \cdot \bar{y}_{\text{ref}}[n]\}$$

where $y_{\text{ref}}$ is the sliced decision output. Loop filter adjusts $\phi[n]$ to minimize $\phi_e$.

**Decision-Directed Loop for QAM:**
$$\phi_e[n] = \text{Im}\{(y[n] - d[n]) \cdot \bar{d}[n]\}$$

where $d[n]$ is the nearest constellation point.

Loop bandwidth: 0.1–0.5 rad/sample (tunable).

### 9.2 Symbol Timing Synchronization

**Gardner Timing Error Detector (for linear modulation):**
$$e_t[n] = \text{Re}\{(y[n] - y[n-2]) \cdot \overline{y[n-1]}\}$$

Adjusts sampling phase until error converges to zero.

**Alternative:** Mueller-Müller TED for lower SNR.

### 9.3 Symbol Slicing

- Map synchronized I/Q samples to nearest constellation centroids
- Hard decision: binary quantization
- Soft decision: log-likelihood ratios (LLR)
  $$\text{LLR} = \frac{d_0^2 - d_1^2}{2\sigma_n^2}$$
  where $d_0, d_1$ are distances to constellation points for bit=0 and bit=1.

---

## 10. De-interleaving Algorithms

### 10.1 Block De-interleaving

**Definition:** Data written row-by-row into $R \times C$ matrix, read column-by-column.

```python
def deinterleave_block(bits, rows, cols):
    """De-interleave block-interleaved bitstream."""
    matrix = bits.reshape(rows, cols)
    return matrix.T.flatten()  # Transpose and flatten
```

### 10.2 Convolutional De-interleaving

**Definition:** Shift bits through $N$ delay lines with incremental shift lengths.

```python
def deinterleave_convolutional(bits, num_branches, shift_increments):
    """De-interleave convolutional-interleaved bitstream."""
    branches = [deque() for _ in range(num_branches)]
    output = []
    
    for i, bit in enumerate(bits):
        branch_idx = i % num_branches
        shift_len = shift_increments[branch_idx]
        branches[branch_idx].append(bit)
        
        if len(branches[branch_idx]) > shift_len:
            output.append(branches[branch_idx].popleft())
    
    return np.array(output)
```

### 10.3 Diagonal De-interleaving

**Definition:** Read bits along diagonal paths through a matrix.

### 10.4 Pseudo-Random De-interleaving (PRNG)

**Definition:** Re-index bitstream using LFSR-generated permutation.

```python
def deinterleave_prng(bits, lfsr_seed, num_bits):
    """De-interleave PRNG-interleaved bitstream."""
    lfsr = LFSR(seed=lfsr_seed, length=num_bits)
    permutation = lfsr.generate_permutation()
    
    deinterleaved = np.zeros_like(bits)
    for i, perm_idx in enumerate(permutation):
        deinterleaved[i] = bits[perm_idx]
    
    return deinterleaved
```

---

## 11. Forward Error Correction (FEC) Decoding

### 11.1 Convolutional Codes (Viterbi Decoding)

**Supported Parameters:**
- Constraint length: $K = 3, 5, 7, 9$
- Code rates: $1/2, 1/3, 2/3, 3/4$

**Algorithm:** Viterbi trellis decoding with soft-decision metric:
$$\text{metric}[n] = \sum_k \text{LLR}[k] \cdot s[k]$$

where $s[k] \in \{+1, -1\}$ for bit 0/1 and $\text{LLR}[k]$ is the soft bit metric.

### 11.2 Reed-Solomon (RS) Codes

**Parameters:**
- Symbol field: $\text{GF}(2^8)$ (255, $k$) with $0 \le k \le 255$
- Error correction capability: $t = (255-k)/2$

**Algorithm:** Berlekamp-Massey syndrome polynomial + Chien search for error locators.

### 11.3 Concatenated Codes (Outer RS + Inner Convolutional)

**Decoding Strategy:**
1. Apply Viterbi decoding to inner convolutional code
2. Pass hard decisions to RS decoder as syndrome input
3. Iterative refinement (if soft info preserved) optional

### 11.4 LDPC Codes

**Algorithm:** Belief Propagation (Sum-Product) message-passing on sparse parity-check matrix $H$:

1. Initialize bit LLRs from channel
2. Iteratively update check-to-bit and bit-to-check messages
3. Compute bit estimates and check parity syndrome
4. Return converged estimate or declare failure after max iterations

**Max Iterations:** 50–100 (tunable).

---

## 12. Bitstream Analysis & Frame Synchronization

### 12.1 Sync Word Detection

**Method:** Sliding-window bitwise correlation

For candidate sync word $s$ and bitstream $b$:
$$\text{corr}[i] = \sum_j s[j] \oplus b[i+j]$$

Find peaks in correlation; peaks below threshold indicate potential frame boundaries.

### 12.2 Header Parsing

Once sync word is located, parse header fields:
- **Frame length** (# bytes or bits)
- **Transmitter ID / Source address**
- **Sequence number**
- **Modulation / FEC indicators** (if present)
- **CRC checksum**

### 12.3 Payload Extraction

- Extract payload bytes according to frame length
- Validate CRC; report success/failure
- Export raw bytes, hex dump, or interpreted content

---

## 13. GUI Architecture & Implementation

### 13.1 Technology Stack

| Component | Framework | Rationale |
|:---|:---|:---|
| **GUI Framework** | PyQt6 / PySide6 | Cross-platform, native widgets, mature async support |
| **Plotting** | pyqtgraph | OpenGL-accelerated 2D/3D rendering, high FPS |
| **DSP Core** | SciPy, NumPy, liquid-dsp | Optimized C-libraries for FFT, filtering, sync loops |
| **ML Engine** | PyTorch + ONNX Runtime | Lightweight inference, optional GPU acceleration |
| **Threading** | QThread, ThreadPool | Non-blocking file I/O, DSP computation, model inference |

### 13.2 Main Window Layout

```
┌─────────────────────────────────────────────────────────┐
│ File: [Browse...] | Analysis: [Start] [Cancel] | Logs ▼ │
├──────────────────┬──────────────────┬───────────────────┤
│                  │                  │                   │
│  Waterfall Plot  │  Constellation   │  Parameter Panel  │
│  (Frequency vs   │  (I/Q scatter)   │  ├─ Fs            │
│   Time)          │                  │  ├─ Rs            │
│  (2D heatmap)    │  (500x500 px)    │  ├─ Modulation    │
│                  │                  │  ├─ SNR           │
│  (Scrollbar)     │                  │  └─ Confidence    │
│                  │                  │                   │
├──────────────────┼──────────────────┼───────────────────┤
│                                                          │
│  Analysis Log / Status Messages                          │
│  [Stage: Demodulation] [95%] ████████░                  │
│                                                          │
├──────────────────┬──────────────────┬───────────────────┤
│ Export: [PDF] [CSV] [Bitstream] | Advanced: [Settings] │
└──────────────────┴──────────────────┴───────────────────┘
```

### 13.3 Multi-threading Model

```python
class SignalProcessor(QThread):
    """Background worker for DSP/ML processing."""
    progress = pyqtSignal(int)          # 0–100%
    waterfall_ready = pyqtSignal(np.ndarray)
    parameters_ready = pyqtSignal(dict)
    finished = pyqtSignal(dict)         # Final results
    error = pyqtSignal(str)
    
    def run(self):
        try:
            # Load file
            signal = load_iq_file(self.file_path)
            self.progress.emit(10)
            
            # Preprocess
            signal = preprocess(signal)
            self.progress.emit(20)
            
            # Compute waterfall
            waterfall = compute_waterfall(signal)
            self.waterfall_ready.emit(waterfall)
            self.progress.emit(40)
            
            # Classify modulation
            mod_class = classify_modulation(signal)
            params = extract_parameters(signal)
            self.parameters_ready.emit(params)
            self.progress.emit(60)
            
            # Demodulate & decode
            bits = demodulate(signal, params)
            payload = decode_payload(bits)
            self.progress.emit(100)
            
            self.finished.emit({"payload": payload, "params": params})
        except Exception as e:
            self.error.emit(str(e))
```

### 13.4 Visualization Widgets

- **Waterfall Widget:** Use `pg.ImageView` with spectrogram data; support real-time scrolling and colormap selection
- **Constellation Widget:** Scatter plot of I/Q points with grid overlay; overlay ideal constellation points
- **Parameter Panel:** Text labels for $F_s$, $R_s$, modulation, SNR, confidence percentages
- **Status Bar:** Real-time progress indicator and log messages

---

## 14. Dataset & Training Strategy

### 14.1 Synthetic Dataset Generation

**Tool:** Python + NumPy + GNU Radio (optional for advanced scenarios)

```bash
python scripts/generate_training_data.py \
    --modulations QPSK 16QAM 8PSK \
    --snr-range -10 20 2 \
    --num-samples 50000 \
    --output datasets/train/
```

**Output:** HDF5 file with structure:
```
train.h5
├── QPSK
│   ├── snr_-10dB/
│   │   ├── signal (50000, 1024) complex64
│   │   └── label (50000,) uint8
│   ├── snr_-8dB/
│   └── ...
├── 16QAM
└── 8PSK
```

### 14.2 Real-World Captured Dataset (Future)

- Coordinate with NTRO field teams to collect labeled captures
- Preserve ground truth (known transmitter, known modulation, known FEC)
- Cover diverse propagation scenarios (AWGN, fading, interference)

### 14.3 Model Validation Strategy

| Stage | Metric | Target |
|:---|:---|:---|
| **Modulation Classification** | Accuracy at SNR ≥ 5 dB | ≥ 90% |
| **Parameter Extraction** | RMSE(Fs estimate) | < 1% |
| **Demodulation** | Symbol Error Rate | < 10% at SNR ≥ 10 dB |
| **FEC Decoding** | Bit Error Rate post-decode | < $10^{-5}$ on synthetic test data |
| **End-to-End** | Payload Recovery Success | ≥ 80% on labeled captures |

---

## 15. Technology Stack & Rationale

| Layer | Technology | Rationale |
|:---|:---|:---|
| **Language** | Python 3.11 + C++20 | Python for agility; C++ for performance (Viterbi, FFT) |
| **DSP** | SciPy, NumPy | Well-optimized, mature signal processing routines |
| **ML Framework** | PyTorch | Flexible training; ONNX export for lightweight inference |
| **GUI** | PyQt6 + pyqtgraph | Cross-platform, responsive, high-FPS rendering |
| **DSP Extensions** | liquid-dsp, FFTW3 (C++) | Production-grade implementations of Viterbi, RS, FFT |
| **Deployment** | PyInstaller | Bundle Python, models, and C++ libs into standalone EXE |

---

## 16. Implementation Phases

### Phase 1: Foundation (Weeks 1–2)
- Project setup, repo structure, CI/CD pipeline
- Input parser (`ingestion.py`) for `.IQ` and `.wav`
- File validation and normalization
- Basic test suite

### Phase 2: DSP Fundamentals (Weeks 3–4)
- FFT, waterfall, PSD computation
- Preprocessing (DC removal, IQ imbalance, normalization)
- Parameter estimation (Fs, bandwidth, SNR)
- Basic GUI skeleton with file browser and plots

### Phase 3: Modulation Classification (Weeks 5–6)
- Dataset generation script
- ResNet-18 model architecture and training pipeline
- Model evaluation and validation
- Integration with GUI parameter panel

### Phase 4: Demodulation (Weeks 7–8)
- Carrier recovery loop (Costas/Decision-Directed)
- Symbol timing synchronization (Gardner/Mueller-Müller)
- FSK, PSK, QAM demodulator implementations
- End-to-end testing on synthetic signals

### Phase 5: Interleaving & FEC (Weeks 9–11)
- Block, convolutional, diagonal, PRNG de-interleavers
- Viterbi decoder (convolutional codes)
- Reed-Solomon decoder (algebraic)
- LDPC belief-propagation decoder
- Concatenated RS+Viterbi decoder chain

### Phase 6: Bitstream Analysis (Weeks 12–13)
- Sync word detection and correlation
- Header parsing and frame extraction
- Payload validation (CRC checks)
- Export to hex/binary/ASCII formats

### Phase 7: Integration & Hardening (Weeks 14–16)
- Connect all modules through orchestrator
- End-to-end testing with synthetic + real captures
- GUI polish (progress indicators, error handling, logging)
- Performance profiling and optimization
- Documentation and deployment packaging

---

## 17. Team Organization & Module Ownership

| Module | Responsibilities | Suggested Size |
|:---|:---|:---|
| **A: Input & DSP** | IQ/WAV parsers, FFT, waterfall, parameter estimation, SNR, filtering | 2–3 engineers |
| **B: ML & Classification** | Dataset generation, model training, evaluation, feature extraction | 2 engineers |
| **C: Communication Recovery** | Sync loops, demodulation, de-interleaving, FEC decoding, bitstream analysis | 2–3 engineers |
| **D: GUI & Integration** | PyQt6 interface, workflow orchestration, plotting, reports, packaging | 2 engineers |

**Total:** 8–11 person-months for 36-hour hackathon sprint with adequate pre-work.

---

## 18. Risk Analysis & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|:---|:---|:---|:---|
| Limited labeled training data | High | High | Use controlled synthetic datasets; validate on public benchmarks (RadioML, etc.) |
| Model accuracy drops at low SNR | High | High | Augment training with phase noise, CFO variations; ensemble with DSP features |
| FEC/interleaver identification fails on unknown schemes | High | Medium | Report "Unknown/Unsupported" instead of forcing classification; provide manual override UI |
| Large files exceed available RAM | Medium | Medium | Implement chunked processing with ring buffers; memory-map large files |
| GUI thread blocks during heavy DSP | Medium | Medium | Use QThread workers; implement progress signals; offload to C++ extensions |
| Decoder produces plausible but incorrect output | High | Medium | Validate using structural checks (CRC, frame length, repeated patterns) |
| Tight coupling between modules | Medium | Medium | Define clear interfaces; separate concerns (DSP vs. ML vs. GUI); use dependency injection |
| Dataset leakage (train/val/test not properly isolated) | Medium | Low | Stratify by source, geographic location, and time epoch; audit splits |

---

## 19. Success Criteria & KPIs

### Functional Success Criteria

1. ✓ System accepts `.IQ` and `.wav` files without user metadata
2. ✓ Displays real-time waterfall and constellation plots
3. ✓ Extracts $F_s$, $R_s$, modulation type, SNR with <10% error
4. ✓ Demodulates FSK, PSK, QAM signals correctly
5. ✓ De-interleaves block, convolutional, diagonal, PRNG patterns
6. ✓ Decodes convolutional (Viterbi), RS, LDPC codes
7. ✓ Correlates and extracts frame payloads
8. ✓ Exports results in multiple formats (PDF, CSV, hex dump)

### Performance KPIs

| KPI | Target | Actual |
|:---|:---|:---|
| Modulation classification accuracy at SNR ≥ 5 dB | ≥ 90% | TBD |
| Parameter extraction (Fs, Rs) RMSE | < 5% | TBD |
| Demodulation symbol error rate (SNR=10dB) | < 5% | TBD |
| FEC decode success on synthetic test data | ≥ 95% | TBD |
| GUI responsiveness (waterfall FPS) | ≥ 30 FPS | TBD |
| File processing latency for 10 MB IQ | < 30 sec | TBD |

---

## 20. Key Engineering Principles

1. **Transparency First** — Never force a classification the system cannot support; report confidence and unknown/unsupported states clearly.
2. **Modularity Over Monolith** — Each stage (ingestion, DSP, ML, decoding, GUI) should be independently testable and replaceable.
3. **Preserve Ground Truth** — Maintain labeled datasets and test fixtures; version models and configurations.
4. **Validate the Whole Pipeline** — Do not evaluate only the classifier; measure end-to-end payload recovery success.
5. **Separate Concerns** — Keep training code away from inference; GUI independent of core processing; configuration externalized.
6. **Memory Safety** — Handle large files safely; use chunked processing and memory mapping.
7. **Measure Before Claiming** — Report actual test results, not aspirational performance.

---

## 21. Traceability to Problem Statement

| Requirement | System Component | Status |
|:---|:---|:---|
| Accept `.IQ` and `.wav` files | Input Layer (`ingestion.py`) | ✓ In Scope |
| Extract sampling frequency ($F_s$) | Parameter Estimation Module | ✓ In Scope |
| Extract modulation type | ML AMC + DSP Features | ✓ In Scope |
| Extract FEC scheme | FEC Detection Engine | ✓ In Scope |
| Extract interleaving pattern | De-interleaver Detector | ✓ In Scope |
| Demodulate FSK, PSK, QAM | Demodulation Engine | ✓ In Scope |
| De-interleave block/conv/diag/PRNG | Four De-interleaver Modules | ✓ In Scope |
| Decode convolutional codes (Viterbi) | Viterbi Decoder Module | ✓ In Scope |
| Decode Reed-Solomon codes | RS Decoder Module | ✓ In Scope |
| Decode concatenated codes | Concatenated Decoder Module | ✓ In Scope |
| Decode LDPC codes | LDPC BP Decoder Module | ✓ In Scope |
| Perform bit-stream correlation | Correlation Engine | ✓ In Scope |
| Provide GUI with spectrum/waterfall/constellation | Visualization Layer | ✓ In Scope |
| Identify header and payload | Frame Sync Engine | ✓ In Scope |

---

## 22. Assumptions & Constraints

### Assumptions

- Single-signal input (not wideband multi-signal decomposition)
- Signals are not encrypted or proprietary (or if encrypted, only payload is encrypted)
- Sufficient SNR for detection (SNR ≥ −5 dB for reliable modulation classification)
- Symbol rate and sampling rate have known rational relationship
- Frame structures follow common standards or can be inferred from pattern analysis

### Constraints

- **Computational:** Must run on standard desktop/laptop hardware; GPU optional but not required
- **Data:** No guaranteed labeled dataset; must use synthetic data for initial training
- **Timeline:** 36-hour hackathon sprint (realistic prototype, not production-hardened)
- **Security:** Air-gapped operation required; no external network calls
- **Licensing:** All dependencies must be open-source or permissively licensed

---

## 23. Open Questions & Future Work

1. **FEC Detection:** How to automatically identify unknown FEC schemes? Constraint length search, BER minimization, or heuristics?
2. **Interleaver Identification:** Is parametric search (try all block sizes, depths) feasible within acceptable latency?
3. **Multi-Signal Handling:** Should the system support deconvolution of multiple overlapping signals in wideband captures?
4. **Real-Time SDR Integration:** Can the pipeline be upgraded to accept live I/Q streams from USRP, HackRF, etc.?
5. **Model Portability:** Should models be quantized (INT8, FP16) for deployment on embedded devices?
6. **Encrypted Payloads:** How should the system report on encrypted/encoded data that passes FEC checks structurally but contains unrecoverable content?

---

## 24. Document Governance

This System Design:

- **Is authoritative for:** Overall architecture, module responsibilities, technology choices, and phased roadmap
- **Is not a substitute for:**
  - Detailed Algorithm Design Specifications (per module)
  - Model Experiment Reports and Validation Data
  - Test Plans and Coverage Reports
  - Deployment Runbooks and Operations Manuals
  - Final Implementation Code Comments and API Documentation

**Document Updates:** Synchronize with significant implementation decisions; version incrementally.

---

## 25. References & Further Reading

### Problem Statement
- **Source:** Smart India Hackathon (SIH) 2026, Problem Statement 26147
- **Title:** Automated model for analysis of .IQ and .wav files along with signal parameter extraction
- **Organization:** National Technical Research Organisation (NTRO)

### Technical References
- **Modulation Classification:** Automatic Modulation Classification (AMC); RadioML dataset (O'Shea et al., 2016)
- **DSP:** Proakis & Salehi, *Digital Communications*, 6th ed.
- **FEC:** MacKay, *Information Theory, Inference, and Learning Algorithms* (LDPC); Lin & Costello, *Error Control Coding*, 2nd ed.
- **Synchronization:** Gardner, Carrier and Timing Recovery in Digital Receivers; Costas Loop analysis

### Open-Source Frameworks
- **GNU Radio:** RF signal capture, modulation generation, USRP interfacing
- **liquid-dsp:** DSP library (filtering, FEC, synchronization)
- **PySDR:** Python-based signal processing examples

---

## 26. Approval & Sign-Off

| Role | Name | Date | Signature |
|:---|:---|:---|:---|
| Technical Lead | — | — | — |
| Project Manager | — | — | — |
| NTRO Sponsor | — | — | — |

---

**Document Version:** 2.0 (Consolidated)  
**Last Updated:** September 2026  
**Status:** Ready for Implementation Planning
