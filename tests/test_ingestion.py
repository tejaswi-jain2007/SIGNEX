"""
Unit Test Suite for Module 1: File Ingestion & Parsing
Corresponds to Master Test Plan TC-ING-001 through TC-ING-015.
"""

import os
import json
import wave
import struct
import tempfile
import pytest
import numpy as np

from ntro_sigint.core.ingestion import SignalReader, SignalData


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


class TestSignalIngestion:
    
    def test_tc_ing_001_parse_float32_iq(self, temp_dir):
        """TC-ING-001: Parse float32 IQ file."""
        file_path = os.path.join(temp_dir, "sample_float32.iq")
        # Generate 1000 complex samples (2000 float32 scalars)
        t = np.linspace(0, 1e-3, 1000, endpoint=False)
        i_data = np.cos(2 * np.pi * 10e3 * t).astype(np.float32)
        q_data = np.sin(2 * np.pi * 10e3 * t).astype(np.float32)
        interleaved = np.empty(2000, dtype=np.float32)
        interleaved[0::2] = i_data
        interleaved[1::2] = q_data
        interleaved.tofile(file_path)

        data = SignalReader.load(file_path, format_type="float32", sample_rate=1e6)
        assert isinstance(data, SignalData)
        assert data.num_samples == 1000
        assert data.samples.dtype == np.complex64
        assert np.max(np.abs(data.samples)) > 0.0
        np.testing.assert_allclose(data.samples.real, i_data, atol=1e-6)
        np.testing.assert_allclose(data.samples.imag, q_data, atol=1e-6)

    def test_tc_ing_002_parse_int16_iq(self, temp_dir):
        """TC-ING-002: Parse int16 IQ file."""
        file_path = os.path.join(temp_dir, "sample_int16.iq")
        scalars = np.array([16384, -16384, 32767, -32768], dtype=np.int16)
        scalars.tofile(file_path)

        data = SignalReader.load(file_path, format_type="int16", sample_rate=1e6)
        assert data.num_samples == 2
        assert np.all(data.samples.real >= -1.0) and np.all(data.samples.real <= 1.0)
        assert np.all(data.samples.imag >= -1.0) and np.all(data.samples.imag <= 1.0)
        np.testing.assert_allclose(data.samples.real[0], 0.5, atol=1e-4)
        np.testing.assert_allclose(data.samples.imag[0], -0.5, atol=1e-4)

    def test_tc_ing_003_parse_int8_iq(self, temp_dir):
        """TC-ING-003: Parse int8 IQ file."""
        file_path = os.path.join(temp_dir, "sample_int8.iq")
        scalars = np.array([64, -64, 127, -128], dtype=np.int8)
        scalars.tofile(file_path)

        data = SignalReader.load(file_path, format_type="int8", sample_rate=1e6)
        assert data.num_samples == 2
        assert np.all(data.samples.real >= -1.0) and np.all(data.samples.real <= 1.0)
        assert np.all(data.samples.imag >= -1.0) and np.all(data.samples.imag <= 1.0)
        np.testing.assert_allclose(data.samples.real[0], 0.5, atol=1e-2)
        np.testing.assert_allclose(data.samples.imag[0], -0.5, atol=1e-2)

    def test_tc_ing_004_parse_mono_wav(self, temp_dir):
        """TC-ING-004: Parse mono WAV file."""
        file_path = os.path.join(temp_dir, "mono.wav")
        fs = 48000
        duration = 0.05
        n_samples = int(fs * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        audio = (np.sin(2 * np.pi * 1000 * t) * 32767).astype(np.int16)

        with wave.open(file_path, 'wb') as wav_out:
            wav_out.setnchannels(1)
            wav_out.setsampwidth(2)
            wav_out.setframerate(fs)
            wav_out.writeframes(audio.tobytes())

        data = SignalReader.load(file_path)
        assert data.format_type == "wav"
        assert data.sample_rate == 48000
        assert data.metadata["channels"] == 1
        assert data.num_samples == n_samples
        assert not data.is_complex
        assert np.max(np.abs(data.samples)) > 0.5

    def test_tc_ing_005_parse_multi_channel_wav(self, temp_dir):
        """TC-ING-005: Parse multi-channel (stereo) WAV."""
        file_path = os.path.join(temp_dir, "stereo.wav")
        fs = 48000
        n_samples = 1000
        ch1 = (np.ones(n_samples) * 16384).astype(np.int16)
        ch2 = (np.ones(n_samples) * -16384).astype(np.int16)
        interleaved = np.empty(2000, dtype=np.int16)
        interleaved[0::2] = ch1
        interleaved[1::2] = ch2

        with wave.open(file_path, 'wb') as wav_out:
            wav_out.setnchannels(2)
            wav_out.setsampwidth(2)
            wav_out.setframerate(fs)
            wav_out.writeframes(interleaved.tobytes())

        data = SignalReader.load(file_path)
        assert data.metadata["channels"] == 2
        assert data.is_complex
        np.testing.assert_allclose(data.samples.real, 0.5, atol=1e-3)
        np.testing.assert_allclose(data.samples.imag, -0.5, atol=1e-3)

    def test_tc_ing_006_handle_endianness(self, temp_dir):
        """TC-ING-006: Handle byte-order (Endianness)."""
        file_path = os.path.join(temp_dir, "sample_endian.iq")
        # Write 500 samples in big-endian
        ref_samples = np.linspace(-1.0, 1.0, 1000, dtype='>f4')
        ref_samples.tofile(file_path)

        # Load with correct big-endian
        data_be = SignalReader.load(file_path, format_type="float32", endianness="big")
        # Load with wrong little-endian
        data_le = SignalReader.load(file_path, format_type="float32", endianness="little")

        # Correct byte-order reproduces reference accurately
        assert np.all(np.isfinite(data_be.samples))
        np.testing.assert_allclose(data_be.samples.real, ref_samples[0::2], atol=1e-6)
        np.testing.assert_allclose(data_be.samples.imag, ref_samples[1::2], atol=1e-6)

        # Wrong endianness causes severe data corruption: either NaNs, Infs, or massive statistical shift
        has_nan_inf = np.isnan(data_le.samples).any() or np.isinf(data_le.samples).any()
        if not has_nan_inf:
            stat_diff = np.abs(np.mean(data_be.samples.real) - np.mean(data_le.samples.real))
            assert stat_diff > 0.1 or np.std(data_le.samples.real) > 3.0 * np.std(data_be.samples.real)
        else:
            assert has_nan_inf

    def test_tc_ing_007_detect_odd_sample_count(self, temp_dir):
        """TC-ING-007: Detect odd sample count."""
        file_path = os.path.join(temp_dir, "odd_samples.iq")
        # Write 5 float32 scalars (odd number: 2.5 I/Q pairs)
        odd_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
        odd_data.tofile(file_path)

        with pytest.raises(ValueError, match="odd sample count"):
            SignalReader.load(file_path, format_type="float32")

    def test_tc_ing_008_reject_unsupported_extension(self, temp_dir):
        """TC-ING-008: Reject unsupported extension."""
        file_path = os.path.join(temp_dir, "document.txt")
        with open(file_path, "w") as f:
            f.write("Some text")

        with pytest.raises(ValueError, match="Unsupported file format"):
            SignalReader.load(file_path)

    def test_tc_ing_009_handle_empty_file(self, temp_dir):
        """TC-ING-009: Handle empty file."""
        file_path = os.path.join(temp_dir, "empty.iq")
        with open(file_path, "wb") as f:
            pass

        with pytest.raises(ValueError, match="File is empty"):
            SignalReader.load(file_path, format_type="float32")

    def test_tc_ing_010_detect_truncated_payload(self, temp_dir):
        """TC-ING-010: Detect truncated IQ payload."""
        file_path = os.path.join(temp_dir, "truncated.iq")
        # Write 3 bytes (float32 requires multiple of 4 bytes)
        with open(file_path, "wb") as f:
            f.write(b'\x00\x00\x01')

        with pytest.raises(ValueError, match="Truncated IQ payload"):
            SignalReader.load(file_path, format_type="float32")

    def test_tc_ing_011_detect_corrupt_wav_header(self, temp_dir):
        """TC-ING-011: Detect corrupt WAV header."""
        file_path = os.path.join(temp_dir, "corrupt.wav")
        # Write fake bytes with broken RIFF chunk
        with open(file_path, "wb") as f:
            f.write(b"NOT_A_RIFF_WAV_HEADER_CORRUPTED_STREAM_DATA")

        with pytest.raises(ValueError, match="Invalid WAV Header"):
            SignalReader.load(file_path)

    def test_tc_ing_012_use_iq_metadata_sidecar(self, temp_dir):
        """TC-ING-012: Use IQ metadata sidecar."""
        file_path = os.path.join(temp_dir, "signal_with_meta.iq")
        sidecar_path = os.path.join(temp_dir, "signal_with_meta.json")

        scalars = np.zeros(100, dtype=np.float32)
        scalars.tofile(file_path)

        meta = {
            "sample_rate": 20000000.0,
            "center_frequency": 433920000.0,
            "receiver_gain_db": 30.0,
            "location": "Site-Alpha"
        }
        with open(sidecar_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f)

        data = SignalReader.load(file_path, format_type="float32")
        assert data.sample_rate == 20000000.0
        assert data.center_freq == 433920000.0
        assert data.metadata["receiver_gain_db"] == 30.0
        assert data.metadata["location"] == "Site-Alpha"

    def test_tc_ing_013_handle_missing_optional_metadata(self, temp_dir):
        """TC-ING-013: Handle missing optional metadata."""
        file_path = os.path.join(temp_dir, "no_meta.iq")
        scalars = np.zeros(100, dtype=np.float32)
        scalars.tofile(file_path)

        data = SignalReader.load(file_path, format_type="float32")
        # Missing center_freq defaults to "Unknown"
        assert data.metadata["center_frequency"] == "Unknown"
        assert data.center_freq is None
        assert data.num_samples == 50

    def test_tc_ing_014_ingest_large_file_memmap(self, temp_dir):
        """TC-ING-014: Ingest large file using memmap."""
        file_path = os.path.join(temp_dir, "large_sample.iq")
        # Create 100,000 samples via memmap mode
        total_scalars = 200000
        mem = np.memmap(file_path, dtype=np.float32, mode='w+', shape=(total_scalars,))
        mem[0::2] = 0.707
        mem[1::2] = 0.707
        del mem # Flush to disk

        data = SignalReader.load(file_path, format_type="float32", use_memmap=True)
        assert data.num_samples == 100000
        assert np.isclose(data.samples[0], 0.707 + 0.707j, atol=1e-4)

    def test_tc_ing_015_streaming_chunked_processing(self, temp_dir):
        """TC-ING-015: Streaming/chunked processing."""
        file_path = os.path.join(temp_dir, "stream_test.iq")
        total_complex = 10000
        i_ref = np.arange(total_complex, dtype=np.float32)
        q_ref = -np.arange(total_complex, dtype=np.float32)
        interleaved = np.empty(total_complex * 2, dtype=np.float32)
        interleaved[0::2] = i_ref
        interleaved[1::2] = q_ref
        interleaved.tofile(file_path)

        # Stream in chunks of 2000 samples with 0 overlap
        collected = []
        for chunk in SignalReader.read_chunks(file_path, chunk_size=2000, overlap=0, format_type="float32"):
            collected.append(chunk)

        assert len(collected) == 5
        full_recon = np.concatenate(collected)
        assert len(full_recon) == total_complex
        np.testing.assert_allclose(full_recon.real, i_ref)
        np.testing.assert_allclose(full_recon.imag, q_ref)
