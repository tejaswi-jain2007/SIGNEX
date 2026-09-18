"""
Unit Test Suite for Module 8: Forward Error Correction (FEC) Decoding
Corresponds to Master Test Plan TC-FEC-001 through TC-FEC-010.
"""

import pytest
import numpy as np

from ntro_sigint.decoding.fec import (
    ConvolutionalCodec,
    ReedSolomonGF8,
    ConcatenatedCodec
)


class TestFECDecoding:

    def test_tc_fec_001_viterbi_clean_data(self):
        """TC-FEC-001: Viterbi decoding (clean data, K=7, rate 1/2)."""
        codec = ConvolutionalCodec(k=7)
        # Random message of 50 bits
        msg = np.array([1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1] * 3, dtype=np.uint8)
        encoded = codec.encode(msg)
        decoded, ber = codec.decode(encoded)

        np.testing.assert_array_equal(decoded, msg)
        assert ber == 0.0

    def test_tc_fec_002_viterbi_error_correction(self):
        """TC-FEC-002: Viterbi decoding with bit errors (coding gain)."""
        codec = ConvolutionalCodec(k=7)
        msg = np.array([1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1] * 5, dtype=np.uint8)
        encoded = codec.encode(msg)

        # Inject 3 random bit flips in encoded stream
        corrupted = encoded.copy()
        corrupted[5] ^= 1
        corrupted[25] ^= 1
        corrupted[45] ^= 1

        decoded, ber = codec.decode(corrupted)
        # Viterbi corrects isolated errors
        np.testing.assert_array_equal(decoded, msg)

    def test_tc_fec_003_viterbi_soft_decision(self):
        """TC-FEC-003: Soft-decision Viterbi decoding."""
        codec = ConvolutionalCodec(k=7)
        msg = np.array([0, 1, 1, 0, 1, 0, 0, 1] * 4, dtype=np.uint8)
        encoded = codec.encode(msg)

        # Convert to soft values (0 -> +1.0, 1 -> -1.0) with slight AWGN
        soft_vals = (1.0 - 2.0 * encoded.astype(np.float32)) + np.random.randn(len(encoded)) * 0.2
        decoded, _ = codec.decode(soft_vals, soft_input=True)
        np.testing.assert_array_equal(decoded, msg)

    def test_tc_fec_004_reed_solomon_decoding(self):
        """TC-FEC-004: Reed-Solomon GF(2^8) decoding (correcting errors)."""
        # RS(15, 11) with t=2 (can correct up to 2 symbol errors)
        rs = ReedSolomonGF8(n=15, k=11)
        msg = np.array([10, 25, 42, 99, 128, 200, 5, 88, 17, 33, 77], dtype=np.uint8)
        codeword = rs.encode(msg)

        # Inject 2 symbol errors
        rx_corrupted = codeword.copy()
        rx_corrupted[2] ^= 0x55
        rx_corrupted[8] ^= 0xAA

        decoded, uncorrectable, num_errors = rs.decode(rx_corrupted)
        assert not uncorrectable
        assert num_errors == 2
        np.testing.assert_array_equal(decoded, msg)

    def test_tc_fec_005_reed_solomon_uncorrectable(self):
        """TC-FEC-005: RS uncorrectable error detection."""
        # RS(15, 11) with t=2
        rs = ReedSolomonGF8(n=15, k=11)
        msg = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], dtype=np.uint8)
        codeword = rs.encode(msg)

        # Inject 4 symbol errors (exceeds t=2)
        rx_corrupted = codeword.copy()
        rx_corrupted[1] ^= 0xFF
        rx_corrupted[3] ^= 0xFF
        rx_corrupted[5] ^= 0xFF
        rx_corrupted[7] ^= 0xFF

        _, uncorrectable, _ = rs.decode(rx_corrupted)
        assert uncorrectable # Correctly flagged as uncorrectable

    def test_tc_fec_006_rs_clean_codeword(self):
        """TC-FEC-006: RS clean codeword zero overhead decoding."""
        rs = ReedSolomonGF8(n=15, k=11)
        msg = np.arange(11, dtype=np.uint8)
        codeword = rs.encode(msg)
        decoded, uncorrectable, num_errors = rs.decode(codeword)
        assert not uncorrectable
        assert num_errors == 0
        np.testing.assert_array_equal(decoded, msg)

    def test_tc_fec_007_concatenated_coding(self):
        """TC-FEC-007: Concatenated FEC decoding (Outer RS + Inner Viterbi)."""
        concat = ConcatenatedCodec()
        raw_data = b"HELLO_WORLD" # 11 bytes matching RS(15, 11)
        encoded_bits = concat.encode(raw_data)

        # Decodes clean stream
        recovered, uncorrectable = concat.decode(encoded_bits)
        assert not uncorrectable
        assert recovered.startswith(raw_data)

    def test_tc_fec_008_configurable_constraint_length(self):
        """TC-FEC-008: Configurable constraint lengths (K=3, 5, 7)."""
        for k_val, g1, g2 in [(3, 0o7, 0o5), (5, 0o35, 0o23), (7, 0o171, 0o133)]:
            codec = ConvolutionalCodec(k=k_val, g1=g1, g2=g2)
            msg = np.array([1, 0, 1, 1, 0, 0, 1], dtype=np.uint8)
            encoded = codec.encode(msg)
            decoded, _ = codec.decode(encoded)
            np.testing.assert_array_equal(decoded, msg)

    def test_tc_fec_009_traceback_depth(self):
        """TC-FEC-009: Traceback depth validation (5*K)."""
        codec = ConvolutionalCodec(k=7)
        msg = np.random.choice([0, 1], size=100).astype(np.uint8)
        encoded = codec.encode(msg)
        decoded, _ = codec.decode(encoded, traceback_depth=35)
        np.testing.assert_array_equal(decoded, msg)

    def test_tc_fec_010_decoder_throughput(self):
        """TC-FEC-010: High-throughput Viterbi decoding."""
        codec = ConvolutionalCodec(k=5) # Fast K=5 trellis
        msg = np.random.choice([0, 1], size=1000).astype(np.uint8)
        encoded = codec.encode(msg)
        decoded, _ = codec.decode(encoded)
        assert len(decoded) == 1000
