# NTRO ID26147 — FINAL END-TO-END SYSTEM TEST MASTER

## Automated Model for Analysis of `.IQ` and `.wav` Files Along with Signal Parameter Extraction

**Purpose:** Professional QA/UAT master test specification for verifying the complete system against Problem Statement 26147, the consolidated SRS/PRD, system architecture, dataset/training handbook, and the existing 147-case Master Test Plan.

**Status:** Release-gate test specification
**Date:** September 2026
**Test ownership:** Product QA / DSP QA / ML QA / Security QA / UAT

> This document is intended to be the execution checklist. A test is not considered passed from screenshots alone: the tester must retain the relevant numeric result, exported artifact, log evidence, or screen recording where appropriate.

## 1. Authoritative Scope

The product baseline requires a GUI desktop system that ingests `.IQ` and `.wav`, performs signal inspection and parameter extraction, modulation analysis, demodulation, de-interleaving, FEC decoding, bitstream correlation, and reporting. The SRS defines FR-01 through FR-40 plus NFR-01 through NFR-08. The architecture explicitly uses deterministic DSP where physical parameters can be estimated, ML for learned classification, and deterministic decoders where coding is known.

### Critical compliance point

Do **not** claim full PS compliance merely because a decoder can be manually selected. The problem statement asks for identification/extraction of sampling frequency, modulation, FEC and interleaving. Therefore the test suite separately checks **automatic identification**, **manual override**, and **actual decoding**. Where the implementation only supports manual configuration, record the feature as a gap rather than marking the PS requirement as satisfied.

## 2. Release Severity

| Severity | Meaning | Release rule |
|---|---|---|
| P0 | Core PS path / data integrity / security failure | Release blocker |
| P1 | Major required feature or acceptance failure | Release blocker unless formally waived |
| P2 | Important non-critical defect | Must be triaged before release |
| P3 | Cosmetic/usability defect | Can be deferred with owner/date |

## 3. Mandatory Evidence Per Test

- Test ID and execution date
- Build/version/commit
- Input fixture name and SHA-256
- Dataset/model version where applicable
- Configuration/manual overrides
- Expected result
- Actual result
- Numeric metric where possible: accuracy, BER, SNR error, Fs error, latency, memory
- Exported artifact or log path
- Pass/Fail/Blocked
- Defect ID for every failure

## 4. Required Test Environments

| Environment | Minimum validation |
|---|---|
| Windows 10 x64 | Install, launch, full smoke, E2E |
| Windows 11 x64 | Install, launch, full smoke, E2E |
| Ubuntu 22.04 LTS | Install, launch, full smoke, E2E |
| RHEL 9 | Install/launch/support validation |
| CPU reference | 8-core CPU, 16 GB RAM for NFR benchmarks |
| GPU reference | NVIDIA/CUDA system where GPU path exists |
| Air-gapped | Network fully disconnected/blocked |
| Low-memory | Resource-constrained test environment |

## 5. Golden Test Data Matrix

| ID | Fixture | Purpose | Ground truth required |
|---|---|---|---|
| G-IQ-F32 | Float32 complex IQ | Input parsing | Exact I/Q samples |
| G-IQ-I16 | Int16 complex IQ | Scaling/parsing | Exact source samples |
| G-IQ-I8 | Int8 complex IQ | Scaling/parsing | Exact source samples |
| G-WAV-16 | PCM16 WAV | WAV parsing | Header + samples |
| G-WAV-24 | PCM24 WAV | WAV parsing | Header + samples |
| G-WAV-32 | PCM32 WAV | WAV parsing | Header + samples |
| G-WAV-F32 | Float32 WAV | WAV parsing | Header + samples |
| G-BPSK | BPSK | Demod/AMC | Bits, symbols, Fs, Rs, SNR |
| G-QPSK | QPSK | Demod/AMC | Bits, symbols, Fs, Rs, SNR |
| G-8PSK | 8PSK | Demod/AMC | Bits, symbols |
| G-2FSK | 2FSK | Demod/AMC | Bits, tone spacing |
| G-4FSK | 4FSK | Demod/AMC | Bits, tone mapping |
| G-16QAM | 16QAM | Demod/AMC | Bits, mapping |
| G-64QAM | 64QAM | Demod/AMC | Bits, mapping |
| G-BLK-INT | Block interleaved | De-interleave | Original bits + dimensions |
| G-CONV-INT | Convolutional interleaved | De-interleave | Original bits + taps |
| G-DIAG-INT | Diagonal | De-interleave | Original bits + permutation |
| G-PRNG-INT | Pseudo-random | De-interleave | Original bits + seed |
| G-CONV-FEC | Convolutional code | Viterbi | Source bits + K/rate/generators |
| G-RS | Reed-Solomon | RS decoder | Source bytes + n/k |
| G-CONCAT | RS + convolutional | Concatenated decoder | Source bytes/bits + params |
| G-LDPC | LDPC | BP decoder | Source bits + H matrix |
| G-FRAME | Preamble/header/payload/CRC | Correlation | Exact boundaries |
| G-LOW-SNR | 5 dB and lower | Robustness | Known injected SNR |
| G-CFO | Positive/negative CFO | Synchronization | Exact offset |
| G-TIMING | Timing offset | Timing recovery | Exact fractional offset |
| G-FADING | Fading channel | Robustness | Known channel configuration |
| G-CORRUPT-IQ | Truncated/malformed | Failure handling | Expected failure |
| G-CORRUPT-WAV | Malformed RIFF/data | Failure handling | Expected failure |
| G-LARGE-IQ | 100 MB and 2 GB | Performance/streaming | File size/hash |

## 6. Test Execution Order

1. Installation and environment smoke
2. Input ingestion and data integrity
3. Preprocessing
4. Visualization
5. Parameter extraction
6. AMC
7. Synchronization and demodulation
8. De-interleaving
9. FEC
10. Correlation/frame extraction
11. GUI workflow and cancellation
12. Reporting/provenance
13. Performance/stress
14. Security/air-gap
15. Dataset/model QA
16. Full end-to-end golden paths
17. Regression suite
18. Final acceptance gates

## 7. New Professional QA Overlay

**New QA overlay test count: 443**

