"""
End-to-End Pipeline Integration Test Suite.
Validates TC-E2E-001 through TC-E2E-010.
"""

import pytest
import os
import tempfile
import struct
import numpy as np

from ntro_sigint.core.pipeline import SignalAnalysisPipeline
from ntro_sigint.ml.dataset import SyntheticSignalGenerator
from ntro_sigint.correlation.correlator import BitstreamCorrelator, BARKER_13
from ntro_sigint.decoding.interleaver import BlockInterleaver
from ntro_sigint.decoding.fec import ConvolutionalCodec


class TestEndToEndPipeline:

    @pytest.fixture
    def pipeline(self):
        return SignalAnalysisPipeline(model_path="models/amc_resnet18.pt", enforce_airgap=False)

    def _create_raw_iq_file(self, tmp_path, filename: str, sig: np.ndarray, fs: float) -> str:
        """Helper to write raw float32 IQ file and optional JSON metadata."""
        filepath = os.path.join(tmp_path, filename)
        iq_interleaved = np.empty(len(sig) * 2, dtype=np.float32)
        iq_interleaved[0::2] = sig.real
        iq_interleaved[1::2] = sig.imag
        with open(filepath, "wb") as f:
            f.write(iq_interleaved.tobytes())

        # Write sidecar
        sidecar = filepath + ".json"
        import json
        with open(sidecar, "w", encoding="utf-8") as f:
            json.dump({"sample_rate": fs, "center_freq": 0.0}, f)

        return filepath

    def _synthesize_frame_bits(self, tx_id: int, seq: int, payload: bytes) -> np.ndarray:
        """Constructs framed bits: BARKER_13 + Header (48) + Payload + CRC-16 (16)."""
        hdr_bytes = struct.pack(">HHH", tx_id, seq, len(payload))
        crc = BitstreamCorrelator.compute_crc16(payload)
        crc_bytes = struct.pack(">H", crc)
        frame_bytes = hdr_bytes + payload + crc_bytes
        frame_bits = BitstreamCorrelator.bytes_to_bits(frame_bytes)
        return np.concatenate([BARKER_13, frame_bits])

    def test_tc_e2e_001_clean_qpsk_e2e(self, pipeline, tmp_path):
        """TC-E2E-001: Clean QPSK E2E (high SNR)."""
        fs = 1.0e6
        payload = b"NTRO_MISSION_ALPHA_QPSK_DATA"
        frame_bits = self._synthesize_frame_bits(0x01, 1, payload)

        # Modulate frame bits to QPSK matching Demodulator Gray mapping
        if len(frame_bits) % 2 != 0:
            frame_bits = np.pad(frame_bits, (0, 1))
        b0 = frame_bits[0::2]
        b1 = frame_bits[1::2]
        min_len = min(len(b0), len(b1))
        real = np.where(b1[:min_len] == 1, -1.0, 1.0)
        imag = np.where(b0[:min_len] == 1, -1.0, 1.0)
        syms = (real + 1j * imag) / np.sqrt(2.0)

        # Signal array (exact symbol sequence)
        sig = syms.astype(np.complex64)
        if len(sig) < 2048:
            repeats = int(np.ceil(2048 / len(sig)))
            sig = np.tile(sig, repeats)[:2048]

        iq_file = self._create_raw_iq_file(str(tmp_path), "clean_qpsk.iq", sig, fs)
        out_dir = str(tmp_path / "out_e2e_001")

        result = pipeline.process_file(iq_file, output_dir=out_dir, generate_pdf=True)

        assert result.classification["predicted_class"] == "QPSK"
        assert result.classification["confidence"] >= 0.70
        assert os.path.exists(result.exported_files["json"])
        assert os.path.exists(result.exported_files["pdf"])
        assert len(result.frames) >= 1
        assert result.frames[0]["crc_valid"] is True

    def test_tc_e2e_002_bpsk_with_fec_e2e(self, pipeline, tmp_path):
        """TC-E2E-002: BPSK with FEC E2E."""
        fs = 1.0e6
        payload = b"SECURE_FEC_PACKET"
        frame_bits = self._synthesize_frame_bits(0x02, 1, payload)

        # Encode with Viterbi rate 1/2 K=7
        codec = ConvolutionalCodec(k=7)
        encoded_bits = codec.encode(frame_bits)

        # Modulate to BPSK (0 -> +1.0, 1 -> -1.0)
        bpsk_syms = np.where(encoded_bits == 0, 1.0, -1.0).astype(np.complex64)
        sig = bpsk_syms
        if len(sig) < 2048:
            repeats = int(np.ceil(2048 / len(sig)))
            sig = np.tile(sig, repeats)[:2048]

        iq_file = self._create_raw_iq_file(str(tmp_path), "bpsk_fec.iq", sig, fs)
        out_dir = str(tmp_path / "out_e2e_002")

        result = pipeline.process_file(iq_file, output_dir=out_dir, fec_scheme="viterbi_k7")

        assert result.classification["predicted_class"] == "BPSK"
        assert len(result.frames) >= 1
        assert result.frames[0]["crc_valid"] is True

    def test_tc_e2e_003_fsk_with_deinterleaving_e2e(self, pipeline, tmp_path):
        """TC-E2E-003: FSK with de-interleaving E2E."""
        fs = 1.0e6
        payload = b"TELEMETRY_FSK_BLOCK"
        frame_bits = self._synthesize_frame_bits(0x03, 1, payload)

        # Block interleaver 8x16
        r, c = 8, 16
        block_size = r * c
        n_pad = (block_size - (len(frame_bits) % block_size)) % block_size
        padded_bits = np.pad(frame_bits, (0, n_pad))
        interleaved_bits = BlockInterleaver.interleave(padded_bits, r, c)

        # Synthesize 2-FSK signal
        f_dev = 50.0e3
        dt = 1.0 / fs
        # 4 samples per symbol
        sps = 4
        freq_seq = np.repeat(np.where(interleaved_bits == 1, f_dev, -f_dev), sps)
        repeats = int(np.ceil(4096 / len(freq_seq)))
        freq_long = np.tile(freq_seq, repeats)[:4096]
        phase = np.cumsum(2.0 * np.pi * freq_long * dt)
        sig = np.exp(1j * phase).astype(np.complex64)

        iq_file = self._create_raw_iq_file(str(tmp_path), "fsk_interleaved.iq", sig, fs)
        out_dir = str(tmp_path / "out_e2e_003")

        result = pipeline.process_file(iq_file, output_dir=out_dir, deinterleaver_config=(r, c))

        assert result.classification["predicted_class"] == "2-FSK"
        assert result.classification["confidence"] >= 0.70

    def test_tc_e2e_004_low_snr_qpsk_e2e(self, pipeline, tmp_path):
        """TC-E2E-004: Low-SNR E2E (5 dB QPSK)."""
        fs = 1.0e6
        sig = SyntheticSignalGenerator.generate_signal("QPSK", num_samples=4096, snr_db=5.0)

        iq_file = self._create_raw_iq_file(str(tmp_path), "low_snr.iq", sig, fs)
        out_dir = str(tmp_path / "out_e2e_004")

        result = pipeline.process_file(iq_file, output_dir=out_dir)

        # Must flag low confidence
        assert result.classification["is_low_confidence"] is True
        # Parameters still extracted without crash
        assert result.parameters["snr_db"] < 10.0

    def test_tc_e2e_005_multi_signal_separation_e2e(self, pipeline, tmp_path):
        """TC-E2E-005: Multi-signal separation E2E (Multiple framed bursts)."""
        fs = 1.0e6
        frame1 = self._synthesize_frame_bits(0x10, 1, b"STREAM_ALPHA")
        frame2 = self._synthesize_frame_bits(0x20, 2, b"STREAM_BETA")
        multi_bits = np.concatenate([frame1, np.zeros(64, dtype=np.uint8), frame2])

        # Modulate to QPSK matching Demodulator Gray mapping
        b0 = multi_bits[0::2]
        b1 = multi_bits[1::2]
        mlen = min(len(b0), len(b1))
        real = np.where(b1[:mlen] == 1, -1.0, 1.0)
        imag = np.where(b0[:mlen] == 1, -1.0, 1.0)
        syms = (real + 1j * imag) / np.sqrt(2.0)
        sig = syms.astype(np.complex64)
        if len(sig) < 2048:
            repeats = int(np.ceil(2048 / len(sig)))
            sig = np.tile(sig, repeats)[:2048]

        iq_file = self._create_raw_iq_file(str(tmp_path), "multi_signal.iq", sig, fs)
        out_dir = str(tmp_path / "out_e2e_005")

        result = pipeline.process_file(iq_file, output_dir=out_dir)
        # Should identify multiple distinct frames
        assert len(result.frames) >= 2

    def test_tc_e2e_006_batch_processing_e2e(self, pipeline, tmp_path):
        """TC-E2E-006: Batch processing E2E across multiple recordings."""
        fs = 1.0e6
        f_list = []
        for i, mod in enumerate(["BPSK", "QPSK", "8-PSK"]):
            sig = SyntheticSignalGenerator.generate_signal(mod, num_samples=2048, snr_db=20.0)
            fp = self._create_raw_iq_file(str(tmp_path), f"batch_{mod.lower()}.iq", sig, fs)
            f_list.append(fp)

        out_dir = str(tmp_path / "batch_out")
        batch_res = pipeline.process_batch(f_list, output_dir=out_dir)

        assert batch_res["total_files"] == 3
        assert os.path.exists(batch_res["manifest_path"])
        assert len(batch_res["items"]) == 3
        assert all(item["status"] == "SUCCESS" for item in batch_res["items"])

    def test_tc_e2e_007_persistence_reload_e2e(self, pipeline, tmp_path):
        """TC-E2E-007: Result persistence and reload consistency."""
        sig = SyntheticSignalGenerator.generate_signal("QPSK", num_samples=2048, snr_db=20.0)
        iq_file = self._create_raw_iq_file(str(tmp_path), "persist.iq", sig, 1.0e6)
        out_dir = str(tmp_path / "persist_out")

        res = pipeline.process_file(iq_file, output_dir=out_dir)
        json_path = res.exported_files["json"]

        from ntro_sigint.core.exporter import ResultStore
        loaded = ResultStore.load_json(json_path)

        assert loaded["parameters"]["symbol_rate"] == res.parameters["symbol_rate"]
        assert loaded["modulation_classification"]["predicted_class"] == res.classification["predicted_class"]

    def test_tc_e2e_008_model_version_traceability_e2e(self, pipeline, tmp_path):
        """TC-E2E-008: Model version traceability in outputs."""
        sig = SyntheticSignalGenerator.generate_signal("QPSK", num_samples=2048, snr_db=20.0)
        iq_file = self._create_raw_iq_file(str(tmp_path), "trace.iq", sig, 1.0e6)
        out_dir = str(tmp_path / "trace_out")

        res = pipeline.process_file(iq_file, output_dir=out_dir)
        from ntro_sigint.core.exporter import ResultStore
        loaded = ResultStore.load_json(res.exported_files["json"])

        assert loaded["metadata"]["model_version"] == "amc_resnet18_v1.0"

    def test_tc_e2e_009_failed_decoder_partial_report_e2e(self, pipeline, tmp_path):
        """TC-E2E-009: Failed decoder partial report on corrupted frame."""
        payload = b"INTENTIONALLY_CORRUPTED_TRAILER_PACKET"
        frame_bits = self._synthesize_frame_bits(0x99, 1, payload)

        # Corrupt CRC trailer bits (last 16 bits)
        frame_bits[-8:] = 1 - frame_bits[-8:]

        # Modulate to BPSK
        bpsk_syms = 2 * frame_bits.astype(np.float32) - 1.0
        repeats = int(np.ceil(4096 / len(bpsk_syms)))
        sig = np.tile(bpsk_syms, repeats)[:4096].astype(np.complex64)

        iq_file = self._create_raw_iq_file(str(tmp_path), "corrupted_crc.iq", sig, 1.0e6)
        out_dir = str(tmp_path / "corrupt_out")

        res = pipeline.process_file(iq_file, output_dir=out_dir)
        assert len(res.frames) >= 1
        # CRC valid is False, flagged appropriately without pipeline failure
        assert res.frames[0]["crc_valid"] is False

    def test_tc_e2e_010_repeated_analysis_isolation_e2e(self, pipeline, tmp_path):
        """TC-E2E-010: Repeated analysis runs remain isolated without memory bleeding."""
        sig1 = SyntheticSignalGenerator.generate_signal("BPSK", num_samples=2048, snr_db=20.0, random_seed=1)
        sig2 = SyntheticSignalGenerator.generate_signal("16-QAM", num_samples=2048, snr_db=20.0, random_seed=2)

        f1 = self._create_raw_iq_file(str(tmp_path), "iso_bpsk.iq", sig1, 1.0e6)
        f2 = self._create_raw_iq_file(str(tmp_path), "iso_qam.iq", sig2, 1.0e6)

        res1 = pipeline.process_file(f1, output_dir=str(tmp_path / "iso1"))
        res2 = pipeline.process_file(f2, output_dir=str(tmp_path / "iso2"))

        assert res1.classification["predicted_class"] == "BPSK"
        assert "QAM" in res2.classification["predicted_class"]
        assert res1.input_file != res2.input_file
