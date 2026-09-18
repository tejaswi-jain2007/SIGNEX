"""
Unit Test Suite for Module 2: Signal Preprocessing & Validation
Corresponds to Master Test Plan TC-PRE-001 through TC-PRE-008.
"""

import pytest
import numpy as np

from ntro_sigint.core.preprocessor import SignalPreprocessor, PreprocessorStats


class TestSignalPreprocessor:

    def test_tc_pre_001_dc_offset_removal(self):
        """TC-PRE-001: DC offset removal."""
        np.random.seed(42)
        n = 10000
        # Signal with +0.15V DC bias on I and -0.10V on Q
        i_biased = np.random.randn(n) * 0.5 + 0.15
        q_biased = np.random.randn(n) * 0.5 - 0.10
        signal_in = (i_biased + 1j * q_biased).astype(np.complex64)

        cleaned = SignalPreprocessor.remove_dc_offset(signal_in)
        assert np.abs(np.mean(cleaned.real)) < 1e-5
        assert np.abs(np.mean(cleaned.imag)) < 1e-5

    def test_tc_pre_002_iq_imbalance_correction(self):
        """TC-PRE-002: I/Q imbalance correction."""
        np.random.seed(42)
        n = 20000
        # 10% amplitude imbalance (A_q = 1.10) and 5 degrees phase error
        theta = np.deg2rad(5.0)
        phi = np.random.uniform(0, 2 * np.pi, n)
        i_ideal = np.cos(phi)
        q_ideal = np.sin(phi)

        # Apply imbalance model: Q_unbal = 1.10 * (sin(phi)*cos(theta) - cos(phi)*sin(theta))
        i_unbal = i_ideal
        q_unbal = 1.10 * (q_ideal * np.cos(theta) - i_ideal * np.sin(theta))
        unbalanced_signal = (i_unbal + 1j * q_unbal).astype(np.complex64)

        # Initial power ratio and cross-correlation
        p_i_before = np.mean(unbalanced_signal.real ** 2)
        p_q_before = np.mean(unbalanced_signal.imag ** 2)
        amp_imb_before_db = 10 * np.log10(p_q_before / p_i_before)
        cross_corr_before = np.abs(np.mean(unbalanced_signal.real * unbalanced_signal.imag))

        corrected = SignalPreprocessor.correct_iq_imbalance(unbalanced_signal)

        p_i_after = np.mean(corrected.real ** 2)
        p_q_after = np.mean(corrected.imag ** 2)
        amp_imb_after_db = 10 * np.log10(p_q_after / p_i_after)
        cross_corr_after = np.abs(np.mean(corrected.real * corrected.imag))

        # Power equalized to within 0.05 dB
        assert np.abs(amp_imb_after_db) < 0.05
        # Orthogonality restored: cross-correlation reduced significantly
        assert cross_corr_after < cross_corr_before * 0.1

    def test_tc_pre_003_sample_rate_normalization(self):
        """TC-PRE-003: Sample rate normalization (resampling)."""
        orig_fs = 44100.0
        target_fs = 48000.0
        duration = 0.1
        t = np.arange(0, duration, 1.0 / orig_fs)
        tone_freq = 2000.0
        tone = np.exp(1j * 2 * np.pi * tone_freq * t).astype(np.complex64)

        resampled = SignalPreprocessor.resample(tone, orig_fs, target_fs)

        expected_n = int(round(len(tone) * target_fs / orig_fs))
        assert abs(len(resampled) - expected_n) <= 2

        # Verify spectral peak remains at 2000 Hz in resampled domain
        fft_res = np.abs(np.fft.fft(resampled))
        freqs = np.fft.fftfreq(len(resampled), 1.0 / target_fs)
        peak_freq = np.abs(freqs[np.argmax(fft_res)])
        assert np.abs(peak_freq - tone_freq) < 15.0 # within 15 Hz

    def test_tc_pre_004_clipping_detection(self):
        """TC-PRE-004: Saturation / clipping detection."""
        n = 1000
        # Normal unclipped signal
        clean_signal = (np.random.randn(n) * 0.2 + 1j * np.random.randn(n) * 0.2).astype(np.complex64)
        is_clip_clean, pct_clean = SignalPreprocessor.detect_clipping(clean_signal)
        assert not is_clip_clean
        assert pct_clean == 0.0

        # Clipped signal: 5% of samples saturated at 1.0
        clipped_signal = clean_signal.copy()
        clipped_signal.real[:50] = 1.0
        is_clip_sat, pct_sat = SignalPreprocessor.detect_clipping(clipped_signal, threshold=0.99)
        assert is_clip_sat
        assert pct_sat > 2.0

    def test_tc_pre_005_snr_estimation(self):
        """TC-PRE-005: SNR estimation via cumulants."""
        np.random.seed(123)
        n = 16384
        # Generate constant-modulus PSK signal at target SNR = 15 dB
        target_snr_db = 15.0
        symbols = np.random.choice([1+1j, 1-1j, -1+1j, -1-1j], size=n) / np.sqrt(2.0)
        signal_power = 1.0
        noise_power = signal_power / (10 ** (target_snr_db / 10.0))
        noise = (np.random.randn(n) + 1j * np.random.randn(n)) * np.sqrt(noise_power / 2.0)
        noisy_signal = (symbols + noise).astype(np.complex64)

        est_snr = SignalPreprocessor.estimate_snr_cumulants(noisy_signal)
        # Criteria: |SNR_est - SNR_true| <= 2 dB
        assert np.abs(est_snr - target_snr_db) <= 2.0

    def test_tc_pre_006_windowing_consistency(self):
        """TC-PRE-006: Windowing consistency."""
        n = 1024
        t = np.linspace(0, 1, n)
        tone = np.sin(2 * np.pi * 10 * t)

        for win_type in ["hann", "hamming", "blackman"]:
            windowed = SignalPreprocessor.apply_window(tone, window_type=win_type)
            assert len(windowed) == n
            assert np.all(np.isfinite(windowed))
            # Windowing attenuates boundaries
            assert np.abs(windowed[0]) < np.max(np.abs(windowed)) * 0.1
            assert np.abs(windowed[-1]) < np.max(np.abs(windowed)) * 0.1

    def test_tc_pre_007_normalization_by_power(self):
        """TC-PRE-007: Normalization by power."""
        np.random.seed(99)
        # Arbitrary scaled signal
        raw_signal = (np.random.randn(5000) * 17.5 + 1j * np.random.randn(5000) * 17.5).astype(np.complex64)
        normalized = SignalPreprocessor.normalize_power(raw_signal, target_power=1.0)

        p_after = np.mean(np.abs(normalized) ** 2)
        power_db = 10.0 * np.log10(p_after)
        # Criteria: 10*log10(E[s^2]) ~= 0 dB
        assert np.abs(power_db) < 1e-4

    def test_tc_pre_008_filter_artifact_inspection(self):
        """TC-PRE-008: Filter artifact inspection / warm-up handling."""
        # Lowpass filter FIR
        b = np.array([0.1, 0.2, 0.4, 0.2, 0.1])
        samples = np.ones(100, dtype=np.float32)

        # Full filtering with warmup return
        filtered, warmup_len = SignalPreprocessor.filter_with_warmup(samples, b, trim_warmup=False)
        assert len(filtered) == 100
        assert warmup_len == 15

        # Trimmed filtering
        trimmed, _ = SignalPreprocessor.filter_with_warmup(samples, b, trim_warmup=True)
        assert len(trimmed) == 100 - warmup_len