| ID | Level | Requirement | Test / Check | Preconditions | Action | Expected | Pass Gate |
|---|---|---|---|---|---|---|---|
| ENV-001 | System | NFR-04, NFR-02 | Clean install on Windows 10 | Clean Windows 10 x64 reference machine | Install packaged application; launch; inspect bundled dependencies | Application launches without missing-runtime prompts and all core modules load | PASS only if clean install works |
| ENV-002 | System | NFR-04, NFR-02 | Clean install on Windows 11 | Clean Windows 11 x64 reference machine | Install and launch | Application launches and analyzes a golden signal | PASS only if end-to-end smoke test passes |
| ENV-003 | System | NFR-04, NFR-02 | Clean install on Ubuntu 22.04 | Clean Ubuntu 22.04 x64 reference machine | Install package; launch; run smoke test | No manual runtime installation required beyond documented installer behavior | PASS only if smoke test passes |
| ENV-004 | System | NFR-04, NFR-02 | Clean install on RHEL 9 | Clean RHEL 9 reference machine | Install; launch; run smoke test | Application operates or clearly documents unsupported packaging state | PASS only if support claim matches reality |
| ENV-005 | System | NFR-04, NFR-02 | Launch with no network | All network adapters disabled | Launch application; load bundled model; analyze golden file | No startup network dependency | Mandatory for offline claim |
| ENV-006 | System | NFR-04, NFR-02 | Launch with blocked DNS | DNS requests blocked | Launch and analyze | No retries/timeouts caused by external services | Zero external dependency |
| ENV-007 | System | NFR-04, NFR-02 | Missing model artifact | Temporarily remove/rename model file | Launch app | Actionable diagnostic identifies missing model and safe recovery path | No crash |
| ENV-008 | System | NFR-04, NFR-02 | Missing config | Temporarily remove user config | Launch app | Safe defaults or explicit configuration recovery is applied | No crash |
| ENV-009 | System | NFR-04, NFR-02 | Corrupt model artifact | Replace model with invalid bytes | Launch or initialize inference | Integrity error is surfaced; arbitrary code is not executed | Secure failure |
| ENV-010 | System | NFR-04, NFR-02 | Version mismatch between model and runtime | Model metadata version intentionally incompatible | Run inference | Mismatch is detected or safely rejected | No silent incompatible inference |
| ENV-011 | System | NFR-04, NFR-02 | GPU unavailable | CPU-only machine | Launch and run AMC | System falls back to CPU without functional failure | Core functionality remains available |
| ENV-012 | System | NFR-04, NFR-02 | GPU present but CUDA unavailable | NVIDIA system with incompatible/missing CUDA runtime | Launch and run AMC | Graceful CPU fallback or clear actionable error | No crash |
| ENV-013 | System | NFR-04, NFR-02 | Insufficient disk space | Test environment with constrained free space | Export large report/result | Operation fails cleanly without corrupting prior results | Data integrity preserved |
| ENV-014 | System | NFR-04, NFR-02 | Read-only install directory | Application installed where executable directory is read-only | Launch and analyze | Writable runtime data is redirected to supported user data location | No permission crash |
| ENV-015 | System | NFR-04, NFR-02 | Non-ASCII user path | Application/data path contains Unicode characters | Load and analyze signal | Path is handled correctly | No encoding/path failure |
| ENV-016 | System | NFR-04, NFR-02 | Spaces in file path | Signal located in path with spaces | Open via GUI and process | Correct file is loaded | No path parsing bug |
| ENV-017 | System | NFR-04, NFR-02 | Very long path | Signal at long but supported filesystem path | Open and export | Path handling is safe or clear platform limitation is shown | No truncation or wrong-file access |
| ENV-018 | System | NFR-04, NFR-02 | First-run initialization | Clean user profile | Launch and observe first-run setup | Initialization completes once and creates required local state | No hidden network action |
| ENV-019 | System | NFR-04, NFR-02 | Application restart after crash | Terminate process during test analysis | Relaunch and inspect state/logs | Application restarts safely and prior input is not silently corrupted | Recovery evidence recorded |
| ENV-020 | System | NFR-04, NFR-02 | Installer/uninstaller cleanup | Installed application | Uninstall then inspect | No critical executable/runtime residue remains except documented user data | Cleanup matches installer policy |
| ING2-001 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | WAV PCM 16-bit mono | Valid RIFF PCM16 mono | Open and inspect metadata/sample array | Sample rate, channels, bit depth, duration and samples are correct | Zero metadata mismatch |
| ING2-002 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | WAV PCM 24-bit | Valid RIFF PCM24 | Open and compare reference samples | 24-bit decoding is byte-accurate | Reference match |
| ING2-003 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | WAV PCM 32-bit | Valid RIFF PCM32 | Open and compare | 32-bit PCM is decoded correctly | Reference match |
| ING2-004 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | WAV IEEE float32 | Valid IEEE float32 WAV | Open and compare | Float samples preserve sign, scale and count | Reference match |
| ING2-005 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | WAV stereo channel preservation | Known L/R test tone | Load and inspect channels separately | Channels remain separated with no cross-talk | Channel correlation matches fixture |
| ING2-006 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | WAV extra metadata chunks | WAV with LIST/JUNK/custom chunks | Load | Data chunk is located correctly; nonessential chunks do not break parsing | Waveform exact |
| ING2-007 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | WAV malformed RIFF size | Header size intentionally wrong | Load | Malformed file is rejected or bounded safely | No out-of-bounds read |
| ING2-008 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | WAV truncated data chunk | Data shorter than header claims | Load | Incomplete file is reported clearly | No silent padding |
| ING2-009 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | IQ float32 little-endian | Known complex fixture | Load with correct format | I/Q values match reference | Exact within float tolerance |
| ING2-010 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | IQ int16 little-endian | Known complex fixture | Load | Scaling and sign extension are correct | Exact within tolerance |
| ING2-011 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | IQ int8 | Known complex fixture | Load | Scaling is documented and correct | Reference match |
| ING2-012 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | IQ big-endian | Known BE fixture | Load with BE setting | Samples match reference | Reference match |
| ING2-013 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | IQ wrong endianness | BE file loaded as LE or vice versa | Load | Corruption is detectable and not silently treated as correct | Diagnostic/warning shown |
| ING2-014 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | IQ odd scalar count | Odd number of interleaved scalar values | Load | Incomplete final I/Q pair is detected | No data shift |
| ING2-015 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | IQ empty file | 0-byte file | Load | Clear empty-file error | No pipeline start |
| ING2-016 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | IQ huge file streaming | 2 GB synthetic IQ | Load and run partial analysis | Chunked processing occurs without full RAM materialization | Memory remains within budget |
| ING2-017 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | IQ sidecar metadata | IQ plus valid JSON metadata | Load | Sidecar metadata is read and provenance records source | Fields match sidecar |
| ING2-018 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | Missing IQ metadata | Raw IQ without sample-rate metadata | Load | System marks unknown values and exposes manual entry | No fabricated Fs |
| ING2-019 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | Conflicting metadata sources | Filename and sidecar disagree | Load | Conflict is surfaced and resolution is explicit | No silent choice |
| ING2-020 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | Sample-count integrity | Known-length fixture | Load and compare count | Loaded complex sample count matches expected | 100% count match |
| ING2-021 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | Unsupported extension | Random unsupported file | Attempt load | Unsupported format message appears | Application stable |
| ING2-022 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | Wrong-content extension | Random bytes named .wav | Open | Header/content validation rejects it | No crash |
| ING2-023 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | Permission denied input | Unreadable signal file | Attempt open | Actionable permission error | No crash |
| ING2-024 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | Symlink input | Supported symlink policy | Open signal through symlink | Behavior matches documented policy and avoids unsafe traversal | Policy-compliant |
| ING2-025 | Integration/System | FR-01–FR-03, NFR-06, NFR-08 | Original input immutability | Writable source file | Analyze, cancel, export | Input bytes/hash remain unchanged | Pre/post hash identical |
| PRE2-001 | Unit/Integration | FR-03, NFR-06, NFR-08 | DC removal zero-mean | Signal with known DC offset | Run preprocessing | Post-DC mean is near zero within configured tolerance | Tolerance documented |
| PRE2-002 | Unit/Integration | FR-03, NFR-06, NFR-08 | DC removal preserves modulation | Modulated signal + DC | Run preprocessing then demodulate | Demodulated payload matches clean reference | No introduced BER beyond tolerance |
| PRE2-003 | Unit/Integration | FR-03, NFR-06, NFR-08 | IQ amplitude imbalance correction | Known gain skew | Preprocess | I/Q power ratio moves toward calibrated balance | Residual skew within target |
| PRE2-004 | Unit/Integration | FR-03, NFR-06, NFR-08 | IQ phase imbalance correction | Known phase skew | Preprocess | Quadrature relationship improves | Residual error within target |
| PRE2-005 | Unit/Integration | FR-03, NFR-06, NFR-08 | Power normalization bounds | Wide dynamic range IQ | Normalize | Samples remain finite and within declared normalization behavior | No clipping unless source already clipped |
| PRE2-006 | Unit/Integration | FR-03, NFR-06, NFR-08 | Constant-zero signal | All-zero IQ | Preprocess | No divide-by-zero; result marked degenerate | Graceful status |
| PRE2-007 | Unit/Integration | FR-03, NFR-06, NFR-08 | NaN/Inf input detection | Fixture containing non-finite values | Preprocess | Non-finite data is rejected or sanitized per documented policy | No propagation to downstream stage |
| PRE2-008 | Unit/Integration | FR-03, NFR-06, NFR-08 | Clipping detection | Int16 full-scale clipped waveform | Load/preprocess | Clipping warning is raised | Warning visible |
| PRE2-009 | Unit/Integration | FR-03, NFR-06, NFR-08 | Resampling identity | Signal at target rate | Apply optional resampling factor 1 | Samples/phase preserved | Reference match |
| PRE2-010 | Unit/Integration | FR-03, NFR-06, NFR-08 | Resampling anti-alias | High-rate tone above target Nyquist | Decimate | Out-of-band content is attenuated | Measured attenuation meets config |
| PRE2-011 | Unit/Integration | FR-03, NFR-06, NFR-08 | Preprocessing repeatability | Same input and settings | Run twice | Outputs are identical within float tolerance | Deterministic |
| PRE2-012 | Unit/Integration | FR-03, NFR-06, NFR-08 | Preprocessing immutability | Known source array | Run all preprocessing | Source object remains unchanged | Hash/equality preserved |
| PRE2-013 | Unit/Integration | FR-03, NFR-06, NFR-08 | Chunk-boundary consistency | Signal processed as one chunk and many chunks | Run both | Outputs align within numerical tolerance | No chunk artifact |
| PRE2-014 | Unit/Integration | FR-03, NFR-06, NFR-08 | Windowed processing equivalence | Signal longer than streaming window | Process full and chunked | Aggregate features are consistent | Deviation within tolerance |
| PRE2-015 | Unit/Integration | FR-03, NFR-06, NFR-08 | Gain metadata preservation | Input includes gain metadata | Preprocess | Gain context is preserved in provenance | No provenance loss |
| PRE2-016 | Unit/Integration | FR-03, NFR-06, NFR-08 | Manual preprocessing override | User override enabled | Disable auto DC removal or change normalization | User choice is applied and recorded | Provenance contains override |
| PRE2-017 | Unit/Integration | FR-03, NFR-06, NFR-08 | Cancellation during preprocessing | Long preprocessing job | Cancel mid-stage | Worker stops safely and partial state is not presented as complete | No orphan process |
| PRE2-018 | Unit/Integration | FR-03, NFR-06, NFR-08 | Error propagation | Injected preprocessing failure | Run pipeline | Failure is logged, surfaced, and downstream stages do not consume invalid output | Stage status correct |
| VIS2-001 | System/UI | FR-04–FR-08, FR-10, NFR-03 | Waveform rendering | Valid signal loaded | Open waveform view | Amplitude vs time is displayed with correct scale | Visual/reference check passes |
| VIS2-002 | System/UI | FR-04–FR-08, FR-10, NFR-03 | Waveform zoom | Waveform visible | Zoom in/out | Windowed samples and axes update correctly | No stale plot |
| VIS2-003 | System/UI | FR-04–FR-08, FR-10, NFR-03 | Waveform pan | Waveform visible | Pan across signal | Displayed region follows user action | No data jump |
| VIS2-004 | System/UI | FR-04–FR-08, FR-10, NFR-03 | FFT 512 | Signal loaded | Select FFT=512 | Spectrum uses 512-point transform | Metadata/control matches |
| VIS2-005 | System/UI | FR-04–FR-08, FR-10, NFR-03 | FFT 1024 | Signal loaded | Select FFT=1024 | Correct frequency bin spacing | Reference match |
| VIS2-006 | System/UI | FR-04–FR-08, FR-10, NFR-03 | FFT 2048 | Signal loaded | Select FFT=2048 | Correct output | Reference match |
| VIS2-007 | System/UI | FR-04–FR-08, FR-10, NFR-03 | FFT 4096 | Signal loaded | Select FFT=4096 | Correct output | Reference match |
| VIS2-008 | System/UI | FR-04–FR-08, FR-10, NFR-03 | FFT 8192 | Signal loaded | Select FFT=8192 | Correct output and meets timing budget | <50 ms benchmark |
| VIS2-009 | System/UI | FR-04–FR-08, FR-10, NFR-03 | Window Hann | Signal loaded | Select Hann | Window coefficients and spectrum match reference | Numerical match |
| VIS2-010 | System/UI | FR-04–FR-08, FR-10, NFR-03 | Window Hamming | Signal loaded | Select Hamming | Correct spectrum | Numerical match |
| VIS2-011 | System/UI | FR-04–FR-08, FR-10, NFR-03 | Window Blackman-Harris | Signal loaded | Select Blackman-Harris | Correct spectrum | Numerical match |
| VIS2-012 | System/UI | FR-04–FR-08, FR-10, NFR-03 | Window Rectangular | Signal loaded | Select rectangular | Correct spectrum | Numerical match |
| VIS2-013 | System/UI | FR-04–FR-08, FR-10, NFR-03 | Waterfall frequency axis | Known tone | Open waterfall | Tone occupies expected frequency bin | Frequency error within tolerance |
| VIS2-014 | System/UI | FR-04–FR-08, FR-10, NFR-03 | Waterfall time axis | Known periodic signal | Inspect time progression | Time spacing is consistent with Fs | No time-scale drift |
| VIS2-015 | System/UI | FR-04–FR-08, FR-10, NFR-03 | Waterfall dynamic range | Signal + noise | Adjust dB range | Visible dynamic range changes without altering source | UI value applied |
| VIS2-016 | System/UI | FR-04–FR-08, FR-10, NFR-03 | Waterfall overlap 50/75/87.5 | Long signal | Cycle overlap settings | Expected frame count changes consistently | No indexing errors |
| VIS2-017 | System/UI | FR-04–FR-08, FR-10, NFR-03 | PSD peak labeling | Single-tone fixture | Open PSD | Peak is detected near known frequency | Peak error within tolerance |
| VIS2-018 | System/UI | FR-04–FR-08, FR-10, NFR-03 | Noise floor display | Known AWGN fixture | Open PSD | Noise floor estimate is stable | Within reference tolerance |
| VIS2-019 | System/UI | FR-04–FR-08, FR-10, NFR-03 | 3 dB bandwidth marker | Known modulated waveform | Open PSD | Marker spans expected bandwidth | Within defined tolerance |
| VIS2-020 | System/UI | FR-04–FR-08, FR-10, NFR-03 | Constellation display | Known PSK/QAM signal | Open constellation | Expected symbol geometry is visible | Matches reference pattern |
| VIS2-021 | System/UI | FR-04–FR-08, FR-10, NFR-03 | Constellation persistence | Signal stream | Enable trails and vary persistence | Trail length changes as configured | No plot corruption |
| VIS2-022 | System/UI | FR-04–FR-08, FR-10, NFR-03 | Constellation density mapping | Noisy constellation | Enable density coloring | Density corresponds to sample distribution | Qualitative + numerical spot check |
| VIS2-023 | System/UI | FR-04–FR-08, FR-10, NFR-03 | 2D/3D waterfall claim check | Build matching UI if specified | Inspect available visualization modes | Implementation status explicitly matches product scope | No undocumented capability claim |
| PAR2-001 | DSP/System | FR-09–FR-14, PS parameter extraction | WAV Fs from header | WAV with known sample rate | Run analysis | Reported Fs equals RIFF Fs | Exact match |
| PAR2-002 | DSP/System | FR-09–FR-14, PS parameter extraction | IQ Fs unknown state | Raw IQ with no metadata and ambiguous signal | Run auto analysis | Fs reported unknown rather than invented | No fabricated value |
| PAR2-003 | DSP/System | FR-09–FR-14, PS parameter extraction | IQ Fs metadata | IQ + authoritative sidecar | Run analysis | Fs taken from metadata and labeled as metadata-derived | Provenance correct |
| PAR2-004 | DSP/System | FR-09–FR-14, PS parameter extraction | Fs ±2% synthetic validation | Synthetic cases with known Fs | Run estimator over benchmark set | Absolute relative error ≤2% where estimator is expected to work | FR-09 gate |
| PAR2-005 | DSP/System | FR-09–FR-14, PS parameter extraction | Fs low-SNR uncertainty | Low-SNR signals | Estimate Fs | Confidence falls or unknown is reported when evidence is insufficient | No false certainty |
| PAR2-006 | DSP/System | FR-09–FR-14, PS parameter extraction | Symbol-rate estimation clean | Known Rs digital signal | Run estimator | Rs estimate is within configured tolerance | Reference comparison |
| PAR2-007 | DSP/System | FR-09–FR-14, PS parameter extraction | Symbol-rate estimation noisy | Known Rs + AWGN | Run estimator across SNR levels | Error degrades predictably and uncertainty is visible | No silent overclaim |
| PAR2-008 | DSP/System | FR-09–FR-14, PS parameter extraction | 99% occupied bandwidth | Known synthetic waveform | Run bandwidth estimator | Estimate matches generated occupied-power definition | Tolerance defined by fixture |
| PAR2-009 | DSP/System | FR-09–FR-14, PS parameter extraction | 3 dB bandwidth | Known pulse-shaped signal | Run 3 dB estimator | Bandwidth marker is correct | Reference match |
| PAR2-010 | DSP/System | FR-09–FR-14, PS parameter extraction | SNR high | 20 dB reference | Estimate SNR | Estimate near known SNR | Tolerance documented |
| PAR2-011 | DSP/System | FR-09–FR-14, PS parameter extraction | SNR low | 5 dB reference | Estimate SNR | Estimate and confidence are reported | Within validation tolerance |
| PAR2-012 | DSP/System | FR-09–FR-14, PS parameter extraction | Noise-only SNR | Noise-only signal | Estimate SNR | System reports no meaningful signal / SNR unavailable | No misleading positive signal |
| PAR2-013 | DSP/System | FR-09–FR-14, PS parameter extraction | Carrier frequency offset positive | Known +CFO | Run CFO estimator | Estimated sign and magnitude are correct | Within tolerance |
| PAR2-014 | DSP/System | FR-09–FR-14, PS parameter extraction | Carrier frequency offset negative | Known -CFO | Run CFO estimator | Estimated sign and magnitude are correct | Within tolerance |
| PAR2-015 | DSP/System | FR-09–FR-14, PS parameter extraction | CFO correction vector | Known CFO | Run analysis and inspect correction | Correction is opposite-signed and usable by synchronizer | Residual CFO reduced |
| PAR2-016 | DSP/System | FR-09–FR-14, PS parameter extraction | Spectral centroid | Known asymmetric spectrum | Compute feature | Centroid matches numerical reference | Numerical tolerance |
| PAR2-017 | DSP/System | FR-09–FR-14, PS parameter extraction | Spectral kurtosis | Known waveform families | Compute feature | Value matches reference implementation | Numerical tolerance |
| PAR2-018 | DSP/System | FR-09–FR-14, PS parameter extraction | C40 feature | Known modulation fixture | Compute cumulant | C40 matches reference | Numerical tolerance |
| PAR2-019 | DSP/System | FR-09–FR-14, PS parameter extraction | C42 feature | Known modulation fixture | Compute cumulant | C42 matches reference | Numerical tolerance |
| PAR2-020 | DSP/System | FR-09–FR-14, PS parameter extraction | Feature determinism | Same signal twice | Compute features twice | Same output within float tolerance | Deterministic |
| PAR2-021 | DSP/System | FR-09–FR-14, PS parameter extraction | Feature NaN handling | Degenerate signal | Compute all features | Undefined metrics are marked unavailable, not NaN-propagated into classifier | Graceful |
| PAR2-022 | DSP/System | FR-09–FR-14, PS parameter extraction | Parameter confidence | High-confidence fixture | Inspect result object | Each estimated parameter has confidence/evidence where designed | No missing required fields |
| PAR2-023 | DSP/System | FR-09–FR-14, PS parameter extraction | Parameter provenance | Mixed metadata/estimated case | Inspect report | Each value indicates source/method | Traceable |
| PAR2-024 | DSP/System | FR-09–FR-14, PS parameter extraction | Parameter manual override | Known wrong auto result | Override Fs/Rs/CFO | Downstream analysis uses override and result records it | Override effective |
| PAR2-025 | DSP/System | FR-09–FR-14, PS parameter extraction | Subset re-analysis | Long signal with known event | Select time/frequency window and rerun | Parameters correspond to selected subset | No stale global results |
| PAR2-026 | DSP/System | FR-09–FR-14, PS parameter extraction | Parameter cross-stage consistency | Known QPSK fixture | Compare Fs, Rs, bandwidth | Values are internally consistent | No physically contradictory result |
| PAR2-027 | DSP/System | FR-09–FR-14, PS parameter extraction | Unsupported estimation case | Signal outside estimator assumptions | Run | System states unsupported/unknown with reason | No fabricated estimate |
| AMC2-001 | ML/System | FR-11–FR-12, dataset handbook | BPSK classification clean | High-SNR labeled BPSK benchmark | Run AMC | BPSK selected with high confidence | Correct label |
| AMC2-002 | ML/System | FR-11–FR-12, dataset handbook | QPSK classification clean | High-SNR QPSK benchmark | Run AMC | QPSK selected | Correct label |
| AMC2-003 | ML/System | FR-11–FR-12, dataset handbook | 8PSK classification clean | High-SNR 8PSK benchmark | Run AMC | 8PSK selected | Correct label |
| AMC2-004 | ML/System | FR-11–FR-12, dataset handbook | 2FSK classification clean | High-SNR 2FSK benchmark | Run AMC | 2FSK/FSK family selected according to taxonomy | Correct taxonomy |
| AMC2-005 | ML/System | FR-11–FR-12, dataset handbook | 4FSK classification clean | High-SNR 4FSK benchmark | Run AMC | 4FSK selected | Correct label |
| AMC2-006 | ML/System | FR-11–FR-12, dataset handbook | 16QAM classification clean | High-SNR 16QAM benchmark | Run AMC | 16QAM selected | Correct label |
| AMC2-007 | ML/System | FR-11–FR-12, dataset handbook | 64QAM classification clean | High-SNR 64QAM benchmark | Run AMC | 64QAM selected | Correct label |
| AMC2-008 | ML/System | FR-11–FR-12, dataset handbook | PSK subtype separation | BPSK/QPSK/8PSK mixed set | Run AMC | Subtypes are separated according to supported taxonomy | Confusion matrix reviewed |
| AMC2-009 | ML/System | FR-11–FR-12, dataset handbook | QAM subtype separation | 16/64QAM mixed set | Run AMC | Subtypes separated where supported | Confusion matrix reviewed |
| AMC2-010 | ML/System | FR-11–FR-12, dataset handbook | AM/FM detection | Supported analog detection fixture | Run AMC | AM/FM detection status follows declared scope | No false claim of digital decoding |
| AMC2-011 | ML/System | FR-11–FR-12, dataset handbook | SNR sweep | Benchmark set at SNR from low to high | Run AMC | Accuracy-vs-SNR curve is produced | Metrics stored |
| AMC2-012 | ML/System | FR-11–FR-12, dataset handbook | ≥90% benchmark accuracy | Held-out benchmark SNR≥5 dB | Evaluate full test set | Overall AMC accuracy meets ≥90% | FR-11 gate |
| AMC2-013 | ML/System | FR-11–FR-12, dataset handbook | Per-class recall | Held-out benchmark | Compute per-class metrics | No class is hidden by aggregate-only reporting | Per-class report present |
| AMC2-014 | ML/System | FR-11–FR-12, dataset handbook | Confusion matrix | Held-out benchmark | Generate matrix | All supported classes appear | Artifact saved |
| AMC2-015 | ML/System | FR-11–FR-12, dataset handbook | Top-N alternatives | Ambiguous low-SNR fixture | Run AMC | Top-N alternatives and scores are reported | FR-12 gate |
| AMC2-016 | ML/System | FR-11–FR-12, dataset handbook | Confidence calibration | Validation labels + probabilities | Compute calibration metrics | Confidence scores are monotonic/useful enough for review | Calibration report |
| AMC2-017 | ML/System | FR-11–FR-12, dataset handbook | Low-confidence flag | Ambiguous signal | Run AMC | Manual review flag appears | No false certainty |
| AMC2-018 | ML/System | FR-11–FR-12, dataset handbook | Tier 1 vs Tier 2 disagreement | Fixture engineered to create disagreement | Run hybrid classifier | Both outputs + combined/conflict status are shown | Conflict not hidden |
| AMC2-019 | ML/System | FR-11–FR-12, dataset handbook | Model unavailable | Inference model missing | Run AMC | App reports model unavailable and does not fabricate result | Graceful |
| AMC2-020 | ML/System | FR-11–FR-12, dataset handbook | Model version provenance | Known model artifact | Run AMC/export | Model version/hash stored | FR-40 gate |
| AMC2-021 | ML/System | FR-11–FR-12, dataset handbook | Cross-dataset RadioML 2018 | Model trained per handbook | Evaluate on 2018 set | Generalization metrics are produced | No training contamination |
| AMC2-022 | ML/System | FR-11–FR-12, dataset handbook | Cross-dataset HisarMod | Model trained on RadioML | Evaluate on HisarMod holdout | Cross-dataset performance is measured independently | No leakage |
| AMC2-023 | ML/System | FR-11–FR-12, dataset handbook | Real-data transfer | Authorized real capture | Run without retraining on test data | Performance and failure modes are logged | Separate real-world report |
| AMC2-024 | ML/System | FR-11–FR-12, dataset handbook | Window-length shift | 128-sample trained model, 1024-sample evaluation path | Evaluate using supported preprocessing | Input adaptation is correct or limitation is explicit | No shape crash |
| AMC2-025 | ML/System | FR-11–FR-12, dataset handbook | Inference determinism | Same model/input/config | Run 10 times | Same class and equivalent probabilities within tolerance | Reproducible |
| AMC2-026 | ML/System | FR-11–FR-12, dataset handbook | Seed control | Model with stochastic layers disabled for inference | Run twice under same config | Deterministic output | No random drift |
| AMC2-027 | ML/System | FR-11–FR-12, dataset handbook | Unknown modulation | Unsupported modulation fixture | Run AMC | Unknown/out-of-scope state is returned | No forced known class |
| DEM2-001 | DSP/Integration | FR-15–FR-19 | BPSK clean demodulation | Known BPSK waveform | Sync, demod, compare bits | Recovered bits match source | BER=0 on clean fixture |
| DEM2-002 | DSP/Integration | FR-15–FR-19 | BPSK phase offset | BPSK with known phase offset | Run Costas/PLL then demod | Bit recovery remains correct | BER within tolerance |
| DEM2-003 | DSP/Integration | FR-15–FR-19 | BPSK frequency offset | BPSK + CFO | Estimate/correct CFO, demod | Payload recovered | Residual BER acceptable |
| DEM2-004 | DSP/Integration | FR-15–FR-19 | BPSK timing offset | BPSK with fractional timing offset | Run timing recovery | Symbol decisions recover source | BER target met |
| DEM2-005 | DSP/Integration | FR-15–FR-19 | QPSK clean demodulation | Known QPSK | Demod and compare | Bits match source | BER=0 |
| DEM2-006 | DSP/Integration | FR-15–FR-19 | QPSK 45-degree rotation | Known rotated QPSK | Recover carrier phase | Correct symbol mapping after sync | BER target met |
| DEM2-007 | DSP/Integration | FR-15–FR-19 | QPSK CFO + noise | QPSK with CFO and AWGN | Run full sync/demod | Recovered bits within expected BER | Reference curve |
| DEM2-008 | DSP/Integration | FR-15–FR-19 | 8PSK clean demodulation | Known 8PSK | Demod | Symbols/bits match | BER=0 |
| DEM2-009 | DSP/Integration | FR-15–FR-19 | 8PSK phase ambiguity handling | 8PSK with carrier ambiguity | Run synchronization | Phase ambiguity is resolved or explicitly reported | No silent bit inversion |
| DEM2-010 | DSP/Integration | FR-15–FR-19 | 2FSK clean demodulation | Known 2FSK | Demod | Recovered bits match | BER=0 |
| DEM2-011 | DSP/Integration | FR-15–FR-19 | 2FSK tone spacing | Known deviation and symbol rate | Measure instantaneous frequency/demodulate | Tone decisions align with reference | Correct tone mapping |
| DEM2-012 | DSP/Integration | FR-15–FR-19 | 4FSK clean demodulation | Known 4FSK | Demod | 4-level symbols map correctly | BER=0 |
| DEM2-013 | DSP/Integration | FR-15–FR-19 | 4FSK frequency offset | 4FSK + CFO | Sync and demod | Tone classification remains correct | BER target |
| DEM2-014 | DSP/Integration | FR-15–FR-19 | 16QAM clean demodulation | Known 16QAM Gray-mapped | Equalize/sync/demod | Bits match source | BER=0 |
| DEM2-015 | DSP/Integration | FR-15–FR-19 | 16QAM amplitude impairment | 16QAM with gain/scale change | Run AGC/equalizer/demod | Constellation recovers | BER target |
| DEM2-016 | DSP/Integration | FR-15–FR-19 | 64QAM clean demodulation | Known 64QAM | Demod | Bits match source | BER=0 |
| DEM2-017 | DSP/Integration | FR-15–FR-19 | 64QAM noise | 64QAM + AWGN | Demod | BER follows expected impairment | Reference comparison |
| DEM2-018 | DSP/Integration | FR-15–FR-19 | LLR output PSK | Soft-decision demod enabled | Run BPSK/QPSK/8PSK | LLRs are finite, signed correctly and mapped to bits | Decoder-compatible |
| DEM2-019 | DSP/Integration | FR-15–FR-19 | Hard-bit output | Hard-decision mode | Run demod | 0/1 bitstream is emitted with exact length | Length and values correct |
| DEM2-020 | DSP/Integration | FR-15–FR-19 | LLR vs hard consistency | High-SNR signal | Run both modes | Hard decisions equal LLR sign decisions | Consistency |
| DEM2-021 | DSP/Integration | FR-15–FR-19 | Gardner timing recovery | Oversampled PSK fixture | Run timing recovery | Timing error converges | Stable lock |
| DEM2-022 | DSP/Integration | FR-15–FR-19 | Mueller-Muller timing recovery | Oversampled PSK fixture | Run M&M | Timing error converges | Stable lock |
| DEM2-023 | DSP/Integration | FR-15–FR-19 | Timing loop failure | Extreme timing offset/noise | Run demod | Lock failure is detected and reported | No misleading output |
| DEM2-024 | DSP/Integration | FR-15–FR-19 | Carrier loop failure | Extreme CFO/phase noise | Run demod | Failure/low-confidence state shown | No silent garbage |
| DEM2-025 | DSP/Integration | FR-15–FR-19 | Bit-length accounting | Known symbol count and modulation order | Demod | Output bit count equals expected mapping length | Exact length |
| DEM2-026 | DSP/Integration | FR-15–FR-19 | Preamble preservation | Frame with known preamble | Demodulate | Preamble remains aligned | Offset tracked |
| DEM2-027 | DSP/Integration | FR-15–FR-19 | Frame-start offset | Signal begins mid-symbol | Run synchronization | System either reacquires or reports unresolved timing | No false success |
| DEM2-028 | DSP/Integration | FR-15–FR-19 | Burst noise | Signal + impulse noise | Demod | Failure rate and BER reported | No crash |
| DEM2-029 | DSP/Integration | FR-15–FR-19 | Rayleigh fading | Fading fixture | Demod | Performance is measured; severe failure is reported | No silent success |
| DEM2-030 | DSP/Integration | FR-15–FR-19 | Sample clipping | Clipped digital signal | Demod | Output reflects degraded quality and warns | Warning present |
| DEM2-031 | DSP/Integration | FR-15–FR-19 | Modulation override | AMC intentionally wrong | User overrides modulation | Selected demodulator runs and provenance records override | FR-32 |
| DEM2-032 | DSP/Integration | FR-15–FR-19 | Independent demod stage | Known synchronized input | Run demod module without upstream AMC | Module accepts explicit config and produces output | FR-33 |
| DEM2-033 | DSP/Integration | FR-15–FR-19 | Demod cancellation | Long demodulation run | Cancel | Worker terminates cleanly and no partial completion is reported as final | FR-36 |
| DEM2-034 | DSP/Integration | FR-15–FR-19 | Demod reproducibility | Same input/config | Run twice | Equivalent bits/LLRs within tolerance | Deterministic |
| DEM2-035 | DSP/Integration | FR-15–FR-19 | Unsupported modulation | Unsupported fixture | Run pipeline | System refuses/flags unsupported modulation | No fabricated bitstream |
| DEM2-036 | DSP/Integration | FR-15–FR-19 | QAM equalizer disabled | 16QAM known signal | Disable optional equalization | Behavior and limitation are explicit | Scope consistency |
| INT2-001 | DSP/Integration | FR-20–FR-23, PS interleaving | Block interleave round-trip | Known bitstream + 4x4 block interleaver | Interleave then de-interleave | Exact original bitstream recovered | Bit-exact |
| INT2-002 | DSP/Integration | FR-20–FR-23, PS interleaving | Block row/column depth variation | Multiple dimensions | Test row-major and column-major configurations | Correct inverse permutation for each config | All configs pass |
| INT2-003 | DSP/Integration | FR-20–FR-23, PS interleaving | Block incomplete tail | Length not divisible by block size | De-interleave | Tail policy is explicit and no bits silently disappear | Documented behavior |
| INT2-004 | DSP/Integration | FR-20–FR-23, PS interleaving | Convolutional interleave round-trip | Known delay/tap configuration | Interleave then inverse | Original stream recovered | Bit-exact |
| INT2-005 | DSP/Integration | FR-20–FR-23, PS interleaving | Convolutional delay variation | Multiple tap delays | Test configs | Inverse works for each declared config | All supported configs |
| INT2-006 | DSP/Integration | FR-20–FR-23, PS interleaving | Diagonal interleave round-trip | Known diagonal permutation | Apply inverse | Original recovered | Bit-exact |
| INT2-007 | DSP/Integration | FR-20–FR-23, PS interleaving | Pseudo-random interleave round-trip | Known seed/permutation | Interleave then inverse | Original recovered | Bit-exact |
| INT2-008 | DSP/Integration | FR-20–FR-23, PS interleaving | Wrong PRNG seed | Known PRNG-interleaved data | De-interleave with wrong seed | Mismatch is visible and not treated as success | Failure detection |
| INT2-009 | DSP/Integration | FR-20–FR-23, PS interleaving | Auto-detect block | Unknown block-interleaved fixture | Run limited search | Correct scheme candidate identified or uncertainty reported | No false certainty |
| INT2-010 | DSP/Integration | FR-20–FR-23, PS interleaving | Auto-detect convolutional | Unknown convolutional fixture | Run detector | Candidate identified or unknown reported | Confidence threshold respected |
| INT2-011 | DSP/Integration | FR-20–FR-23, PS interleaving | Auto-detect diagonal | Unknown diagonal fixture | Run detector | Candidate identified or unknown reported | Confidence threshold respected |
| INT2-012 | DSP/Integration | FR-20–FR-23, PS interleaving | Auto-detect PRNG | Unknown PRNG fixture | Run detector | Seed search bounded and result auditable | No unbounded search |
| INT2-013 | DSP/Integration | FR-20–FR-23, PS interleaving | No interleave | Uninterleaved reference | Run detector | None is a candidate | No unnecessary transform |
| INT2-014 | DSP/Integration | FR-20–FR-23, PS interleaving | Noise robustness | Interleaved bits with random errors | Detect/de-interleave | De-interleaver preserves intended ordering | Permutation correct |
| INT2-015 | DSP/Integration | FR-20–FR-23, PS interleaving | Burst-error dispersion | Interleaved stream with burst corruption | De-interleave | Error distribution matches reference behavior | No permutation bug |
| INT2-016 | DSP/Integration | FR-20–FR-23, PS interleaving | Parameter provenance | Manual depth/seed | Run de-interleaver | Config recorded in report | Traceable |
| INT2-017 | DSP/Integration | FR-20–FR-23, PS interleaving | Standalone stage execution | Known interleaved bitstream | Run only de-interleaver | Stage works independently | FR-33 |
| INT2-018 | DSP/Integration | FR-20–FR-23, PS interleaving | Wrong configuration recovery | Known interleaver, wrong params | Run | System reports degraded/no match and allows retry | No false pass |
| INT2-019 | DSP/Integration | FR-20–FR-23, PS interleaving | Large bitstream | Large interleaved stream | De-interleave | Memory use is bounded | No OOM |
| INT2-020 | DSP/Integration | FR-20–FR-23, PS interleaving | Cancellation | Long de-interleaving job | Cancel | Operation ends safely | No corrupted output saved as final |
| INT2-021 | DSP/Integration | FR-20–FR-23, PS interleaving | Deterministic ordering | Same input/config | Run twice | Exact same output | Bit-exact |
| INT2-022 | DSP/Integration | FR-20–FR-23, PS interleaving | E2E interleave + FEC compatibility | Known interleaved coded stream | De-interleave then decode | FEC sees correct bit ordering and recovers source | End-to-end gate |
| FEC2-001 | DSP/Integration | FR-24–FR-27, PS FEC | Viterbi K=3 rate 1/2 | Known convolutional code | Decode clean encoded bits | Source bits recovered | Bit-exact |
| FEC2-002 | DSP/Integration | FR-24–FR-27, PS FEC | Viterbi K=5 rate 1/2 | Known code | Decode | Source recovered | Bit-exact |
| FEC2-003 | DSP/Integration | FR-24–FR-27, PS FEC | Viterbi K=7 rate 1/2 | Known G=[133,171] oct | Decode | Source recovered | Bit-exact |
| FEC2-004 | DSP/Integration | FR-24–FR-27, PS FEC | Viterbi K=9 supported boundary | K=9 fixture if implementation claims K=3–9 | Decode | Source recovered | FR-24 |
| FEC2-005 | DSP/Integration | FR-24–FR-27, PS FEC | Viterbi rate 2/3 | Supported punctured/configured code | Decode | Source recovered | FR-24 |
| FEC2-006 | DSP/Integration | FR-24–FR-27, PS FEC | Viterbi rate 3/4 | Supported punctured/configured code | Decode | Source recovered | FR-24 |
| FEC2-007 | DSP/Integration | FR-24–FR-27, PS FEC | Viterbi soft decision | Known LLR stream | Decode | Soft decoder recovers more reliably than hard at comparable SNR | Performance report |
| FEC2-008 | DSP/Integration | FR-24–FR-27, PS FEC | Viterbi hard decision fallback | Known hard bits | Decode | Hard decoder works where supported | Correct output |
| FEC2-009 | DSP/Integration | FR-24–FR-27, PS FEC | Viterbi noisy correction | Known code + AWGN | Decode across SNRs | BER reduction is measured and documented | Reference curve |
| FEC2-010 | DSP/Integration | FR-24–FR-27, PS FEC | Viterbi traceback boundary | Short frame | Decode | No off-by-one or tail-bit corruption | Reference match |
| FEC2-011 | DSP/Integration | FR-24–FR-27, PS FEC | RS 255,223 clean | Known RS codeword | Decode | Original recovered | Bit/byte exact |
| FEC2-012 | DSP/Integration | FR-24–FR-27, PS FEC | RS 255,251 clean | Known RS codeword | Decode | Original recovered | Bit/byte exact |
| FEC2-013 | DSP/Integration | FR-24–FR-27, PS FEC | RS single-byte error | Single corrupted symbol | Decode | Error corrected | Exact payload |
| FEC2-014 | DSP/Integration | FR-24–FR-27, PS FEC | RS multi-byte errors within capability | Known correctable errors | Decode | All correctable errors fixed | Exact payload |
| FEC2-015 | DSP/Integration | FR-24–FR-27, PS FEC | RS beyond capability | Errors above t | Decode | Decoder flags uncorrectable | No silent corruption |
| FEC2-016 | DSP/Integration | FR-24–FR-27, PS FEC | RS invalid parameters | Invalid n/k | Configure decoder | Validation rejects impossible config | Actionable error |
| FEC2-017 | DSP/Integration | FR-24–FR-27, PS FEC | Concatenated RS+Viterbi | Known two-stage coded stream | Decode inner then outer | Original payload recovered | Exact |
| FEC2-018 | DSP/Integration | FR-24–FR-27, PS FEC | Concatenated wrong order | Known coded stream | Attempt outer before inner | System rejects or fails clearly | No silent garbage |
| FEC2-019 | DSP/Integration | FR-24–FR-27, PS FEC | Concatenated error budget | Mixed errors | Decode | Stage-wise correction metrics shown | Diagnostics |
| FEC2-020 | DSP/Integration | FR-24–FR-27, PS FEC | LDPC clean decode | Known parity-check matrix | Decode | Parity satisfied and source recovered | Syndrome zero |
| FEC2-021 | DSP/Integration | FR-24–FR-27, PS FEC | LDPC noisy decode | Known code + AWGN | Decode | Convergence and BER improvement reported | Reference curve |
| FEC2-022 | DSP/Integration | FR-24–FR-27, PS FEC | LDPC iteration 10 | Configurable iteration setting | Decode | Exactly configured max iterations honored | Parameter honored |
| FEC2-023 | DSP/Integration | FR-24–FR-27, PS FEC | LDPC iteration 100 | Configurable iteration setting | Decode | No hidden cap below configured limit | Parameter honored |
| FEC2-024 | DSP/Integration | FR-24–FR-27, PS FEC | LDPC invalid matrix | Malformed parity-check matrix | Load/decode | Rejected with diagnostic | No crash |
| FEC2-025 | DSP/Integration | FR-24–FR-27, PS FEC | FEC auto-identification | Known unlabeled coded streams | Run detector if feature implemented | Candidate code and confidence are reported, or feature is explicitly marked unsupported | PS compliance check |
| FEC2-026 | DSP/Integration | FR-24–FR-27, PS FEC | FEC wrong scheme | Stream encoded with different code | Select wrong decoder | Failure is visible and no false successful decode is claimed | No silent corruption |
| FEC2-027 | DSP/Integration | FR-24–FR-27, PS FEC | BER before/after FEC | Known source/corrupted stream | Measure BER before and after | Decoder improvement or failure is quantified | Metric present |
| FEC2-028 | DSP/Integration | FR-24–FR-27, PS FEC | Syndrome diagnostics | Corrupted codeword | Inspect diagnostic output | Syndrome/error status is available where supported | NFR-07 |
| FEC2-029 | DSP/Integration | FR-24–FR-27, PS FEC | Bitstream length validation | Known code rate | Decode | Output length is consistent with expected payload/tail rules | Exact |
| FEC2-030 | DSP/Integration | FR-24–FR-27, PS FEC | Standalone FEC stage | Demodulated bits/LLRs available | Run only FEC stage | Stage executes independently | FR-33 |
| FEC2-031 | DSP/Integration | FR-24–FR-27, PS FEC | FEC cancellation | Long LDPC/Viterbi job | Cancel | Decoder terminates safely | No partial final artifact |
| FEC2-032 | DSP/Integration | FR-24–FR-27, PS FEC | FEC determinism | Same input/config | Run twice | Equivalent decoded output and diagnostics | Reproducible |
| FEC2-033 | DSP/Integration | FR-24–FR-27, PS FEC | FEC partial failure preservation | Demod good, FEC bad | Run full pipeline | Earlier-stage result remains accessible | NFR-06 |
| COR2-001 | Integration/System | FR-28–FR-30 | Exact preamble match | Known preamble inserted once | Run sliding correlation | Peak at exact start | Index exact |
| COR2-002 | Integration/System | FR-28–FR-30 | Preamble with bit errors | Known preamble + bounded flips | Run Hamming/correlation search | Correct frame still detected when within threshold | Threshold respected |
| COR2-003 | Integration/System | FR-28–FR-30 | No-match random stream | Random bits | Correlate | No frame declared above threshold | False positive = 0 on fixture |
| COR2-004 | Integration/System | FR-28–FR-30 | User-provided preamble | Custom preamble | Import and correlate | Custom pattern used | Match exact |
| COR2-005 | Integration/System | FR-28–FR-30 | Library preamble | Built-in preamble library | Select and correlate | Selected pattern applied | Correct match |
| COR2-006 | Integration/System | FR-28–FR-30 | Multiple frames | Multiple sync words | Correlate | All expected frame starts found | Count exact |
| COR2-007 | Integration/System | FR-28–FR-30 | Overlapping frame candidates | Constructed ambiguous stream | Correlate | Candidates ranked/filtered per documented rule | No duplicate frame explosion |
| COR2-008 | Integration/System | FR-28–FR-30 | Correlation threshold change | Known match/noise distribution | Vary threshold | Detection count changes predictably | Parameter effective |
| COR2-009 | Integration/System | FR-28–FR-30 | Hamming distance metric | Known mismatch count | Compute metrics | Reported Hamming distance equals reference | Exact |
| COR2-010 | Integration/System | FR-28–FR-30 | Correlation peak value | Known numeric fixture | Compute metric | Peak value matches reference | Tolerance |
| COR2-011 | Integration/System | FR-28–FR-30 | Header boundary | Known frame with fixed header | Run extraction | Header boundaries highlighted | Index exact |
| COR2-012 | Integration/System | FR-28–FR-30 | Payload boundary | Known frame with payload | Extract | Payload start/end indices correct | Index exact |
| COR2-013 | Integration/System | FR-28–FR-30 | CSV structured export | Detected frames | Export CSV | Rows correspond one-to-one with detections | No dropped rows |
| COR2-014 | Integration/System | FR-28–FR-30 | JSON structured export | Detected frames | Export JSON | Schema contains required fields | Schema validation passes |
| COR2-015 | Integration/System | FR-28–FR-30 | Malformed preamble input | Invalid length/characters | Import pattern | Validation error and no crash | Graceful |
| COR2-016 | Integration/System | FR-28–FR-30 | Very short bitstream | Shorter than preamble | Correlate | No false frame; reason reported | Graceful |
| COR2-017 | Integration/System | FR-28–FR-30 | Bit ordering LSB/MSB | Known reference requiring declared bit order | Toggle bit-order setting | Correct mode finds frame | Ordering explicit |
| COR2-018 | Integration/System | FR-28–FR-30 | Correlation after FEC | Known coded frame | Run full pipeline | Correlation operates on correct decoded stream stage | E2E correct |
| COR2-019 | Integration/System | FR-28–FR-30 | Correlation after failed FEC | FEC fails partially | Attempt correlation | System reports whether correlation is attempted and confidence is reduced where appropriate | No overclaim |
| COR2-020 | Integration/System | FR-28–FR-30 | Payload binary export | Known payload bytes | Export BIN | Byte-for-byte match | Exact |
| COR2-021 | Integration/System | FR-28–FR-30 | Payload HEX export | Known payload bytes | Export HEX | Hex representation round-trips to original bytes | Exact |
| COR2-022 | Integration/System | FR-28–FR-30 | Payload ASCII export | ASCII-safe payload | Export ASCII | Text matches byte interpretation | Exact |
| COR2-023 | Integration/System | FR-28–FR-30 | Multi-frame ordering | Frames with sequence numbers | Extract/export | Output preserves chronological/input order | Order exact |
| GUI2-001 | System/UI | FR-31–FR-36, NFR-03 | Open file button | Main window | Click open and select file | File loads and state updates | Pass |
| GUI2-002 | System/UI | FR-31–FR-36, NFR-03 | Drag-and-drop | Main window | Drop valid file | File loads | Pass |
| GUI2-003 | System/UI | FR-31–FR-36, NFR-03 | Run full pipeline | Valid loaded file | Click full analysis | All configured stages execute in order | Stage log correct |
| GUI2-004 | System/UI | FR-31–FR-36, NFR-03 | Run individual stage | Input available | Run one stage only | Only selected stage executes | No unintended stages |
| GUI2-005 | System/UI | FR-31–FR-36, NFR-03 | Progress stage labels | Analysis running | Observe progress | Current stage and overall progress update | Visible |
| GUI2-006 | System/UI | FR-31–FR-36, NFR-03 | Progress update frequency | Long operation | Record timestamps of UI progress updates | Updates at least once per 100 ms where NFR-03 applies | Measured |
| GUI2-007 | System/UI | FR-31–FR-36, NFR-03 | Cancel ingestion | Large file | Start then cancel | Read operation stops and UI returns to idle | Safe cleanup |
| GUI2-008 | System/UI | FR-31–FR-36, NFR-03 | Cancel FFT | Long FFT job | Cancel | Worker stops and no final result is emitted | Safe |
| GUI2-009 | System/UI | FR-31–FR-36, NFR-03 | Cancel AMC | Batch inference | Cancel | Inference worker stops safely | Safe |
| GUI2-010 | System/UI | FR-31–FR-36, NFR-03 | Cancel FEC | Long decode | Cancel | Decoder stops safely | Safe |
| GUI2-011 | System/UI | FR-31–FR-36, NFR-03 | Disable network during analysis | Network is available at OS but firewall blocks app | Run full analysis | No network is needed | Offline compliant |
| GUI2-012 | System/UI | FR-31–FR-36, NFR-03 | Manual Fs override | Auto Fs wrong/unknown | Edit Fs and rerun | Downstream modules use new Fs | FR-32 |
| GUI2-013 | System/UI | FR-31–FR-36, NFR-03 | Manual modulation override | AMC low confidence | Override and rerun | Demod uses selected modulation | FR-32 |
| GUI2-014 | System/UI | FR-31–FR-36, NFR-03 | Manual FEC override | FEC detector uncertain | Select decoder/config | Selected decoder runs | FR-32 |
| GUI2-015 | System/UI | FR-31–FR-36, NFR-03 | Time window selection | Long signal | Select subrange | Plots and analysis use selected window | FR-31 |
| GUI2-016 | System/UI | FR-31–FR-36, NFR-03 | Frequency window selection | Wideband signal | Select frequency range | Displayed/processed range changes accordingly | FR-31 |
| GUI2-017 | System/UI | FR-31–FR-36, NFR-03 | Window reset | Subset selected | Reset selection | Full signal restored | No stale subset |
| GUI2-018 | System/UI | FR-31–FR-36, NFR-03 | Error dialog content | Malformed file | Trigger failure | Message states what failed and corrective action | NFR-03 |
| GUI2-019 | System/UI | FR-31–FR-36, NFR-03 | Unknown status | Unsupported signal | Run analysis | UI visibly marks unknown/unsupported | No false success |
| GUI2-020 | System/UI | FR-31–FR-36, NFR-03 | Intermediate results inspection | Analysis complete | Open FFT/constellation/FEC diagnostics | Internal artifacts are inspectable | NFR-07 |
| GUI2-021 | System/UI | FR-31–FR-36, NFR-03 | Session state isolation | Analyze file A then file B | Switch files | No A-specific state contaminates B | Isolation |
| GUI2-022 | System/UI | FR-31–FR-36, NFR-03 | Window resize | Main UI | Resize to minimum/maximum | Controls remain usable | No clipping |
| GUI2-023 | System/UI | FR-31–FR-36, NFR-03 | Keyboard focus | Main UI | Navigate controls with keyboard | Logical focus order works for supported controls | Usability |
| GUI2-024 | System/UI | FR-31–FR-36, NFR-03 | Tooltip accuracy | UI with help text | Hover controls | Help text matches actual behavior | No stale docs |
| GUI2-025 | System/UI | FR-31–FR-36, NFR-03 | Busy-state controls | Long operation | Inspect buttons | Unsafe conflicting actions disabled or handled | No race |
| GUI2-026 | System/UI | FR-31–FR-36, NFR-03 | Repeated run same config | Completed analysis | Run again | Equivalent result and no duplicated state | Reproducibility |
| GUI2-027 | System/UI | FR-31–FR-36, NFR-03 | Application close during active job | Running analysis | Close window | User prompted or safe cancellation/cleanup occurs | No orphan worker |
| REP2-001 | System | FR-37–FR-40, NFR-07–NFR-08 | JSON report schema | Completed analysis | Export JSON | Required fields exist and validate against schema | Schema passes |
| REP2-002 | System | FR-37–FR-40, NFR-07–NFR-08 | PDF report generation | Completed analysis | Export PDF | Readable report contains summary, parameters and visuals | Content audit |
| REP2-003 | System | FR-37–FR-40, NFR-07–NFR-08 | Binary bitstream export | Decoded bits | Export BIN | Byte-accurate binary file | Exact |
| REP2-004 | System | FR-37–FR-40, NFR-07–NFR-08 | HEX bitstream export | Decoded bits | Export HEX | Round-trip exact | Exact |
| REP2-005 | System | FR-37–FR-40, NFR-07–NFR-08 | ASCII bitstream export | Printable payload | Export ASCII | Text matches defined interpretation | Exact |
| REP2-006 | System | FR-37–FR-40, NFR-07–NFR-08 | Provenance file hash | Known input file | Export report | Input hash is present | FR-40 |
| REP2-007 | System | FR-37–FR-40, NFR-07–NFR-08 | Provenance parameters | Mixed auto/manual run | Export report | All parameters and overrides are recorded | FR-40 |
| REP2-008 | System | FR-37–FR-40, NFR-07–NFR-08 | Provenance algorithm versions | Known package/model versions | Export | Versions/hashes appear | FR-40 |
| REP2-009 | System | FR-37–FR-40, NFR-07–NFR-08 | Provenance timestamp | Any run | Export | Timestamp present in declared timezone/format | FR-40 |
| REP2-010 | System | FR-37–FR-40, NFR-07–NFR-08 | Model version in report | AMC run | Export | Model identity/version/hash included | Traceable |
| REP2-011 | System | FR-37–FR-40, NFR-07–NFR-08 | Dataset version in training artifact | Trained model | Inspect model metadata | Training dataset/version is identifiable | Traceable |
| REP2-012 | System | FR-37–FR-40, NFR-07–NFR-08 | Visualization inclusion | Completed analysis | Export PDF | Spectrum/waterfall/constellation are included where applicable | FR-39 |
| REP2-013 | System | FR-37–FR-40, NFR-07–NFR-08 | Intermediate artifact export | Analysis complete | Export FFT/constellation/syndrome | Files are generated with source/config metadata | NFR-07 |
| REP2-014 | System | FR-37–FR-40, NFR-07–NFR-08 | Export overwrite protection | Existing file with same name | Export | Overwrite behavior is explicit | No silent loss |
| REP2-015 | System | FR-37–FR-40, NFR-07–NFR-08 | Invalid output path | Unwritable folder | Export | Actionable error and prior results preserved | Graceful |
| REP2-016 | System | FR-37–FR-40, NFR-07–NFR-08 | Large report | 2GB-scale signal result metadata | Export | Report generation remains bounded and does not include raw samples unnecessarily | Resource safe |
| REP2-017 | System | FR-37–FR-40, NFR-07–NFR-08 | JSON round-trip | Exported result | Load JSON back | All required fields restore | No data loss |
| REP2-018 | System | FR-37–FR-40, NFR-07–NFR-08 | Model/output mismatch warning | Report from older model | Load/inspect | Version mismatch is visible | Traceable |
| REP2-019 | System | FR-37–FR-40, NFR-07–NFR-08 | Re-analysis from report | Self-contained report/config | Load and rerun where supported | Equivalent configuration can be reconstructed | Reproducible |
| REP2-020 | System | FR-37–FR-40, NFR-07–NFR-08 | Audit log stage coverage | Complete run | Inspect logs | Load/FFT/AMC/Demod/FEC/Export events are present | NFR-07 |
| REP2-021 | System | FR-37–FR-40, NFR-07–NFR-08 | Log verbosity modes | Logging enabled | Change verbosity | Expected level of diagnostic detail is produced | Config effective |
| REP2-022 | System | FR-37–FR-40, NFR-07–NFR-08 | Sensitive content redaction | Signal with sensitive payload | Inspect logs | Raw IQ/payload is not unnecessarily written to logs | No data leakage |
| REP2-023 | System | FR-37–FR-40, NFR-07–NFR-08 | Original input unchanged after export | Known source hash | Export all formats | Input hash remains unchanged | Integrity |
| REP2-024 | System | FR-37–FR-40, NFR-07–NFR-08 | Duplicate export consistency | Same result twice | Export twice | Equivalent outputs aside from timestamp where applicable | Deterministic content |
| PERF2-001 | Performance/Stress | NFR-01, NFR-03, NFR-06 | 100 MB E2E benchmark | Reference 8-core CPU/16 GB RAM | Run complete 100 MB pipeline | <5 seconds per NFR-01 | Mandatory NFR gate |
| PERF2-002 | Performance/Stress | NFR-01, NFR-03, NFR-06 | 8192 FFT latency | Reference CPU | Run benchmark | <50 ms | Mandatory NFR gate |
| PERF2-003 | Performance/Stress | NFR-01, NFR-03, NFR-06 | AMC inference latency | Reference CPU | Run one inference | <100 ms | Mandatory NFR gate |
| PERF2-004 | Performance/Stress | NFR-01, NFR-03, NFR-06 | Viterbi 1 Mbps throughput | Reference CPU | Decode 1 Mbps | ≥1 Mbps effective throughput / <500 ms criterion as configured | Mandatory NFR gate |
| PERF2-005 | Performance/Stress | NFR-01, NFR-03, NFR-06 | 1000 repeated small analyses | Stable valid fixture | Run 1000 cycles | No unbounded memory growth or state leakage | Trend reviewed |
| PERF2-006 | Performance/Stress | NFR-01, NFR-03, NFR-06 | 2 GB ingestion | 2 GB IQ fixture | Load/partial analysis | Streaming path works without memory exhaustion | Mandatory robustness |
| PERF2-007 | Performance/Stress | NFR-01, NFR-03, NFR-06 | 2 GB end-to-end sampled window | 2 GB source | Analyze selected windows only | System avoids full materialization and remains responsive | Streaming |
| PERF2-008 | Performance/Stress | NFR-01, NFR-03, NFR-06 | Long-duration signal | Hours-equivalent synthetic recording | Analyze chunks | No counter overflow or time-axis drift | Integrity |
| PERF2-009 | Performance/Stress | NFR-01, NFR-03, NFR-06 | Large constellation point count | Large signal | Render/downsample | UI remains responsive with bounded memory | No freeze |
| PERF2-010 | Performance/Stress | NFR-01, NFR-03, NFR-06 | Large waterfall | Large signal | Render waterfall | Rendering remains within resource budget | No OOM |
| PERF2-011 | Performance/Stress | NFR-01, NFR-03, NFR-06 | Concurrent analysis attempt | One active job | Start second job | System serializes/rejects clearly or isolates jobs safely | No race |
| PERF2-012 | Performance/Stress | NFR-01, NFR-03, NFR-06 | CPU saturation | CPU stress environment | Run analysis | No deadlock; graceful degradation | Stability |
| PERF2-013 | Performance/Stress | NFR-01, NFR-03, NFR-06 | Low-memory environment | Memory below recommended | Run large job | System switches to chunking or returns controlled OOM message | NFR-06 |
| PERF2-014 | Performance/Stress | NFR-01, NFR-03, NFR-06 | Disk full during export | Low free space | Export | No partial file presented as complete | Integrity |
| PERF2-015 | Performance/Stress | NFR-01, NFR-03, NFR-06 | Repeated cancellation | Long job | Start/cancel repeatedly | No orphan threads/processes or resource accumulation | Cleanup |
| PERF2-016 | Performance/Stress | NFR-01, NFR-03, NFR-06 | Thermal throttling scenario | Sustained benchmark | Run repeated workloads | Application remains functionally correct under slower hardware | Correctness first |
| PERF2-017 | Performance/Stress | NFR-01, NFR-03, NFR-06 | Cold start | Fresh process | Measure launch to ready | Time recorded and reproducible | Baseline |
| PERF2-018 | Performance/Stress | NFR-01, NFR-03, NFR-06 | Warm start | Previously initialized process | Measure second run | Performance improvement/variance documented | Baseline |
| PERF2-019 | Performance/Stress | NFR-01, NFR-03, NFR-06 | Disk vs RAM cache behavior | Same file twice | Compare runs | Results identical; caching does not alter semantics | Deterministic |
| PERF2-020 | Performance/Stress | NFR-01, NFR-03, NFR-06 | Multi-core scaling | Reference CPU | Vary worker count | Performance scales without data corruption | Benchmark |
| PERF2-021 | Performance/Stress | NFR-01, NFR-03, NFR-06 | GPU acceleration correctness | GPU available | Compare CPU/GPU results | Outputs numerically equivalent within tolerance | Correctness |
| PERF2-022 | Performance/Stress | NFR-01, NFR-03, NFR-06 | GPU memory pressure | Large signal/batch | Run inference | OOM is caught with CPU fallback or controlled error | Graceful |
| PERF2-023 | Performance/Stress | NFR-01, NFR-03, NFR-06 | Model cold inference | Model not loaded | Run first inference | No crash; timing separately recorded | Stable |
| PERF2-024 | Performance/Stress | NFR-01, NFR-03, NFR-06 | Model repeated inference | Loaded model | Run 1000 inferences | Latency stable and memory bounded | No leak |
| PERF2-025 | Performance/Stress | NFR-01, NFR-03, NFR-06 | Batch 10 independent files | 10 golden fixtures | Process sequentially | No cross-file contamination | Isolation |
| SEC2-001 | Security | NFR-02, NFR-06–NFR-08 | Zero outbound TCP | Network monitor active | Launch/run/export | No outbound TCP connections | Zero |
| SEC2-002 | Security | NFR-02, NFR-06–NFR-08 | Zero outbound UDP | Network monitor active | Launch/run/export | No outbound UDP | Zero |
| SEC2-003 | Security | NFR-02, NFR-06–NFR-08 | Zero DNS | DNS monitor | Launch/run | No DNS queries | Zero |
| SEC2-004 | Security | NFR-02, NFR-06–NFR-08 | Zero HTTP/HTTPS | Packet capture | Run all workflows | No web traffic | Zero |
| SEC2-005 | Security | NFR-02, NFR-06–NFR-08 | No telemetry | Inspect processes/config/logs | Run repeated sessions | No analytics/telemetry events | Zero |
| SEC2-006 | Security | NFR-02, NFR-06–NFR-08 | Bundled model only | Air-gapped machine | Run AMC | Model loads locally | No network dependency |
| SEC2-007 | Security | NFR-02, NFR-06–NFR-08 | Malicious filename | Filename with shell metacharacters | Open/export | No command execution | Secure |
| SEC2-008 | Security | NFR-02, NFR-06–NFR-08 | Path traversal filename | Filename containing ../ patterns | Open/save | Resolved safely within allowed path | Secure |
| SEC2-009 | Security | NFR-02, NFR-06–NFR-08 | Null byte path input | Programmatic open path | Attempt malicious path | Input is rejected safely | Secure |
| SEC2-010 | Security | NFR-02, NFR-06–NFR-08 | Symlink escape | Symlink points outside allowed area | Open | Behavior follows explicit policy; no unsafe write | Secure |
| SEC2-011 | Security | NFR-02, NFR-06–NFR-08 | Malicious JSON sidecar | Sidecar with unexpected types/fields | Load | Parser rejects or safely ignores malicious content | No code execution |
| SEC2-012 | Security | NFR-02, NFR-06–NFR-08 | Malicious YAML/config | Config with executable/object tags if parser supports YAML | Load config | Safe loader only; no code execution | Mandatory |
| SEC2-013 | Security | NFR-02, NFR-06–NFR-08 | Oversized metadata chunk | WAV/sidecar metadata abuse | Open | Parser bounds allocation | No memory exhaustion |
| SEC2-014 | Security | NFR-02, NFR-06–NFR-08 | Corrupt HDF5/model | Malformed model/data artifact | Load | Integrity check rejects safely | No crash |
| SEC2-015 | Security | NFR-02, NFR-06–NFR-08 | Log injection | Input fields containing newline/control chars | Process/export | Logs remain structured; no forged log entries | Secure |
| SEC2-016 | Security | NFR-02, NFR-06–NFR-08 | Sensitive payload not logged | Known payload | Run analysis | Payload absent from routine logs unless explicit export | No leakage |
| SEC2-017 | Security | NFR-02, NFR-06–NFR-08 | Temp-file cleanup | Long analysis creates cache | Cancel/close | Temporary sensitive artifacts are removed or access-restricted | Cleanup |
| SEC2-018 | Security | NFR-02, NFR-06–NFR-08 | Crash dump review | Intentional crash in test build | Inspect dump files | Sensitive signal data handling matches security policy | Policy review |
| SEC2-019 | Security | NFR-02, NFR-06–NFR-08 | Permissions on outputs | Linux filesystem | Export | Permissions meet documented minimum | Policy-compliant |
| SEC2-020 | Security | NFR-02, NFR-06–NFR-08 | Unauthorized output directory | No write permissions | Export | Actionable permission error | No corruption |
| SEC2-021 | Security | NFR-02, NFR-06–NFR-08 | Concurrent users | Two user sessions | Analyze separate files | No cross-user data leakage | Isolation |
| SEC2-022 | Security | NFR-02, NFR-06–NFR-08 | Model tamper detection | Alter model bytes after deployment | Run | Tamper/integrity issue is detected if integrity mechanism is implemented | No silent use of altered model |
| SEC2-023 | Security | NFR-02, NFR-06–NFR-08 | Report tamper detection | Alter exported report/hash | Reload/verify if supported | Mismatch is detectable if verification is supported | Auditability |
| SEC2-024 | Security | NFR-02, NFR-06–NFR-08 | Offline clock dependency | No network, valid local clock | Run | Timestamping works without network | Offline |
| SEC2-025 | Security | NFR-02, NFR-06–NFR-08 | Package dependency audit | Installed build | Enumerate dependencies | No runtime dependency unexpectedly reaches internet | Offline |
| SEC2-026 | Security | NFR-02, NFR-06–NFR-08 | External plugin disablement | No optional network plugins installed | Run all features | Core app remains functional | Air-gap |
| SEC2-027 | Security | NFR-02, NFR-06–NFR-08 | Recovery after security rejection | Blocked malicious input | Return to normal valid file | Application remains usable | No poisoned state |
| DATA2-001 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Raw dataset hash validation | Dataset downloaded | Compute checksum vs recorded value | Hash is recorded and stable | Acquisition gate |
| DATA2-002 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Dataset source provenance | Dataset card exists | Inspect card | Source, DOI/URL, date, license are recorded | Traceable |
| DATA2-003 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Canonical format validation | Canonical dataset | Load random records | Expected shape/dtype/ranges are correct | 100% schema compliance |
| DATA2-004 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | No NaN in dataset | Canonical dataset | Scan all arrays | No NaN | Zero NaN |
| DATA2-005 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | No Inf in dataset | Canonical dataset | Scan all arrays | No Inf | Zero Inf |
| DATA2-006 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | No degenerate samples | Canonical dataset | Compute norms/variance | Degenerate samples follow policy and are removed/flagged | QA report |
| DATA2-007 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Modulation label taxonomy | Dataset metadata | Enumerate labels | Labels match declared taxonomy exactly | No accidental aliases |
| DATA2-008 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | SNR metadata integrity | Dataset with SNR labels | Recompute/spot-check | Stored SNR matches generator/source | No mismatch |
| DATA2-009 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Split manifests frozen | Train/val/test manifests | Hash manifests | Frozen and versioned | Traceable |
| DATA2-010 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | No split overlap | All manifests | Compare sample IDs/hashes | Zero overlap | Mandatory |
| DATA2-011 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | No augmentation leakage | Augmented dataset pipeline | Trace ancestry | Augmented samples do not cross split boundaries | Mandatory |
| DATA2-012 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Class balance report | Training set | Generate counts | Distribution reported and reviewed | Artifact |
| DATA2-013 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | SNR distribution report | All splits | Generate histograms | SNR coverage documented | Artifact |
| DATA2-014 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Visualization QC | Random samples each class | Plot waveform/spectrum/constellation | Expected structures visible; no corruption | Review gate |
| DATA2-015 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Generator seed reproducibility | Custom GNU Radio/Python generator | Generate same seed twice | Outputs and metadata match | Deterministic |
| DATA2-016 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | FEC encoder round-trip | Custom generator | Encode/decode clean bits | Exact source recovery | Generator valid |
| DATA2-017 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Interleaver generator round-trip | Custom generator | Interleave/de-interleave | Exact recovery | Generator valid |
| DATA2-018 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | End-to-end generator provenance | Generated sample | Inspect metadata | Original bits, modulation, FEC, interleaver, channel, seed all linked | Mandatory |
| DATA2-019 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Channel impairment correctness | Generator configured AWGN/CFO/phase/timing/fading | Compare measured vs target | Applied impairments match configuration | Reference |
| DATA2-020 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Custom dataset class coverage | Generator config | Enumerate combinations | All required FEC/interleaver/modulation classes have examples | Coverage matrix |
| DATA2-021 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Real capture segregation | Authorized real data | Inspect splits | Real test data are not used for training unless explicitly documented | No contamination |
| DATA2-022 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Benchmark integrity RadioML 2016 | Canonical RML2016 | Inspect expected counts/shapes | Dataset statistics match documented acquisition | Dataset card |
| DATA2-023 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Cross-dataset generalization isolation | RadioML-trained model | Evaluate on HisarMod | No HisarMod tuning leakage | Independent test |
| DATA2-024 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Model input shape validation | Trained model | Feed invalid shape | Clear shape error | No memory corruption |
| DATA2-025 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Model output label mapping | Known class mapping | Run known sample | Predicted index maps to correct label | No label permutation bug |
| DATA2-026 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Model checkpoint hash | Final model | Hash checkpoint | Hash stored in provenance | Traceable |
| DATA2-027 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Training config capture | Final model | Inspect metadata | Dataset version, optimizer/config, seed, code commit recorded | Reproducibility |
| DATA2-028 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Training/validation curve sanity | Training logs | Inspect curves | No obvious train/val contamination anomalies; anomalies investigated | Review gate |
| DATA2-029 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Model ablation sanity | Hybrid AMC | Disable ML or rule tier separately | System behavior matches architecture design | Architecture verification |
| DATA2-030 | Data/ML QA | Dataset handbook; AMC/FEC/interleaver requirements | Unknown/abstain policy | Out-of-distribution fixture | Run model | System can report unknown/manual review where configured | No forced certainty |
| E2E2-001 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Golden BPSK clean | Known end-to-end BPSK fixture | Load → analyze → demod → export | Fs/visualization/AMC/demod/export all correct | Critical path PASS |
| E2E2-002 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Golden QPSK clean | Known QPSK fixture | Full pipeline | QPSK classified and payload recovered | Critical path PASS |
| E2E2-003 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Golden 8PSK clean | Known 8PSK fixture | Full pipeline | 8PSK payload recovered | Critical path PASS |
| E2E2-004 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Golden 2FSK clean | Known 2FSK fixture | Full pipeline | 2FSK detected/demodulated and payload recovered | Critical path PASS |
| E2E2-005 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Golden 4FSK clean | Known 4FSK fixture | Full pipeline | 4FSK detected/demodulated and payload recovered | Critical path PASS |
| E2E2-006 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Golden 16QAM clean | Known 16QAM fixture | Full pipeline | 16QAM classified/demodulated | Critical path PASS |
| E2E2-007 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Golden 64QAM clean | Known 64QAM fixture | Full pipeline | 64QAM classified/demodulated | Critical path PASS |
| E2E2-008 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | QPSK + block interleaver | Known interleaved QPSK stream | Full pipeline including de-interleave | Source bitstream restored | Critical |
| E2E2-009 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | QPSK + conv interleaver | Known convolutional interleave | Full pipeline | Source restored | Critical |
| E2E2-010 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | QPSK + diagonal interleaver | Known diagonal interleave | Full pipeline | Source restored | Critical |
| E2E2-011 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | QPSK + PRNG interleaver | Known seed | Full pipeline | Source restored | Critical |
| E2E2-012 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | BPSK + Viterbi | BPSK with convolutional code | Full pipeline | FEC reduces BER/recover payload | Critical |
| E2E2-013 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | QPSK + RS | QPSK + RS corrupted codewords | Full pipeline | RS corrects within capability | Critical |
| E2E2-014 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | QPSK + RS+Viterbi | Concatenated coded signal | Full pipeline | Payload recovered | Critical |
| E2E2-015 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | QPSK + LDPC | QPSK + LDPC coded signal | Full pipeline | Payload recovered/convergence reported | Critical if LDPC implemented |
| E2E2-016 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Multi-impairment signal | Known signal + CFO + phase + timing + AWGN | Full pipeline | Synchronization and demod recover expected data or report failure | Impairment gate |
| E2E2-017 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Low-SNR signal | 5 dB benchmark | Full pipeline | AMC/parameter confidence degrades appropriately; no false success | Low-SNR gate |
| E2E2-018 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | FEC failure partial success | Demod succeeds, FEC uncorrectable | Full pipeline | Earlier results preserved and failure clearly shown | NFR-06 |
| E2E2-019 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Unknown modulation | Unsupported modulation | Full pipeline | Unknown/manual path | No fabricated decode |
| E2E2-020 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Missing Fs | IQ without metadata | Full pipeline | Unknown/manual Fs flow works | No fabricated metadata |
| E2E2-021 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Wrong manual parameter recovery | Auto result intentionally wrong | Override and rerun | Correct downstream decode after override | Control gate |
| E2E2-022 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Time-windowed analysis | Long file with signal event | Select window and analyze | Results correspond to selected region | Subset gate |
| E2E2-023 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Frequency-windowed analysis | Wideband multi-content fixture | Select frequency region | Analysis isolates selected region where feature supports it | Subset gate |
| E2E2-024 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Large 100 MB file | 100 MB valid IQ | Full pipeline and export | Completes under 5 sec on reference hardware | NFR-01 |
| E2E2-025 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | 2 GB file | 2 GB IQ | Streaming + targeted analysis | No memory exhaustion | NFR-02/NFR-06 |
| E2E2-026 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Corrupt WAV E2E | Broken WAV | Load/run | Graceful failure | Robustness |
| E2E2-027 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Corrupt IQ E2E | Truncated IQ | Load/run | Graceful failure | Robustness |
| E2E2-028 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Repeated file isolation | File A then B | Analyze sequentially | No state contamination | Isolation |
| E2E2-029 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Export/reload | Completed analysis | Export JSON/report; reload | Results remain traceable | FR-37–FR-40 |
| E2E2-030 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | CPU/GPU equivalence | GPU-capable environment | Run same input CPU and GPU | Equivalent semantic results | Correctness |
| E2E2-031 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Offline full workflow | Air-gapped machine | Run complete workflow | All required features operate offline | Security gate |
| E2E2-032 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | End-to-end provenance | Golden test run | Inspect report/logs | Input hash + config + model + algorithm versions + timestamp + overrides recorded | FR-40 |
| E2E2-033 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Cancellation/recovery | Long-running E2E | Cancel then rerun from clean state | Rerun succeeds and no stale partial result is shown | FR-36 |
| E2E2-034 | Full System | PS 26147; FR-01–FR-40; NFR-01–NFR-08 | Release candidate smoke suite | Final build | Run all critical golden paths | All mandatory gates pass before release | Release gate |
| REG2-001 | Regression | All FR/NFR | Golden fixture snapshot | Versioned golden outputs | Run all after each build | No unexpected numerical or structural drift | Diff reviewed |
| REG2-002 | Regression | All FR/NFR | API/module import smoke | Built package | Import every core module | No missing symbol/import failures | All pass |
| REG2-003 | Regression | All FR/NFR | Schema compatibility | Prior result exports | Load with current build | Old supported schema remains readable | Migration if needed |
| REG2-004 | Regression | All FR/NFR | Model checkpoint compatibility | Prior approved model | Load/infer | Current runtime supports approved checkpoint | Pass |
| REG2-005 | Regression | All FR/NFR | Config compatibility | Prior supported config | Load | Configuration migrates or loads correctly | Pass |
| REG2-006 | Regression | All FR/NFR | Feature flag regression | All optional features | Toggle and rerun | No side-effect regressions | Pass |
| REG2-007 | Regression | All FR/NFR | Manual override regression | Known override fixture | Repeat override tests | Overrides remain effective | Pass |
| REG2-008 | Regression | All FR/NFR | Cancellation regression | Long fixtures | Cancel at each major stage | All cancellation paths remain safe | Pass |
| REG2-009 | Regression | All FR/NFR | Export regression | Golden result | Export all formats | Schema/content unchanged except approved changes | Pass |
| REG2-010 | Regression | All FR/NFR | Performance regression | Reference benchmark | Run benchmark suite | No budget regression beyond agreed tolerance | Pass |
| REG2-011 | Regression | All FR/NFR | Security regression | Air-gapped fixture | Run network monitor | Still zero network traffic | Mandatory |
| REG2-012 | Regression | All FR/NFR | Memory regression | Repeated-run fixture | Measure memory | No new leak | Pass |
| REG2-013 | Regression | All FR/NFR | Visualization regression | Golden plot snapshots | Render | Axes/labels/feature positions remain correct | Visual diff reviewed |
| REG2-014 | Regression | All FR/NFR | FFT numerical regression | Known tone fixture | Compare to reference | Spectrum unchanged within tolerance | Pass |
| REG2-015 | Regression | All FR/NFR | Demod regression | Golden modulations | Demod all | BER/output unchanged | Pass |
| REG2-016 | Regression | All FR/NFR | Interleaver regression | Permutation fixtures | Round-trip | Bit-exact outputs unchanged | Pass |
| REG2-017 | Regression | All FR/NFR | FEC regression | Codec fixtures | Decode | Corrected output unchanged | Pass |
| REG2-018 | Regression | All FR/NFR | Correlation regression | Frame fixtures | Detect/extract | Offsets and payload boundaries unchanged | Pass |
| REG2-019 | Regression | All FR/NFR | Dataset loader regression | Canonical datasets | Load random batches | Shapes/labels preserved | Pass |
| REG2-020 | Regression | All FR/NFR | Inference regression | Known model/test batch | Infer | Predictions remain within approved drift threshold | Pass |
| REG2-021 | Regression | All FR/NFR | Installer regression | Windows/Linux packages | Install/update/uninstall | No packaging regressions | Pass |
| REG2-022 | Regression | All FR/NFR | Documentation/version regression | Release artifacts | Verify versions and hashes | Artifacts match release manifest | Pass |

