"""
NTRO SIGINT Signal Ingestion Module
Handles parsing of raw .iq (Float32, Int16, Int8) and .wav (mono/stereo) files.
Supports memory-mapped ingestion (np.memmap) for large files (up to 2 GB),
metadata sidecar parsing, and chunked streaming.
Conforms to SRS FR-1.1 and Master Test Plan TC-ING-001 through TC-ING-015.
"""

import os
import json
import wave
import struct
from typing import Dict, Any, Optional, Generator, Tuple
from dataclasses import dataclass, field
import numpy as np


SUPPORTED_EXTENSIONS = {'.iq', '.wav', '.raw', '.dat'}
VALID_IQ_FORMATS = {'float32', 'int16', 'int8', 'auto'}


@dataclass
class SignalData:
    """Standardized internal representation of an ingested signal."""
    samples: np.ndarray
    sample_rate: float
    format_type: str
    num_samples: int
    duration_sec: float
    center_freq: Optional[float] = None
    is_complex: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    file_path: Optional[str] = None

    def __post_init__(self):
        if self.num_samples == 0 and len(self.samples) > 0:
            self.num_samples = len(self.samples)
        if self.duration_sec == 0.0 and self.sample_rate > 0:
            self.duration_sec = self.num_samples / self.sample_rate


