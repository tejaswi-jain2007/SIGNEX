# **Project Charter & Vision Document**

**Project Title:** Automated Model for Analysis of .IQ and .wav Files along with Signal Parameter Extraction  
**Problem Statement ID:** ID26147  
Organization: National Technical Research Organisation (NTRO)  
Category: Software

# **1\. Problem Statement**

## **Background**

Signal Intelligence (SIGINT) and electronic surveillance sensors record off-the-air terrestrial radio frequency (RF) transmissions across HF, VHF, and UHF bands. These recordings are stored as raw complex baseband (.IQ) or real audio (.wav) files to preserve original waveform characteristics. However, signals collected from diverse sensors and locations lack standardized metadata, requiring manual inspection by analysts to determine signal parameters before processing can occur.

## **Core Problem**

Manual signal parameter extraction is slow, inconsistent, and often provides insufficient detail for fine-grained analysis. Raw files frequently lack essential parameters such as exact sampling rate, modulation type, interleaving pattern, and Forward Error Correction (FEC) structure. Furthermore, .IQ and .wav formats store information differently, demanding distinct digital signal processing (DSP) workflows. An automated, software-driven GUI application is needed to process both formats, extract spectral parameters, demodulate signals, perform de-interleaving and error correction, and recover header and payload structures through bitstream correlation.

# **2\. Goals**

* **Automated Parameter Extraction:** Automatically detect and compute sampling frequency, modulation type, FEC scheme, and interleaving type from input `.IQ` and `.wav` files.  
* **Unified Graphical User Interface (GUI):** Provide an intuitive desktop GUI with dynamic spectral visualizations, including dynamic 2D/3D waterfall plots (time-frequency domain) and constellation diagrams.  
* **Complete Signal Processing Pipeline:** Build a robust DSP chain capable of handling demodulation, de-interleaving, FEC decoding, and frame synchronization in a single workflow.  
* **Comprehensive Scheme Support:**  
  * **Demodulation:** FSK, PSK (BPSK, QPSK, 8PSK), and QAM (16-QAM, 64-QAM).  
  * **De-interleaving:** Block, Convolutional, Diagonal, and Pseudo-Random techniques.  
  * **FEC Decoding:** Viterbi decoding for short-constrained convolutional codes, Reed-Solomon (RS) block codes, Concatenated codes, and LDPC.  
* **Bitstream Correlation:** Enable cross-correlation of extracted bitstreams to identify sync words, frame headers, and payload structures.

# **3\. Target Users**

* **SIGINT Analysts & Technical Operators:** Defense and intelligence personnel responsible for inspecting unknown radio signals and extracting actionable payloads.  
* **Electronic Warfare (EW) & Defense Researchers:** Engineers at organizations like NTRO who test signal classification models and develop advanced DSP algorithms.  
* **Communication & DSP Engineers:** Developers validating modulation schemes, forward error correction performance, and channel coding resilience under noise.

# **4\. Success Criteria**

| Metric | Target Objective |
| :---- | :---- |
| **Classification Accuracy** | Achieve high accuracy (≥90%) in automatic modulation classification and sampling frequency estimation across varying Signal-to-Noise Ratios (SNR). |
| **UI Performance** | Smooth, high-FPS GUI rendering of waterfall spectrums and constellation plots without application lag. |
| **Verification** | Successful processing of test `.IQ` and `.wav` files from raw input to fully decoded payload text/data. |
| **Efficiency** | Decrease analyst workflow time from manual multi-tool inspection (taking 30+ minutes per file) to automated processing (taking seconds). |

# **5\. Scope**

## **In-Scope**

* Ingestion and parsing of raw `.IQ` (complex baseband) and `.wav` audio files.  
* Fast Fourier Transform (FFT) and spectral estimation for waterfall and constellation plotting.  
* Automatic parameter estimation (sampling rate, carrier offset, modulation type).  
* Demodulation algorithms for FSK, PSK, and QAM families.  
* De-interleaving engines for Block, Convolutional, Diagonal, and Pseudo-Random matrices.  
* FEC decoders for Viterbi (convolutional), Reed-Solomon, Concatenated, and LDPC codes.  
* Bitstream pattern correlation for header and payload separation.  
* Desktop GUI wrapper (built with PyQt6 / PySide6 / GNU Radio bindings).

## **Out-of-Scope**

* Live real-time RF capture hardware / Software-Defined Radio (SDR) hardware integration (focus is on post-capture file analysis).  
* Decryption of high-level cryptographic protocols or military-grade payload encryption beyond channel coding/FEC.  
* Cloud/SaaS hosting deployment (tool must operate as an air-gapped, offline desktop application for security compliance).

