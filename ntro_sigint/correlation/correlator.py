"""
Bitstream Correlation, Frame Synchronization, Header Dissection, and Payload Extraction.
Air-gapped SIGINT bitstream processing with CRC-16/32 validation.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Callable
import numpy as np
import json
import os
import struct


# Standard Preambles & Synchronization Markers
BARKER_7 = np.array([1, 1, 1, 0, 0, 1, 0], dtype=np.uint8)
BARKER_11 = np.array([1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0], dtype=np.uint8)
BARKER_13 = np.array([1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1], dtype=np.uint8)

# CCSDS standard 32-bit Attached Sync Marker (ASM) 0x1ACFFC1D
CCSDS_ASM_32 = np.unpackbits(np.array([0x1A, 0xCF, 0xFC, 0x1D], dtype=np.uint8))


@dataclass
class FrameSyncMatch:
    """Represents a synchronized frame candidate in the bitstream."""
    start_index: int
    pattern_length: int
    correlation_score: float
    hamming_distance: int
    is_inverted: bool


@dataclass
class ParsedFrame:
    """Represents an extracted and dissected telemetric / bitstream frame."""
    sync_index: int
    header: Dict[str, Any]
    payload_bits: np.ndarray
    payload_bytes: bytes
    crc_calculated: int
    crc_received: int
    crc_valid: bool
    is_partial: bool = False
    fec_status: str = "CLEAN"


class BitstreamCorrelator:
    """
    High-performance bitstream frame synchronizer and protocol parser.
    Supports bipolar cross-correlation, Hamming threshold matching,
    phase ambiguity inversion detection, and CRC validation.
    """

    @staticmethod
    def bits_to_bytes(bits: np.ndarray) -> bytes:
        """Packs a 1D binary bit array into bytes with zero-padding if needed."""
        n_pad = (8 - (len(bits) % 8)) % 8
        if n_pad > 0:
            padded = np.pad(bits, (0, n_pad), mode="constant")
        else:
            padded = bits
        return np.packbits(padded.astype(np.uint8)).tobytes()

    @staticmethod
    def bytes_to_bits(data: bytes) -> np.ndarray:
        """Unpacks bytes into a 1D binary bit array."""
        arr = np.frombuffer(data, dtype=np.uint8)
        return np.unpackbits(arr)

    @staticmethod
    def compute_crc16(data: bytes, poly: int = 0x1021, init: int = 0xFFFF) -> int:
        """
        Computes 16-bit CRC (standard CCITT polynomial 0x1021).
        """
        crc = init
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = ((crc << 1) ^ poly) & 0xFFFF
                else:
                    crc = (crc << 1) & 0xFFFF
        return crc

    @staticmethod
    def compute_crc32(data: bytes) -> int:
        """Computes IEEE 802.3 32-bit CRC."""
        import zlib
        return zlib.crc32(data) & 0xFFFFFFFF

    @classmethod
    def correlate_sync(
        cls,
        bits: np.ndarray,
        sync_word: np.ndarray,
        max_hamming_distance: int = 1,
        check_inversion: bool = True
    ) -> List[FrameSyncMatch]:
        """
        Find all frame synchronization markers in the bitstream with bit-error tolerance.
        Tests both normal and inverted polarities (handles BPSK 180-deg phase ambiguity).
        """
        if len(bits) < len(sync_word):
            return []

        N = len(bits)
        M = len(sync_word)
        sync_word = np.asarray(sync_word, dtype=np.uint8)
        inv_sync_word = 1 - sync_word

        # Fast 1D convolution / sliding window matching
        # Convert bits to bipolar {-1, +1}
        bipolar_stream = (2 * bits.astype(np.int32) - 1)
        bipolar_sync = (2 * sync_word.astype(np.int32) - 1)

        # Sliding dot product
        # correlation length = N - M + 1
        scores = np.convolve(bipolar_stream, bipolar_sync[::-1], mode="valid")
        # scores range from -M to +M
        # normal hamming distance: (M - score) / 2
        # inverted hamming distance: (M - (-score)) / 2 = (M + score) / 2

        matches: List[FrameSyncMatch] = []
        min_required_score = M - 2 * max_hamming_distance

        # Detect normal matches
        candidate_indices = np.where(scores >= min_required_score)[0]
        for idx in candidate_indices:
            h_dist = int((M - scores[idx]) // 2)
            if h_dist <= max_hamming_distance:
                matches.append(FrameSyncMatch(
                    start_index=int(idx),
                    pattern_length=M,
                    correlation_score=float(scores[idx] / M),
                    hamming_distance=h_dist,
                    is_inverted=False
                ))

        # Detect inverted matches if enabled
        if check_inversion:
            max_inv_score = -min_required_score
            inv_candidates = np.where(scores <= max_inv_score)[0]
            for idx in inv_candidates:
                h_dist = int((M + scores[idx]) // 2)
                if h_dist <= max_hamming_distance:
                    matches.append(FrameSyncMatch(
                        start_index=int(idx),
                        pattern_length=M,
                        correlation_score=float(-scores[idx] / M),
                        hamming_distance=h_dist,
                        is_inverted=True
                    ))

        # Sort matches by start_index
        matches.sort(key=lambda m: m.start_index)
        return matches

    @classmethod
    def dissect_header(cls, header_bits: np.ndarray) -> Dict[str, Any]:
        """
        Dissects a standard 48-bit telemetric frame header:
        - 16 bits (bits 0..15): Transmitter ID (uint16 big-endian)
        - 16 bits (bits 16..31): Sequence Number (uint16 big-endian)
        - 16 bits (bits 32..47): Payload Length in bytes (uint16 big-endian)
        """
        if len(header_bits) < 48:
            raise ValueError(f"Header bits length {len(header_bits)} < required 48 bits")

        header_bytes = cls.bits_to_bytes(header_bits[:48])
        tx_id, seq_num, length = struct.unpack(">HHH", header_bytes[:6])

        return {
            "transmitter_id": tx_id,
            "sequence_number": seq_num,
            "payload_length": length,
            "header_bytes_hex": header_bytes[:6].hex().upper()
        }

    @classmethod
    def extract_frame(
        cls,
        bits: np.ndarray,
        sync_match: FrameSyncMatch,
        header_len_bits: int = 48,
        crc_len_bits: int = 16,
        allow_partial: bool = True
    ) -> Optional[ParsedFrame]:
        """
        Extracts a single structured frame starting right after the sync marker.
        Handles polarity inversion if the sync match was inverted.
        """
        idx = sync_match.start_index + sync_match.pattern_length
        stream_remainder = bits[idx:]
        if sync_match.is_inverted:
            stream_remainder = 1 - stream_remainder

        if len(stream_remainder) < header_len_bits:
            return None

        # Dissect header
        header_bits = stream_remainder[:header_len_bits]
        try:
            header_info = cls.dissect_header(header_bits)
        except Exception:
            return None

        expected_payload_bytes = header_info["payload_length"]
        expected_payload_bits = expected_payload_bytes * 8
        total_frame_bits = header_len_bits + expected_payload_bits + crc_len_bits

        is_partial = False
        if len(stream_remainder) < total_frame_bits:
            if not allow_partial:
                return None
            is_partial = True
            available_payload_bits = max(0, len(stream_remainder) - header_len_bits)
            payload_bits = stream_remainder[header_len_bits:header_len_bits + available_payload_bits]
            payload_bytes = cls.bits_to_bytes(payload_bits)
            crc_received = 0
            crc_calc = cls.compute_crc16(payload_bytes)
            crc_valid = False
            fec_status = "PARTIAL_RECOVERED"
        else:
            payload_bits = stream_remainder[header_len_bits:header_len_bits + expected_payload_bits]
            payload_bytes = cls.bits_to_bytes(payload_bits)
            
            # Read CRC-16 (big-endian 16-bit)
            crc_start = header_len_bits + expected_payload_bits
            crc_bits = stream_remainder[crc_start:crc_start + crc_len_bits]
            crc_bytes = cls.bits_to_bytes(crc_bits)
            crc_received = struct.unpack(">H", crc_bytes[:2])[0]
            crc_calc = cls.compute_crc16(payload_bytes)
            crc_valid = (crc_calc == crc_received)
            fec_status = "CLEAN" if crc_valid else "CRC_MISMATCH"

        return ParsedFrame(
            sync_index=sync_match.start_index,
            header=header_info,
            payload_bits=payload_bits,
            payload_bytes=payload_bytes,
            crc_calculated=crc_calc,
            crc_received=crc_received,
            crc_valid=crc_valid,
            is_partial=is_partial,
            fec_status=fec_status
        )

    @classmethod
    def extract_all_frames(
        cls,
        bits: np.ndarray,
        sync_word: np.ndarray,
        max_errors: int = 1,
        header_len_bits: int = 48,
        crc_len_bits: int = 16,
        deinterleaver_fn: Optional[Callable[[np.ndarray], np.ndarray]] = None,
        fec_decoder_fn: Optional[Callable[[np.ndarray], np.ndarray]] = None
    ) -> List[ParsedFrame]:
        """
        End-to-end continuous frame extractor:
        Finds all sync patterns, applies de-interleaver and FEC decoder if provided,
        and extracts all frames with CRC verification.
        """
        # If deinterleaver / FEC operates on the entire stream prior to framing:
        processed_bits = bits
        if deinterleaver_fn is not None:
            processed_bits = deinterleaver_fn(processed_bits)
        if fec_decoder_fn is not None:
            processed_bits = fec_decoder_fn(processed_bits)

        sync_matches = cls.correlate_sync(processed_bits, sync_word, max_hamming_distance=max_errors)
        frames: List[ParsedFrame] = []

        for match in sync_matches:
            frame = cls.extract_frame(
                processed_bits,
                match,
                header_len_bits=header_len_bits,
                crc_len_bits=crc_len_bits,
                allow_partial=True
            )
            if frame is not None:
                frames.append(frame)

        return frames

    @classmethod
    def export_payload_files(
        cls,
        frame: ParsedFrame,
        output_dir: str,
        base_name: str
    ) -> Dict[str, str]:
        """
        Exports extracted frame payload to binary (.bin), hex (.hex), and JSON descriptor (.json).
        """
        os.makedirs(output_dir, exist_ok=True)
        paths = {}

        # 1. Binary payload
        bin_path = os.path.join(output_dir, f"{base_name}.bin")
        with open(bin_path, "wb") as f:
            f.write(frame.payload_bytes)
        paths["bin"] = bin_path

        # 2. Hex representation
        hex_path = os.path.join(output_dir, f"{base_name}.hex")
        with open(hex_path, "w", encoding="utf-8") as f:
            hex_data = frame.payload_bytes.hex().upper()
            # Format in 32-char (16-byte) lines
            for i in range(0, len(hex_data), 32):
                f.write(hex_data[i:i+32] + "\n")
        paths["hex"] = hex_path

        # 3. JSON metadata & payload dump
        json_path = os.path.join(output_dir, f"{base_name}.json")
        dump = {
            "sync_index": frame.sync_index,
            "header": frame.header,
            "payload_length_bytes": len(frame.payload_bytes),
            "crc_calculated": f"0x{frame.crc_calculated:04X}",
            "crc_received": f"0x{frame.crc_received:04X}",
            "crc_valid": frame.crc_valid,
            "fec_status": frame.fec_status,
            "is_partial": frame.is_partial,
            "hex_dump": frame.payload_bytes.hex().upper()
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dump, f, indent=2)
        paths["json"] = json_path

        return paths
