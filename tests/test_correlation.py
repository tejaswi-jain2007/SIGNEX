"""
Test Suite for Bitstream Correlation, Frame Synchronization & Payload Extraction.
Validates TC-COR-001 through TC-COR-010.
"""

import pytest
import numpy as np
import os
import struct
import tempfile
import json

from ntro_sigint.correlation.correlator import (
    BitstreamCorrelator,
    BARKER_7,
    BARKER_11,
    BARKER_13,
    CCSDS_ASM_32,
    FrameSyncMatch,
    ParsedFrame
)
from ntro_sigint.decoding.interleaver import BlockInterleaver


class TestBitstreamCorrelation:

    def _build_test_frame(self, tx_id: int, seq_num: int, payload_bytes: bytes, sync_word: np.ndarray) -> np.ndarray:
        """Helper to construct a complete transmitted frame bitstream."""
        # Header: tx_id (16), seq_num (16), length (16)
        hdr_bytes = struct.pack(">HHH", tx_id, seq_num, len(payload_bytes))
        crc_val = BitstreamCorrelator.compute_crc16(payload_bytes)
        crc_bytes = struct.pack(">H", crc_val)

        full_frame_bytes = hdr_bytes + payload_bytes + crc_bytes
        frame_bits = BitstreamCorrelator.bytes_to_bits(full_frame_bytes)

        # Prepend sync word
        return np.concatenate([sync_word, frame_bits])

    def test_tc_cor_001_frame_sync_exact(self):
        """TC-COR-001: Frame sync correlation (exact match). Peak occurs at exact sync start index."""
        sync = BARKER_13
        # Prepend 100 random noise bits
        np.random.seed(42)
        prefix = np.random.randint(0, 2, 100, dtype=np.uint8)
        frame_bits = self._build_test_frame(0x1234, 1, b"HELLO_NTRO_SIGINT", sync)
        suffix = np.random.randint(0, 2, 50, dtype=np.uint8)

        stream = np.concatenate([prefix, frame_bits, suffix])

        matches = BitstreamCorrelator.correlate_sync(stream, sync, max_hamming_distance=0)
        assert len(matches) == 1
        assert matches[0].start_index == 100
        assert matches[0].hamming_distance == 0
        assert matches[0].correlation_score == 1.0

    def test_tc_cor_002_sync_with_bit_errors(self):
        """TC-COR-002: Sync with bit errors (Hamming tolerance). Peak detected at correct offset despite errors."""
        sync = BARKER_13
        prefix = np.zeros(64, dtype=np.uint8)
        frame_bits = self._build_test_frame(0xABCD, 2, b"CORRUPTED_SYNC_TEST", sync)

        # Corrupt 2 bits inside the sync pattern
        corrupted_frame = frame_bits.copy()
        corrupted_frame[2] = 1 - corrupted_frame[2]
        corrupted_frame[5] = 1 - corrupted_frame[5]

        stream = np.concatenate([prefix, corrupted_frame])

        matches = BitstreamCorrelator.correlate_sync(stream, sync, max_hamming_distance=2)
        assert len(matches) >= 1
        assert matches[0].start_index == 64
        assert matches[0].hamming_distance == 2
        assert matches[0].correlation_score >= (13 - 4) / 13

    def test_tc_cor_003_header_field_dissection(self):
        """TC-COR-003: Header field dissection (payload length, tx ID, seq number)."""
        tx_id = 0x55AA
        seq_num = 1042
        payload = b"MISSION_DATA_PAYLOAD_001"

        frame_bits = self._build_test_frame(tx_id, seq_num, payload, BARKER_11)
        sync_match = BitstreamCorrelator.correlate_sync(frame_bits, BARKER_11, max_hamming_distance=0)[0]

        parsed = BitstreamCorrelator.extract_frame(frame_bits, sync_match)
        assert parsed is not None
        assert parsed.header["transmitter_id"] == tx_id
        assert parsed.header["sequence_number"] == seq_num
        assert parsed.header["payload_length"] == len(payload)

    def test_tc_cor_004_crc16_verification(self):
        """TC-COR-004: Payload extraction & CRC-16 verification."""
        payload = b"CRITICAL_INTELLIGENCE_PACKET"
        frame_bits = self._build_test_frame(0x01, 100, payload, BARKER_13)

        sync_match = BitstreamCorrelator.correlate_sync(frame_bits, BARKER_13, max_hamming_distance=0)[0]
        parsed = BitstreamCorrelator.extract_frame(frame_bits, sync_match)

        assert parsed is not None
        assert parsed.crc_valid is True
        assert parsed.fec_status == "CLEAN"
        assert parsed.payload_bytes == payload

        # Test with corrupted bit in payload
        corrupted_bits = frame_bits.copy()
        # Flip a bit in the payload region (after 13 sync + 48 header = bit index 65)
        corrupted_bits[65] = 1 - corrupted_bits[65]
        parsed_corrupted = BitstreamCorrelator.extract_frame(corrupted_bits, sync_match)
        assert parsed_corrupted.crc_valid is False
        assert parsed_corrupted.fec_status == "CRC_MISMATCH"

    def test_tc_cor_005_payload_export(self):
        """TC-COR-005: Payload export (binary, hex, JSON)."""
        payload = b"SECURE_NTRO_PAYLOAD_EXPORT_VERIFY"
        frame_bits = self._build_test_frame(0x99, 1, payload, BARKER_7)

        sync_match = BitstreamCorrelator.correlate_sync(frame_bits, BARKER_7, max_hamming_distance=0)[0]
        parsed = BitstreamCorrelator.extract_frame(frame_bits, sync_match)

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = BitstreamCorrelator.export_payload_files(parsed, tmpdir, "frame_001")
            
            assert os.path.exists(paths["bin"])
            assert os.path.exists(paths["hex"])
            assert os.path.exists(paths["json"])

            with open(paths["bin"], "rb") as f:
                assert f.read() == payload

            with open(paths["hex"], "r", encoding="utf-8") as f:
                content = f.read().replace("\n", "").strip()
                assert content == payload.hex().upper()

            with open(paths["json"], "r", encoding="utf-8") as f:
                data = json.load(f)
                assert data["crc_valid"] is True
                assert data["header"]["transmitter_id"] == 0x99

    def test_tc_cor_006_false_sync_rejection(self):
        """TC-COR-006: False sync rejection on random noise."""
        np.random.seed(999)
        noise_bits = np.random.randint(0, 2, 5000, dtype=np.uint8)

        # CCSDS 32-bit sync word is 32 bits long
        matches = BitstreamCorrelator.correlate_sync(noise_bits, CCSDS_ASM_32, max_hamming_distance=2)
        # Random noise should have near-zero probability of 30+ bit matches
        assert len(matches) == 0

    def test_tc_cor_007_multi_frame_extraction(self):
        """TC-COR-007: Continuous multi-frame extraction (N frames identified and extracted)."""
        sync = BARKER_13
        frames_payloads = [
            (0x101, 1, b"FRAME_ONE_PAYLOAD"),
            (0x101, 2, b"FRAME_TWO_PAYLOAD"),
            (0x101, 3, b"FRAME_THREE_PAYLOAD")
        ]

        stream_parts = []
        for tx, seq, p in frames_payloads:
            stream_parts.append(np.random.randint(0, 2, 40, dtype=np.uint8)) # Inter-frame noise/gap
            stream_parts.append(self._build_test_frame(tx, seq, p, sync))

        full_stream = np.concatenate(stream_parts)

        extracted = BitstreamCorrelator.extract_all_frames(full_stream, sync, max_errors=0)
        assert len(extracted) == 3
        for i, frame in enumerate(extracted):
            assert frame.crc_valid is True
            assert frame.header["sequence_number"] == i + 1
            assert frame.payload_bytes == frames_payloads[i][2]

    def test_tc_cor_008_payload_size_inference(self):
        """TC-COR-008: Payload size inference from header fields."""
        payload_var = b"A" * 250
        frame_bits = self._build_test_frame(0x42, 77, payload_var, BARKER_11)

        sync_match = BitstreamCorrelator.correlate_sync(frame_bits, BARKER_11, max_hamming_distance=0)[0]
        parsed = BitstreamCorrelator.extract_frame(frame_bits, sync_match)

        assert parsed is not None
        assert parsed.header["payload_length"] == 250
        assert len(parsed.payload_bytes) == 250

    def test_tc_cor_009_interleaved_payload_recovery(self):
        """TC-COR-009: Interleaved payload recovery across de-interleaver."""
        payload = b"INTERLEAVED_SECRET_TELEMETRY_DATA"
        frame_bits = self._build_test_frame(0x88, 5, payload, BARKER_13)

        # Pad to multiple of 128 (8x16)
        rows, cols = 8, 16
        block_size = rows * cols
        n_pad = (block_size - (len(frame_bits) % block_size)) % block_size
        padded_bits = np.pad(frame_bits, (0, n_pad), mode="constant")

        interleaved_bits = BlockInterleaver.interleave(padded_bits, rows, cols)

        # Extract using de-interleaver callback
        deint_fn = lambda b: BlockInterleaver.deinterleave(b, rows, cols)
        recovered = BitstreamCorrelator.extract_all_frames(
            interleaved_bits,
            BARKER_13,
            max_errors=0,
            deinterleaver_fn=deint_fn
        )

        assert len(recovered) >= 1
        assert recovered[0].crc_valid is True
        assert recovered[0].payload_bytes == payload

    def test_tc_cor_010_partial_payload_recovery_on_fec_failure(self):
        """TC-COR-010: Partial payload recovery on truncated/failing frames."""
        payload = b"VERY_LONG_PAYLOAD_THAT_WILL_BE_CUT_OFF_DUE_TO_DROPPED_CARRIER"
        frame_bits = self._build_test_frame(0x77, 9, payload, BARKER_11)

        # Truncate frame prematurely (drop the last 50 bits including CRC)
        truncated_bits = frame_bits[:-50]

        sync_match = BitstreamCorrelator.correlate_sync(truncated_bits, BARKER_11, max_hamming_distance=0)[0]
        parsed = BitstreamCorrelator.extract_frame(truncated_bits, sync_match, allow_partial=True)

        assert parsed is not None
        assert parsed.is_partial is True
        assert parsed.fec_status == "PARTIAL_RECOVERED"
        assert len(parsed.payload_bytes) > 0
        assert parsed.crc_valid is False
