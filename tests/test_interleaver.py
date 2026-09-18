"""
Unit Test Suite for Module 7: De-interleaving
Corresponds to Master Test Plan TC-INT-001 through TC-INT-007.
"""

import pytest
import numpy as np

from ntro_sigint.decoding.interleaver import (
    BlockInterleaver,
    ConvolutionalInterleaver,
    PseudoRandomInterleaver,
    DiagonalInterleaver
)


class TestInterleaver:

    def test_tc_int_001_block_deinterleaving(self):
        """TC-INT-001: Block de-interleaving."""
        bits = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1], dtype=np.uint8) # 12 bits
        rows, cols = 3, 4
        interleaved = BlockInterleaver.interleave(bits, rows, cols)
        deinterleaved = BlockInterleaver.deinterleave(interleaved, rows, cols, orig_len=len(bits))
        np.testing.assert_array_equal(deinterleaved, bits)

    def test_tc_int_002_convolutional_deinterleaving(self):
        """TC-INT-002: Convolutional de-interleaving (Forney)."""
        conv_int = ConvolutionalInterleaver(num_branches=4, delay_increment=1)
        bits = np.random.choice([0, 1], size=100).astype(np.uint8)
        interleaved = conv_int.interleave(bits)
        deinterleaved = conv_int.deinterleave(interleaved)
        # Verify de-interleaver restores original stream (after pipeline delay)
        # Pipeline delay = B * (B - 1) * M = 4 * 3 * 1 = 12 samples
        delay = conv_int.B * (conv_int.B - 1) * conv_int.M
        np.testing.assert_array_equal(deinterleaved[delay:], bits[:-delay])

    def test_tc_int_003_diagonal_deinterleaving(self):
        """TC-INT-003: Diagonal de-interleaving."""
        bits = np.random.choice([0, 1], size=64).astype(np.uint8)
        interleaved = DiagonalInterleaver.interleave(bits, size=8)
        deinterleaved = DiagonalInterleaver.deinterleave(interleaved, size=8, orig_len=64)
        np.testing.assert_array_equal(deinterleaved, bits)

    def test_tc_int_004_pseudorandom_lfsr_deinterleaving(self):
        """TC-INT-004: Pseudo-Random (LFSR) de-interleaving."""
        bits = np.random.choice([0, 1], size=256).astype(np.uint8)
        seed = 1234
        interleaved = PseudoRandomInterleaver.interleave(bits, seed=seed)
        # Verify interleaved is different from original
        assert not np.array_equal(interleaved, bits)
        # De-interleave and verify exact match
        deinterleaved = PseudoRandomInterleaver.deinterleave(interleaved, seed=seed)
        np.testing.assert_array_equal(deinterleaved, bits)

    def test_tc_int_005_inversion_roundtrip(self):
        """TC-INT-005: Full roundtrip inversion D(I(x)) == x."""
        bits = np.random.choice([0, 1], size=120).astype(np.uint8)
        for r, c in [(4, 5), (6, 10), (3, 8)]:
            intl = BlockInterleaver.interleave(bits, r, c)
            deintl = BlockInterleaver.deinterleave(intl, r, c, orig_len=len(bits))
            np.testing.assert_array_equal(deintl, bits)

    def test_tc_int_006_incomplete_block_padding(self):
        """TC-INT-006: Incomplete block padding handling."""
        # 17 bits with block size 4x5 = 20 (3 padding bits added)
        bits = np.ones(17, dtype=np.uint8)
        interleaved = BlockInterleaver.interleave(bits, rows=4, cols=5)
        assert len(interleaved) == 20
        deinterleaved = BlockInterleaver.deinterleave(interleaved, rows=4, cols=5, orig_len=17)
        assert len(deinterleaved) == 17
        np.testing.assert_array_equal(deinterleaved, bits)

    def test_tc_int_007_processing_throughput(self):
        """TC-INT-007: Processing throughput (> 1M bits)."""
        large_bits = np.random.choice([0, 1], size=100000).astype(np.uint8)
        interleaved = BlockInterleaver.interleave(large_bits, rows=100, cols=100)
        assert len(interleaved) == 100000
