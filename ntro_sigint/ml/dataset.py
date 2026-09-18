"""
NTRO SIGINT Machine Learning Dataset Engine
Implements synthetic RF signal generator for target modulation classes:
BPSK, QPSK, 8-PSK, 16-QAM, 64-QAM, 2-FSK, 4-FSK, AM-DSB, WBFM.
Includes AWGN, carrier frequency offset (CFO), phase noise channel simulation,
and RadioML 2016/2018 compatible HDF5 data loaders.
Conforms to SIH_26147_DATASET_HANDBOOK_v3_UPDATED.md.
"""

import os
from typing import Dict, Any, Tuple, List, Optional
import numpy as np
import scipy.signal as signal
import h5py


MODULATION_CLASSES = [
    "BPSK", "QPSK", "8-PSK", "16-QAM", "64-QAM",
    "2-FSK", "4-FSK", "AM-DSB", "WBFM"
]

CLASS_TO_IDX = {name: idx for idx, name in enumerate(MODULATION_CLASSES)}
IDX_TO_CLASS = {idx: name for idx, name in enumerate(MODULATION_CLASSES)}


class SyntheticSignalGenerator:
    """
    Generates deterministic and stochastic RF test fixtures with
    realistic channel impairments: AWGN, Carrier Frequency Offset (CFO),
    and phase noise.
    """

    @staticmethod
    def generate_signal(
        mod_type: str,
        num_samples: int = 1024,
        snr_db: float = 20.0,
        fs: float = 1.0e6,
        sps: int = 8,
        cfo_hz: float = 0.0,
        phase_noise_std: float = 0.0,
        random_seed: Optional[int] = None
    ) -> np.ndarray:
        """
        Generate synthetic baseband I/Q signal for specified modulation.
        Returns complex64 ndarray of length num_samples.
        """
        if random_seed is not None:
            np.random.seed(random_seed)

        n_symbols = int(np.ceil(num_samples / sps)) + 10
        mod_upper = mod_type.upper().replace("_", "-")

        if mod_upper == "BPSK":
            bits = np.random.choice([-1.0, 1.0], size=n_symbols)
            symbols = bits.astype(np.complex64)
        elif mod_upper == "QPSK":
            bits_i = np.random.choice([-1.0, 1.0], size=n_symbols)
            bits_q = np.random.choice([-1.0, 1.0], size=n_symbols)
            symbols = (bits_i + 1j * bits_q) / np.sqrt(2.0)
        elif mod_upper in ("8-PSK", "8PSK"):
            phases = np.random.choice(np.arange(8)) * (2.0 * np.pi / 8.0)
            symbols = np.exp(1j * phases).astype(np.complex64)
        elif mod_upper in ("16-QAM", "16QAM"):
            grid = np.array([-3.0, -1.0, 1.0, 3.0])
            i_sym = np.random.choice(grid, size=n_symbols)
            q_sym = np.random.choice(grid, size=n_symbols)
            symbols = (i_sym + 1j * q_sym) / np.sqrt(10.0) # Average power = 1.0
        elif mod_upper in ("64-QAM", "64QAM"):
            grid = np.array([-7.0, -5.0, -3.0, -1.0, 1.0, 3.0, 5.0, 7.0])
            i_sym = np.random.choice(grid, size=n_symbols)
            q_sym = np.random.choice(grid, size=n_symbols)
            symbols = (i_sym + 1j * q_sym) / np.sqrt(42.0) # Average power = 1.0
        elif mod_upper in ("2-FSK", "2FSK", "FSK"):
            dev = (fs / sps) / 2.0
            bits = np.random.choice([-1.0, 1.0], size=n_symbols)
            # Repeat bits for duration of symbol
            t_sample = np.arange(n_symbols * sps) / fs
            freq_dev = np.repeat(bits * dev, sps)
            phase = 2.0 * np.pi * np.cumsum(freq_dev) / fs
            raw_signal = np.exp(1j * phase[:num_samples]).astype(np.complex64)
            return SyntheticSignalGenerator._apply_channel(
                raw_signal, snr_db, fs, cfo_hz, phase_noise_std
            )
        elif mod_upper in ("4-FSK", "4FSK"):
            dev = (fs / sps) / 4.0
            levels = np.random.choice([-3.0, -1.0, 1.0, 3.0], size=n_symbols)
            freq_dev = np.repeat(levels * dev, sps)
            phase = 2.0 * np.pi * np.cumsum(freq_dev) / fs
            raw_signal = np.exp(1j * phase[:num_samples]).astype(np.complex64)
            return SyntheticSignalGenerator._apply_channel(
                raw_signal, snr_db, fs, cfo_hz, phase_noise_std
            )
        elif mod_upper in ("AM-DSB", "AM"):
            # Analog AM modulation: (1 + m*audio(t)) * exp(j0)
            t = np.arange(num_samples) / fs
            audio = np.sin(2 * np.pi * 5000.0 * t) + 0.5 * np.cos(2 * np.pi * 12000.0 * t)
            audio = audio / np.max(np.abs(audio))
            m = 0.8
            raw_signal = ((1.0 + m * audio) + 0.0j).astype(np.complex64)
            return SyntheticSignalGenerator._apply_channel(
                raw_signal, snr_db, fs, cfo_hz, phase_noise_std
            )
        elif mod_upper in ("WBFM", "FM"):
            # Frequency modulation: exp(j * 2pi * kf * int(audio))
            t = np.arange(num_samples) / fs
            audio = np.sin(2 * np.pi * 1000.0 * t)
            freq_dev = 75000.0 * audio
            phase = 2.0 * np.pi * np.cumsum(freq_dev) / fs
            raw_signal = np.exp(1j * phase).astype(np.complex64)
            return SyntheticSignalGenerator._apply_channel(
                raw_signal, snr_db, fs, cfo_hz, phase_noise_std
            )
        else:
            raise ValueError(f"Unknown modulation class: {mod_type}")

        # Linear modulation pulse shaping (Root Raised Cosine)
        upsampled = np.zeros(n_symbols * sps, dtype=np.complex64)
        upsampled[0::sps] = symbols

        # RRC pulse filter
        t_filter = np.arange(-4 * sps, 4 * sps + 1) / fs
        beta = 0.35
        ts = sps / fs
        # RRC impulse response
        numerator = np.sin(np.pi * t_filter / ts * (1 - beta)) + 4 * beta * (t_filter / ts) * np.cos(np.pi * t_filter / ts * (1 + beta))
        denominator = np.pi * t_filter / ts * (1 - (4 * beta * t_filter / ts) ** 2) + 1e-12
        rrc = numerator / denominator
        # Center sample
        rrc[4 * sps] = 1.0 - beta + (4 * beta / np.pi)
        rrc /= np.sqrt(np.sum(rrc ** 2))

        tx = np.convolve(upsampled, rrc, mode='same')
        raw_signal = tx[:num_samples]

        return SyntheticSignalGenerator._apply_channel(
            raw_signal, snr_db, fs, cfo_hz, phase_noise_std
        )

    @staticmethod
    def _apply_channel(
        signal_in: np.ndarray,
        snr_db: float,
        fs: float,
        cfo_hz: float,
        phase_noise_std: float
    ) -> np.ndarray:
        """Apply CFO, phase noise, and AWGN noise."""
        n = len(signal_in)
        t = np.arange(n) / fs

        # 1. Carrier Frequency Offset (CFO)
        if abs(cfo_hz) > 1e-6:
            cfo_rot = np.exp(1j * 2.0 * np.pi * cfo_hz * t)
            signal_in = signal_in * cfo_rot

        # 2. Phase Noise (Wiener random walk)
        if phase_noise_std > 1e-6:
            p_noise = np.cumsum(np.random.randn(n) * phase_noise_std)
            signal_in = signal_in * np.exp(1j * p_noise)

        # 3. AWGN Noise
        # Normalize signal power to 1.0
        p_sig = np.mean(np.abs(signal_in) ** 2)
        if p_sig > 1e-12:
            signal_in = signal_in / np.sqrt(p_sig)

        snr_lin = 10.0 ** (snr_db / 10.0)
        noise_pwr = 1.0 / snr_lin
        noise = (np.random.randn(n) + 1j * np.random.randn(n)) * np.sqrt(noise_pwr / 2.0)

        noisy = signal_in + noise
        return noisy.astype(np.complex64)


