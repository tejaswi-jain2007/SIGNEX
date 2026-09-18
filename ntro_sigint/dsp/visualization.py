"""
Signal Visualization Engine for Spectral, Temporal, and Constellation Analysis.
Covers TC-VIS-001 through TC-VIS-010.
"""

from typing import Tuple, Optional, Dict, Any
import numpy as np
import scipy.signal
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os


class SignalVisualizer:
    """
    High-performance visualization engine for RF signal intelligence.
    Produces waterfall spectrograms, PSD plots, constellation diagrams,
    and phase trajectory tracks.
    """

    @staticmethod
    def compute_spectrogram(
        signal_iq: np.ndarray,
        fs: float = 1.0e6,
        nfft: int = 1024,
        hop_length: int = 256,
        window: str = "hann",
        dynamic_range_db: float = 80.0
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Computes calibrated 2D waterfall STFT power matrix in dBFS.
        Returns:
            times: 1D array of time coordinates (seconds)
            freqs: 1D array of frequency coordinates (Hz, centered at 0)
            spectrogram_db: 2D array of power values in dB (shape: [len(freqs), len(times)])
        """
        if len(signal_iq) < nfft:
            # Pad signal if shorter than nfft
            signal_iq = np.pad(signal_iq, (0, nfft - len(signal_iq)))

        noverlap = nfft - hop_length
        f, t, Zxx = scipy.signal.stft(
            signal_iq,
            fs=fs,
            window=window,
            nperseg=nfft,
            noverlap=noverlap,
            return_onesided=False,
            boundary=None
        )

        # Shift zero-frequency component to center of spectrum
        f_shifted = np.fft.fftshift(f)
        Zxx_shifted = np.fft.fftshift(Zxx, axes=0)

        # Power spectrum in dB
        power = np.abs(Zxx_shifted) ** 2 + 1e-15
        power_db = 10.0 * np.log10(power)

        # Normalize relative to maximum peak and clamp to dynamic range
        max_db = np.max(power_db)
        spectrogram_db = np.clip(power_db - max_db, -dynamic_range_db, 0.0)

        return t, f_shifted, spectrogram_db

    @staticmethod
    def compute_fft_spectrum(
        signal_iq: np.ndarray,
        fs: float = 1.0e6,
        nfft: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes frequency axis and magnitude spectrum in dB.
        Identifies sharp spectral peaks with sub-bin precision.
        """
        if nfft is None:
            nfft = max(1024, 1 << int(np.ceil(np.log2(len(signal_iq)))))

        window = np.hanning(len(signal_iq))
        sig_win = signal_iq * window

        fft_raw = np.fft.fftshift(np.fft.fft(sig_win, n=nfft))
        freqs = np.fft.fftshift(np.fft.fftfreq(nfft, d=1.0/fs))

        mag = np.abs(fft_raw) / len(signal_iq)
        mag_db = 20.0 * np.log10(np.maximum(mag, 1e-12))
        return freqs, mag_db

    @staticmethod
    def compute_welch_psd(
        signal_iq: np.ndarray,
        fs: float = 1.0e6,
        nperseg: int = 1024
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes Power Spectral Density (PSD) in dB/Hz using Welch's smoothed periodogram.
        """
        nperseg = min(len(signal_iq), nperseg)
        f, Pxx = scipy.signal.welch(
            signal_iq,
            fs=fs,
            window="hann",
            nperseg=nperseg,
            return_onesided=False,
            scaling="density"
        )
        f_shifted = np.fft.fftshift(f)
        Pxx_shifted = np.fft.fftshift(Pxx)

        psd_db = 10.0 * np.log10(np.maximum(Pxx_shifted, 1e-15))
        return f_shifted, psd_db

    @staticmethod
    def compute_phase_trajectory(
        signal_iq: np.ndarray,
        fs: float = 1.0e6
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Computes time vector, unwrapped phase (rad), and instantaneous frequency (Hz).
        """
        t = np.arange(len(signal_iq)) / fs
        phase = np.unwrap(np.angle(signal_iq))
        # Instantaneous frequency: (1 / 2pi) * d(theta)/dt
        inst_freq = np.gradient(phase, 1.0 / fs) / (2.0 * np.pi)
        return t, phase, inst_freq

    @staticmethod
    def slice_viewport(
        spectrogram_db: np.ndarray,
        freqs: np.ndarray,
        times: np.ndarray,
        f_min: Optional[float] = None,
        f_max: Optional[float] = None,
        t_min: Optional[float] = None,
        t_max: Optional[float] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Extracts sub-viewport slice for zoom & pan operations (TC-VIS-009).
        """
        f_mask = np.ones(len(freqs), dtype=bool)
        if f_min is not None:
            f_mask &= (freqs >= f_min)
        if f_max is not None:
            f_mask &= (freqs <= f_max)

        t_mask = np.ones(len(times), dtype=bool)
        if t_min is not None:
            t_mask &= (times >= t_min)
        if t_max is not None:
            t_mask &= (times <= t_max)

        sliced_spec = spectrogram_db[np.ix_(f_mask, t_mask)]
        return times[t_mask], freqs[f_mask], sliced_spec

    @classmethod
    def plot_waterfall(
        cls,
        spectrogram_db: np.ndarray,
        freqs: np.ndarray,
        times: np.ndarray,
        title: str = "RF Waterfall Spectrogram",
        colormap: str = "viridis",
        output_path: Optional[str] = None
    ) -> plt.Figure:
        """Renders 2D waterfall spectrogram with colorbar and frequency axis."""
        fig, ax = plt.subplots(figsize=(10, 6))
        extent = [times[0], times[-1], freqs[0] / 1e3, freqs[-1] / 1e3]

        im = ax.imshow(
            spectrogram_db,
            aspect="auto",
            origin="lower",
            extent=extent,
            cmap=colormap,
            interpolation="nearest"
        )
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label("Power Relative to Peak (dBFS)", fontsize=10)

        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_xlabel("Time (s)", fontsize=10)
        ax.set_ylabel("Frequency (kHz)", fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.3)

        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            fig.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close(fig)

        return fig

    @classmethod
    def plot_constellation(
        cls,
        symbols: np.ndarray,
        modulation_name: str = "Constellation",
        title: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> plt.Figure:
        """Renders scatter plot of I/Q complex symbols."""
        fig, ax = plt.subplots(figsize=(6, 6))
        sub = symbols[:3000]

        ax.scatter(sub.real, sub.imag, s=10, alpha=0.6, c="#2B6CB0", edgecolors="none")
        ax.axhline(0, color="#A0AEC0", linestyle="--", lw=0.8)
        ax.axvline(0, color="#A0AEC0", linestyle="--", lw=0.8)

        ax.set_title(title or f"I/Q Constellation ({modulation_name})", fontsize=11, fontweight="bold")
        ax.set_xlabel("In-Phase (I)", fontsize=10)
        ax.set_ylabel("Quadrature (Q)", fontsize=10)
        ax.grid(True, linestyle=":", alpha=0.5)

        # Equal aspect ratio for geometric fidelity
        ax.set_aspect("equal", adjustable="box")

        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            fig.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close(fig)

        return fig
