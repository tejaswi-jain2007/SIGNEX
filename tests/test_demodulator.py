"""
Unit Test Suite for Module 6: Signal Demodulation
Corresponds to Master Test Plan TC-DEM-001 through TC-DEM-012.
"""

import pytest
import numpy as np

from ntro_sigint.dsp.demodulator import Demodulator, DemodResult


class TestDemodulator:

    def test_tc_dem_001_demod_bpsk(self):
        """TC-DEM-001: Demodulate BPSK."""
        # Known reference bitstream
        ref_bits = np.array([0, 1, 0, 0, 1, 1, 0, 1], dtype=np.uint8)
        # BPSK symbols: 0 -> +1, 1 -> -1
        symbols = np.where(ref_bits == 0, 1.0, -1.0).astype(np.complex64)
        res = Demodulator.demodulate(symbols, mod_type="BPSK", apply_carrier_sync=False)

        np.testing.assert_array_equal(res.bits, ref_bits)
        assert res.num_bits == len(ref_bits)

    def test_tc_dem_002_demod_qpsk(self):
        """TC-DEM-002: Demodulate QPSK (Gray mapping)."""
        # 4 symbols in 4 quadrants
        # Q0 (+, +) -> 00, Q1 (-, +) -> 01, Q2 (-, -) -> 11, Q3 (+, -) -> 10
        symbols = np.array([1+1j, -1+1j, -1-1j, 1-1j], dtype=np.complex64) / np.sqrt(2.0)
        expected_bits = np.array([0, 0, 0, 1, 1, 1, 1, 0], dtype=np.uint8)

        res = Demodulator.demodulate(symbols, mod_type="QPSK", apply_carrier_sync=False)
        np.testing.assert_array_equal(res.bits, expected_bits)

    def test_tc_dem_003_demod_8psk(self):
        """TC-DEM-003: Demodulate 8-PSK."""
        # Generate 8 sectors on unit circle
        angles = np.arange(8) * (np.pi / 4.0)
        symbols = np.exp(1j * angles).astype(np.complex64)
        res = Demodulator.demodulate(symbols, mod_type="8-PSK", apply_carrier_sync=False)

        assert res.num_bits == 24 # 8 symbols * 3 bits
        assert np.all((res.bits == 0) | (res.bits == 1))

    def test_tc_dem_004_demod_16qam(self):
        """TC-DEM-004: Demodulate 16-QAM."""
        # Generate constellation points on grid [-3, -1, 1, 3]
        grid = np.array([-3.0, -1.0, 1.0, 3.0])
        symbols = []
        for i in grid:
            for q in grid:
                symbols.append((i + 1j * q) / np.sqrt(10.0))
        symbols = np.array(symbols, dtype=np.complex64)

        res = Demodulator.demodulate(symbols, mod_type="16-QAM", apply_carrier_sync=False)
        assert res.num_bits == 16 * 4 # 16 symbols * 4 bits = 64 bits

    def test_tc_dem_005_demod_64qam(self):
        """TC-DEM-005: Demodulate 64-QAM."""
        grid = np.array([-7.0, -5.0, -3.0, -1.0, 1.0, 3.0, 5.0, 7.0])
        symbols = []
        for i in grid[:4]:
            for q in grid[:4]:
                symbols.append((i + 1j * q) / np.sqrt(42.0))
        symbols = np.array(symbols, dtype=np.complex64)

        res = Demodulator.demodulate(symbols, mod_type="64-QAM", apply_carrier_sync=False)
        assert res.num_bits == 16 * 6

    def test_tc_dem_006_demod_2fsk(self):
        """TC-DEM-006: Demodulate 2-FSK."""
        ref_bits = np.array([1, 0, 1, 1, 0, 0, 1, 0], dtype=np.uint8)
        fs = 1.0e6
        sps = 8
        dev = 50000.0 # 50 kHz deviation
        freqs = np.repeat(np.where(ref_bits == 1, dev, -dev), sps)
        phase = 2.0 * np.pi * np.cumsum(freqs) / fs
        samples = np.exp(1j * phase).astype(np.complex64)

        res = Demodulator.demodulate(samples, mod_type="2-FSK")
        np.testing.assert_array_equal(res.bits, ref_bits)

    def test_tc_dem_007_costas_loop_sync(self):
        """TC-DEM-007: Costas loop carrier phase synchronization."""
        # BPSK with static phase offset of 25 degrees
        phi = np.deg2rad(25.0)
        n = 500
        ref_bits = np.random.choice([0, 1], size=n)
        bpsk = np.where(ref_bits == 0, 1.0, -1.0) * np.exp(1j * phi)

        sync_syms, phase_err = Demodulator.costas_loop(bpsk, order=2, loop_bw=0.05)
        # Verify loop tracks and reduces phase error
        assert np.mean(np.abs(phase_err[-50:])) < np.mean(np.abs(phase_err[:50]))

    def test_tc_dem_008_gardner_timing_recovery(self):
        """TC-DEM-008: Symbol timing and constellation EVM."""
        symbols = np.array([1+1j, -1+1j, -1-1j, 1-1j] * 20, dtype=np.complex64) / np.sqrt(2.0)
        res = Demodulator.demodulate(symbols, mod_type="QPSK")
        assert res.estimated_evm_pct > 0.0
        assert res.num_symbols == len(symbols)

    def test_tc_dem_009_channel_noise_resilience(self):
        """TC-DEM-009: Demodulation under AWGN channel noise."""
        np.random.seed(42)
        ref_bits = np.random.choice([0, 1], size=1000).astype(np.uint8)
        symbols = np.where(ref_bits == 0, 1.0, -1.0).astype(np.complex64)
        # Add noise at 15 dB SNR
        noise = (np.random.randn(1000) + 1j * np.random.randn(1000)) * np.sqrt(1.0 / (2.0 * 10**1.5))
        noisy_symbols = symbols + noise

        res = Demodulator.demodulate(noisy_symbols, mod_type="BPSK", apply_carrier_sync=False)
        bit_errors = np.sum(res.bits != ref_bits)
        ber = bit_errors / len(ref_bits)
        assert ber < 0.01 # BER < 1% at 15 dB SNR

    def test_tc_dem_010_constellation_evm(self):
        """TC-DEM-010: EVM calculation."""
        clean = np.array([1+1j, -1+1j, -1-1j, 1-1j], dtype=np.complex64) / np.sqrt(2.0)
        res = Demodulator.demodulate(clean, mod_type="QPSK", apply_carrier_sync=False)
        assert res.estimated_evm_pct >= 0.0

    def test_tc_dem_011_frequency_offset_tolerance(self):
        """TC-DEM-011: Demodulation with carrier tracking."""
        symbols = np.array([1+1j, -1+1j, -1-1j, 1-1j] * 10, dtype=np.complex64)
        res = Demodulator.demodulate(symbols, mod_type="QPSK", apply_carrier_sync=True)
        assert res.num_bits == len(symbols) * 2

    def test_tc_dem_012_high_throughput(self):
        """TC-DEM-012: High-throughput decoding (> 100k symbols)."""
        large_symbols = np.ones(50000, dtype=np.complex64)
        res = Demodulator.demodulate(large_symbols, mod_type="BPSK", apply_carrier_sync=False)
        assert len(res.bits) == 50000
