"""
NTRO SIGINT De-interleaving Module
Supports Block (Matrix), Convolutional (Forney), Diagonal,
and Pseudo-Random (LFSR) interleavers and de-interleavers.
Conforms to SRS FR-6.1 and Master Test Plan TC-INT-001 through TC-INT-007.
"""

from typing import List, Optional, Tuple
import numpy as np


class BlockInterleaver:
    """Matrix (Block) interleaver and de-interleaver."""

    @staticmethod
    def interleave(bits: np.ndarray, rows: int, cols: int) -> np.ndarray:
        """Write by rows, read by columns."""
        total_needed = int(np.ceil(len(bits) / (rows * cols))) * (rows * cols)
        padded = np.pad(bits, (0, total_needed - len(bits)), mode='constant')
        matrix = padded.reshape(-1, rows, cols)
        interleaved = matrix.transpose(0, 2, 1).flatten()
        return interleaved.astype(np.uint8)

    @staticmethod
    def deinterleave(bits: np.ndarray, rows: int, cols: int, orig_len: Optional[int] = None) -> np.ndarray:
        """Write by columns, read by rows."""
        block_size = rows * cols
        num_blocks = len(bits) // block_size
        matrix = bits[:num_blocks * block_size].reshape(num_blocks, cols, rows)
        deinterleaved = matrix.transpose(0, 2, 1).flatten()
        if orig_len is not None:
            return deinterleaved[:orig_len].astype(np.uint8)
        return deinterleaved.astype(np.uint8)


class ConvolutionalInterleaver:
    """Forney Convolutional Interleaver with branch delays."""

    def __init__(self, num_branches: int = 4, delay_increment: int = 1):
        self.B = num_branches
        self.M = delay_increment

    def interleave(self, bits: np.ndarray) -> np.ndarray:
        """Process bitstream through B shift register delay lines."""
        n = len(bits)
        out = np.zeros(n, dtype=np.uint8)
        # Shift registers for each branch
        delays = [list(np.zeros(i * self.M, dtype=np.uint8)) for i in range(self.B)]

        for i, b in enumerate(bits):
            branch_idx = i % self.B
            delay_line = delays[branch_idx]
            if len(delay_line) > 0:
                delay_line.append(b)
                out[i] = delay_line.pop(0)
            else:
                out[i] = b
        return out

    def deinterleave(self, bits: np.ndarray) -> np.ndarray:
        """Inverse Forney de-interleaver with complementary delays."""
        n = len(bits)
        out = np.zeros(n, dtype=np.uint8)
        comp_delays = [list(np.zeros((self.B - 1 - i) * self.M, dtype=np.uint8)) for i in range(self.B)]

        for i, b in enumerate(bits):
            branch_idx = i % self.B
            delay_line = comp_delays[branch_idx]
            if len(delay_line) > 0:
                delay_line.append(b)
                out[i] = delay_line.pop(0)
            else:
                out[i] = b
        return out


class PseudoRandomInterleaver:
    """LFSR-based pseudo-random interleaver with repeatable seed."""

    @staticmethod
    def generate_permutation(length: int, seed: int = 42) -> np.ndarray:
        rng = np.random.RandomState(seed)
        return rng.permutation(length)

    @staticmethod
    def interleave(bits: np.ndarray, seed: int = 42) -> np.ndarray:
        perm = PseudoRandomInterleaver.generate_permutation(len(bits), seed)
        return bits[perm].astype(np.uint8)

    @staticmethod
    def deinterleave(bits: np.ndarray, seed: int = 42) -> np.ndarray:
        perm = PseudoRandomInterleaver.generate_permutation(len(bits), seed)
        inv_perm = np.empty_like(perm)
        inv_perm[perm] = np.arange(len(bits))
        return bits[inv_perm].astype(np.uint8)


class DiagonalInterleaver:
    """Diagonal matrix interleaver."""

    @staticmethod
    def interleave(bits: np.ndarray, size: int = 8) -> np.ndarray:
        block_size = size * size
        n_blocks = int(np.ceil(len(bits) / block_size))
        padded = np.pad(bits, (0, n_blocks * block_size - len(bits)))
        out = np.empty_like(padded)

        for b in range(n_blocks):
            blk = padded[b * block_size:(b + 1) * block_size].reshape(size, size)
            # Diagonal roll
            diag_blk = np.empty_like(blk)
            for r in range(size):
                diag_blk[r] = np.roll(blk[r], r)
            out[b * block_size:(b + 1) * block_size] = diag_blk.T.flatten()
        return out.astype(np.uint8)

    @staticmethod
    def deinterleave(bits: np.ndarray, size: int = 8, orig_len: Optional[int] = None) -> np.ndarray:
        block_size = size * size
        n_blocks = len(bits) // block_size
        out = np.empty(len(bits), dtype=np.uint8)

        for b in range(n_blocks):
            diag_blk = bits[b * block_size:(b + 1) * block_size].reshape(size, size).T
            blk = np.empty_like(diag_blk)
            for r in range(size):
                blk[r] = np.roll(diag_blk[r], -r)
            out[b * block_size:(b + 1) * block_size] = blk.flatten()

        if orig_len is not None:
            return out[:orig_len]
        return out
