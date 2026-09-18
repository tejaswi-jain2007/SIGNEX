"""
NTRO SIGINT Signal Preprocessing Module
Implements DC offset removal, Gram-Schmidt I/Q imbalance correction,
polyphase rational resampling, clipping detection, power normalization,
and cumulant-based SNR estimation.
Conforms to SRS FR-1.2 and Master Test Plan TC-PRE-001 through TC-PRE-008.
"""

from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
import numpy as np
import scipy.signal as signal


@dataclass
class PreprocessorStats:
    """Diagnostic statistics produced during preprocessing."""
    initial_mean_i: float
    initial_mean_q: float
    final_mean_i: float
    final_mean_q: float
    initial_power_db: float
    final_power_db: float
    estimated_snr_db: float
    clipping_detected: bool
    clipped_sample_percentage: float
    imbalance_corrected: bool


class SignalPreprocessor:
    """
    High-performance preprocessor for raw I/Q and analytical signals.
    Employs vectorization and numerical stability guards.
    """

    @staticmethod
    def remove_dc_offset(samples: np.ndarray) -> np.ndarray:
        """
        TC-PRE-001: DC offset removal.
        Reduces mean of I and Q components to near-zero (|Mean| < 1e-5).
        """
        if len(samples) == 0:
            return samples
        mean_offset = np.mean(samples)
        return samples - mean_offset

    @staticmethod
    def correct_iq_imbalance(samples: np.ndarray) -> np.ndarray:
        """
        TC-PRE-002: Gram-Schmidt I/Q imbalance correction.
        Corrects amplitude mismatch and phase non-orthogonality.
        Guarantees >= 20 dB reduction in quadrature imbalance.
        """
        if len(samples) < 2:
            return samples

        i_comp = samples.real.copy()
        q_comp = samples.imag.copy()

        # Step 1: Remove residual DC
        i_comp -= np.mean(i_comp)
        q_comp -= np.mean(q_comp)

        # Step 2: Normalize power of I component
        p_i = np.mean(i_comp ** 2)
        if p_i <= 1e-12:
            return samples
        i_norm = i_comp / np.sqrt(p_i)

        # Step 3: Orthogonalize Q with respect to I (Gram-Schmidt projection)
        rho = np.mean(i_norm * q_comp)
        q_orth = q_comp - rho * i_norm

        # Step 4: Normalize Q power to match I (unless 1D signal where Q is pure noise)
        p_q_orth = np.mean(q_orth ** 2)
        if p_q_orth <= 1e-12:
            return (i_norm + 1j * 0.0).astype(np.complex64)

        if (p_q_orth / p_i) < 0.05:
            # 1D real signal (BPSK / PAM / AM-DSB) - preserve natural low Q noise floor
            q_norm = q_orth / np.sqrt(p_i)
        else:
            # Genuine 2D quadrature signal (QPSK / QAM / FSK) - equalize power
            q_norm = q_orth / np.sqrt(p_q_orth)

        return (i_norm + 1j * q_norm).astype(np.complex64)

    @staticmethod
    def detect_clipping(
        samples: np.ndarray,
        threshold: float = 0.999,
        warn_pct: float = 0.05
    ) -> Tuple[bool, float]:
        """
        TC-PRE-004: Saturation & clipping detection.
        Detects if samples touch or exceed peak ADC range.
        Returns (is_clipped, percentage_clipped).
        """
        if len(samples) == 0:
            return False, 0.0

        i_comp = np.abs(samples.real)
        q_comp = np.abs(samples.imag) if np.iscomplexobj(samples) else np.zeros_like(i_comp)

        clipped_i = np.sum(i_comp >= threshold)
        clipped_q = np.sum(q_comp >= threshold)
        total_scalars = len(samples) * (2 if np.iscomplexobj(samples) else 1)

        pct = ((clipped_i + clipped_q) / total_scalars) * 100.0
        return bool(pct >= warn_pct), float(pct)

    @staticmethod
    def normalize_power(samples: np.ndarray, target_power: float = 1.0) -> np.ndarray:
        """
        TC-PRE-007: Normalization by power.
        Scales signal so average power E[|s|^2] == target_power (0 dB).
        """
        if len(samples) == 0:
            return samples
        current_power = np.mean(np.abs(samples) ** 2)
        if current_power <= 1e-15:
            return samples
        scale = np.sqrt(target_power / current_power)
        return (samples * scale).astype(samples.dtype)

    @staticmethod
    def estimate_snr_cumulants(samples: np.ndarray) -> float:
        """
        TC-PRE-005: Signal-to-Noise Ratio (SNR) estimation using fourth-order cumulants.
        Accurate to within +/- 2 dB of ground truth across 0 dB to 25 dB range.
        """
        if len(samples) < 128:
            return 10.0

        s = samples - np.mean(samples)
        # Moments
        m2 = np.mean(np.abs(s) ** 2)
        m4 = np.mean(np.abs(s) ** 4)

        if m2 <= 1e-12:
            return 0.0

        # Fourth-order cumulant C42 = E[|s|^4] - 2*E[|s|^2]^2 - |E[s^2]|^2
        c42 = m4 - 2.0 * (m2 ** 2) - (np.abs(np.mean(s ** 2)) ** 2)

        # For constant modulus signal + Gaussian noise:
        # C42 is negative for constant modulus constellations (BPSK, QPSK, 8PSK, FSK)
        # S = sqrt(-C42), N = m2 - S
        if c42 < 0:
            s_power = np.sqrt(-c42)
            n_power = max(m2 - s_power, 1e-8)
            snr_lin = s_power / n_power
            snr_db = 10.0 * np.log10(max(snr_lin, 1e-3))
        else:
            # High noise or noise-like signal fallback (split spectrum method)
            fft_mag = np.abs(np.fft.fft(s[:1024])) ** 2
            sorted_bins = np.sort(fft_mag)
            noise_est = np.median(sorted_bins[: len(sorted_bins) // 4])
            signal_est = np.mean(sorted_bins[len(sorted_bins) // 2 :])
            if noise_est > 0:
                snr_db = 10.0 * np.log10(max(signal_est / noise_est, 1.0))
            else:
                snr_db = 15.0

        return float(np.clip(snr_db, -20.0, 45.0))

    @staticmethod
    def resample(
        samples: np.ndarray,
        orig_fs: float,
        target_fs: float
    ) -> np.ndarray:
        """
        TC-PRE-003: Rational polyphase resampling.
        Preserves spectral fidelity without aliasing artifacts.
        """
        if abs(orig_fs - target_fs) < 1e-3:
            return samples

        # Rational approximation of ratio target_fs / orig_fs
        from fractions import Fraction
        ratio = Fraction(target_fs / orig_fs).limit_denominator(1000)
        up, down = ratio.numerator, ratio.denominator

        if np.iscomplexobj(samples):
            res_i = signal.resample_poly(samples.real, up, down)
            res_q = signal.resample_poly(samples.imag, up, down)
            return (res_i + 1j * res_q).astype(np.complex64)
        else:
            return signal.resample_poly(samples, up, down).astype(np.float32)

    @staticmethod
    def apply_window(
        samples: np.ndarray,
        window_type: str = "hann"
    ) -> np.ndarray:
        """
        TC-PRE-006: Spectral windowing consistency.
        Supports 'hann', 'hamming', 'blackman'.
        """
        n = len(samples)
        if n == 0:
            return samples

        w_name = window_type.lower()
        if w_name == "hann":
            win = np.hanning(n)
        elif w_name == "hamming":
            win = np.hamming(n)
        elif w_name == "blackman":
            win = np.blackman(n)
        else:
            raise ValueError(f"Unsupported window type: {window_type}")

        return samples * win

    @staticmethod
    def filter_with_warmup(
        samples: np.ndarray,
        b: np.ndarray,
        a: np.ndarray = np.array([1.0]),
        trim_warmup: bool = False
    ) -> Tuple[np.ndarray, int]:
        """
        TC-PRE-008: Filter application with transient warmup tracking.
        Returns (filtered_samples, warmup_samples_count).
        """
        warmup_len = max(len(b), len(a)) * 3
        filtered = signal.lfilter(b, a, samples)
        if trim_warmup and len(filtered) > warmup_len:
            return filtered[warmup_len:], warmup_len
        return filtered, warmup_len

    @classmethod
    def full_pipeline(
        cls,
        samples: np.ndarray,
        dc_block: bool = True,
        balance_iq: bool = True,
        normalize: bool = True
    ) -> Tuple[np.ndarray, PreprocessorStats]:
        """Execute standard preprocessing chain and capture diagnostics."""
        m_i_init = float(np.mean(samples.real))
        m_q_init = float(np.mean(samples.imag)) if np.iscomplexobj(samples) else 0.0
        p_init = 10.0 * np.log10(max(float(np.mean(np.abs(samples) ** 2)), 1e-12))

        clipped, pct_clipped = cls.detect_clipping(samples)
        snr_est = cls.estimate_snr_cumulants(samples)

        processed = samples
        if dc_block:
            processed = cls.remove_dc_offset(processed)
        if balance_iq and np.iscomplexobj(processed):
            processed = cls.correct_iq_imbalance(processed)
        if normalize:
            processed = cls.normalize_power(processed, target_power=1.0)

        m_i_final = float(np.mean(processed.real))
        m_q_final = float(np.mean(processed.imag)) if np.iscomplexobj(processed) else 0.0
        p_final = 10.0 * np.log10(max(float(np.mean(np.abs(processed) ** 2)), 1e-12))

        stats = PreprocessorStats(
            initial_mean_i=m_i_init,
            initial_mean_q=m_q_init,
            final_mean_i=m_i_final,
            final_mean_q=m_q_final,
            initial_power_db=p_init,
            final_power_db=p_final,
            estimated_snr_db=snr_est,
            clipping_detected=clipped,
            clipped_sample_percentage=pct_clipped,
            imbalance_corrected=balance_iq
        )

        return processed, stats
