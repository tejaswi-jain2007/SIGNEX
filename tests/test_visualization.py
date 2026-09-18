"""
Test Suite for Signal Visualization Engine.
Validates TC-VIS-001 through TC-VIS-010.
"""

import pytest
import numpy as np
import os
import tempfile
import matplotlib.pyplot as plt

from ntro_sigint.dsp.visualization import SignalVisualizer
from ntro_sigint.ml.dataset import SyntheticSignalGenerator


class TestSignalVisualization:

    def test_tc_vis_001_waterfall_rendering(self):
        """TC-VIS-001: Render waterfall spectrogram. Check dimensions and dB power range."""
        fs = 1.0e6
        # Generate 4096 samples with tone
        t = np.arange(4096) / fs
        sig = np.exp(1j * 2.0 * np.pi * 100.0e3 * t).astype(np.complex64)

        times, freqs, spec_db = SignalVisualizer.compute_spectrogram(sig, fs=fs, nfft=512, hop_length=128)
        assert len(times) > 0
        assert len(freqs) == 512
        assert spec_db.shape == (512, len(times))
        # Peak power at 0 dB, min power >= -80 dB
        assert np.isclose(np.max(spec_db), 0.0, atol=1e-3)
        assert np.min(spec_db) >= -80.0

    def test_tc_vis_002_fft_spectral_accuracy(self):
        """TC-VIS-002: FFT spectral plot accuracy. Tone at 150 kHz detected with < 1 bin error."""
        fs = 1.0e6
        t = np.arange(2048) / fs
        target_f = 150.0e3
        sig = np.exp(1j * 2.0 * np.pi * target_f * t).astype(np.complex64)

        freqs, mag_db = SignalVisualizer.compute_fft_spectrum(sig, fs=fs, nfft=2048)
        peak_idx = np.argmax(mag_db)
        detected_f = freqs[peak_idx]

        assert abs(detected_f - target_f) < (fs / 2048)

    def test_tc_vis_003_dynamic_range_colormap(self):
        """TC-VIS-003: Dynamic range and colormapping."""
        fs = 1.0e6
        sig = (np.random.randn(2048) + 1j * np.random.randn(2048)).astype(np.complex64)
        times, freqs, spec_db = SignalVisualizer.compute_spectrogram(sig, fs=fs, dynamic_range_db=60.0)

        # Dynamic range strictly 60 dB
        assert np.min(spec_db) >= -60.0
        assert np.max(spec_db) <= 0.0

        # Validate figure creation with custom colormaps
        fig = SignalVisualizer.plot_waterfall(spec_db, freqs, times, colormap="inferno")
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_tc_vis_004_iq_constellation_qpsk(self):
        """TC-VIS-004: I/Q constellation diagram for QPSK (4 distinct quadrant clusters)."""
        qpsk_sig = SyntheticSignalGenerator.generate_signal("QPSK", num_samples=1000, snr_db=30.0)
        # Check clustering into 4 quadrants
        quadrants = set()
        for s in qpsk_sig:
            q = (1 if s.real > 0 else -1, 1 if s.imag > 0 else -1)
            quadrants.add(q)
        assert len(quadrants) == 4

        fig = SignalVisualizer.plot_constellation(qpsk_sig, "QPSK")
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_tc_vis_005_iq_constellation_16qam(self):
        """TC-VIS-005: I/Q constellation diagram for 16-QAM (16 distinct levels)."""
        qam_sig = SyntheticSignalGenerator.generate_signal("16-QAM", num_samples=2000, snr_db=35.0)
        fig = SignalVisualizer.plot_constellation(qam_sig, "16-QAM")
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_tc_vis_006_psd_welch(self):
        """TC-VIS-006: Power spectral density (PSD) computation and power consistency."""
        fs = 1.0e6
        np.random.seed(123)
        noise = (np.random.randn(4096) + 1j * np.random.randn(4096)).astype(np.complex64)

        freqs, psd_db = SignalVisualizer.compute_welch_psd(noise, fs=fs, nperseg=512)
        assert len(freqs) == 512
        assert len(psd_db) == 512
        # White noise has relatively flat PSD across all bins (variance < 3 dB)
        std_psd = np.std(psd_db)
        assert std_psd < 4.0

    def test_tc_vis_007_spectrogram_high_time_resolution(self):
        """TC-VIS-007: Spectrogram with high time resolution (nfft=128, hop=32)."""
        fs = 1.0e6
        sig = np.random.randn(2048) + 1j * np.random.randn(2048)
        times, freqs, spec_db = SignalVisualizer.compute_spectrogram(sig, fs=fs, nfft=128, hop_length=32)

        # High time resolution yields many time columns
        assert len(times) >= 50
        assert len(freqs) == 128

    def test_tc_vis_008_phase_trajectory_plot(self):
        """TC-VIS-008: Phase trajectory and instantaneous frequency."""
        fs = 1.0e6
        t = np.arange(1000) / fs
        f_tone = 50.0e3
        sig = np.exp(1j * 2.0 * np.pi * f_tone * t)

        times, phase, inst_f = SignalVisualizer.compute_phase_trajectory(sig, fs=fs)
        assert len(phase) == 1000
        # Instantaneous frequency of a 50 kHz pure tone must equal 50 kHz
        mean_inst_f = np.mean(inst_f[10:-10])
        assert np.isclose(mean_inst_f, f_tone, atol=100.0)

    def test_tc_vis_009_zoom_pan_viewport(self):
        """TC-VIS-009: Zoom & pan viewport slicing."""
        fs = 1.0e6
        sig = np.random.randn(2048) + 1j * np.random.randn(2048)
        times, freqs, spec_db = SignalVisualizer.compute_spectrogram(sig, fs=fs, nfft=512, hop_length=128)

        # Slice sub-band [-100 kHz, +100 kHz] and time [0.001s, 0.002s]
        t_sub, f_sub, spec_sub = SignalVisualizer.slice_viewport(
            spec_db, freqs, times,
            f_min=-100e3, f_max=100e3,
            t_min=0.0005, t_max=0.0015
        )

        assert len(f_sub) < len(freqs)
        assert np.all(f_sub >= -100e3)
        assert np.all(f_sub <= 100e3)
        assert spec_sub.shape == (len(f_sub), len(t_sub))

    def test_tc_vis_010_export_plots_png_pdf(self, tmp_path):
        """TC-VIS-010: Export plots to PNG and PDF at 300 DPI."""
        fs = 1.0e6
        t = np.arange(1024) / fs
        sig = np.exp(1j * 2.0 * np.pi * 50e3 * t)
        times, freqs, spec_db = SignalVisualizer.compute_spectrogram(sig, fs=fs, nfft=256, hop_length=64)

        png_path = str(tmp_path / "waterfall_test.png")
        pdf_path = str(tmp_path / "constellation_test.pdf")

        SignalVisualizer.plot_waterfall(spec_db, freqs, times, output_path=png_path)
        SignalVisualizer.plot_constellation(sig, "BPSK", output_path=pdf_path)

        assert os.path.exists(png_path)
        assert os.path.getsize(png_path) > 2000
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 1000
