"""
Unit Test Suite for Module 4: Parameter Extraction
Corresponds to Master Test Plan TC-PAR-001 through TC-PAR-010.
"""

import pytest
import numpy as np

from ntro_sigint.dsp.parameter_extractor import ParameterExtractor, SignalParameters


class TestParameterExtraction:

    def test_tc_par_001_sampling_rate_estimation(self):
        """TC-PAR-001: Sampling frequency (Fs) estimation."""
        nominal_fs = 20000000.0 # 20 MHz
        samples = np.random.randn(1000) + 1j * np.random.randn(1000)
        est_fs = ParameterExtractor.estimate_sampling_rate(samples, nominal_fs)
        rel_error = abs(est_fs - nominal_fs) / nominal_fs
        assert rel_error < 0.01

    def test_tc_par_002_symbol_rate_detection(self):
        """TC-PAR-002: Symbol rate detection."""
        fs = 1.0e6 # 1 MHz
        true_sym_rate = 50000.0 # 50 kbaud
        sps = int(fs / true_sym_rate) # 20 samples per symbol
        n_symbols = 2000

        # Generate QPSK symbols
        bits_i = np.random.choice([-1.0, 1.0], size=n_symbols)
        bits_q = np.random.choice([-1.0, 1.0], size=n_symbols)
        symbols = bits_i + 1j * bits_q

        # Pulse shape with square-root raised cosine (RRC) or rectangular
        upsampled = np.zeros(n_symbols * sps, dtype=np.complex64)
        upsampled[0::sps] = symbols
        # Lowpass filter / pulse shape
        pulse = np.ones(sps, dtype=np.float32) / np.sqrt(sps)
        tx_signal = np.convolve(upsampled, pulse, mode='same')

        detected_rate, confidence = ParameterExtractor.detect_symbol_rate(
            tx_signal, fs=fs, expected_range=(10000, 100000)
        )

        rel_error = abs(detected_rate - true_sym_rate) / true_sym_rate
        assert rel_error <= 0.02 # Within +/- 2%
        assert confidence > 0.70

    def test_tc_par_003_bandwidth_measurement(self):
        """TC-PAR-003: Bandwidth measurement."""
        fs = 1.0e6
        # Generate signal with known bandwidth: lowpass filtered noise
        target_bw = 100000.0 # 100 kHz bandwidth (single-sided 50 kHz)
        n = 16384
        noise = (np.random.randn(n) + 1j * np.random.randn(n)).astype(np.complex64)

        # Ideal brick-wall filter in frequency domain to establish exact ground truth
        fft_noise = np.fft.fftshift(np.fft.fft(noise))
        freqs = np.fft.fftshift(np.fft.fftfreq(n, 1.0 / fs))
        fft_noise[np.abs(freqs) > (target_bw / 2.0)] = 0.0
        filtered = np.fft.ifft(np.fft.ifftshift(fft_noise))

        bw_3db, obw_99 = ParameterExtractor.estimate_bandwidth_3db(filtered, fs=fs)
        # Measured bandwidth within +/- 5% of target
        rel_error = abs(obw_99 - target_bw) / target_bw
        assert rel_error <= 0.05

    def test_tc_par_004_center_frequency_estimation(self):
        """TC-PAR-004: Center frequency estimation."""
        fs = 1.0e6
        true_fc = 75000.0 # 75 kHz offset from DC
        duration = 0.02
        t = np.arange(0, duration, 1.0 / fs)
        # Narrowband carrier modulated tone
        carrier = np.exp(1j * 2 * np.pi * true_fc * t).astype(np.complex64)
        noise = (np.random.randn(len(t)) + 1j * np.random.randn(len(t))) * 0.05
        signal_in = carrier + noise

        est_fc = ParameterExtractor.estimate_center_frequency(signal_in, fs=fs)
        rel_error = abs(est_fc - true_fc) / true_fc
        assert rel_error <= 0.02 # Within +/- 2%

    def test_tc_par_005_snr_noise_estimation(self):
        """TC-PAR-005: SNR & noise power estimation."""
        target_snr_db = 18.0
        n = 16384
        symbols = np.random.choice([1+1j, 1-1j, -1+1j, -1-1j], size=n) / np.sqrt(2.0)
        noise_power = 1.0 / (10 ** (target_snr_db / 10.0))
        noise = (np.random.randn(n) + 1j * np.random.randn(n)) * np.sqrt(noise_power / 2.0)
        noisy = (symbols + noise).astype(np.complex64)

        from ntro_sigint.core.preprocessor import SignalPreprocessor
        est_snr = SignalPreprocessor.estimate_snr_cumulants(noisy)
        assert abs(est_snr - target_snr_db) <= 2.0 # Within +/- 2 dB

    def test_tc_par_006_papr_measurement(self):
        """TC-PAR-006: Power measurement (PAPR)."""
        # Constant modulus signal has theoretical PAPR of 0 dB
        n = 4000
        const_mod = np.exp(1j * np.random.uniform(0, 2*np.pi, n)).astype(np.complex64)
        papr_cm, cf_cm = ParameterExtractor.estimate_papr_and_crest_factor(const_mod)
        assert abs(papr_cm - 0.0) < 0.1 # 0 dB for PSK
        assert abs(cf_cm - 1.0) < 0.05 # Crest factor = 1.0

        # Multi-carrier or pulse with known peak: e.g. single peak 10x higher
        peaked = const_mod.copy()
        peaked[0] = 10.0 # Peak power = 100, avg ~ 1.025
        papr_peaked, _ = ParameterExtractor.estimate_papr_and_crest_factor(peaked)
        assert papr_peaked > 15.0 # PAPR increased by > 15 dB

    def test_tc_par_007_frequency_offset_detection(self):
        """TC-PAR-007: Frequency offset detection."""
        fs = 1.0e6
        true_offset = 10000.0 # 10 kHz
        n = 8192
        t = np.arange(n) / fs
        # QPSK symbols with 10 kHz frequency offset
        qpsk_syms = np.random.choice([1, 1j, -1, -1j], size=n)
        cfo_signal = qpsk_syms * np.exp(1j * 2 * np.pi * true_offset * t)

        est_cfo = ParameterExtractor.estimate_carrier_offset(cfo_signal, fs=fs, modulation_order=4)
        # Measured as 10 +/- 2 kHz
        assert abs(abs(est_cfo) - true_offset) <= 2000.0

    def test_tc_par_008_envelope_analysis(self):
        """TC-PAR-008: Time-domain envelope analysis."""
        n = 2000
        # Bursty signal: on for 500 samples, off for 1500 samples (duty cycle ~ 25%)
        burst = np.zeros(n, dtype=np.complex64)
        burst[:500] = np.exp(1j * np.random.uniform(0, 2*np.pi, 500))

        p_env, m_env, v_env, duty = ParameterExtractor.analyze_envelope(burst)
        assert abs(p_env - 1.0) < 0.05
        assert abs(duty - 0.25) < 0.05 # Duty cycle 25% +/- 5%

    def test_tc_par_009_spectral_flatness(self):
        """TC-PAR-009: Spectral flatness (Wiener entropy)."""
        n = 4096
        # Pure tone: highly non-flat (low entropy < 0.1)
        t = np.linspace(0, 1, n)
        tone = np.exp(1j * 2 * np.pi * 50 * t).astype(np.complex64)
        flatness_tone = ParameterExtractor.compute_spectral_flatness(tone)
        assert flatness_tone < 0.10

        # White Gaussian noise: flat spectrum (high entropy > 0.70)
        noise = (np.random.randn(n) + 1j * np.random.randn(n)).astype(np.complex64)
        flatness_noise = ParameterExtractor.compute_spectral_flatness(noise)
        assert flatness_noise > 0.70

    def test_tc_par_010_crest_factor_measurement(self):
        """TC-PAR-010: Crest factor measurement."""
        n = 5000
        # QPSK constant modulus
        qpsk = np.random.choice([1+1j, 1-1j, -1+1j, -1-1j], size=n) / np.sqrt(2.0)
        _, cf_qpsk = ParameterExtractor.estimate_papr_and_crest_factor(qpsk)
        assert abs(cf_qpsk - 1.0) < 0.05 # CF ~ 1.0 for unshaped QPSK

        # Extract all integration test
        all_params = ParameterExtractor.extract_all(qpsk, fs=1.0e6)
        assert isinstance(all_params, SignalParameters)
        assert all_params.estimated_fs == 1.0e6
        assert all_params.crest_factor > 0.0