def create_synthetic_dataset(
    num_samples_per_class: int = 50,
    snr_range: Tuple[float, float] = (0.0, 20.0),
    window_len: int = 1024,
    save_h5_path: Optional[str] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate balanced multi-class dataset for training and verification.
    Returns:
      X: ndarray shape [N, 2, window_len] (I/Q channels)
      Y: ndarray shape [N] (class integer indices)
    """
    x_list = []
    y_list = []

    for c_idx, mod_name in enumerate(MODULATION_CLASSES):
        for _ in range(num_samples_per_class):
            snr = np.random.uniform(snr_range[0], snr_range[1])
            sig = SyntheticSignalGenerator.generate_signal(
                mod_type=mod_name,
                num_samples=window_len,
                snr_db=snr,
                fs=1.0e6
            )
            # Power normalize
            pwr = np.sqrt(np.mean(np.abs(sig) ** 2)) + 1e-12
            sig_norm = sig / pwr

            iq_tensor = np.stack([sig_norm.real, sig_norm.imag], axis=0).astype(np.float32)
            x_list.append(iq_tensor)
            y_list.append(c_idx)

    x_arr = np.array(x_list, dtype=np.float32)
    y_arr = np.array(y_list, dtype=np.int64)

    if save_h5_path:
        os.makedirs(os.path.dirname(save_h5_path), exist_ok=True)
        with h5py.File(save_h5_path, 'w') as h5f:
            h5f.create_dataset('X', data=x_arr, compression='gzip')
            h5f.create_dataset('Y', data=y_arr)
            h5f.attrs['classes'] = [c.encode('utf-8') for c in MODULATION_CLASSES]

    return x_arr, y_arr