## 8. Existing Master Test Plan — All 147 Baseline Cases

The prior Master Test Plan contributes **147** executable baseline cases. They are reproduced below so this document can stand alone.

| ID | Objective | Preconditions | Steps | Expected | Pass/Fail Criteria | Requirement Area |
|---|---|---|---|---|---|---|
| TC-ING-001 | Parse float32 IQ file | Valid `.iq` file (float32) available | 1. Open file picker → select `sample_float32.iq` → specify Float32 format → Load | Complex array populated; metadata loaded | Non-zero array; zero parse exceptions | FR-01–FR-03 |
| TC-ING-002 | Parse int16 IQ file | Valid `.iq` file (int16) available | 1. Select `sample_int16.iq` → specify Int16 format → Load | Samples normalized to [-1.0, +1.0] range | Correct scaling; correct sample count | FR-01–FR-03 |
| TC-ING-003 | Parse int8 IQ file | Valid `.iq` file (int8) available | 1. Select `sample_int8.iq` → specify Int8 format → Load | Samples normalized correctly | Min/max values within bounds | FR-01–FR-03 |
| TC-ING-004 | Parse mono WAV file | Valid mono `.wav` file (16-bit PCM, 48 kHz) | 1. Select `mono.wav` → Load | RIFF header parsed; sample rate, channels, duration extracted | Metadata matches RIFF chunk; waveform rendered | FR-01–FR-03 |
| TC-ING-005 | Parse multi-channel WAV | Stereo/multi-channel `.wav` file | 1. Select `stereo.wav` → Load | All channels ingested as separate time series | Channel count verified; no cross-talk | FR-01–FR-03 |
| TC-ING-006 | Handle byte-order (Endianness) | IQ file with explicit endian marker | 1. Load under correct endianness → verify statistics → Load under wrong endianness → observe corruption | Correct byte-order reproduces reference; wrong order is detected as invalid | Power/mean statistics differ by >3σ under wrong endian | FR-01–FR-03 |
| TC-ING-007 | Detect odd sample count | IQ file with incomplete I/Q pair | 1. Load file with odd scalar sample count | System detects incomplete pair; error message shown; no silent data shift | Parse error raised; no corruption | FR-01–FR-03 |
| TC-ING-008 | Reject unsupported extension | File with `.txt` or `.bin` (non-signal) extension | 1. Attempt to open unsupported file | System displays error dialog: "Unsupported file format" | User clearly informed; app remains stable | FR-01–FR-03 |
| TC-ING-009 | Handle empty file | 0-byte `.iq` or `.wav` file | 1. Attempt to load empty file | Error dialog: "File is empty" | No processing initiated; app stable | FR-01–FR-03 |
| TC-ING-010 | Detect truncated IQ payload | `.iq` file with incomplete samples (truncated) | 1. Load truncated `.iq` file | Parser identifies incomplete payload or fails with actionable error | Exception caught; user-friendly error shown | FR-01–FR-03 |
| TC-ING-011 | Detect corrupt WAV header | `.wav` file with broken RIFF/fmt chunk | 1. Attempt to load corrupted `.wav` | System catches exception; error dialog shown; app operational | "Invalid WAV Header" message; GUI responsive | FR-01–FR-03 |
| TC-ING-012 | Use IQ metadata sidecar | `.iq` file with accompanying `.json` metadata | 1. Load file with metadata tags (sample rate, center freq) | Metadata parsed and associated with signal object | Metadata fields populated correctly | FR-01–FR-03 |
| TC-ING-013 | Handle missing optional metadata | `.iq` file with no center frequency tag | 1. Load file; check metadata inspector | System marks missing fields as "Unknown" | File loads; missing metadata does not block processing | FR-01–FR-03 |
| TC-ING-014 | Ingest large file (2 GB) | 2 GB raw `.iq` file on NVMe drive | 1. Select 2 GB `.iq` file → Execute load → Monitor RAM | File mapped via `np.memmap` or chunking; MemoryError not raised | RAM usage < 2 GB above baseline; load completes in < 3 sec | FR-01–FR-03 |
| TC-ING-015 | Streaming/chunked processing | File larger than available RAM | 1. Process in chunks; verify chunk boundary handling | Signal integrity maintained across chunk boundaries | No sample loss/duplication at boundaries | FR-01–FR-03 |
| TC-PRE-001 | DC offset removal | IQ signal with +0.15V DC bias | 1. Load signal → Execute preprocessing → Compute mean of I/Q | Mean of I and Q reduced to ~0.0 | \ | Mean(I)\ | < 1e-5; \ | Mean(Q)\ | < 1e-5 | FR-03, NFR-06, NFR-08 |
| TC-PRE-002 | I/Q imbalance correction | Signal with 10% amplitude imbalance, 5° phase | 1. Load unbalanced signal → Apply Gram-Schmidt correction | Amplitude and phase orthogonalized | Imbalance reduced by ≥20 dB; power equalized | FR-03, NFR-06, NFR-08 |
| TC-PRE-003 | Sample rate normalization | Signal sampled at non-standard rate (44.1 kHz) | 1. Load signal → Resample to standard rate (48 kHz) if needed | Resampling preserves spectral characteristics | Spectral shape preserved; no aliasing artifacts | FR-03, NFR-06, NFR-08 |
| TC-PRE-004 | Clipping detection | Signal with clipping/saturation | 1. Load clipped signal → Analyze peak statistics | System detects saturation and warns user | Clipping indicator displayed; recommendation offered | FR-03, NFR-06, NFR-08 |
| TC-PRE-005 | SNR estimation | Known signal + AWGN at target SNR | 1. Load signal → Estimate SNR via cumulant method | Estimated SNR within ±2 dB of true SNR | \ | SNR_est - SNR_true\ | ≤ 2 dB | FR-03, NFR-06, NFR-08 |
| TC-PRE-006 | Windowing consistency | Signal preprocessed with multiple window types | 1. Apply Hann, Hamming, Blackman windows → compare spectral leakage | Window choice does not corrupt signal classification | Modulation decision consistent across windows | FR-03, NFR-06, NFR-08 |
| TC-PRE-007 | Normalization by power | Raw signal with arbitrary scaling | 1. Load signal → Normalize by power → Verify unit power | Signal power normalized to ~1.0 | 10*log10(E[s^2]) ≈ 0 dB | FR-03, NFR-06, NFR-08 |
| TC-PRE-008 | Filter artifact inspection | High-pass/low-pass filter application | 1. Apply filter → Check impulse response duration | Filter transients do not corrupt signal start | First N_filt samples marked as warmup | FR-03, NFR-06, NFR-08 |
| TC-VIS-001 | Render waterfall spectrogram | IQ signal loaded; FFT parameters configured | 1. Set FFT size=2048, window=Hann → Start waterfall rendering → Measure FPS | Smooth time-frequency-power spectrogram rendered at ≥25 FPS | FPS ≥ 25; color gradient smooth; no flicker | FR-04–FR-08 |
| TC-VIS-002 | FFT spectral plot accuracy | Known reference signal (e.g., pure tone) | 1. Load known tone → Compute FFT → Verify peak location and magnitude | Peak occurs at expected frequency; magnitude matches theory | Peak within ±1 bin; magnitude ±1 dB | FR-04–FR-08 |
| TC-VIS-003 | Dynamic range & color mapping | Waterfall with signals over wide power range | 1. Render waterfall → Inspect color scale mapping | Low-power details visible; high-power not saturated | Color map spans 60+ dB range; no clipping | FR-04–FR-08 |
| TC-VIS-004 | I/Q constellation diagram (QPSK) | QPSK demodulated symbols | 1. Load QPSK signal → Render constellation → Measure cluster positions | 4 symbol clusters appear at ±1±j locations | Cluster separation > 2σ noise | FR-04–FR-08 |
| TC-VIS-005 | I/Q constellation diagram (16QAM) | 16-QAM demodulated symbols | 1. Load 16-QAM signal → Render constellation | 16 symbol clusters at correct Gray-code positions | All clusters visible; separation quantified | FR-04–FR-08 |
| TC-VIS-006 | Power spectral density (PSD) | IQ signal | 1. Compute Welch PSD → Render → Compare to theoretical | PSD shape matches expected signal spectrum | Bandwidth measurement within ±5% | FR-04–FR-08 |
| TC-VIS-007 | Spectrogram with high time resolution | Chirp or frequency-hopping signal | 1. Render spectrogram with 512-point FFT, high overlap | Frequency transitions clearly visible over time | Chirp slope, hop times visible | FR-04–FR-08 |
| TC-VIS-008 | Phase trajectory plot | Demodulated symbols | 1. Render phase vs. time for PSK signal | Phase progression smooth; jumps only at symbol boundaries | No spurious phase discontinuities | FR-04–FR-08 |
| TC-VIS-009 | Zoom & pan functionality | Waterfall/spectrum displayed | 1. Click-drag to zoom; scroll to pan | Rendering responsive; no redraw lag | Interaction latency < 100 ms | FR-04–FR-08 |
| TC-VIS-010 | Export plots (PNG/PDF) | Visualization rendered | 1. Click "Export" → select format → save | Plot image saved to disk with correct resolution | File size appropriate; image readable | FR-04–FR-08 |
| TC-PAR-001 | Sampling frequency ($F_s$) estimation | IQ signal with known $F_s$ | 1. Compute autocorrelation peaks → Identify repetition → Estimate $F_s$ | Estimated $F_s$ within ±1% of true value | \ | $F_s$_est - $F_s$_true\ | / $F_s$_true < 0.01 | FR-09–FR-10, FR-13–FR-14 |
| TC-PAR-002 | Symbol rate detection | BPSK/QPSK at known symbol rate | 1. Compute cumulants over sliding windows → Detect cyclostationary peaks | Detected symbol rate ±2% of true rate | Confidence score > 0.8 | FR-09–FR-10, FR-13–FR-14 |
| TC-PAR-003 | Bandwidth measurement | Signal with known 3-dB bandwidth | 1. Compute spectrum → Find -3 dB points → Calculate BW | Measured BW within ±5% of reference | Tolerance range achievable on real RF | FR-09–FR-10, FR-13–FR-14 |
| TC-PAR-004 | Center frequency estimation | Bandpass IQ signal | 1. Compute spectrum → Find peak → Read carrier freq | Center frequency within ±2% | Accuracy sufficient for subsequent analysis | FR-09–FR-10, FR-13–FR-14 |
| TC-PAR-005 | SNR & noise power estimation | Signal + AWGN at target SNR | 1. Estimate signal power (via cumulants) → Estimate noise floor (via FFT min) → Compute SNR | Estimated SNR ±2 dB of true SNR | Confidence intervals reported | FR-09–FR-10, FR-13–FR-14 |
| TC-PAR-006 | Power measurement (PAPR) | OFDM or multi-symbol signal | 1. Compute peak and average power → Calculate PAPR | PAPR measurement within ±1 dB of reference | Useful for modulation detection | FR-09–FR-10, FR-13–FR-14 |
| TC-PAR-007 | Frequency offset detection | Signal with 10 kHz frequency offset | 1. Estimate residual frequency offset via cumulant method | Offset measured as 10±2 kHz | Enable subsequent synchronization | FR-09–FR-10, FR-13–FR-14 |
| TC-PAR-008 | Time-domain envelope analysis | AM-modulated or bursty signal | 1. Compute analytical signal envelope → Extract envelope from IQ | Envelope shape matches expected modulation | Burst duty cycle measurable | FR-09–FR-10, FR-13–FR-14 |
| TC-PAR-009 | Spectral flatness (Wiener entropy) | Wideband noise vs. narrow signal | 1. Compute spectral entropy → Normalize | Entropy low for pure tone; high for noise | Useful for signal presence detection | FR-09–FR-10, FR-13–FR-14 |
| TC-PAR-010 | Crest factor measurement | Multi-carrier or linear modulation | 1. Compute crest factor (peak/RMS) | Crest factor within expected range for modulation | Parameter feeds into modulation classifier | FR-09–FR-10, FR-13–FR-14 |
| TC-AMC-001 | BPSK classification (high SNR) | Ground-truth BPSK reference, 20 dB SNR | 1. Load BPSK signal → Run classifier → Read prediction | Predicted class = BPSK; confidence > 0.95 | Accuracy ≥95% on held-out BPSK set | FR-11–FR-12 |
| TC-AMC-002 | QPSK classification (high SNR) | Ground-truth QPSK reference, 20 dB SNR | 1. Load QPSK signal → Run classifier → Read prediction | Predicted class = QPSK; confidence > 0.90 | Accuracy ≥90% on held-out QPSK set | FR-11–FR-12 |
| TC-AMC-003 | 8-PSK classification | Ground-truth 8-PSK reference | 1. Load 8-PSK signal → Classify | Predicted class = 8-PSK | Accuracy ≥85% | FR-11–FR-12 |
| TC-AMC-004 | 16-QAM classification | Ground-truth 16-QAM reference | 1. Load 16-QAM signal → Classify | Predicted class = 16-QAM | Accuracy ≥80% | FR-11–FR-12 |
| TC-AMC-005 | 64-QAM classification | Ground-truth 64-QAM reference | 1. Load 64-QAM signal → Classify | Predicted class = 64-QAM | Accuracy ≥80% | FR-11–FR-12 |
| TC-AMC-006 | FSK classification (2-FSK) | Ground-truth 2-FSK reference | 1. Load 2-FSK signal → Classify | Predicted class = FSK | Accuracy ≥85% | FR-11–FR-12 |
| TC-AMC-007 | Low-SNR classification (5 dB) | QPSK at 5 dB SNR | 1. Load low-SNR signal → Classify → Check confidence | Prediction made; confidence appropriately reduced (0.6-0.7) | Low-confidence predictions flagged; not presented as certain | FR-11–FR-12 |
| TC-AMC-008 | Out-of-Distribution rejection | Signal of unknown modulation (not in training set) | 1. Load OOD signal → Classify | Prediction made; confidence < 0.5 or explicit "Unknown" flag | OOD detection working; no false high confidence | FR-11–FR-12 |
| TC-AMC-009 | Ambiguous class distinction (QPSK vs. 16-QAM) | Signal that resembles both | 1. Load ambiguous signal → Inspect confidence scores | Top-2 classes identified; confidence spread quantified | Tie-breaking logic documented | FR-11–FR-12 |
| TC-AMC-010 | Model version traceability | Analysis with 2 different trained models | 1. Analyze same input with Model v1 and v2 → Compare results | Results clearly tagged with model version; no artifact mixing | Version info in output report | FR-11–FR-12 |
| TC-AMC-011 | Batch classification | 100 sequential analysis runs | 1. Run batch mode on 100 files → Verify no data leakage | Results for file N do not contain artifacts from file N-1 | Batch isolation verified | FR-11–FR-12 |
| TC-AMC-012 | Confidence calibration | Classification confidence vs. actual accuracy | 1. Plot confidence vs. error rate on test set | Calibration curve monotonic; high-confidence predictions accurate | Brier score < 0.1 | FR-11–FR-12 |
| TC-DEM-001 | Symbol timing recovery (Müller & Müller) | QPSK signal with unknown symbol phase | 1. Load signal without symbol timing → Run timing recovery → Examine eye diagram | Eye diagram opens; symbol decisions aligned | Timing error < 0.2 symbols | FR-15–FR-19 |
| TC-DEM-002 | Carrier phase/frequency recovery (PLL) | QPSK with 5 kHz frequency offset | 1. Load signal → Run PLL (Costas loop) → Measure residual offset | Residual offset < 100 Hz | Enable demodulation without error floors | FR-15–FR-19 |
| TC-DEM-003 | BPSK demodulation (clean) | Reference BPSK, 20 dB SNR, perfect timing | 1. Load BPSK → Demodulate → Extract bitstream → Compare to known bits | BER = 0 | Perfect recovery on clean reference | FR-15–FR-19 |
| TC-DEM-004 | QPSK demodulation (clean) | Reference QPSK, 20 dB SNR, perfect timing | 1. Load QPSK → Demodulate → Extract bits | BER = 0 | Perfect recovery on clean reference | FR-15–FR-19 |
| TC-DEM-005 | 16-QAM demodulation (clean) | Reference 16-QAM, 20 dB SNR | 1. Load 16-QAM → Demodulate → Extract bits | BER = 0 | Perfect recovery on clean reference | FR-15–FR-19 |
| TC-DEM-006 | FSK demodulation (2-FSK) | Reference 2-FSK with known tone spacing | 1. Load 2-FSK → Run tone detector → Extract bits | Bits match reference bitstream | BER = 0 on clean signal | FR-15–FR-19 |
| TC-DEM-007 | QPSK demodulation (low SNR, 5 dB) | QPSK at 5 dB SNR | 1. Demodulate at low SNR → Measure BER | BER consistent with theoretical performance | Soft-decision BER ~2% at 5 dB SNR | FR-15–FR-19 |
| TC-DEM-008 | PSK ambiguity resolution | PSK signal with unknown phase rotation | 1. Attempt demod with Viterbi sequence detection → Resolve ambiguity | Differential encoding or Viterbi resolves 4-way ambiguity | Phase ambiguity eliminated | FR-15–FR-19 |
| TC-DEM-009 | Differential detection (DQPSK) | Differentially-encoded QPSK | 1. Load DQPSK signal → Demodulate using differential detector | Bits recovered without requiring explicit phase ref | BER < 1e-3 on clean signal | FR-15–FR-19 |
| TC-DEM-010 | Matched filter + decision | Gaussian-shaped pulses (GMSK) | 1. Design matched filter → Apply to received signal → Make hard decisions | Maximize SNR; align decisions to symbol boundaries | ISI minimized; BER near theory | FR-15–FR-19 |
| TC-DEM-011 | Soft-decision symbol output (LLR) | Demodulator configured for soft output | 1. Demodulate → Generate log-likelihood ratios (LLRs) for each bit | LLRs provided to FEC decoder | LLRs have correct sign/magnitude relationship | FR-15–FR-19 |
| TC-DEM-012 | Demod with frequency offset | Signal with 5 kHz frequency offset | 1. Run demodulator → Correct frequency offset → Measure BER | Offset correction enables BER < 1e-3 | Frequency correction working | FR-15–FR-19 |
| TC-INT-001 | Block de-interleaving (4x4) | Bitstream with known block interleaving | 1. Load interleaved bits → Apply 4x4 block de-interleaver → Compare to reference | De-interleaved bits match ground-truth order | Zero bit transpositions; correct permutation inverse | FR-20–FR-23 |
| TC-INT-002 | Convolutional de-interleaving (depth=4) | Bitstream with convolutional interleaving | 1. Load interleaved bits → Apply convolutional de-interleaver (depth=4) → Compare | De-interleaved order matches reference | Correct delay accumulation/reversal | FR-20–FR-23 |
| TC-INT-003 | Diagonal (rail-fence) de-interleaving | Bitstream with diagonal interleaving | 1. Load interleaved bits → Apply diagonal de-interleaver → Compare | De-interleaved bits match reference permutation | Rail-fence reversal correct | FR-20–FR-23 |
| TC-INT-004 | Pseudo-random de-interleaving | Bitstream with pseudo-random permutation (seed=12345) | 1. Load interleaved bits → Apply PRNG de-interleaver (seed match) → Compare | De-interleaved order matches reference | PRNG state synchronization correct | FR-20–FR-23 |
| TC-INT-005 | De-interleaver auto-detection | Unknown interleaved bitstream | 1. Attempt to auto-detect interleaver type → Run appropriate de-interleaver | System identifies correct interleaving scheme | Detected scheme matches injected type with >80% confidence | FR-20–FR-23 |
| TC-INT-006 | Cascaded de-interleaving (2-stage) | Double-interleaved bitstream | 1. Apply first de-interleaver → Apply second de-interleaver → Compare | Bitstream de-interleaved correctly (order-sensitive) | Both stage permutations applied in correct order | FR-20–FR-23 |
| TC-INT-007 | Burst error protection (interleaving resilience) | Interleaved bitstream; apply burst error | 1. Corrupt 10 consecutive bits after interleaving → De-interleave → Analyze error spread | Burst error dispersed across multiple codewords | Error spread improves downstream FEC performance | FR-20–FR-23 |
| TC-FEC-001 | Viterbi hard-decision decoding (K=7, R=1/2) | Convolutional-coded bitstream (K=7, R=1/2, G=[133,171]) | 1. Load coded bitstream → Run hard Viterbi decoder → Compare to reference bits | Decoded bits match reference; BER improvement observed | Hard-decision works; ~3 dB gain at high SNR | FR-24–FR-27 |
| TC-FEC-002 | Viterbi soft-decision decoding (LLR input) | LLRs from demodulator over noisy QPSK | 1. Feed LLRs to Soft Viterbi Decoder → Decode → Measure BER | Soft-decision yields ~2 dB coding gain vs. hard | Zero bit errors at lower SNR than hard Viterbi | FR-24–FR-27 |
| TC-FEC-003 | Reed-Solomon (255,223) decoding | RS-coded block over GF(2^8); 10 byte errors inserted | 1. Input corrupted RS codeword → Execute Berlekamp-Massey decoder → Verify output | All 10 byte errors corrected (t ≤ 16) | Decoded block matches ground truth; error count = 10 | FR-24–FR-27 |
| TC-FEC-004 | Reed-Solomon beyond error capability | RS(255,223) with 20 byte errors (exceeds t=16) | 1. Input block with 20 errors → Execute RS decoder | Decoder flags "Uncorrectable Error" exception | No silent corruption; user informed of failure | FR-24–FR-27 |
| TC-FEC-005 | Concatenated coding (RS outer + Viterbi inner) | Dual-layer encoded stream (outer RS + inner Viterbi) with burst noise | 1. Run Inner Viterbi → De-interleave → Run Outer RS → Inspect output | All error types corrected (random via Viterbi, bursts via RS) | Final output 100% error-free | FR-24–FR-27 |
| TC-FEC-006 | LDPC soft-decision decoding (sum-product) | LDPC code (rate 1/2) corrupted by AWGN | 1. Feed soft LLRs → Run iterative BP algorithm (max 50 iter) → Check parity | Syndrome $H \cdot x^T = 0$ satisfied within 12 iterations | Clean codeword recovered; iterations ≤ 50 | FR-24–FR-27 |
| TC-FEC-007 | FEC scheme auto-detection | Unknown encoded bitstream | 1. Run syndrome likelihood estimator → Measure detected FEC type | System identifies candidate FEC structure | Detected scheme matches injected coding | FR-24–FR-27 |
| TC-FEC-008 | Turbo code decoding (if applicable) | Turbo-coded bitstream | 1. Run turbo decoder with 4 iterations → Check output | Interleaver-dependent gain achieved | Performance near Shannon limit (within 1 dB) | FR-24–FR-27 |
| TC-FEC-009 | Erasure channel with FEC (fountain codes if used) | Coded data with packet loss | 1. Decode with missing packets → Verify recovery | Packets recovered up to code rate limit | Recovery threshold matches theoretical bound | FR-24–FR-27 |
| TC-FEC-010 | FEC failure reporting | FEC decoder unable to correct | 1. Force uncorrectable error scenario → Observe error handling | Decoder returns failure status; earlier-stage results preserved | Partial report generated; failure clearly documented | FR-24–FR-27 |
| TC-COR-001 | Frame sync correlation (exact match) | Decoded bitstream containing 32-bit sync word `0x1ACFFC1D` | 1. Load sync pattern → Execute sliding-window correlator → Locate peak | Peak occurs at exact sync start index | Correlation score = 32 at correct bit offset | FR-28–FR-30 |
| TC-COR-002 | Sync with bit errors (Hamming tolerance) | Bitstream with sync word + 2 flipped bits | 1. Set Hamming distance tolerance = 3 → Run correlator | Peak detected at correct offset despite errors | Match score = 30 ≥ threshold (29) | FR-28–FR-30 |
| TC-COR-003 | Header field dissection | Synchronized frame with 16-byte header (Sync + Length + ID + CRC) | 1. Execute header parser → Extract fields | Payload length, transmitter ID, sequence number extracted | Fields parsed into UI inspector table | FR-28–FR-30 |
| TC-COR-004 | Payload extraction & CRC-16 verification | Frame with payload + CRC-16 trailer | 1. Strip header/trailer → Compute CRC over payload → Compare with trailer | Calculated CRC matches frame trailer | Payload flagged as "Valid" | FR-28–FR-30 |
| TC-COR-005 | Payload export (binary/hex/JSON) | Valid extracted payload | 1. Click Export → Select format `.bin` / `.hex` / `.json` → Save | Files generated with correct content | Exported data byte-accurate | FR-28–FR-30 |
| TC-COR-006 | False sync rejection (random noise) | White noise bitstream | 1. Run correlator with pattern `0x1ACFFC1D` | Scores remain below threshold → "No Frame Sync Found" | Zero false-positive sync detections | FR-28–FR-30 |
| TC-COR-007 | Multi-frame extraction | Bitstream with N sequentially-framed payloads | 1. Correlate multiple sync words → Extract all frames | All N frames identified and extracted | Frame count = N; no frame loss | FR-28–FR-30 |
| TC-COR-008 | Payload size inference | Unknown frame structure | 1. Run heuristic length field parser → Infer payload size | System correctly interprets length field or reports ambiguity | Length extracted; extraction succeeds | FR-28–FR-30 |
| TC-COR-009 | Interleaved payload recovery | Payload with de-interleaving already applied | 1. Extract payload (assuming de-interleave already done) → Render bitstream | Payload bits in correct order | De-interleaving prerequisite validated | FR-28–FR-30 |
| TC-COR-010 | Partial payload recovery on FEC failure | FEC decoder unable to correct; partial payload available | 1. Attempt payload extract despite FEC failure → Report what's recoverable | Partial payload extracted; FEC failure documented | User sees recoverable data + warnings | FR-28–FR-30 |
| TC-GUI-001 | File picker dialog | Application main window open | 1. Click "Open File" → Browse to signal file → Select → Confirm | File selected; path displayed in UI | File path field updated; preview triggered | FR-31–FR-36 |
| TC-GUI-002 | Analysis start / progress indicator | File loaded; parameters set | 1. Click "Run Analysis" → Observe progress bar | Progress bar advances; stages labeled (Ingestion → Preprocessing → AMC → Demod → FEC) | Progress updates smoothly; ETA displayed | FR-31–FR-36 |
| TC-GUI-003 | Real-time plot rendering (waterfall) | Analysis in progress | 1. Observe waterfall plot during live processing | Spectrogram updates smoothly in real-time | Rendering non-blocking; GUI interactive | FR-31–FR-36 |
| TC-GUI-004 | Result inspection panel | Analysis complete | 1. Click each result tab (Spectrum / Constellation / Parameters / Classification) | Each tab displays appropriate visualization + metrics | All views load on demand; no delays | FR-31–FR-36 |
| TC-GUI-005 | Export report dialog | Analysis complete | 1. Click "Export Report" → Select format (PDF / JSON / CSV) → Save location | Report file generated on disk | Report contains analysis metadata + results | FR-31–FR-36 |
| TC-GUI-006 | Error message clarity | File loading fails (e.g., corrupt WAV) | 1. Attempt to load corrupt file → Observe error dialog | Clear error message with corrective action suggested | User understands problem; path forward offered | FR-31–FR-36 |
| TC-GUI-007 | Tooltip & help text | Mouse hover over UI elements | 1. Hover over parameter fields, buttons, etc. → Observe tooltips | Context-sensitive help appears | Tooltips accurate and concise | FR-31–FR-36 |
| TC-GUI-008 | Window resize & layout responsiveness | Application window resized | 1. Drag window edges to change size → Observe layout | Plots and tables resize correctly; no element clipping | Responsive layout preserved | FR-31–FR-36 |
| TC-GUI-009 | Multi-file batch mode | Multiple input files listed | 1. Select 5 files → Click "Batch Process" → Monitor completion | All files processed sequentially; results linked to sources | Batch output organized by input file | FR-31–FR-36 |
| TC-GUI-010 | Configuration persistence | User modifies settings (FFT size, window type, etc.) | 1. Change parameters → Close application → Reopen | Settings restored from previous session | Configuration file on disk; session state replayed | FR-31–FR-36 |
| TC-GUI-011 | Dark/Light theme toggle | Application theme selector present | 1. Click theme option → Observe UI colors | Entire GUI switches themes; plots readable in both modes | Theme consistent across all windows | FR-31–FR-36 |
| TC-GUI-012 | Keyboard shortcuts | Keyboard input focus | 1. Press Ctrl+O (open), Ctrl+S (save), etc. → Observe action | Shortcuts trigger expected operations | Shortcuts documented in Help menu | FR-31–FR-36 |
| TC-GUI-013 | Undo/Redo functionality (if applicable) | User makes analysis choices | 1. Run analysis A → Run analysis B → Click Undo → Verify return to A state | Previous analysis state restored | Undo stack maintained correctly | FR-31–FR-36 |
| TC-GUI-014 | Status bar updates | Various operations in progress | 1. Observe status bar during file load, processing, export | Status messages update in real-time | Clear indication of current operation | FR-31–FR-36 |
| TC-GUI-015 | Drag-and-drop file loading | GUI main window visible | 1. Drag `.iq` or `.wav` file onto window → Drop | File automatically loaded; processing can start | Drag-drop handler functional | FR-31–FR-36 |
| TC-PER-001 | Processing speed (100 MB file) | 100 MB raw `.iq` file on disk | 1. Start timer → Execute E2E pipeline → Stop timer | Entire pipeline completes in < 5.0 seconds on 8-core CPU | Total time ≤ 5.0 sec | NFR-01, NFR-03 |
| TC-PER-002 | GUI responsiveness during processing | 1 GB file being processed in background | 1. Trigger processing → Interact with GUI (move window, click tabs) → Measure latency | Main thread remains responsive; no "Not Responding" freezes | UI latency < 100 ms per interaction | NFR-01, NFR-03 |
| TC-PER-003 | Memory leak detection | 100 sequential file analysis runs | 1. Execute batch loop (100 files) → Log memory via `psutil` → Plot trend | Memory stabilizes after warmup; no unbounded growth | RAM growth < 50 MB over 100 iterations | NFR-01, NFR-03 |
| TC-PER-004 | Multi-core CPU utilization | 8-core workstation available | 1. Process large file with multiprocessing enabled → Monitor CPU cores via `htop` | Load distributed evenly; all cores active | All cores show > 80% utilization during processing | NFR-01, NFR-03 |
| TC-PER-005 | GPU acceleration (if available) | NVIDIA GPU with CUDA available | 1. Enable GPU mode → Process file → Compare GPU vs. CPU time | GPU processing faster by ≥2x vs. single-core | GPU/CPU speedup ratio quantified | NFR-01, NFR-03 |
| TC-PER-006 | Disk I/O throughput | Large file on fast NVMe SSD | 1. Load 2 GB file → Time ingestion step only | File read completes in < 2 seconds | Disk throughput ≥ 1 GB/sec achieved | NFR-01, NFR-03 |
| TC-PER-007 | FFT performance (parallelization) | FFT size 4096, 10k operations | 1. Benchmark single-threaded FFT → Benchmark multi-threaded → Compare | Multi-threaded FFT faster by ≥N (N = # cores) | Parallelization scaling near-linear | NFR-01, NFR-03 |
| TC-PER-008 | Model inference latency (AMC) | ML classifier running on CPU/GPU | 1. Measure time for single inference pass | Inference time < 100 ms per window (for real-time viability) | Inference latency within budget | NFR-01, NFR-03 |
| TC-PER-009 | Viterbi decoder throughput | Decoding 1M bits | 1. Measure bits/second decoded by Viterbi | Throughput > 1 Mbps on single core | Decoding speed meets real-time requirement | NFR-01, NFR-03 |
| TC-PER-010 | Scaling with file size | Files of 10 MB, 100 MB, 1 GB | 1. Process each file → Plot time vs. size → Measure scaling factor | Processing time scales linearly with file size | O(N) complexity confirmed | NFR-01, NFR-03 |
| TC-SEC-001 | Zero network socket verification | Wireshark packet capture active | 1. Launch app → Ingest file → Run analysis → Export report → Close → Inspect Wireshark log | Zero network sockets opened; zero DNS/HTTP/telemetry packets | Network log contains 0 packets from app PID | NFR-02, NFR-06 |
| TC-SEC-002 | Temporary file cleanup | Application session with signal file loaded | 1. Close application → Inspect `/tmp` and app cache dirs | Temporary buffers wiped; no unencrypted temp files remaining | Temp cache clean; zero orphan signal files on disk | NFR-02, NFR-06 |
| TC-SEC-003 | Offline standalone execution | Workstation disconnected from network (air-gapped) | 1. Disable network adapters → Boot system → Launch app → Run full pipeline | All functions work 100%; no network timeouts or errors | Zero network-related failures | NFR-02, NFR-06 |
| TC-SEC-004 | Input path sanitization (injection prevention) | File picker allows arbitrary paths | 1. Attempt to open file with path containing special chars: `../`, `\x00`, etc. | System sanitizes path; no command injection or directory traversal | File loading safe; no symlink attacks | NFR-02, NFR-06 |
| TC-SEC-005 | Config file validation | Application configuration file (JSON/YAML) | 1. Inject malicious config (code exec, symlink) → Run app → Observe behavior | Config parsed safely; malicious entries rejected or logged as errors | No arbitrary code execution from config | NFR-02, NFR-06 |
| TC-SEC-006 | Sensitive data in logs | Logging enabled during analysis | 1. Run analysis → Examine log files → Search for raw signal data, IQ samples, or keys | Logs do not contain raw signal samples; only metadata/parameters | Zero leakage of sensitive IQ data in logs | NFR-02, NFR-06 |
| TC-SEC-007 | Memory isolation (process sandboxing) | Multi-user workstation | 1. Run app under different user accounts simultaneously → Check process isolation | Each process memory isolated; no cross-user data leakage | Proc memory maps do not overlap | NFR-02, NFR-06 |
| TC-SEC-008 | Signal file permissions | Processed signal file in output directory | 1. Process file → Check output permissions → Verify readability by intended user only | Output files owned by user; world-readable bits not set | Permissions 0640 (rw-r-----) or stricter | NFR-02, NFR-06 |
| TC-STORE-001 | Result persistence (JSON export) | Analysis complete | 1. Export result as JSON → Close app → Reload JSON in Python → Verify content | Result file contains all analysis metadata and findings | File format parseable; data lossless | FR-37–FR-40, NFR-07–NFR-08 |
| TC-STORE-002 | Result traceability (input metadata) | Analysis result exported | 1. Inspect exported result → Check input filename, file hash, config, model version | Result linked to input file (name/hash), config version, model version | Audit trail complete; reproducibility possible | FR-37–FR-40, NFR-07–NFR-08 |
| TC-STORE-003 | Report generation (PDF) | Analysis complete | 1. Export as PDF → Open PDF → Verify content (plots, tables, text) | PDF contains analysis summary, plots, parameter table, classification | PDF readable; formatting intact | FR-37–FR-40, NFR-07–NFR-08 |
| TC-STORE-004 | Batch export with input mapping | 10 files processed in batch | 1. Export batch results → Verify each output filename maps to correct input | Every output maps to correct source file; no result mixing | Input/output mapping verified for all files | FR-37–FR-40, NFR-07–NFR-08 |
| TC-STORE-005 | Result versioning | Same file analyzed with 2 model versions | 1. Analyze with Model v1 → Export → Analyze with Model v2 → Export → Compare results | Results clearly tagged with model version; no artifact mixing | Version info prevents accidental comparison of incompatible results | FR-37–FR-40, NFR-07–NFR-08 |
| TC-STORE-006 | Incremental result saving (checkpoint) | Long-running analysis | 1. Start analysis → Kill process at 50% completion → Restart → Resume from checkpoint | Earlier stages' results saved and reused; no re-computation | Checkpoint files on disk; resume working | FR-37–FR-40, NFR-07–NFR-08 |
| TC-STORE-007 | Result archive compression | 50 result files | 1. Select "Archive Results" → Choose `.zip` or `.tar.gz` format → Save | Archive created with all results; metadata intact | Archive extractable; all files recoverable | FR-37–FR-40, NFR-07–NFR-08 |
| TC-STORE-008 | Encryption at rest (if required) | Sensitive result file | 1. Enable encryption option → Save result → Verify file is encrypted on disk → Reopen | File encrypted; unreadable without key/password | Decryption on load successful; content matches | FR-37–FR-40, NFR-07–NFR-08 |
| TC-STORE-009 | Metadata embedding in output | Analysis result saved to multiple formats | 1. Save result as JSON, CSV, PDF → Open each → Verify metadata present | Metadata (timestamp, user, model version) embedded in each format | Metadata human-readable or machine-extractable | FR-37–FR-40, NFR-07–NFR-08 |
| TC-STORE-010 | Long-term result reproducibility | Result saved 1 year ago | 1. Reload old result file with current software version → Compare analysis | System can parse old format; results match original | Backward compatibility maintained or clear migration path | FR-37–FR-40, NFR-07–NFR-08 |
| TC-E2E-001 | Clean QPSK E2E (high SNR) | Reference QPSK signal (20 dB SNR) | 1. Load QPSK file → Run analysis → Export report | File → Parameter extraction → AMC (QPSK detected, confidence > 0.9) → Demodulation (BER = 0) → Output | E2E success; all stages pass; clean bitstream recovered | FR-01–FR-40, NFR-01–NFR-08 |
| TC-E2E-002 | BPSK with FEC E2E | BPSK signal with Viterbi coding | 1. Load → Analyze → Demodulate → Run Viterbi → Export | Viterbi decoding succeeds; output bitstream error-free | Coding gain demonstrated; FEC working | FR-01–FR-40, NFR-01–NFR-08 |
| TC-E2E-003 | FSK with de-interleaving E2E | 2-FSK signal with block interleaving | 1. Load → Classify → Demodulate FSK → De-interleave (block) → Compare output | De-interleaved bitstream matches reference order | Multi-stage pipeline integrated correctly | FR-01–FR-40, NFR-01–NFR-08 |
| TC-E2E-004 | Low-SNR E2E (5 dB QPSK) | QPSK at 5 dB SNR | 1. Load → Analyze → Demodulate → Measure BER | BER consistent with theoretical low-SNR performance (~2% at 5 dB) | System handles impaired signal gracefully | FR-01–FR-40, NFR-01–NFR-08 |
| TC-E2E-005 | Multi-signal separation E2E (optional) | Two signals (BPSK + FSK) overlapping | 1. Load → Attempt separation → Classify each → Demodulate each | System identifies both signals; classifies separately; demodulates both | Signal separation capability (if implemented) works | FR-01–FR-40, NFR-01–NFR-08 |
| TC-E2E-006 | Batch processing E2E | 5 different signal files | 1. Select all 5 files → Click "Batch Process" → Wait for completion | All 5 processed independently; results exported per file | Batch mode isolates analyses; no cross-contamination | FR-01–FR-40, NFR-01–NFR-08 |
| TC-E2E-007 | Persistence & reload E2E | Analysis result exported and closed | 1. Export result → Close application → Reopen → Load exported result | Result re-loaded; all analysis data restored; plots recreated | Result file self-contained; reload functional | FR-01–FR-40, NFR-01–NFR-08 |
| TC-E2E-008 | Model version traceability E2E | Analyze with Model A → Switch to Model B → Re-analyze same file | 1. Analyze file with Model A → Export → Switch to Model B → Re-analyze → Compare results | Results tagged with correct model; no artifact mixing | Version info prevents accidental comparison | FR-01–FR-40, NFR-01–NFR-08 |
| TC-E2E-009 | Failed decoder partial report E2E | Demodulation succeeds; FEC fails | 1. Run analysis on file with uncorrectable errors → Export report | Report retains demodulation results; FEC failure documented; partial success shown | System graceful on FEC failure; earlier results preserved | FR-01–FR-40, NFR-01–NFR-08 |
| TC-E2E-010 | Repeated analysis isolation E2E | Analyze file A then file B sequentially | 1. Load A → Analyze → Load B → Analyze → Verify B result has no A artifacts | B result clean; no state leak from A | Session isolation working; no cross-file contamination | FR-01–FR-40, NFR-01–NFR-08 |

## 9. PS-to-Test Traceability

| PS capability | Mandatory tests | Evidence required |
|---|---|---|
| Input `.IQ` / `.wav` | ING2-001..025, legacy TC-ING-* | File hash + parsed metadata + sample-count verification |
| Sampling frequency | PAR2-001..006, legacy TC-PAR-* | True Fs vs reported Fs; metadata/estimated provenance |
| Modulation identification | AMC2-001..028 | Confusion matrix, accuracy, per-class metrics, confidence |
| FEC identification | FEC2-026 plus manual-override tests | Candidate scheme + confidence OR explicit gap |
| Interleaving identification | INT2-009..014 plus manual-override tests | Candidate scheme/parameters + confidence OR explicit gap |
| FSK demodulation | DEM2-010..013, E2E2-004..005 | Source bitstream comparison/BER |
| PSK demodulation | DEM2-001..009, E2E2-001..003 | BER/constellation/synchronization evidence |
| QAM demodulation | DEM2-014..017, E2E2-006..007 | BER/constellation/equalization evidence |
| Block de-interleaving | INT2-001..003, E2E2-008 | Bit-exact round trip |
| Convolutional de-interleaving | INT2-004..006, E2E2-009 | Bit-exact round trip |
| Diagonal de-interleaving | INT2-006..007, E2E2-010 | Bit-exact round trip |
| Pseudo-random de-interleaving | INT2-007..008, E2E2-011 | Seeded bit-exact round trip |
| Viterbi FEC | FEC2-001..011, E2E2-012 | BER before/after + decoded source |
| Reed-Solomon | FEC2-012..017, E2E2-013 | Correctable and uncorrectable cases |
| Concatenated coding | FEC2-018..020, E2E2-014 | Correct stage ordering + source recovery |
| LDPC | FEC2-021..025, E2E2-015 | Syndrome/convergence + recovered bits |
| Bitstream correlation | COR2-001..024, E2E2-016 | Frame offsets + match metrics + exports |
| GUI visibility | VIS2, GUI2 | Screenshots/video + measured responsiveness |
| Offline operation | SEC2-001..028, E2E2-029 | Packet capture/system trace showing zero external communication |

## 10. Critical Spec Consistency Checks

| Check | Why it matters | Tester action |
|---|---|---|
| PS vs SRS FEC/interleaver identification | PS asks for identification; SRS heavily specifies decoding | Verify automatic detection exists. Manual selection alone is not full identification. |
| 2D vs 3D waterfall | Charter mentions dynamic 2D/3D; SRS/system design emphasize 2D waterfall | Confirm exactly what the delivered UI supports and document any scope decision. |
| QAM coverage | PS says QAM generically; SRS expands to 16/64 and also lists 256-QAM in AMC taxonomy | Verify implemented classes and keep documentation consistent with actual support. |
| Fs for metadata-free IQ | Raw IQ may not contain enough information to uniquely infer physical sample rate | Verify the product can return `unknown` and request/accept manual metadata rather than inventing Fs. |
| Multi-signal separation | System design assumes a single isolated signal; some legacy cases mention multi-signal separation | Do not count multi-signal separation toward mandatory PS compliance unless the implementation explicitly includes it. |
| Encryption/decryption | Out of scope | Test that the application does not falsely advertise decryption support. |
| Real-time SDR | Out of scope | Test file-analysis workflow only; do not use live SDR hardware as a release blocker. |

## 11. Accuracy Metrics — Required Calculation Rules

### AMC
- Overall accuracy
- Per-class precision, recall, F1
- Confusion matrix
- Accuracy stratified by SNR
- Top-1 and top-N accuracy where top-N is supported
- Unknown/abstain rate on unsupported/OOD signals

### Parameter estimation
- Relative Fs error = `abs(Fs_est - Fs_true) / Fs_true`
- Absolute CFO error
- Absolute/relative symbol-rate error
- Occupied-bandwidth error
- SNR estimation error

### Demodulation / decoding
- BER before decoding
- BER after FEC
- Symbol error rate where applicable
- Frame recovery rate
- Payload exact-match rate
- FEC failure rate

### Correlation
- Correct frame-start index rate
- False positive rate
- Hamming distance
- Correlation peak value
- Header/payload boundary exactness

### Performance
- End-to-end latency
- Stage-wise latency
- Peak RSS memory
- CPU utilization
- GPU memory/utilization if applicable
- Cancellation latency

## 12. Required Negative Testing Matrix

Every supported stage must be tested with:

- Empty input
- Truncated input
- Corrupt header/metadata
- Wrong datatype
- Wrong endianness
- Invalid parameter value
- Out-of-range parameter value
- NaN/Inf where programmatically injectable
- Noise-only signal
- Unsupported modulation
- Low-SNR signal
- Wrong manual configuration
- Unrecoverable FEC
- Wrong interleaver seed/parameters
- Missing model/config
- Permission error
- Insufficient disk space
- Insufficient memory
- Cancellation at that stage
- Repeated execution
- Same input with different valid configuration

## 13. Mandatory End-to-End Acceptance Gates

| Gate | Required result | Blocking? |
|---|---|---|
| A1 Installation | Windows 10/11 + Ubuntu 22.04 supported build launches and runs smoke test | P0 |
| A2 Input | Valid IQ/WAV fixtures parse correctly; malformed files fail safely | P0 |
| A3 Visualization | Waveform + FFT + waterfall; constellation where applicable | P0 |
| A4 Fs | Correct metadata or estimate within ±2%; otherwise `unknown` | P0 |
| A5 AMC | ≥90% benchmark accuracy at SNR ≥5 dB | P0 |
| A6 Demod | FSK, PSK and QAM required families recover known test bits within defined BER limits | P0 |
| A7 De-interleave | All four required methods pass bit-exact reference tests | P0 |
| A8 FEC | Viterbi, RS, concatenated and LDPC pass their enabled acceptance fixtures | P0/P1 by implementation status |
| A9 Correlation | Preamble/header/payload boundaries correct on known frames | P0 |
| A10 GUI | Non-blocking, progress, cancellation, actionable errors | P0 |
| A11 Reporting | JSON/PDF + bitstream exports + provenance | P1 |
| A12 Performance | 100 MB E2E <5s; FFT <50ms; AMC <100ms; Viterbi target met on reference system | P0 |
| A13 Security | Zero external network activity; offline model execution | P0 |
| A14 Reproducibility | Same input/config/model yields equivalent result and complete provenance | P1 |
| A15 Robustness | No crash on malformed input, OOM, partial files, decoder failure | P0 |

## 14. Tester Sign-Off Checklist

- [ ] All P0 tests executed
- [ ] All P1 tests executed or formally waived
- [ ] No open P0 defects
- [ ] No unresolved data-integrity defects
- [ ] No network traffic observed
- [ ] Benchmark evidence archived
- [ ] AMC ≥90% benchmark evidence archived
- [ ] Every required modulation has a golden fixture
- [ ] Every required interleaver has a bit-exact golden fixture
- [ ] Every required FEC has correctable and uncorrectable fixtures
- [ ] FEC/interleaver **identification** behavior documented separately from decode behavior
- [ ] All manual overrides recorded in provenance
- [ ] Exported report, JSON, bitstream and logs are reproducible
- [ ] Final build/version/hash recorded
- [ ] Dataset/model version and hashes recorded
- [ ] Release candidate smoke suite passes

## 15. Defect Reporting Template

```text
Defect ID:
Test ID:
Build / Commit:
Severity:
Environment:
Input Fixture:
Input SHA-256:
Dataset / Model Version:
Configuration:
Manual Overrides:
Expected:
Actual:
Numeric Evidence:
Logs / Artifact Paths:
Reproduction Steps:
Frequency: Always / Intermittent
Regression: Yes / No
Owner:
Status:
```

## 16. Final Rule

**Do not mark the product 'PS compliant' because the GUI looks complete.** The release claim must be backed by measured signal-level evidence: correct parsing, correct physical parameter estimates, correct modulation classification, successful synchronization/demodulation, correct de-interleaving, measurable FEC correction, correct correlation/frame extraction, reproducible exports, and verified offline operation.

**Document source basis:**
- Problem Statement ID 26147
- Consolidated SRS/PRD v2.0, September 2026
- System Design v2.0, September 2026
- Dataset Acquisition, Preparation, Training & Evaluation Handbook v2.0, September 2026
- Existing Master Test Plan v2.0