class SignalReader:
    """
    Ingestion engine for RF signal files and audio recordings.
    Enforces air-gapped security, input sanitization, and robust error handling.
    """

    @staticmethod
    def load(
        file_path: str,
        format_type: str = "auto",
        sample_rate: Optional[float] = None,
        center_freq: Optional[float] = None,
        endianness: str = "little",
        use_memmap: bool = False
    ) -> SignalData:
        """
        Load an RF signal or audio recording from disk into a SignalData object.
        
        Parameters
        ----------
        file_path : str
            Path to the input file (.iq, .wav, etc.)
        format_type : str
            Data type: 'float32', 'int16', 'int8', 'wav', or 'auto'
        sample_rate : float, optional
            Sampling frequency in Hz (if not specified in WAV or sidecar)
        center_freq : float, optional
            RF center frequency in Hz
        endianness : str
            'little' (<) or 'big' (>) byte ordering
        use_memmap : bool
            If True, uses np.memmap for zero-copy memory mapping of large files.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise ValueError("File is empty")

        _, ext = os.path.splitext(file_path)
        ext_lower = ext.lower()

        # Reject unsupported extension unless explicit known format requested
        if ext_lower not in SUPPORTED_EXTENSIONS and format_type == "auto":
            raise ValueError(f"Unsupported file format: '{ext}'. Supported formats: {sorted(list(SUPPORTED_EXTENSIONS))}")

        # Attempt to load metadata sidecar (.json)
        sidecar_meta = SignalReader._parse_metadata_sidecar(file_path)

        # Merge metadata with parameters
        if sample_rate is None:
            sample_rate = sidecar_meta.get("sample_rate")
        if center_freq is None:
            center_freq = sidecar_meta.get("center_frequency")

        # Fallback defaults
        effective_fs = float(sample_rate) if sample_rate is not None else 1.0e6
        effective_fc = float(center_freq) if center_freq is not None else None

        if ext_lower == ".wav" or format_type.lower() == "wav":
            signal_data = SignalReader._parse_wav_file(file_path, effective_fc, sidecar_meta)
        else:
            signal_data = SignalReader._parse_iq_file(
                file_path=file_path,
                format_type=format_type,
                sample_rate=effective_fs,
                center_freq=effective_fc,
                endianness=endianness,
                use_memmap=use_memmap,
                sidecar_meta=sidecar_meta
            )

        return signal_data

    @staticmethod
    def _parse_iq_file(
        file_path: str,
        format_type: str,
        sample_rate: float,
        center_freq: Optional[float],
        endianness: str,
        use_memmap: bool,
        sidecar_meta: Dict[str, Any]
    ) -> SignalData:
        """Parse raw interleaved I/Q binary file."""
        fmt = format_type.lower()
        if fmt == "auto":
            # Default to float32 if unstated in metadata
            fmt = sidecar_meta.get("data_type", "float32").lower()

        endian_prefix = "<" if endianness.lower() in ("little", "<", "le") else ">"

        if fmt in ("float32", "f32"):
            dtype = np.dtype(f"{endian_prefix}f4")
            scale = 1.0
        elif fmt in ("int16", "i16", "s16"):
            dtype = np.dtype(f"{endian_prefix}i2")
            scale = 32768.0
        elif fmt in ("int8", "i8", "s8"):
            dtype = np.dtype("i1")
            scale = 128.0
        else:
            raise ValueError(f"Unsupported IQ format: {format_type}. Valid: {sorted(list(VALID_IQ_FORMATS))}")

        file_size = os.path.getsize(file_path)
        itemsize = dtype.itemsize

        if file_size % itemsize != 0:
            raise ValueError(f"Truncated IQ payload: file size {file_size} bytes is not a multiple of itemsize {itemsize}")

        total_scalars = file_size // itemsize

        # Incomplete I/Q pair check (odd number of scalars)
        if total_scalars % 2 != 0:
            raise ValueError(f"Detect odd sample count: {total_scalars} scalars found; cannot form complete I/Q pairs")

        num_complex_samples = total_scalars // 2

        if use_memmap:
            # Memory mapped mode for large datasets up to 2 GB
            raw_mem = np.memmap(file_path, dtype=dtype, mode='r')
            i_samples = raw_mem[0::2].astype(np.float32) / scale
            q_samples = raw_mem[1::2].astype(np.float32) / scale
            complex_samples = i_samples + 1j * q_samples
        else:
            raw_data = np.fromfile(file_path, dtype=dtype)
            i_samples = raw_data[0::2].astype(np.float32) / scale
            q_samples = raw_data[1::2].astype(np.float32) / scale
            complex_samples = i_samples + 1j * q_samples

        meta = {
            "endianness": endianness,
            "raw_dtype": str(dtype),
            "source_format": fmt,
            "center_frequency": center_freq if center_freq is not None else "Unknown",
            "sample_rate": sample_rate,
            "file_size_bytes": file_size
        }
        meta.update(sidecar_meta)

        return SignalData(
            samples=complex_samples,
            sample_rate=sample_rate,
            format_type=fmt,
            num_samples=num_complex_samples,
            duration_sec=num_complex_samples / sample_rate,
            center_freq=center_freq,
            is_complex=True,
            metadata=meta,
            file_path=file_path
        )

    @staticmethod
    def _parse_wav_file(
        file_path: str,
        center_freq: Optional[float],
        sidecar_meta: Dict[str, Any]
    ) -> SignalData:
        """Parse standard RIFF WAV file."""
        # Sanity check RIFF chunk header
        try:
            with open(file_path, 'rb') as f:
                header = f.read(12)
                if len(header) < 12 or header[:4] != b'RIFF' or header[8:12] != b'WAVE':
                    raise ValueError("Invalid WAV Header: missing RIFF/WAVE identifier")
        except IOError as e:
            raise ValueError(f"Invalid WAV Header: cannot read file ({e})")

        try:
            with wave.open(file_path, 'rb') as wav_in:
                num_channels = wav_in.getnchannels()
                sample_width = wav_in.getsampwidth()
                sample_rate = wav_in.getframerate()
                num_frames = wav_in.getnframes()
                raw_bytes = wav_in.readframes(num_frames)
        except Exception as e:
            raise ValueError(f"Invalid WAV Header: {e}")

        if sample_width == 1:
            # 8-bit unsigned PCM [0, 255]
            raw_array = np.frombuffer(raw_bytes, dtype=np.uint8).astype(np.float32)
            norm_array = (raw_array - 128.0) / 128.0
        elif sample_width == 2:
            # 16-bit signed PCM
            norm_array = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        elif sample_width == 3:
            # 24-bit PCM
            raw_ints = []
            for i in range(0, len(raw_bytes), 3):
                b = raw_bytes[i:i+3] + (b'\x00' if raw_bytes[i+2] < 128 else b'\xff')
                val = struct.unpack('<i', b)[0]
                raw_ints.append(val)
            norm_array = np.array(raw_ints, dtype=np.float32) / 8388608.0
        elif sample_width == 4:
            # 32-bit float or signed PCM
            norm_array = np.frombuffer(raw_bytes, dtype=np.float32)
        else:
            raise ValueError(f"Unsupported WAV sample width: {sample_width} bytes")

        if num_channels == 1:
            # Mono channel: real audio signal
            samples = norm_array
            is_complex = False
        elif num_channels == 2:
            # Stereo: can be treated as I (ch0) and Q (ch1)
            i_ch = norm_array[0::2]
            q_ch = norm_array[1::2]
            samples = (i_ch + 1j * q_ch).astype(np.complex64)
            is_complex = True
        else:
            # Multi-channel
            samples = norm_array.reshape(-1, num_channels)
            is_complex = False

        duration = num_frames / sample_rate if sample_rate > 0 else 0.0

        meta = {
            "channels": num_channels,
            "sample_width": sample_width,
            "sample_rate": sample_rate,
            "duration": duration,
            "center_frequency": center_freq if center_freq is not None else "Unknown",
            "source_format": "wav"
        }
        meta.update(sidecar_meta)

        return SignalData(
            samples=samples,
            sample_rate=float(sample_rate),
            format_type="wav",
            num_samples=num_frames,
            duration_sec=duration,
            center_freq=center_freq,
            is_complex=is_complex,
            metadata=meta,
            file_path=file_path
        )

    @staticmethod
    def _parse_metadata_sidecar(file_path: str) -> Dict[str, Any]:
        """Check for and parse JSON metadata sidecar (TC-ING-012, TC-ING-013)."""
        base, _ = os.path.splitext(file_path)
        sidecar_candidates = [
            f"{base}.json",
            f"{file_path}.json",
            f"{base}.meta"
        ]
        for candidate in sidecar_candidates:
            if os.path.exists(candidate):
                try:
                    with open(candidate, 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                    # Normalize known keys
                    if "center_frequency" not in meta and "center_freq" in meta:
                        meta["center_frequency"] = meta["center_freq"]
                    if "sample_rate" not in meta and "fs" in meta:
                        meta["sample_rate"] = meta["fs"]
                    return meta
                except Exception:
                    pass
        return {}

    @staticmethod
    def read_chunks(
        file_path: str,
        chunk_size: int = 1048576,
        overlap: int = 0,
        format_type: str = "float32",
        endianness: str = "little"
    ) -> Generator[np.ndarray, None, None]:
        """
        Streaming chunk iterator for files larger than available RAM (TC-ING-015).
        Maintains continuity and avoids boundary distortion.
        """
        fmt = format_type.lower()
        endian_prefix = "<" if endianness.lower() in ("little", "<", "le") else ">"

        if fmt in ("float32", "f32"):
            dtype = np.dtype(f"{endian_prefix}f4")
            scale = 1.0
        elif fmt in ("int16", "i16"):
            dtype = np.dtype(f"{endian_prefix}i2")
            scale = 32768.0
        elif fmt in ("int8", "i8"):
            dtype = np.dtype("i1")
            scale = 128.0
        else:
            raise ValueError(f"Unsupported format for streaming: {format_type}")

        itemsize = dtype.itemsize
        step = chunk_size - overlap
        if step <= 0:
            raise ValueError("chunk_size must be strictly greater than overlap")

        file_size = os.path.getsize(file_path)
        total_scalars = file_size // itemsize
        total_complex = total_scalars // 2

        with open(file_path, 'rb') as f:
            offset = 0
            while offset < total_complex:
                count = min(chunk_size, total_complex - offset)
                bytes_to_read = count * 2 * itemsize
                
                # Seek to correct position for I/Q pair
                f.seek(offset * 2 * itemsize)
                buf = f.read(bytes_to_read)
                if not buf:
                    break

                raw = np.frombuffer(buf, dtype=dtype)
                if len(raw) % 2 != 0:
                    raw = raw[:-1]

                i_part = raw[0::2].astype(np.float32) / scale
                q_part = raw[1::2].astype(np.float32) / scale
                chunk_complex = i_part + 1j * q_part

                yield chunk_complex
                offset += step
